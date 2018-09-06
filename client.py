#!/usr/bin/env python3

import os
import socket
import _thread

def receber(cliente):
	while True:
		msg = cliente.recv(1024).decode('utf-8')
		print('\n{0}\nDigite sua mensagem:'.format(msg))
		if msg == '/exit': break
	cliente.close()

def enviar(cliente):
	while True:
		msg = input('Digite a mensagem: ')
		msgf = msg.encode('utf-8')
		cliente.send(msgf)
		print(msg)
		if msg == '/exit': break
	cliente.close()



os.system('clear')

HOST = '127.0.0.1'
PORT = str(input('Digite o número de porta em que o cliente TCP irá rodar (default = 50000): '))
if (not PORT.isdigit()) or (int(PORT) > 65535) or (int(PORT) < 1024): PORT = '50000'

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

cliente.connect((HOST, int(PORT)))

while True:
	msg = cliente.recv(1024).decode('utf-8')
	if msg == '/loginok': break
	print(msg, end='')
	login = str(input())
	if not login: login = '\x00'
	cliente.send(login.encode('utf-8'))

print('Para sair, use o comando \'/exit\'\n')
_thread.start_new_thread(receber, tuple([cliente]))
enviar(cliente)
