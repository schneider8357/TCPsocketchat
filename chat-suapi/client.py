#!/usr/bin/env python3

import os
import socket
import _thread
import getpass



def ajuda():
	print('-----> Para sair, use o comando \'/exit\'')
	print('-----> Para limpar a tela, use o comando \'/clear\'')
	print('-----> Para exibir a lista de clientes conectados, use o comando \'/clients\'')
	print('-----> Para enviar mensagens privadas, use o comando \'/msg\' (beta)')
	print('-----> Para pedir ajuda, use o comando \'/help\'')

def comando(msg):
	c = msg.split()[0]
	if c == '/clear' and len(msg.split()) == 1: os.system('clear')
	elif c == '/help' and len(msg.split()) == 1: ajuda()
	elif c == '/clients' and len(msg.split()) == 1: cliente.send(msg.encode('utf-8'))
	elif c == '/msg': cliente.send(msg.encode('utf-8'))
	elif c == '/help' or c == '/clear' or c == '/clients': print('Argumentos demais no comando \'%s\'.'%c)
	else: print('Comando \'%s\' não reconhecido. Para ver todos os comandos, digite \'/help\'.'%msg.split()[0])

def receber(cliente):
	while True:
		msg = cliente.recv(1024).decode('utf-8')
		if not msg: break
		print('\n{0}\nDigite a mensagem: '.format(msg), end='')
	print('\nServidor inalcançável.\n')
	os._exit(0)
	cliente.close()

def enviar():
	while True:
		msg = input('Digite a mensagem: ')
		if not msg: pass
		elif msg == '/exit':
			cliente.send(msg.encode('utf-8'))
			break
		elif msg[0] == '/': comando(msg)
		else: cliente.send(msg.encode('utf-8'))
	cliente.close()
	print('\nConexão encerrada.\n')
	os._exit(0)

def setLogin():
	while True:
		msg = cliente.recv(1024).decode('utf-8')
		if msg == '/loginok': break
		print(msg, end='')
		login = str(input())
		if not login: login = '\x00'
		cliente.send(login.encode('utf-8'))
		msg = cliente.recv(1024).decode('utf-8')
		senha = getpass.getpass(msg)
		if not senha: senha = '\x00'
		cliente.send(senha.encode('utf-8'))
	login = cliente.recv(1024).decode('utf-8')
	return login

#MAIN
os.system('clear')

HOST = '127.0.0.1'
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

try: login = setLogin()
except:
	cliente.close()
	print('\nNão foi possível efetuar o login.\n')
	os._exit(0)

print('\nBem vindo, %s!'%login)
ajuda()
_thread.start_new_thread(receber, tuple([cliente]))

try: enviar()
except: cliente.close()

