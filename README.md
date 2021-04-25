# SDN-Controller-Coordinator
Instructions so far:
1. Install mininet vm according to the [mininet website](http://mininet.org/download/#option-1-mininet-vm-installation-easy-recommended)
2. Replace the tutorial SDN controller (in a SSH window):
     1. cd ~/pox/pox/misc
     2. replace the file "of_tutorial.py" with this version
     3. cd ~/pox

3. Start the controller with the following:

``./pox.py log.level --DEBUG misc.of_tutorial``

4. Get the fattree topology using this (In the VM window):
    1. cd ~/mininet/custom
    2. wget https://github.com/panandr/mininet-fattree

5. To start the topology, use the following:

``sudo python2  `which mn` --custom ~/mininet/custom/fattree.py --topo fattree,4 --mac --switch ovsk --controller remote,ip=<insert ip here>``
