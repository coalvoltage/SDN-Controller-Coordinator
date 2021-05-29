from pox.core import core
import pox.openflow.libopenflow_01 as of
import pox.openflow.discovery as ds
import time
import math

try:    
    import thread 
except ImportError:
    import _thread as thread
log = core.getLogger()

#global
GLOBAL_SDN_CONTROLLER_LIST = []

class SDNControllerFat (object):
  def __init__ (self, connection):
    GLOBAL_SDN_CONTROLLER_LIST.append(self)
    self.connection = connection
    connection.addListeners(self)
    self.mac_to_port = {}

  def clear_tables(self):
    self.mac_to_port.clear()
  
  def resend_packet (self, packet_in, out_port):
    msg = of.ofp_packet_out()
    msg.data = packet_in

    action = of.ofp_action_output(port = out_port)
    msg.actions.append(action)

    self.connection.send(msg)
  
  def _handle_PortStatus(self, event):
    #If anything happens to the ports, assume table is compromised and delete table
    if event.modified or event.added or event.deleted:
        log.debug("Ports Modified")
            
        for i in GLOBAL_SDN_CONTROLLER_LIST:
            i.clear_tables() 
        
  def _handle_FlowRemoved(self, event):
    self.mac_to_port.clear()
  
  def _handle_PacketIn (self, event):
    """
    Handles packet in messages from the switch.
    """
    packet = event.parsed # This is the parsed packet data.
    if not packet.parsed:
      log.warning("Ignoring incomplete packet")
      return
    
    packet_in = event.ofp
    
    if str(packet.src) not in self.mac_to_port:
      self.mac_to_port[str(packet.src)] = packet_in.in_port
      isFirstTime = True
        
    if str(packet.src) == "00:00:00:00:00:01":
      log.debug("start: switch status")
      printList = []
      for i in core.openflow_discovery.adjacency:
        if ((core.openflow.getConnection(i.dpid1).ports[i.port1].config & of.OFPPC_NO_FLOOD) == 0) and ((core.openflow.getConnection(i.dpid2).ports[i.port2].config & of.OFPPC_NO_FLOOD) == 0) and (not ((i.dpid1, i.port1) in printList) and not ((i.dpid2, i.port2) in printList)) :
          if i.dpid1 < i.dpid2:
            dpidStringTemp = "Link:" + str(i.dpid1) + ",(" + str(i.port1) + ") " + str(i.dpid2)  + ",(" + str(i.port2) + ")"
          else:
            dpidStringTemp = "Link:" + str(i.dpid2) + ",(" + str(i.port2) + ") " + str(i.dpid1)  + ",(" + str(i.port1) + ")"
          printList.append((i.dpid1,i.port1))
          printList.append((i.dpid2,i.port2))
          log.debug(dpidStringTemp)
      printList.clear()
      log.debug("stop")
        
    if str(packet.dst) in self.mac_to_port:
      out_port = self.mac_to_port[str(packet.dst)]
      #drop packet if destination port = src port)
      if self.mac_to_port[str(packet.dst)] == event.port:
        msg = of.ofp_flow_mod()
        msg.match = of.ofp_match.from_packet(packet)
        msg.idle_timeout = 10
        msg.hard_timeout = 10
        msg.buffer_id = packet_in.buffer_id
        self.connection.send(msg)
        sourceMessage = "Drop: Source: " + str(packet.src) +  ", Dest: " + str(packet.dst) + ", Port:" + str(packet_in.in_port)
        log.debug(sourceMessage)
        
        return
      
      sourceMessage = str(event.dpid) + " Source: " + str(packet.src) +  ", Dest: " + str(packet.dst) + ", Port:" + str(packet_in.in_port)
      log.debug(sourceMessage)

      msg = of.ofp_flow_mod()
      msg.match = of.ofp_match.from_packet(packet)
      msg.data = packet_in
      #adjust these timeouts maybe i just guessed on these
      msg.idle_timeout = 10
      msg.hard_timeout = 60
      #do we need to set these two bottom lines
      msg.match.dl_src = packet.src
      msg.match.dl_dst = packet.dst
      msg.actions.append(of.ofp_action_output(port=out_port))
      self.connection.send(msg)
    else:
      self.resend_packet(packet_in, of.OFPP_FLOOD)
      
def print_time(event):
  if event.removed:
    log.debug("Link failure detected. Information below:")
    log.debug("dpid1: " + str(event.link.dpid1) + ", port1: " + str(event.link.port1) + ", dpid2: " + str(event.link.dpid2) + ", port2: " + str(event.link.port2))

def launch():
  """
  Starts the component
  """
  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    SDNControllerFat(event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)
  core.openflow_discovery.addListenerByName("LinkEvent", print_time)
  #core.Discovery.addListenerByName("LinkEvent", print_time())
