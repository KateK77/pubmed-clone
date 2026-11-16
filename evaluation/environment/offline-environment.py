"""Offline-only CLI wrapper. Denies all non-loopback network and removes API keys."""
import ipaddress
import os
import socket
import sys

for key in list(os.environ):
    if key.startswith('OPENAI_') or key.upper().endswith('_PROXY'):
        del os.environ[key]

def local(host):
    if host == 'localhost':
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False

original_connect = socket.socket.connect
original_connect_ex = socket.socket.connect_ex
original_dns = socket.getaddrinfo
def connect(sock, address):
    if not local(address[0]):
        raise RuntimeError('Offline preflight denies non-loopback connection')
    return original_connect(sock, address)
def connect_ex(sock, address):
    if not local(address[0]):
        raise RuntimeError('Offline preflight denies non-loopback connection')
    return original_connect_ex(sock, address)
def dns(host, *args, **kwargs):
    if not local(host):
        raise RuntimeError('Offline preflight denies external DNS')
    return original_dns(host, *args, **kwargs)
socket.socket.connect = connect
socket.socket.connect_ex = connect_ex
socket.getaddrinfo = dns

import environment
if len(sys.argv) == 3 and sys.argv[1] == 'mail-probe':
    environment.configure(sys.argv[2])
    from django.core.mail import send_mail
    count = send_mail('Offline transport probe', 'Synthetic infrastructure check only.',
                      'evaluation@example.test', ['preflight@example.test'])
    assert count == 1
    print('One synthetic transport probe sent to local capture.')
else:
    environment.main()
