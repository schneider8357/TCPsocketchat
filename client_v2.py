#!/usr/bin/env python3

import os
import socket
import _thread


#def receber():

#def enviar():


HOST = '127.0.0.1'
PORT = str(input('Digite o número de porta em que o cliente TCP irá rodar (default = 50000): '))
if (not PORT.isdigit()) or (int(PORT) > 65535) or (int(PORT) < 1024): PORT = '50000'

tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

tcp_socket.connect((HOST, int(PORT)))

while True:	
	msg = tcp_socket.recv(1024).decode('utf-8')
	if msg == '/loginok': break
	print(msg, end='')
	login = str(input())
	if not login: login = '\x00'
	tcp_socket.send(login.encode('utf-8'))

print('Para sair, use o comando \'/exit\'\n')

msg = input('Digite a mensagem: ')

while True:
	msgf = msg.encode('utf-8')
	tcp_socket.send(msgf)
	print(msg)
	if msg == '/exit': break
	msg = input('Digite a mensagem: ')

tcp_socket.close()
