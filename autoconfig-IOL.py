import telnetlib
import os
import glob
from time import sleep
import subprocess
import sys

lab_file = sys.argv[1]
grep = "grep \'node id" + "\|interface\' " + lab_file
filter_node = subprocess.check_output(grep, shell=True)
list_node = filter_node.splitlines()
filename = str()
node_type = None
###### change host IP A.B.C.D to your eve-ng IP
HOST = "A.B.C.D" 
PORT = "32769"

for line in list_node:
    words = line.split()
    if len(words)!=5:
       id = words[1].replace("id=","")
       id = id.replace("\"","")
    else:
        intf_id = words[4].replace("network","")
        intf_id = intf_id.replace("_id=","")
        intf_id = intf_id.replace("\"","")
        intf_id = intf_id.replace('/>',"")
        temp_file = intf_id + ".temp"
        file = open(temp_file, "a")  
        file.write(id+".")    

for line in list_node:
    words = line.split()
    if len(words)==5:
        interface = words[2].replace("name=","")
        interface = interface.replace("\"","")
        
        intf_id = words[4].replace("network","")
        intf_id = intf_id.replace("_id=","")
        intf_id = intf_id.replace("\"","")
        intf_id = intf_id.replace('/>',"")

        temp_file = intf_id + ".temp"
        network_id_file = open(temp_file,"r")
        network_id = network_id_file.readline()
        network_id_file.close()

        file = open(filename, "a")
        if node_type != "Switch.png":
           file.write("interface " + str(interface) + "\n")
           if node_type == "Switch":
             file.write(" no switchport\n")
           file.write(" ip address 10." + network_id + id + " 255.255.255.0\n")
        if node_type == "Router.png":
           file.write(" no shutdown\n")
        file.write("!\n")
    else:
        id = words[1].replace("id=","")
        id = id.replace("\"","")
        name = words[2].replace("name=","")
        name = name.replace("\"","")
        node_type = words[12].replace("icon=","")
        node_type = node_type.replace("\"","")
        filename = name + ".cfg"
        LoADDR = id + "." + id + "." + id + "." + id
    	file = open(filename, "a")
        file.write("username cisco priv 15 secret cisco\n!\n")
    	file.write("hostname " + name + "\n!\n")
        file.write("ip domain-name cisco.com\n!\n")
        if node_type !="Switch.png":
            file.write("interface Loopback0\n")
    	    file.write(" ip address " + LoADDR + " 255.255.255.255" "\n")
        file.write("!\n")
    file.close()

print "Config files successfully created....Please wait while sending initial config to Nodes"

####    remove temp file #############
for temp_file in glob.glob("*.temp"):
    os.remove(temp_file)
######################################


for line in list_node:
  words = line.split()
  if len(words)!=5:
    id = words[1].replace("id=","")
    id = id.replace("\"","")
    name = words[2].replace("name=","")
    name = name.replace("\"","")
    node_type = words[12].replace("icon=","")
    node_type = node_type.replace("\"","")

    node_id = int(id) - 1
    PORT = 32769 + node_id
    Router = telnetlib.Telnet(HOST,PORT)
    print ("Connected to.... " + name) 
    Router.write("\r")
    Router.write("\r")
    if node_type != "Router.png":
        Router.read_until("Switch>")
    else:
        Router.read_until("Would you like to enter the initial configuration dialog? [yes/no]: ")
        Router.write("no\r")
        sleep(12)
        Router.write("\r")
        Router.read_until("Router>")
    Router.write("enable\r")
    Router.write("conf t\r")
    filename = name + ".cfg"
    file = open(filename, "a")

    if node_type != "Router.png":
       file.write("ip routing\n!\n")
    file.write("line vty 0 4\n")
    file.write(" login local\n")
    file.write(" transport input ssh\n")
    file.write("end\n")
    file.close()
    file = open(filename, "r")
    for command in file:
      Router.write( command + "\r")
      sleep(0.1)
    file.close()
    Router.write("conf t\r")
    Router.write("crypto key generate rsa\r")
    Router.read_until("How many bits in the modulus [512]:")
    Router.write("1024\r")
    Router.write("end\r")
    print ("initial config " + name + " DONE")

print ("initial config COMPLETED")

############### 
##############  YOU MAY WANT MODIFIED THE CODE TO REMOVE CFG FILE GENERATED
