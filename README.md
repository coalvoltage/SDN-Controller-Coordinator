# SDN-Controller-Coordinator

This project is the Jeffery Lai's and Jimmy Im's senior design for CS197I. The goal of this project is to research and create a SDN controller to mitigate failures. This is done using the POX library.


Instructions
1. Install mininet vm according to the [mininet website](http://mininet.org/download/#option-1-mininet-vm-installation-easy-recommended)

2. Add the SDN script to a readable location
     1. cd ~/pox/pox/misc
     2. move the file "sdn_controller.py" here
     3. cd ~/pox

3. Start the controller with the following:

``sudo ./pox.py   openflow.spanning_forest   log.level --DEBUG samples.pretty_log   openflow.discovery misc.sdn_controller host_tracker   info.packet_dump``

4. Get the fattree topology using this (In the VM window):
    1. cd ~/mininet/custom
    2. wget https://raw.githubusercontent.com/panandr/mininet-fattree/master/fattree.py
5. To start the topology, use the following:

``sudo python2  `which mn` --custom ~/mininet/custom/fattree.py --topo fattree,4 --mac --switch ovsk --controller remote,ip=0.0.0.0:6633``

