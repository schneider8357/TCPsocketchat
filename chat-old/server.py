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
	_thread.exit()

def agora():
	now = datetime.now()
	return '{0}:{1} {2}/{3}/{4}'.format(now.hour, now.minute, now.day, now.month, now.year)

def mostrarConexoes():
	print('{0} <servidor> Número de clientes conectados: {1}'.format(agora(),len(conexoes)))
	if len(conexoes) > 0:
		for cliente in logins:
			print('{0} <servidor> Login: {1} Cliente: {2} Conectado desde: {3}'.format(agora(),logins[cliente],cliente,conexoes[cliente][1]))

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
	now = datetime.now()
	conexoes[cliente] = tuple([con,agora()])

def inicioConexao(con, cliente):
	setLogin(con, cliente)
	msg = '{0} <servidor> {1} entrou.'.format(agora(),logins[cliente])
	_thread.start_new_thread(envioBroadcast, tuple([msg, cliente]))
	print('{0} <servidor> {1} {2} entrou.'.format(agora(),logins[cliente],cliente))
	mostrarConexoes()
	while True:
		msg = con.recv(1024).decode('utf-8')
		if msg == '/exit': break
		print('{0} {1} {2}: {3}'.format(agora(),logins[cliente],cliente,msg))
		msg = '{0} {1} diz: {2}'.format(agora(),logins[cliente],msg)
		_thread.start_new_thread(envioBroadcast, tuple([msg, cliente]))
	msg = '{0} <servidor> {1} saiu.'.format(agora(),logins[cliente],cliente)
	print('{0} <servidor> {1} {2} saiu.'.format(agora(),logins[cliente],cliente))
	del logins[cliente]
	del conexoes[cliente]
	mostrarConexoes()
	_thread.start_new_thread(envioBroadcast, tuple([msg, cliente]))
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
	print('{0} <servidor> nova thread iniciada para o cliente {1}'.format(agora(),cliente))
	_thread.start_new_thread(inicioConexao, tuple([con, cliente]))

server.close()
