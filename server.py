#!/usr/bin/env python3

import os
import socket
import _thread
from datetime import datetime

#DECLARACAO
logins = {}
conexoes = {}

#FUNCOES
def envioBroadcast(msg, remetente):
	for cliente in conexoes:
		con = conexoes[cliente][0]
		if cliente == remetente: continue
		msgf = msg.encode('utf-8')
		con.send(msgf)

def setLogin(con, cliente):
	msg = 'Login: '
	msgf = msg.encode('utf-8')
	con.send(msgf)
	login = con.recv(1024).decode('utf-8')
	while True:
		if login in logins.values():
			msg = 'O login escolhido já existe! Tente novamente!\nLogin: '
		elif login == '\x00':
			msg = 'O login não pode ficar em branco! Tente novamente!\nLogin: '
		else:
			msg = '/loginok'
		msgf = msg.encode('utf-8')
		con.send(msgf)
		if msg == '/loginok': break
		login = con.recv(1024).decode('utf-8')
	logins[cliente] = login
	conexoes[cliente] = tuple([con,'{0}:{1} {2}/{3}/{4}'.format(now.hour, now.minute, now.day, now.month, now.year)])
	print(logins)

def inicioConexao(con, cliente):
	setLogin(con, cliente)
	msg = 'Cliente conectado! - Login: {0} Conexao:{1}'.format(logins[cliente],cliente)
	msg = '{0}:{1} {2}/{3}/{4} <servidor> {5}'.format(now.hour,now.minute,now.day,now.month,now.year,msg)
	print(msg)
	print('\nNúmero de clientes conectados: {0}'.format(len(conexoes)))
	for cliente in logins.keys():
		print('Login: {0} Cliente: {1} Conectado desde: {2}'.format(logins[cliente],cliente,conexoes[cliente][1]))
	while True:
		msg = con.recv(1024).decode('utf-8')
		if msg == '/exit': break
		print('{0}:{1} {2}/{3}/{4} {5} {6}: {7}'.format(now.hour, now.minute, now.day, now.month, now.year,logins[cliente],cliente,msg))
		msg = '{0}:{1} {2}/{3}/{4} {5} diz: {6}'.format(now.hour,now.minute,now.day,now.month,now.year,logins[cliente],msg)
		_thread.start_new_thread(envioBroadcast, tuple([msg, cliente]))
	msg = 'Cliente desconectado - Login: {0} Conexao:{1}'.format(logins[cliente],cliente)
	msg = '{0}:{1} {2}/{3}/{4} <servidor> {5}'.format(now.hour,now.minute,now.day,now.month,now.year,msg)
	print(msg)
	_thread.start_new_thread(envioBroadcast, tuple([msg, cliente]))
	del logins[cliente]
	del conexoes[cliente]
	con.close()
	_thread.exit()

#MAIN
os.system('clear')
now = datetime.now()
HOST = '127.0.0.1'
PORT = str(input('Digite o número de porta em que o servidor TCP irá rodar (default = 50000): '))
if (not PORT.isdigit()) or (int(PORT) > 65535) or (int(PORT) < 1024): PORT = '50000'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
addr = (HOST, int(PORT))
server.bind(addr)
server.listen(1)
print('\nServidor TCP-THREAD iniciado no IP', HOST, 'na porta', PORT)


while True:
	con, cliente = server.accept()
	print('\nNova thread iniciada para essa conexão')
	_thread.start_new_thread(inicioConexao, tuple([con, cliente]))

tcp.close()
	print('\nFinalizando conexao do cliente {0} {1}'.format(logins[cliente],cliente))
	del logins[cliente]
	con.close()
	_thread.exit()

#MAIN
os.system('clear')

HOST = '127.0.0.1'
PORT = str(input('Digite o número de porta em que o servidor TCP irá rodar (default = 50000): '))
if (not PORT.isdigit()) or (int(PORT) > 65535) or (int(PORT) < 1024): PORT = '50000'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
addr = (HOST, int(PORT))
server.bind(addr)
server.listen(1)
print('\nServidor TCP-THREAD iniciado no IP', HOST, 'na porta', PORT)


while True:	
	con, cliente = server.accept()
	print('\nNova thread iniciada para essa conexão')
	
	# Abrindo uma thread para a conexão
	_thread.start_new_thread(inicioConexao, tuple([con, cliente]))

tcp.close()
