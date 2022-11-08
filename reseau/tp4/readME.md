# TP4 : TCP, UDP et services réseau

Dans ce TP on va explorer un peu les protocoles TCP et UDP. 

**La première partie est détente**, vous explorez TCP et UDP un peu, en vous servant de votre PC.

La seconde partie se déroule en environnement virtuel, avec des VMs. Les VMs vont nous permettre en place des services réseau, qui reposent sur TCP et UDP.  
**Le but est donc de commencer à mettre les mains de plus en plus du côté administration, et pas simple client.**

Dans cette seconde partie, vous étudierez donc :

- le protocole SSH (contrôle de machine à distance)
- le protocole DNS (résolution de noms)
  - essentiel au fonctionnement des réseaux modernes

![TCP UDP](./pics/tcp_udp.jpg)

# Sommaire

- [TP4 : TCP, UDP et services réseau](#tp4--tcp-udp-et-services-réseau)
- [Sommaire](#sommaire)
- [0. Prérequis](#0-prérequis)
- [I. First steps](#i-first-steps)
- [II. Mise en place](#ii-mise-en-place)
  - [1. SSH](#1-ssh)
  - [2. Routage](#2-routage)
- [III. DNS](#iii-dns)
  - [1. Présentation](#1-présentation)
  - [2. Setup](#2-setup)
  - [3. Test](#3-test)

# 0. Prérequis

➜ Pour ce TP, on va se servir de VMs Rocky Linux. On va en faire plusieurs, n'hésitez pas à diminuer la RAM (512Mo ou 1Go devraient suffire). Vous pouvez redescendre la mémoire vidéo aussi.  

➜ Si vous voyez un 🦈 c'est qu'il y a un PCAP à produire et à mettre dans votre dépôt git de rendu

➜ **L'emoji 🖥️ indique une VM à créer**. Pour chaque VM, vous déroulerez la checklist suivante :

- [x] Créer la machine (avec une carte host-only)
- [x] Définir une IP statique à la VM
- [x] Donner un hostname à la machine
- [x] Vérifier que l'accès SSH fonctionnel
- [x] Vérifier que le firewall est actif
- [x] Remplir votre fichier `hosts`, celui de votre PC, pour accéder au VM avec un nom
- [x] Dès que le routeur est en place, n'oubliez pas d'ajouter une route par défaut aux autres VM pour qu'elles aient internet

> Toutes les commandes pour réaliser ces opérations sont dans [le mémo Rocky](../../cours/memo/rocky_network.md). Aucune de ces étapes ne doit figurer dan le rendu, c'est juste la mise en place de votre environnement de travail.

# I. First steps

Faites-vous un petit top 5 des applications que vous utilisez sur votre PC souvent, des applications qui utilisent le réseau : un site que vous visitez souvent, un jeu en ligne, Spotify, j'sais po moi, n'importe.

🌞 **Déterminez, pour ces 5 applications, si c'est du TCP ou de l'UDP**

- avec Wireshark, on va faire les chirurgiens réseau
- déterminez, pour chaque application :
  - IP et port du serveur auquel vous vous connectez
  - le port local que vous ouvrez pour vous connecter

```
Application 1 := Brawlhalla
ip dest : 199.229.253.221
port dest : 23002
port source : 52152

Application 2 := Among Us
ip dest : 35.244.189.74
port dest : 443
port source : 45770

Application 3 := VsCode
ip dest : 13.107.5.93
port dest : 443
port source : 43816

Application 4 := VrChat
ip dest : 104.18.32.143
port dest : 443
port source : 35250

Application 5 := Discord
ip dest : 35.186.224.47
port dest : 443
port source : 47654
```

> Dès qu'on se connecte à un serveur, notre PC ouvre un port random. Une fois la connexion TCP ou UDP établie, entre le port de notre PC et le port du serveur qui est en écoute, on parle de tunnel TCP ou de tunnel UDP.


> Aussi, TCP ou UDP ? Comment le client sait ? Il sait parce que le serveur a décidé ce qui était le mieux pour tel ou tel type de trafic (un jeu, une page web, etc.) et que le logiciel client est codé pour utiliser TCP ou UDP en conséquence.

🌞 **Demandez l'avis à votre OS**

- votre OS est responsable de l'ouverture des ports, et de placer un programme en "écoute" sur un port
- il est aussi responsable de l'ouverture d'un port quand une application demande à se connecter à distance vers un serveur
- bref il voit tout quoi
- utilisez la commande adaptée à votre OS pour repérer, dans la liste de toutes les connexions réseau établies, la connexion que vous voyez dans Wireshark, pour chacune des 5 applications

```
ESTAB          0               13                        10.33.18.115:52152                    199.229.253.221:inovaport3           users:(("BrawlhallaGame.",pid=27677,fd=83),("wineserver",pid=27554,fd=272)) 

ESTAB           0                0                           10.33.18.115:45770                       35.244.189.74:https           users:(("Among Us.exe",pid=29892,fd=347),("wineserver",pid=29821,fd=834))

ESTAB                  0                       0                                         10.33.18.115:43816                                      13.107.5.93:https                  users:(("code",pid=30866,fd=24)) 

ESTAB           0                0                           10.33.18.115:35258                       104.18.32.143:https           users:(("VRChat.exe",pid=36423,fd=353),("wineserver",pid=36282,fd=788))

ESTAB                      0                      0                                       10.33.18.115:47654                                   35.186.224.47:https                  users:(("Discord",pid=39053,fd=29)) 
```

**Il faudra ajouter des options adaptées aux commandes pour y voir clair. Pour rappel, vous cherchez des connexions TCP ou UDP.**

```
# MacOS
$ netstat

# GNU/Linux
$ ss

# Windows
$ netstat
```

🦈🦈🦈🦈🦈 **Bah ouais, captures Wireshark à l'appui évidemment.** Une capture pour chaque application, qui met bien en évidence le trafic en question.

# II. Mise en place

## 1. SSH

🖥️ **Machine `node1.tp4.b1`**

- n'oubliez pas de dérouler la checklist (voir [les prérequis du TP](#0-prérequis))
- donnez lui l'adresse IP `10.4.1.11/24`

Connectez-vous en SSH à votre VM.

🌞 **Examinez le trafic dans Wireshark**

- **déterminez si SSH utilise TCP ou UDP**
  - pareil réfléchissez-y deux minutes, logique qu'on utilise pas UDP non ?

```
tcp, on veut quelque chose de fiable, preuve dans le wireshark
```

- **repérez le *3-Way Handshake* à l'établissement de la connexion**
  - c'est le `SYN` `SYNACK` `ACK`
- **repérez du trafic SSH**
- **repérez le FIN FINACK à la fin d'une connexion**
- entre le *3-way handshake* et l'échange `FIN`, c'est juste une bouillie de caca chiffré, dans un tunnel TCP

```
tout dans le wireshark 
```

🌞 **Demandez aux OS**

- repérez, avec une commande adaptée (`netstat` ou `ss`), la connexion SSH depuis votre machine

```
ESTAB     0          0                   10.4.1.1:52794               10.4.1.11:ssh       users:(("ssh",pid=10234,fd=3)) 
```

- ET repérez la connexion SSH depuis votre VM

```
ESTAB    0         0                10.4.1.11:ssh              10.4.1.1:38044     
```

🦈 **Je veux une capture clean avec le 3-way handshake, un peu de trafic au milieu et une fin de connexion**

## 2. Routage

Ouais, un peu de répétition, ça fait jamais de mal. On va créer une machine qui sera notre routeur, et **permettra à toutes les autres machines du réseau d'avoir Internet.**

🖥️ **Machine `router.tp4.b1`**

- n'oubliez pas de dérouler la checklist (voir [les prérequis du TP](#0-prérequis))
- donnez lui l'adresse IP `10.4.1.11/24` sur sa carte host-only
- ajoutez-lui une carte NAT, qui permettra de donner Internet aux autres machines du réseau
- référez-vous au TP précédent

> Rien à remettre dans le compte-rendu pour cette partie.

# III. DNS

## 1. Présentation

Un serveur DNS est un serveur qui est capable de répondre à des requêtes DNS.

Une requête DNS est la requête effectuée par une machine lorsqu'elle souhaite connaître l'adresse IP d'une machine, lorsqu'elle connaît son nom.

Par exemple, si vous ouvrez un navigateur web et saisissez `https://www.google.com` alors une requête DNS est automatiquement effectuée par votre PC pour déterminez à quelle adresse IP correspond le nom `www.google.com`.

> La partie `https://` ne fait pas partie du nom de domaine, ça indique simplement au navigateur la méthode de connexion. Ici, c'est HTTPS.

Dans cette partie, on va monter une VM qui porte un serveur DNS. Ce dernier répondra aux autres VMs du LAN quand elles auront besoin de connaître des noms. Ainsi, ce serveur pourra :

- résoudre des noms locaux
  - vous pourrez `ping node1.tp4.b1` et ça fonctionnera
  - mais aussi `ping www.google.com` et votre serveur DNS sera capable de le résoudre aussi

*Dans la vraie vie, il n'est pas rare qu'une entreprise gère elle-même ses noms de domaine, voire gère elle-même son serveur DNS. C'est donc du savoir ré-utilisable pour tous qu'on voit ici.*

> En réalité, ce n'est pas votre serveur DNS qui pourra résoudre `www.google.com`, mais il sera capable de *forward* (faire passer) votre requête à un autre serveur DNS qui lui, connaît la réponse.

![Haiku DNS](./pics/haiku_dns.png)

## 2. Setup

🖥️ **Machine `dns-server.tp4.b1`**

- n'oubliez pas de dérouler la checklist (voir [les prérequis du TP](#0-prérequis))
- donnez lui l'adresse IP `10.4.1.201/24`

Installation du serveur DNS :

```bash
# assurez-vous que votre machine est à jour
$ sudo dnf update -y

# installation du serveur DNS, son p'tit nom c'est BIND9
$ sudo dnf install -y bind bind-utils
```

La configuration du serveur DNS va se faire dans 3 fichiers essentiellement :

- **un fichier de configuration principal**
  - `/etc/named.conf`
  - on définit les trucs généraux, comme les adresses IP et le port où on veu écouter
  - on définit aussi un chemin vers les autres fichiers, les fichiers de zone
- **un fichier de zone**
  - `/var/named/tp4.b1.db`
  - je vous préviens, la syntaxe fait mal
  - on peut y définir des correspondances `IP ---> nom`
- **un fichier de zone inverse**
  - `/var/named/tp4.b1.rev`
  - on peut y définir des correspondances `nom ---> IP`

➜ **Allooooons-y, fichier de conf principal**

```bash
# éditez le fichier de config principal pour qu'il ressemble à :
$ sudo cat /etc/named.conf
options {
        listen-on port 53 { 127.0.0.1; any; };
        listen-on-v6 port 53 { ::1; };
        directory       "/var/named";
[...]
        allow-query     { localhost; any; };
        allow-query-cache { localhost; any; };

        recursion yes;
[...]
# référence vers notre fichier de zone
zone "tp4.b1" IN {
     type master;
     file "tp4.b1.db";
     allow-update { none; };
     allow-query {any; };
};
# référence vers notre fichier de zone inverse
zone "1.4.10.in-addr.arpa" IN {
     type master;
     file "tp4.b1.rev";
     allow-update { none; };
     allow-query { any; };
};
```

➜ **Et pour les fichiers de zone**

```bash
# Fichier de zone pour nom -> IP

$ sudo cat /var/named/tp4.b1.db

$TTL 86400
@ IN SOA dns-server.tp4.b1. admin.tp4.b1. (
    2019061800 ;Serial
    3600 ;Refresh
    1800 ;Retry
    604800 ;Expire
    86400 ;Minimum TTL
)

; Infos sur le serveur DNS lui même (NS = NameServer)
@ IN NS dns-server.tp4.b1.

; Enregistrements DNS pour faire correspondre des noms à des IPs
dns-server IN A 10.4.1.201
node1      IN A 10.4.1.11
```

```bash
# Fichier de zone inverse pour IP -> nom

$ sudo cat /var/named/tp4.b1.rev

$TTL 86400
@ IN SOA dns-server.tp4.b1. admin.tp4.b1. (
    2019061800 ;Serial
    3600 ;Refresh
    1800 ;Retry
    604800 ;Expire
    86400 ;Minimum TTL
)

; Infos sur le serveur DNS lui même (NS = NameServer)
@ IN NS dns-server.tp4.b1.

;Reverse lookup for Name Server
201 IN PTR dns-server.tp4.b1.
11 IN PTR node1.tp4.b1.
```

➜ **Une fois ces 3 fichiers en place, démarrez le service DNS**

```bash
# Démarrez le service tout de suite
$ sudo systemctl start named

# Faire en sorte que le service démarre tout seul quand la VM s'allume
$ sudo systemctl enable named

# Obtenir des infos sur le service
$ sudo systemctl status named

# Obtenir des logs en cas de probème
$ sudo journalctl -xe -u named
```

🌞 **Dans le rendu, je veux**

- un `cat` des fichiers de conf

```
[alexlinux@tp4 ~]$ sudo cat /etc/named.conf 
//
// named.conf
//
// Provided by Red Hat bind package to configure the ISC BIND named(8) DNS
// server as a caching only nameserver (as a localhost DNS resolver only).
//
// See /usr/share/doc/bind*/sample/ for example named configuration files.
//

options {
	listen-on port 53 { 127.0.0.1; any; };
        listen-on-v6 port 53 { ::1; };
        directory       "/var/named";
	dump-file 	"/var/named/data/cache_dump.db";
	statistics-file "/var/named/data/named_stats.txt";
	memstatistics-file "/var/named/data/named_mem_stats.txt";
	secroots-file	"/var/named/data/named.secroots";
	recursing-file	"/var/named/data/named.recursing";

	allow-query     { localhost; any; };
        allow-query-cache { localhost; any; };

        recursion yes;

	/* 
	 - If you are building an AUTHORITATIVE DNS server, do NOT enable recursion.
	 - If you are building a RECURSIVE (caching) DNS server, you need to enable 
	   recursion. 
	 - If your recursive DNS server has a public IP address, you MUST enable access 
	   control to limit queries to your legitimate users. Failing to do so will
	   cause your server to become part of large scale DNS amplification 
	   attacks. Implementing BCP38 within your network would greatly
	   reduce such attack surface 
	*/

	dnssec-validation yes;

	managed-keys-directory "/var/named/dynamic";
	geoip-directory "/usr/share/GeoIP";

	pid-file "/run/named/named.pid";
	session-keyfile "/run/named/session.key";

	/* https://fedoraproject.org/wiki/Changes/CryptoPolicy */
	include "/etc/crypto-policies/back-ends/bind.config";
};

logging {
        channel default_debug {
                file "data/named.run";
                severity dynamic;
        };
};

zone "." IN {
	type hint;
	file "named.ca";
};

include "/etc/named.rfc1912.zones";
include "/etc/named.root.key";

zone "tp4.b1" IN {
     type master;
     file "tp4.b1.db";
     allow-update { none; };
     allow-query {any; };
};
# référence vers notre fichier de zone inverse
zone "1.4.10.in-addr.arpa" IN {
     type master;
     file "tp4.b1.rev";
     allow-update { none; };
     allow-query { any; };
};

```

```
[alexlinux@tp4 ~]$ sudo cat /var/named/tp4.b1.db
$TTL 86400
@ IN SOA dns-server.tp4.b1. admin.tp4.b1. (
    2019061800 ;Serial
    3600 ;Refresh
    1800 ;Retry
    604800 ;Expire
    86400 ;Minimum TTL
)

; Infos sur le serveur DNS lui même (NS = NameServer)
@ IN NS dns-server.tp4.b1.

; Enregistrements DNS pour faire correspondre des noms à des IPs
dns-server IN A 10.4.1.201
node1      IN A 10.4.1.11
```

```
[alexlinux@tp4 ~]$ sudo cat /var/named/tp4.b1.rev
$TTL 86400
@ IN SOA dns-server.tp4.b1. admin.tp4.b1. (
    2019061800 ;Serial
    3600 ;Refresh
    1800 ;Retry
    604800 ;Expire
    86400 ;Minimum TTL
)

; Infos sur le serveur DNS lui même (NS = NameServer)
@ IN NS dns-server.tp4.b1.

;Reverse lookup for Name Server
201 IN PTR dns-server.tp4.b1.
11 IN PTR node1.tp4.b1.

```

- un `systemctl status named` qui prouve que le service tourne bien

```
[alexlinux@tp4 ~]$ systemctl status named
● named.service - Berkeley Internet Name Domain (DNS)
     Loaded: loaded (/usr/lib/systemd/system/named.service; enabled; vendor preset: disabled)
     Active: active (running) since Tue 2022-10-25 17:02:53 CEST; 3min 42s ago
   Main PID: 1269 (named)
      Tasks: 5 (limit: 5908)
     Memory: 19.3M
        CPU: 52ms
     CGroup: /system.slice/named.service
             └─1269 /usr/sbin/named -u named -c /etc/named.conf

Oct 25 17:02:53 tp4.b1 named[1269]: network unreachable resolving './NS/IN': 2001:7fe::53#53
Oct 25 17:02:53 tp4.b1 named[1269]: zone localhost/IN: loaded serial 0
Oct 25 17:02:53 tp4.b1 named[1269]: zone tp4.b1/IN: loaded serial 2019061800
Oct 25 17:02:53 tp4.b1 named[1269]: all zones loaded
Oct 25 17:02:53 tp4.b1 systemd[1]: Started Berkeley Internet Name Domain (DNS).
Oct 25 17:02:53 tp4.b1 named[1269]: running
Oct 25 17:02:53 tp4.b1 named[1269]: network unreachable resolving './DNSKEY/IN': 2001:500:2::c#53
Oct 25 17:02:53 tp4.b1 named[1269]: network unreachable resolving './DNSKEY/IN': 2001:503:ba3e::2:30#53
Oct 25 17:02:53 tp4.b1 named[1269]: managed-keys-zone: Initializing automatic trust anchor management for zone '.'; D>
Oct 25 17:02:53 tp4.b1 named[1269]: resolver priming query complete
```

- une commande `ss` qui prouve que le service écoute bien sur un port

```                                         [::1]:53                                           [::]:*                    users:(("named",pid=1269,fd=22))                
tcp                  LISTEN                0                      10                                        10.4.1.201:53                                        0.0.0.0:*                    users:(("named",pid=1269,fd=21))                
```

🌞 **Ouvrez le bon port dans le firewall**

- grâce à la commande `ss` vous devrez avoir repéré sur quel port tourne le service

```
53
```

  - vous l'avez écrit dans la conf aussi toute façon :)
- ouvrez ce port dans le firewall de la machine `dns-server.tp4.b1` (voir le mémo réseau Rocky)

```
[alexlinux@tp4 ~]$ sudo firewall-cmd --add-port=53/udp 
success
[alexlinux@tp4 ~]$ sudo firewall-cmd --add-port=53/udp --permanent
success
```

## 3. Test

🌞 **Sur la machine `node1.tp4.b1`**

- configurez la machine pour qu'elle utilise votre serveur DNS quand elle a besoin de résoudre des noms
- assurez vous que vous pouvez :
  - résoudre des noms comme `node1.tp4.b1` et `dns-server.tp4.b1`

```
[alexlinux@rock11 ~]$ ping node1.tp4.b1
PING node1.tp4.b1 (10.4.1.11) 56(84) bytes of data.
64 bytes from node1.tp4.b1 (10.4.1.11): icmp_seq=1 ttl=64 time=0.189 ms
64 bytes from node1.tp4.b1 (10.4.1.11): icmp_seq=2 ttl=64 time=0.048 ms
```

```
[alexlinux@rock11 ~]$ ping dns-server.tp4.b1
PING dns-server.tp4.b1 (10.4.1.201) 56(84) bytes of data.
64 bytes from dns-server.tp4.b1 (10.4.1.201): icmp_seq=1 ttl=64 time=0.175 ms
64 bytes from dns-server.tp4.b1 (10.4.1.201): icmp_seq=2 ttl=64 time=1.33 ms
```

  - mais aussi des noms comme `www.google.com`

```
[alexlinux@rock11 ~]$ ping www.google.com
PING www.google.com (142.250.179.100) 56(84) bytes of data.
64 bytes from par21s20-in-f4.1e100.net (142.250.179.100): icmp_seq=1 ttl=61 time=24.9 ms
64 bytes from par21s20-in-f4.1e100.net (142.250.179.100): icmp_seq=2 ttl=61 time=47.5 ms
```

🌞 **Sur votre PC**

- utilisez une commande pour résoudre le nom `node1.tp4.b1` en utilisant `10.4.1.201` comme serveur DNS

```
[alexandrebel@DESKTOP-63CFBH0 ~]$ ping node1.tp4.b1
PING node1.tp4.b1 (10.4.1.11) 56(84) bytes of data.
64 bytes from 10.4.1.11 (10.4.1.11): irange loopeq=2 ttl=64 time=0.270 ms
```

```
[alexandrebel@DESKTOP-63CFBH0 ~]$ cat /etc/resolv.conf 
nameserver 10.4.1.201
```

> Le fait que votre serveur DNS puisse résoudre un nom comme `www.google.com`, ça s'appelle la récursivité et c'est activé avec la ligne `recursion yes;` dans le fichier de conf.

🦈 **Capture d'une requête DNS vers le nom `node1.tp4.b1` ainsi que la réponse**
