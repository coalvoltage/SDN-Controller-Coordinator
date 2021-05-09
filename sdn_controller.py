from pox.core import core
import pox.openflow.libopenflow_01 as of
import pox.openflow.discovery as ds
import time
try:    
    import thread 
except ImportError:
    import _thread as thread
log = core.getLogger()

class SDNControllerFat (object):
  def __init__ (self, connection):
    self.connection = connection
    connection.addListeners(self)
    self.mac_to_port = {}


  def resend_packet (self, packet_in, out_port):
    msg = of.ofp_packet_out()
    msg.data = packet_in

    action = of.ofp_action_output(port = out_port)
    msg.actions.append(action)

    self.connection.send(msg)
  
  
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
        
    if event.port == 1:
        msg = of.ofp_flow_mod()
        msg.match = of.ofp_match.from_packet(packet)
        msg.idle_timeout = 10
        msg.hard_timeout = 10
        msg.buffer_id = packet_in.buffer_id
        self.connection.send(msg)
        sourceMessage = "Drop port 1: Source: " + str(packet.src) +  ", Dest: " + str(packet.dst) + ", Port:" + str(packet_in.in_port)
        log.debug(sourceMessage)
        
        return
        
    if str(event.parsed.dst) == "00:00:00:00:00:04" or str(event.parsed.src) == "00:00:00:00:00:04":
        msg = of.ofp_flow_mod()
        msg.match = of.ofp_match.from_packet(packet)
        msg.idle_timeout = 10
        msg.hard_timeout = 10
        msg.buffer_id = packet_in.buffer_id
        self.connection.send(msg)
        sourceMessage = "Drop Mac: Source: " + str(packet.src) +  ", Dest: " + str(packet.dst) + ", Port:" + str(packet_in.in_port)
        log.debug(sourceMessage)
        
        return
        
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
      
      sourceMessage = "Source: " + str(packet.src) +  ", Dest: " + str(packet.dst) + ", Port:" + str(packet_in.in_port)
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
    log.debug(event.link.dpid1)
    log.debug(event.link.port1)
    log.debug(event.link.dpid2)
    log.debug(event.link.port2)
def launch ():
  """
  Starts the component
  """
  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    SDNControllerFat(event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)
  core.openflow_discovery.addListenerByName("LinkEvent", print_time)
  #core.Discovery.addListenerByName("LinkEvent", print_time())
