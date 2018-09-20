#!/usr/bin/env python3

import os
import socket
import _thread
from datetime import datetime
import json
import requests


urls = { "token":"https://suap.ifrn.edu.br/api/v2/autenticacao/token/",
		 "dados":"https://suap.ifrn.edu.br/api/v2/minhas-informacoes/meus-dados/"}
logins = {}
conexoes = {}
exitall = False


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

def getToken(autenticacao):
	response = requests.post(urls['token'], data=autenticacao)
	if response.status_code == 200:
		return json.loads(response.content.decode('utf-8'))['token']
	return None

def getInformacoes(cabecalho):
	response = requests.get(urls['dados'], headers=cabecalho)
	if response.status_code == 200:
		return response.content.decode('utf-8')
	return None

def autentica(login,senha):
	autenticacao = { "username": login, "password": senha }
	cabecalho = {'Authorization': 'JWT {0}'.format(getToken(autenticacao))}
	informacoes = json.loads(getInformacoes(cabecalho))
	login = informacoes['nome_usual']
	if login in logins.values():
		return 'O usuário já está logado! Tente novamente!\nLogin: '
	else:
		return '/loginok %s'%login

def setLogin(con, cliente):
	msg = 'Matrícula: '
	msgf = msg.encode('utf-8')
	con.send(msgf)
	login = con.recv(1024).decode('utf-8')
	msg = 'Senha: '
	msgf = msg.encode('utf-8')
	con.send(msgf)
	senha = con.recv(1024).decode('utf-8')
	while True:
		if login == '\x00':
			msg = 'O login não pode ficar em branco! Tente novamente!\nLogin: '
		else:
			try:
				msg = autentica(login,senha)
			except:
				msg = 'Usuário ou senha incorretos.\nLogin: '
		msgf = msg.encode('utf-8')
		con.send(msgf)
		if msg.split()[0] == '/loginok': break
		login = con.recv(1024).decode('utf-8')
		msg = 'Senha: '
		msgf = msg.encode('utf-8')
		con.send(msgf)
		senha = con.recv(1024).decode('utf-8')
		
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
	m = '{0} <servidor> {1} saiu.'.format(agora(),logins[cliente],cliente)
	print('{0} <servidor> {1} {2} saiu.'.format(agora(),logins[cliente],cliente))
	del logins[cliente]
	del conexoes[cliente]
	mostrarConexoes()
	_thread.start_new_thread(envioBroadcast, tuple([m, cliente]))
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
	try:
		con, cliente = server.accept()
	except KeyboardInterrupt:
		break
	print('{0} <servidor> nova thread iniciada para o cliente {1}'.format(agora(),cliente))
	_thread.start_new_thread(inicioConexao, tuple([con, cliente]))
print("\nEncerrando servidor...\n")
server.close()
