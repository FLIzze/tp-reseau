<h1>TP5 - MITM</h1>

<h2>How to download script ?</h2>

`git clone https://github.com/FLIzze/tp-reseau.git`

<h2>How to use the script ?</h2>

on linux/mac `sudo python3 tp-reseau/reseau/tp5/main.py `
`pip3 install -r requirements.txt`

on windows / may not work on windows! -> use admin mode for terminal `python3 tp-reseau/reseau/tp5/main.py `

<p>Then all the information you need to use it will be displayed in the termimal.</p>

<h2>How it works ?</h2>

<p>for this instance, the victim will be .69, the router .254 and the "hacker" .11

this is the router's neigh table before using the script</p>

```
[alexlinux@router ~]$ ip n s
10.105.1.11 dev enp0s3 lladdr 08:00:27:47:3b:71 REACHABLE 
10.105.1.69 dev enp0s3 lladdr 08:00:27:98:4a:a4 REACHABLE 
```

<p>same table after the use of the script</p>

```
[alexlinux@router ~]$ ip n s
10.105.1.11 dev enp0s3 lladdr 08:00:27:47:3b:71 REACHABLE 
10.105.1.69 dev enp0s3 lladdr 08:00:27:47:3b:71 STALE 
```
<p>as you can see, they now both got the hacker's mac which mean the router will send data to hacker

victim table before</p>

```
alexlinux@alexlinux-VirtualBox:~$ ip n s
10.105.1.254 dev enp0s3 lladdr 08:00:27:3a:5d:30 REACHABLE
10.105.1.11 dev enp0s3 lladdr 08:00:27:47:3b:71 REACHABLE
```

<p>after</p>

```
alexlinux@alexlinux-VirtualBox:~$ ip n s
10.105.1.254 dev enp0s3 lladdr 08:00:27:47:3b:71 STALE
10.105.1.11 dev enp0s3 lladdr 08:00:27:47:3b:71 STALE
```

<p>router's mac is now the same as the hacker which mean that he'll receive data from you. The hacker is now successfully in the middle.

once you're in the middle you can use wireshark to get your victim's dns requests [like this](/reseau/tp5/tp5.pcapng)</p>

<h2>blablabla only for educational purposes not for an use in illegal situation.</h2>
