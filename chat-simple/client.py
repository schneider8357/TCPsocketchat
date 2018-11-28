#!/usr/bin/env python3

import os
import socket
import _thread
import getpass

HOST = '127.0.0.1'

def ajuda():
	print('-----> Para sair, digite "exit" (sem as aspas)')
	print('-----> Para limpar a tela, digite "clear" (sem as aspas)')
	print('-----> Para ver esta mensagem, digite "help" (sem as aspas)')

def receber(cliente):
	while True:
		msg = cliente.recv(1024).decode('utf-8')
		if not msg: break
		print('\n{0}\nDigite a mensagem: '.format(msg), end='')
	print('\nServidor inalcançável.\n')
	cliente.close()
	os._exit(0)
	

def enviar():
	msg = ''
	while msg != 'exit':
		msg = input('Digite a mensagem: ')
		if not msg: continue
		if msg == 'clear': os.system('clear')
		if msg == 'help': ajuda()
		else: cliente.send(msg.encode('utf-8'))
	cliente.close()
	print('\nConexão encerrada.\n')
	os._exit(0)

def setLogin():
	try:
		msg = ''
		while msg != 'OK':
			login = str(input('Matrícula: '))
			if not login: login = '\x00'

			senha = getpass.getpass('Senha: ')
			if not senha: senha = '\x00'

			cliente.send(login.encode('utf-8'))
			cliente.send(senha.encode('utf-8'))

			msg = cliente.recv(1024).decode('utf-8')
			print(msg,'\n')
			if msg == 'OK': break
		login = cliente.recv(1024).decode('utf-8')
	except:
		return 0
	return login

#MAIN

os.system('clear')

PORT = str(input('Digite o número de porta em que o cliente TCP irá rodar (default = 50000): '))
if (not PORT.isdigit()) or (int(PORT) > 65535) or (int(PORT) < 1024): PORT = '50000'
PORT = int(PORT)

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
	cliente.connect((HOST, PORT))
except:
	try:
		PORT += 2
		cliente.connect((HOST, PORT))
	except:
		print('\nServidor não encontrado.\n')
		os._exit(0)

login = setLogin()

if not login:
	cliente.close()
	print('\nNão foi possível efetuar o login.\n')
	os._exit(0)

print('\nBem vindo, %s!'%login)
ajuda()
_thread.start_new_thread(receber, tuple([cliente]))

try: enviar()
except: cliente.close()
