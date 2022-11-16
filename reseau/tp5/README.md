TP5 - MITM

pour download le script : `git clone https://github.com/FLIzze/tp-reseau.git`

pour use le script, `sudo python3 /reseau/tp5/mitm.py`

Le script va d'abord sniffer le reseau puis spam le routeur et la victime afin de falsifier leurs ARP.

En utilisant wireshark, vous pouvez consulter les recherches DNS de la victime car les requetes dns passent en clair et ne sont pas securisees.