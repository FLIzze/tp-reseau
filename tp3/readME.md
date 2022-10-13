# TP3 : On va router des trucs

Au menu de ce TP, on va revoir un peu ARP et IP histoire de **se mettre en jambes dans un environnement avec des VMs**.

Puis on mettra en place **un routage simple, pour permettre à deux LANs de communiquer**.

![Reboot the router](./pics/reboot.jpeg)

## Sommaire

- [TP3 : On va router des trucs](#tp3--on-va-router-des-trucs)
  - [Sommaire](#sommaire)
  - [0. Prérequis](#0-prérequis)
  - [I. ARP](#i-arp)
    - [1. Echange ARP](#1-echange-arp)
    - [2. Analyse de trames](#2-analyse-de-trames)
  - [II. Routage](#ii-routage)
    - [1. Mise en place du routage](#1-mise-en-place-du-routage)
    - [2. Analyse de trames](#2-analyse-de-trames-1)
    - [3. Accès internet](#3-accès-internet)
  - [III. DHCP](#iii-dhcp)
    - [1. Mise en place du serveur DHCP](#1-mise-en-place-du-serveur-dhcp)
    - [2. Analyse de trames](#2-analyse-de-trames-2)

## 0. Prérequis

➜ Pour ce TP, on va se servir de VMs Rocky Linux. 1Go RAM c'est large large. Vous pouvez redescendre la mémoire vidéo aussi.  

➜ Vous aurez besoin de deux réseaux host-only dans VirtualBox :

- un premier réseau `10.3.1.0/24`
- le second `10.3.2.0/24`
- **vous devrez désactiver le DHCP de votre hyperviseur (VirtualBox) et définir les IPs de vos VMs de façon statique**

➜ Les firewalls de vos VMs doivent **toujours** être actifs (et donc correctement configurés).

➜ **Si vous voyez le p'tit pote 🦈 c'est qu'il y a un PCAP à produire et à mettre dans votre dépôt git de rendu.**

## I. ARP

Première partie simple, on va avoir besoin de 2 VMs.

| Machine  | `10.3.1.0/24` |
|----------|---------------|
| `john`   | `10.3.1.11`   |
| `marcel` | `10.3.1.12`   |

```schema
   john               marcel
  ┌─────┐             ┌─────┐
  │     │    ┌───┐    │     │
  │     ├────┤ho1├────┤     │
  └─────┘    └───┘    └─────┘
```

> Référez-vous au [mémo Réseau Rocky](../../cours/memo/rocky_network.md) pour connaître les commandes nécessaire à la réalisation de cette partie.

### 1. Echange ARP

🌞**Générer des requêtes ARP**

- effectuer un `ping` d'une machine à l'autre

```
[alexlinux@localhost ~]$ ping 10.3.1.12
PING 10.3.1.12 (10.3.1.12) 56(84) bytes of data.
64 bytes from 10.3.1.12: icmp_seq=1 ttl=64 time=0.785 ms
64 bytes from 10.3.1.12: icmp_seq=2 ttl=64 time=1.11 ms
^C
--- 10.3.1.12 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1001ms
rtt min/avg/max/mdev = 0.785/0.945/1.105/0.160 ms
```

- observer les tables ARP des deux machines

```
link/ether 08:00:27:c4:f6:64 brd ff:ff:ff:ff:ff:ff
    inet 10.3.1.11/24 scope global enp0s8
link/ether 08:00:27:63:f3:35 brd ff:ff:ff:ff:ff:ff
    inet 10.3.1.12/24 scope global enp0s8
```

- repérer l'adresse MAC de `john` dans la table ARP de `marcel` et vice-versa

- prouvez que l'info est correcte (que l'adresse MAC que vous voyez dans la table est bien celle de la machine correspondante)
  - une commande pour voir la MAC de `marcel` dans la table ARP de `john`

```
[alexlinux@localhost ~]$ ip n s
10.3.1.12 dev enp0s8 lladdr 08:00:27:63:f3:35 STALE
```

  - et une commande pour afficher la MAC de `marcel`, depuis `marcel`

```
[alexlinux@localhost ~]$ ip a
2: enp0s8: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 08:00:27:63:f3:35 brd ff:ff:ff:ff:ff:ff
    inet 10.3.1.12/24 scope global enp0s8
```

### 2. Analyse de trames

🌞**Analyse de trames**

- utilisez la commande `tcpdump` pour réaliser une capture de trame
- videz vos tables ARP, sur les deux machines, puis effectuez un `ping`

```
ip neigh flush all
ping 10.3.1.12
```

🦈 **Capture réseau `tp3_arp.pcapng`** qui contient un ARP request et un ARP reply

```
00:20:48.257862 ARP, Request who-has 10.3.1.12 tell localhost.localdomain, length 28
00:20:48.258206 ARP, Reply 10.3.1.12 is-at 08:00:27:ff:c5:c3 (oui Unknown), length 46
```

> **Si vous ne savez pas comment récupérer votre fichier `.pcapng`** sur votre hôte afin de l'ouvrir dans Wireshark, et me le livrer en rendu, demandez-moi.

## II. Routage

Vous aurez besoin de 3 VMs pour cette partie. **Réutilisez les deux VMs précédentes.**

| Machine  | `10.3.1.0/24` | `10.3.2.0/24` |
|----------|---------------|---------------|
| `router` | `10.3.1.254`  | `10.3.2.254`  |
| `john`   | `10.3.1.11`   | no            |
| `marcel` | no            | `10.3.2.12`   |

> Je les appelés `marcel` et `john` PASKON EN A MAR des noms nuls en réseau 🌻

```schema
   john                router              marcel
  ┌─────┐             ┌─────┐             ┌─────┐
  │     │    ┌───┐    │     │    ┌───┐    │     │
  │     ├────┤ho1├────┤     ├────┤ho2├────┤     │
  └─────┘    └───┘    └─────┘    └───┘    └─────┘
```

### 1. Mise en place du routage

🌞**Activer le routage sur le noeud `router`**

> Cette étape est nécessaire car Rocky Linux c'est pas un OS dédié au routage par défaut. Ce n'est bien évidemment une opération qui n'est pas nécessaire sur un équipement routeur dédié comme du matériel Cisco.

```
[alexlinux@localhost ~]$ sudo firewall-cmd --add-masquerade --zone=public --permanent
Warning: ALREADY_ENABLED: masquerade
success
```

🌞**Ajouter les routes statiques nécessaires pour que `john` et `marcel` puissent se `ping`**

- il faut taper une commande `ip route add` pour cela, voir mémo
- il faut ajouter une seule route des deux côtés

```
[alexlinux@localhost ~]$ ip route add 10.3.2.0/24 via 10.3.1.254 dev enp0s8
RTNETLINK answers: Operation not permitted
[alexlinux@localhost ~]$ sudo !!
sudo ip route add 10.3.2.0/24 via 10.3.1.254 dev enp0s8

[alexlinux@localhost ~]$ sudo ip r add 10.3.1.0/24 via 10.3.2.254 dev enp0s8
```

- une fois les routes en place, vérifiez avec un `ping` que les deux machines peuvent se joindre

```
[alexlinux@localhost ~]$ ping 10.3.2.12
PING 10.3.2.12 (10.3.2.12) 56(84) bytes of data.
64 bytes from 10.3.2.12: icmp_seq=1 ttl=63 time=0.523 ms
64 bytes from 10.3.2.12: icmp_seq=2 ttl=63 time=0.599 ms
^C
--- 10.3.2.12 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1022ms
rtt min/avg/max/mdev = 0.523/0.561/0.599/0.038 ms

[alexlinux@localhost ~]$ ping 10.3.1.11
PING 10.3.1.11 (10.3.1.11) 56(84) bytes of data.
64 bytes from 10.3.1.11: icmp_seq=1 ttl=63 time=0.582 ms
64 bytes from 10.3.1.11: icmp_seq=2 ttl=63 time=0.625 ms
^C
--- 10.3.1.11 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1056ms
rtt min/avg/max/mdev = 0.582/0.603/0.625/0.021 ms
```

![THE SIZE](./pics/thesize.png)

### 2. Analyse de trames

🌞**Analyse des échanges ARP**

- videz les tables ARP des trois noeuds

```
[alexlinux@localhost ~]$ sudo ip n f all
```

- effectuez un `ping` de `john` vers `marcel`
- regardez les tables ARP des trois noeuds
- essayez de déduire un peu les échanges ARP qui ont eu lieu

```
john devrait faire un message de broadcast avec sa mac comme source et demande dans le reseau "qui a" la mac de l'ip qu'il essaye de ping et rajoute sa propre ip dans le message (request)

puis le routeur devrait lui repondre en lui envoyant son ip "est a" ainsi que son adresse mac (reply)

puis l'inverse devrait se produire dans la lan de destination avec le routeur qui fait la request
```

- répétez l'opération précédente (vider les tables, puis `ping`), en lançant `tcpdump` sur `marcel`
- **écrivez, dans l'ordre, les échanges ARP qui ont eu lieu, puis le ping et le pong, je veux TOUTES les trames** utiles pour l'échange

```
14:37:27.331054 ARP, Request who-has marcel tell 10.3.2.254, length 46
14:37:27.331079 ARP, Reply marcel is-at 08:00:27:ff:c5:c3 (oui Unknown), length 28
14:37:32.775352 ARP, Request who-has 10.3.2.254 tell marcel, length 28
14:37:32.775940 ARP, Reply 10.3.2.254 is-at 08:00:27:b2:1f:08 (oui Unknown), length 46

listening on enp0s8, link-type EN10MB (Ethernet), snapshot length 262144 bytes
14:41:36.952032 IP 10.3.2.254 > marcel: ICMP echo request, id 4, seq 1, length 64
14:41:36.952087 IP marcel > 10.3.2.254: ICMP echo reply, id 4, seq 1, length 64
14:41:37.953502 IP 10.3.2.254 > marcel: ICMP echo request, id 4, seq 2, length 64
```



> Vous pourriez, par curiosité, lancer la capture sur `john` aussi, pour voir l'échange qu'il a effectué de son côté.

🦈 **Capture réseau `tp3_routage_marcel.pcapng`**

### 3. Accès internet

🌞**Donnez un accès internet à vos machines**

- ajoutez une carte NAT en 3ème inteface sur le `router` pour qu'il ait un accès internet
- ajoutez une route par défaut à `john` et `marcel`
  - vérifiez que vous avez accès internet avec un `ping`
  - le `ping` doit être vers une IP, PAS un nom de domaine

```
[alexlinux@marcel ~]$ ip route add default via 10.3.2.254 dev enp0s8
RTNETLINK answers: Operation not permitted
[alexlinux@marcel ~]$ sudo !!
sudo ip route add default via 10.3.2.254 dev enp0s8
[sudo] password for alexlinux: 
[alexlinux@marcel ~]$ ping 1.1.1.1
PING 1.1.1.1 (1.1.1.1) 56(84) bytes of data.
64 bytes from 1.1.1.1: icmp_seq=1 ttl=61 time=50.5 ms
64 bytes from 1.1.1.1: icmp_seq=2 ttl=61 time=20.7 ms
^C
--- 1.1.1.1 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1002ms
rtt min/avg/max/mdev = 20.701/35.603/50.506/14.902 ms
```

- donnez leur aussi l'adresse d'un serveur DNS qu'ils peuvent utiliser

```
[alexlinux@localhost ~]$ cat /etc/resolv.conf 
# Generated by NetworkManager
nameserver 1.1.1.1
```

  - vérifiez que vous avez une résolution de noms qui fonctionne avec `dig`

```
[alexlinux@localhost ~]$ dig google.com

; <<>> DiG 9.16.23-RH <<>> google.com
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 30597
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 1232
;; QUESTION SECTION:
;google.com.			IN	A

;; ANSWER SECTION:
google.com.		231	IN	A	216.58.206.238

;; Query time: 33 msec
;; SERVER: 1.1.1.1#53(1.1.1.1)
;; WHEN: Thu Oct 13 17:05:52 CEST 2022
;; MSG SIZE  rcvd: 55
```

  - puis avec un `ping` vers un nom de domaine

```
[alexlinux@localhost ~]$ ping google.com
PING google.com (142.250.179.78) 56(84) bytes of data.
64 bytes from par21s19-in-f14.1e100.net (142.250.179.78): icmp_seq=1 ttl=61 time=25.0 ms
64 bytes from par21s19-in-f14.1e100.net (142.250.179.78): icmp_seq=2 ttl=61 time=23.3 ms
```

🌞**Analyse de trames**

- effectuez un `ping 8.8.8.8` depuis `john`
- capturez le ping depuis `john` avec `tcpdump`

```
istening on enp0s8, link-type EN10MB (Ethernet), snapshot length 262144 bytes
17:07:53.911126 IP localhost.localdomain > dns.google: ICMP echo request, id 5, seq 1, length 64
17:07:53.950821 IP dns.google > localhost.localdomain: ICMP echo reply, id 5, seq 1, length 64
```

- analysez un ping aller et le retour qui correspond et mettez dans un tableau :

```
17:25:08.255225 IP localhost.localdomain > dns.google: ICMP echo request, id 10, seq 1, length 64
17:25:08.301955 IP dns.google > localhost.localdomain: ICMP echo reply, id 10, seq 1, length 64
```

🦈 **Capture réseau `tp3_routage_internet.pcapng`**

## III. DHCP

On reprend la config précédente, et on ajoutera à la fin de cette partie une 4ème machine pour effectuer des tests.

| Machine  | `10.3.1.0/24`              | `10.3.2.0/24` |
|----------|----------------------------|---------------|
| `router` | `10.3.1.254`               | `10.3.2.254`  |
| `john`   | `10.3.1.11`                | no            |
| `bob`    | oui mais pas d'IP statique | no            |
| `marcel` | no                         | `10.3.2.12`   |

```schema
   john               router              marcel
  ┌─────┐             ┌─────┐             ┌─────┐
  │     │    ┌───┐    │     │    ┌───┐    │     │
  │     ├────┤ho1├────┤     ├────┤ho2├────┤     │
  └─────┘    └─┬─┘    └─────┘    └───┘    └─────┘
   john        │
  ┌─────┐      │
  │     │      │
  │     ├──────┘
  └─────┘
```

### 1. Mise en place du serveur DHCP

🌞**Sur la machine `john`, vous installerez et configurerez un serveur DHCP** (go Google "rocky linux dhcp server").

- installation du serveur sur `john`

```
> [alexlinux@localhost ~]$ sudo !!
sudo cat /etc/dhcp/dhcpd.conf
#
# DHCP Server Configuration file.
#   see /usr/share/doc/dhcp-server/dhcpd.conf.example
#   see dhcpd.conf(5) man page
#

default-lease-time 900;
max-lease-time 10800;
ddns-update-style none;
authoritative;
subnet 10.3.1.0 netmask 255.255.255.0 {
	range 10.3.1.2 10.3.1.252;
}
```

- créer une machine `bob`
- faites lui récupérer une IP en DHCP à l'aide de votre serveur

```
sur bob, ip directement donne par le dhcp
2: enp0s8: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 08:00:27:5a:9c:12 brd ff:ff:ff:ff:ff:ff
    inet 10.3.1.2/24 brd 10.3.1.255 scope global dynamic noprefixroute enp0s8
       valid_lft 544sec preferred_lft 544sec
    inet6 fe80::acf5:2ce2:c8f4:25a1/64 scope link noprefixroute 
       valid_lft forever preferred_lft forever
```

> Il est possible d'utilise la commande `dhclient` pour forcer à la main, depuis la ligne de commande, la demande d'une IP en DHCP, ou renouveler complètement l'échange DHCP (voir `dhclient -h` puis call me et/ou Google si besoin d'aide).

🌞**Améliorer la configuration du DHCP**

- ajoutez de la configuration à votre DHCP pour qu'il donne aux clients, en plus de leur IP :
  - une route par défaut
  - un serveur DNS à utiliser

```
default-lease-time 900;
max-lease-time 10800;
ddns-update-style none;
authoritative;
subnet 10.3.1.0 netmask 255.255.255.0 {
	range 10.3.1.2 10.3.1.252;
	option routers 10.3.1.254;
	option domain-name-servers 1.1.1.1;
}
```

- récupérez de nouveau une IP en DHCP sur `bob` pour tester :
  - `marcel` doit avoir une IP
    - vérifier avec une commande qu'il a récupéré son IP

```
2: enp0s8: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 08:00:27:c4:f6:64 brd ff:ff:ff:ff:ff:ff
    inet 10.3.1.3/24 brd 10.3.1.255 scope global dynamic noprefixroute enp0s8
       valid_lft 460sec preferred_lft 460sec
    inet6 fe80::cfc0:500d:b183:df84/64 scope link noprefixroute 
       valid_lft forever preferred_lft forever
```

  - vérifier qu'il peut `ping` sa passerelle

```
[alexlinux@localhost ~]$ ping 10.3.1.254
PING 10.3.1.254 (10.3.1.254) 56(84) bytes of data.
64 bytes from 10.3.1.254: icmp_seq=1 ttl=64 time=0.411 ms
64 bytes from 10.3.1.254: icmp_seq=2 ttl=64 time=0.456 ms
```

  - il doit avoir une route par défaut
    - vérifier la présence de la route avec une commande

```
[alexlinux@localhost ~]$ ip r s
default via 10.3.1.254 dev enp0s8 proto dhcp src 10.3.1.3 metric 100 
10.3.1.0/24 dev enp0s8 proto kernel scope link src 10.3.1.3 metric 100 
```

  - vérifier que la route fonctionne avec un `ping` vers une IP

```
[alexlinux@localhost ~]$ ping 10.3.2.12
PING 10.3.2.12 (10.3.2.12) 56(84) bytes of data.
64 bytes from 10.3.2.12: icmp_seq=1 ttl=63 time=0.978 ms
64 bytes from 10.3.2.12: icmp_seq=2 ttl=63 time=0.780 ms
```

  - il doit connaître l'adresse d'un serveur DNS pour avoir de la résolution de noms
    - vérifier avec la commande `dig` que ça fonctionne

```
[alexlinux@localhost ~]$ dig google.com

; <<>> DiG 9.16.23-RH <<>> google.com
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 36686
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 1232
;; QUESTION SECTION:
;google.com.			IN	A

;; ANSWER SECTION:
google.com.		217	IN	A	216.58.214.174
```

- vérifier un `ping` vers un nom de domaine

```
[alexlinux@localhost ~]$ ping google.com
PING google.com (216.58.206.238) 56(84) bytes of data.
64 bytes from par10s34-in-f14.1e100.net (216.58.206.238): icmp_seq=1 ttl=61 time=28.0 ms
64 bytes from par10s34-in-f14.1e100.net (216.58.206.238): icmp_seq=2 ttl=61 time=46.0 ms
```

### 2. Analyse de trames

🌞**Analyse de trames**

- lancer une capture à l'aide de `tcpdump` afin de capturer un échange DHCP
- demander une nouvelle IP afin de générer un échange DHCP
- exportez le fichier `.pcapng`

🦈 **Capture réseau `tp3_dhcp.pcapng`**

```
0.0.0.0.bootpc > 255.255.255.255
    DHCP-Message (53), length 1: Discover
0.0.0.0.bootpc > 255.255.255.255
    DHCP-Message (53), length 1: Offer
DHCP-Message (53), length 1: Request
    0.0.0.0.bootpc > 255.255.255.255
DHCP-Message (53), length 1: ACK
    10.3.1.11.bootps > 10.3.1.5
```
