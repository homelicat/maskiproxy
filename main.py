#!/usr/bin/python3

# Project: maskiproxy
# Dev: okbash (origin), lolikotek (new)

import socks
import threading
import select
import socket
from fake_useragent import UserAgent
import re
import requests
from bs4 import BeautifulSoup

VER=5

def foo(conn):
    version, nmethods = conn.recv(2)

    for i in range(nmethods):
        conn.recv(1)
                
    conn.sendall(bytes([5, 0]))

    try:
        version, cmd, _, address_type = conn.recv(4)
    except:
        pass

    if address_type == 1:  # IPv4
        address = socket.inet_ntoa(conn.recv(4))
    elif address_type == 3:  # Domain name
        domain_length = conn.recv(1)[0]
        address = conn.recv(domain_length)
        address = socket.gethostbyname(address)

    port = int.from_bytes(conn.recv(2), 'big', signed=False)

    try:
        if cmd == 1:
            remote = socks.socksocket()
            user_agent = {"User-Agent":ua.random}
            response = requests.get("https://hidemy.name/en/proxy-list/?type=4#list",headers=user_agent)
            soup = BeautifulSoup(response.text,"lxml")
            trs = soup.find_all("tr")
            tds=trs[1].find_all("td")
            remote.set_proxy(socks.SOCKS4, tds[0].text, int(tds[1].text))
            remote.connect((address, port))
            bind_address = remote.getsockname()
        else:
            connection.close()

        addr = int.from_bytes(socket.inet_aton(bind_address[0]), 'big', signed=False)
        port = bind_address[1]

        reply = b''.join([
            VER.to_bytes(1, 'big'),
            int(0).to_bytes(1, 'big'),
            int(0).to_bytes(1, 'big'),
            int(1).to_bytes(1, 'big'),
            addr.to_bytes(4, 'big'),
            port.to_bytes(2, 'big')
        ])
    except Exception as e:
        reply= b''.join([
            VER.to_bytes(1, 'big'),
            VER.to_bytes(1, 'big'),
            int(0).to_bytes(1, 'big'),
            address_type.to_bytes(1, 'big'),
            int(0).to_bytes(4, 'big'),
            int(0).to_bytes(4, 'big')
        ])

    conn.sendall(reply)

    useragent = ua.random

    if reply[1] == 0 and cmd == 1:    
        while True:
            r, w, e = select.select([conn, remote], [], [])

            if conn in r:
                data = conn.recv(4096)    
                if remote.send(data) <= 0:
                    break

            if remote in r:
                data = remote.recv(4096)
                if conn.send(data) <= 0:
                    break


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 9090))
s.listen()
ua = UserAgent()

while True:
    conn, addr = s.accept()
    t = threading.Thread(target=foo,args=(conn,))
    t.start()
