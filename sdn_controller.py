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

class Node ():
  def __init__(self, dpid):
    self.dpid = dpid
    self.links = {}

class Manager():
  def __init__(self):
    self.activeSwitches = {}
    self.topology = {}
    
  def addSwitch(self, dpid):
    self.activeSwitches[dpid] = Node(dpid)
    #self.updateTopo(self.activeSwitches[dpid])
    
  def addLink(self, dpid1, dpid2, port1, port2):
    self.activeSwitches[dpid1].links[dpid2] = (port2, True)
    self.activeSwitches[dpid2].links[dpid1] = (port1, True)
    #self.updateTopo(self.activeSwitches[dpid1])
    
  def removeLink(self, dpid1, dpid2):
    if dpid1 in self.activeSwitches:
        self.activeSwitches[dpid1].links.pop(dpid2, default = None)
    if dpid2 in self.activeSwitches:
        self.activeSwitches[dpid2].links.pop(dpid1, default = None)
    
    #if self.activeSwitches[dpid1]:
    #  self.updateTopo(self.activeSwitches[dpid1])
    #else:
    #  self.updateTopo(self.activeSwitches[dpid2])
    
  def enableLink(self, dpid1, dpid2):
    self.activeSwitches[dpid1].links[dpid2] = (self.activeSwitches[dpid1].links[dpid2][0], True)
    self.activeSwitches[dpid2].links[dpid1] = (self.activeSwitches[dpid1].links[dpid2][1], True)
    
  def disableLink(self, dpid1, dpid2):
    self.activeSwitches[dpid1].links[dpid2] = (self.activeSwitches[dpid1].links[dpid2][0], False)
    self.activeSwitches[dpid2].links[dpid1] = (self.activeSwitches[dpid1].links[dpid2][1], False)

  def updateTopo(self, node):
    shortestSet = []
    previousKey = {}
    initalDistance = {}
    switchesAvaliable = self.activeSwitches.keys()
    
    for i in switchesAvaliable:
      initalDistance[i] = math.inf
    
    initalDistance[node.dpid] = 0
    
    while not all(item in shortestSet for item in switchesAvaliable):
      minVal = math.inf
      newKey = 0
      for key in initalDistance:
        if initalDistance[key] < minVal and key not in shortestSet:
          minVal = initalDistance[key]
          newKey = key
      shortestSet.append(newKey)        
        
      for i in self.activeSwitches[newKey].links.keys():
        tempVal = minVal + 1
        if tempVal < initalDistance[i]:
          initalDistance = tempVal
          previousKey[i] = newKey
                
    for i in self.activeSwitches.keys():
      for j in self.activeSwitches[i].links.keys():
        self.disableLink(i, j)
            
    for i in self.activeSwitches.keys():
      if previousKey[i] != None:
        self.enableLink(i, previousKey[i])
        
    def printTree()
        
        
        


#global class
globalManager = Manager()
GLOBAL_SDN_CONTROLLER_LIST = []

class SDNControllerFat (object):
  def __init__ (self, connection):
    GLOBAL_SDN_CONTROLLER_LIST.append(self)
    self.connection = connection
    connection.addListeners(self)
    self.mac_to_port = {}

  def clear_tables(self):
    self.mac_to_port.clear()
    #log.debug("I am clearing")
  
  def resend_packet (self, packet_in, out_port):
    msg = of.ofp_packet_out()
    msg.data = packet_in

    action = of.ofp_action_output(port = out_port)
    msg.actions.append(action)

    self.connection.send(msg)
  
  def _handle_PortStatus(self, event):
    #If anything happens to the ports, assume table is compromised and delete table
    if event.modified:
        tempString = "Port :" + str(event.port) + " has been modified"
        log.debug(tempString)
        
    if event.deleted:
        tempString = "Port :" + str(event.port) + " has been deleted"
        log.debug(tempString)
    
    if event.modified or event.added or event.deleted:
        #self.mac_to_port.clear()
        log.debug("Ports Modified")
        #msg = of.ofp_flow_mod(command = of.OFPFC_DELETE)
        #msg2 = of.ofp_flow_mod(flags = of.OFPFF_SEND_FLOW_REM )
        
        #for i in GLOBAL_SDN_CONTROLLER_LIST:
            #connection.send(msg)
            #connection.send(msg2)
            #log.debug("Clearing all flows from %s." % (str(connection.dpid),))
            
        for i in GLOBAL_SDN_CONTROLLER_LIST:
            i.clear_tables() 
            #i.connection.send(msg)
        
  def _handle_FlowRemoved(self, event):
    #log.debug("Clearing all flows from %s." % (str(self.connection.dpid),))
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
      #for i in globalManager.activeSwitches[event.dpid].links:
      #  if i[1] == True:
      #      self.resend_packet(packet_in, i[0])
      
def print_time(event):
  if event.removed:
    log.debug("Link failure detected. Information below:")
    log.debug(event.link.dpid1)
    log.debug(event.link.port1)
    log.debug(event.link.dpid2)
    log.debug(event.link.port2)
    globalManager.removeLink(event.link.dpid1, event.link.dpid2)
  else:
    globalManager.addLink(event.link.dpid1, event.link.dpid2, event.link.port1, event.link.port2)

def launch():
  """
  Starts the component
  """
  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    globalManager.addSwitch(event.dpid)
    SDNControllerFat(event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)
  core.openflow_discovery.addListenerByName("LinkEvent", print_time)
  
  #core.Discovery.addListenerByName("LinkEvent", print_time())
