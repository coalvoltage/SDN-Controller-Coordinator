# SDN-Controller-Coordinator
Instructions so far:
1. Install mininet vm according to the [mininet website](http://mininet.org/download/#option-1-mininet-vm-installation-easy-recommended)
2. Get the fattree topology using this:
    cd ~/mininet/custom
    wget https://github.com/panandr/mininet-fattree
To start the topology, use the following:

``sudo python2  `which mn` --custom ~/mininet/custom/fattree.py --topo fattree,4 --mac --switch ovsk --controller remote,ip=<insert ip here>``
