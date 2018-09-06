#!/usr/bin/env python3

import os
import socket
import _thread

#DECLARACAO
logins = {}

#FUNCOES
def escuta():
	pass

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
	print(logins)

def inicioConexao(con, cliente):
	setLogin(con, cliente)
	print('\nCliente conectado - Login: {0} Conexao:{1}'.format(logins[cliente],cliente))
	
	while True:
		msg = con.recv(1024)
		if msg.decode('utf-8') == '/exit': break
		print('O Cliente {0} {1} disse: {2}'.format(logins[cliente],cliente,msg.decode('utf-8')))
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
