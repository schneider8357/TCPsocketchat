#!/usr/bin/env python3

import os
import socket
import _thread
from datetime import datetime
import json
import requests


HOST = '127.0.0.1'
urls = { 'token':'https://suap.ifrn.edu.br/api/v2/autenticacao/token/', 'dados':'https://suap.ifrn.edu.br/api/v2/minhas-informacoes/meus-dados/'}
logins = {}	# { cliente : login }
conexoes = {}	# { cliente : conexao (socket) }
horaInicio = {}	# { cliente : hora de início da conexão }
mensagens = []


#FUNCOES

def logAdd(msg): # Exibe na tela e adiciona ao log uma mensagem.
	mensagens.append('%s'%msg)
	print(msg)
	
def logRec(): # Salva o log do chat em um arquivo.
	print('\nFazendo backup das mensagens...\n')
	now = datetime.now()
	filename = '{0:0=2d}{1:0=2d}{2:0=2d}_{3:0=2d}{4:0=2d}{5}.txt'.format(now.hour, now.minute, now.second, now.day, now.month, now.year)
	with open(filename, 'w') as arq:
		for msg in mensagens:
			arq.write('%s\n'%msg)
		print('\nBackup realizado com sucesso! Log: %s\n'%filename)

def envioBroadcast(msg, remetente): # Envia uma mensagem a todos os clientes exceto àquele que enviou (remetente)
	for cliente in conexoes:
		con = conexoes[cliente]
		if cliente == remetente: continue
		try:
			con.send(msg.encode('utf-8'))
		except:
			continue
	_thread.exit()

def envioPrivado(con,cliente,msg):
	if len(msg.split()) >= 3:
		loginDestino = msg.split()[1]
		loginOrigem = logins[cliente]
		if loginOrigem == loginDestino:
			con.send('Você não pode enviar uma mensagem privada para si.'.encode('utf-8'))
		elif loginDestino in logins.values(): # Comente essa linha para permitir que um cliente mande uma mensagem privada para si.
			clienteOrigem = (list(logins.keys())[list(logins.values()).index(loginOrigem)])
			clienteDestino = (list(logins.keys())[list(logins.values()).index(loginDestino)])
			a = msg.split()
			a.pop(0)
			a.pop(0)
			mensagem = ''
			for i in a: mensagem += i + ' '
			mensagem = mensagem[:-1]
			logAdd('{0} {1} {2} pm {3} {4}: {5}'.format(agora(), loginOrigem, clienteOrigem, loginDestino, clienteDestino, mensagem))
			msg = '{0} {1} diz (privado): {2}'.format(agora(), logins[cliente], mensagem)
			conexoes[clienteDestino].send(msg.encode('utf-8'))
		else:
			m = 'O cliente de login %s não está online.\nO uso do comando \'/msg\' é: \'/msg login_destino sua_mensagem\''%loginDestino
			con.send(m.encode('utf-8'))
	else:
		con.send('Argumentos insuficientes para o comando \'/msg\'\nO uso do comando é: \'/msg login_destino sua_mensagem\''.encode('utf-8'))

def agora(): # Retorna a data e hora atuais.
	now = datetime.now()
	return '{0:0=2d}:{1:0=2d} {2:0=2d}/{3:0=2d}/{4}'.format(now.hour, now.minute, now.day, now.month, now.year)

def mostrarConexoes(i): # Exibe todos os clientes conectados. Quando i == 1, a função retorna a lista. Quando i == 0, a função imprime a lista e adiciona-a ao log.
	if i:
		msg = '{0} <servidor> Número de clientes conectados: {1}'.format(agora(), len(conexoes))
		if len(conexoes):
			for cliente in logins:
				msg = msg + '\n{0} <servidor> Login: {1} Conectado desde: {2}'.format(agora(), logins[cliente], horaInicio[cliente])
		return(msg)
	else:
		logAdd('{0} <servidor> Número de clientes conectados: {1}'.format(agora(),len(conexoes)))
		# Caso queira que a cada conexão feita ou desfeita sejam exibidos todos os clientes  ativos, descomente as linhas abaixo.
		#if len(conexoes):
		#	for cliente in logins: logAdd('{0} <servidor> Login: {1} Cliente: {2} Conectado desde: {3}'.format(agora(), logins[cliente], cliente, horaInicio[cliente]))

def getToken(autenticacao): # Retorna o token para acesso ao SUAP.
	response = requests.post(urls['token'], data=autenticacao)
	if response.status_code == 200:
		return json.loads(response.content.decode('utf-8'))['token']
	return None

def getInformacoes(cabecalho): # Retorna os dados utilizando o token.
	response = requests.get(urls['dados'], headers=cabecalho)
	if response.status_code == 200:
		return response.content.decode('utf-8')
	return None

def autentica(login,senha): # Define o login do cliente de acordo com o nome no SUAP.
	autenticacao = { 'username': login, 'password': senha }
	cabecalho = {'Authorization': 'JWT {0}'.format(getToken(autenticacao))}
	informacoes = json.loads(getInformacoes(cabecalho))
	login = informacoes['nome_usual'].replace(' ','_')
	if login in logins.values():
		return 'O usuário já está logado! Tente novamente!\nMatrícula: ', login
	else:
		return '/loginok', login # '/loginok' é a mensagem que confirma que o login foi efetuado com sucesso. 

def setLogin(con, cliente): # Conversa com a aplicação cliente para autenticá-lo.
	# O servidor define as mensagens que aparecerão para o cliente na hora do login.
	# Isso permite que poucas alterações sejam necessárias na aplicação cliente.
	# Por exemplo, se o servidor deixar de autenticar o usuário no SUAP.
	# É possível fazer isso sem qualquer alteração na aplicação cliente.
	msg = 'Matrícula: '
	con.send(msg.encode('utf-8'))
	login = con.recv(1024).decode('utf-8')
	msg = 'Senha: '
	con.send(msg.encode('utf-8'))
	senha = con.recv(1024).decode('utf-8')
	while True:
		if login == '\x00' or senha == '\x00':
			msg = 'A matrícula e senha não podem ficar em branco! Tente novamente!\nMatrícula: '
		else:
			try:
				msg, login = autentica(login,senha)
			except:
				msg = 'Não foi possível realizar o login.\nVerifique se seu usuário e senha estão corretos.\nMatrícula: '
		con.send(msg.encode('utf-8'))
		if msg == '/loginok': break
		login = con.recv(1024).decode('utf-8')
		msg = 'Senha: '
		con.send(msg.encode('utf-8'))
		senha = con.recv(1024).decode('utf-8')
	logins[cliente] = login
	con.send(login.encode('utf-8'))
	conexoes[cliente] = con
	horaInicio[cliente] = agora()

def inicioConexao(con, cliente):
	try:
		setLogin(con, cliente)
		msg = '{0} <servidor> {1} entrou.'.format(agora(), logins[cliente]) 
		logAdd('{0} <servidor> {1} {2} entrou.'.format(agora(), logins[cliente], cliente))
		# A mensagem enviada é diferente da que aparece no servidor, para não enviar aos clientes os endereços IP dos outros clientes.
		_thread.start_new_thread(envioBroadcast, tuple([msg, cliente]))
		mostrarConexoes(0)
		conexao(con,cliente)
		con.close()
	except:
		logAdd('{0} <servidor> Não foi possível conectar com {1}. Finalizando thread.'.format(agora(),cliente))
		con.close()
	_thread.exit()

def conexao(con,cliente):
	while True:
		msg = con.recv(1024).decode('utf-8')
		if not msg or msg == '/exit': break
		elif msg.split()[0] == '/msg': # Executa o comando /msg (envia mensagens privadas entre clientes).
			envioPrivado(con, cliente, msg)
		elif msg.split()[0] == '/clients': # Executa o comando /clients (envia para o cliente uma lista com os clientes ativos).
			con.send(mostrarConexoes(1).encode('utf-8'))
		else:
			logAdd('{0} {1} {2}: {3}'.format(agora(), logins[cliente], cliente, msg))
			msg = '{0} {1} diz: {2}'.format(agora(), logins[cliente], msg)
			_thread.start_new_thread(envioBroadcast, tuple([msg, cliente]))
	fimConexao(con, cliente)

def fimConexao(con, cliente):
	m = '{0} <servidor> {1} saiu.'.format(agora(), logins[cliente], cliente)
	logAdd('{0} <servidor> {1} {2} saiu.'.format(agora(),logins[cliente], cliente))
	del logins[cliente]
	del conexoes[cliente]
	del horaInicio[cliente]
	mostrarConexoes(0)
	_thread.start_new_thread(envioBroadcast, tuple([m, cliente]))


#MAIN

os.system('clear')

PORT = str(input('Digite o número de porta em que o servidor TCP irá rodar (default = 50000): '))
if (not PORT.isdigit()) or (int(PORT) > 65535) or (int(PORT) < 1024): PORT = '50000'
PORT = int(PORT)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
	server.bind((HOST, PORT))
	server.listen(1)
except:
	try:
		PORT += 2
		server.bind((HOST, PORT))
		server.listen(1)
	except:
		print('\nNão foi possível iniciar o servidor.\n')
		os._exit(0)

m = 'Servidor TCP-THREAD iniciado no IP %s na porta %d às %s'%(HOST,PORT,agora())
mensagens.append(m)
print('\n%s'%m)

while True: # Loop para sempre aceitar novas conexões.
	try:
		con, cliente = server.accept()
	except KeyboardInterrupt:
		break
	logAdd('{0} <servidor> Nova thread iniciada para o cliente {1}'.format(agora(),cliente))
	_thread.start_new_thread(inicioConexao, tuple([con, cliente]))
m = 'Encerrando servidor às %s...'%agora()
mensagens.append(m)
logRec() # Grava o log em um arquivo de texto.
print('\n%s'%m)
server.close()
