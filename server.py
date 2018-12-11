#!/usr/bin/env python3

import os
import socket
import _thread
import datetime
import json
import requests
import time
import psycopg2


HOST = '127.0.0.1'
PORT = 5000
urls = { 'token':'https://suap.ifrn.edu.br/api/v2/autenticacao/token/', 'dados':'https://suap.ifrn.edu.br/api/v2/minhas-informacoes/meus-dados/'}
logins = {} # { cliente : login }
conexoes = {} # { cliente : conexao (socket) }
horaInicio = {} # { cliente : hora de início da conexão }
mensagens = []
servername = 'Servidor TCP'
logins[servername] = '<server>'

strConexaoPostgres = "dbname=postgres user=postgres host=localhost password=aluno"
strConexaoChat = "dbname=db_chat user=postgres host=localhost password=aluno"
strCreateMensagem = "create table mensagem (id serial primary key, " \
										"dataehora timestamp not null, "\
										"login_src varchar(200), "\
										"endpoint_src varchar(50), "\
										"msg varchar(500))"

#FUNCOES DB
# -----------------------------------------------------------------------------------------------
def db_exists():
	exists = False
	try:
		strSQL = "select datname from pg_database where datname='db_chat'"
		con = psycopg2.connect(strConexaoPostgres)
		cur = con.cursor()
		cur.execute(strSQL)
		if cur.fetchone(): exists = True
		cur.close()
		con.close()
	except psycopg2.Error as e:
		print (e)
	return exists

def table_exists():
	exists = False
	try:
		strSQL = "select relname from pg_class where relname='mensagem'"
		con = psycopg2.connect(strConexaoChat)
		cur = con.cursor()
		cur.execute(strSQL)
		if cur.fetchone(): exists = True
		cur.close()
		con.close()
	except psycopg2.Error as e:
		print (e)
	return exists

def db_create():
	try:
		from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
		strSQL = "create database db_chat"
		con = psycopg2.connect(strConexaoPostgres)
		con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
		cur = con.cursor()
		cur.execute(strSQL)
		cur.close()
		con.close()
	except psycopg2.Error as e:
		print (e)

def table_create():
	try:
		con = psycopg2.connect(strConexaoChat)
		cur = con.cursor()
		cur.execute(strCreateMensagem)
		cur.close()
		con.commit()
		con.close()
	except psycopg2.Error as e:
		print (e)

def msg_insert(dataehora,login,cliente,msg):
	con = psycopg2.connect(strConexaoChat)
	cur = con.cursor()
	strSQLInsereDados = "insert into mensagem (dataehora, login_src, endpoint_src, msg) values (%s, %s, %s, %s)"
	cur.execute(strSQLInsereDados,(dataehora,login,cliente,msg))
	con.commit()
	con.close()

def msg_retrieve():
	try:
		strSQL = "select * from mensagem where login_src <> '{}'".format(logins[servername])
		con = psycopg2.connect(strConexaoChat)
		cur = con.cursor()
		cur.execute(strSQL)
		r = cur.fetchall()
		cur.close()
		con.close()
		return r
	except psycopg2.Error as e:
		print (e)

# -----------------------------------------------------------------------------------------------


#FUNCOES CHAT
# -----------------------------------------------------------------------------------------------
def logAdd(dataehora, remetente, msg): # Exibe na tela e adiciona ao log uma mensagem.
	msg_insert(dataehora,logins[remetente],remetente,msg)
	msg = '{0} {1} {2}: {3}'.format(dataehora, logins[remetente], remetente, msg)
	mensagens.append('%s'%msg)
	print(msg)

def logRec(): # Salva o log do chat em um arquivo.
	print('\nFazendo backup das mensagens...\n')
	now = datetime.datetime.now()
	filename = '{0:0=2d}{1:0=2d}{2:0=2d}_{3:0=2d}{4:0=2d}{5}.txt'.format(now.hour, now.minute, now.second, now.day, now.month, now.year)
	with open(filename, 'w') as arq:
		for msg in mensagens:
			arq.write('%s\n'%msg)
		print('\nBackup realizado com sucesso! Log: %s\n'%filename)

def envioBroadcast(dataehora, remetente, msg): # Envia uma mensagem a todos os clientes exceto àquele que enviou (remetente)
	logAdd(dataehora,remetente,msg)
	msg = '{0} {1}: {2}'.format(dataehora, logins[remetente], msg)
	for cliente in conexoes:
		con = conexoes[cliente]
		if cliente == remetente: continue
		try:
			con.send(msg.encode('utf-8'))
		except:
			continue
	_thread.exit()

def agora(): # Retorna a data e hora atuais.
	now = datetime.datetime.now()
	return '{0}-{1:0=2d}-{2:0=2d} {3:0=2d}:{4:0=2d}:{5:0=2d}'.format(now.year, now.month, now.day, now.hour, now.minute, now.second)

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
	token = getToken(autenticacao)
	cabecalho = {'Authorization': 'JWT {0}'.format(token)}
	if token == None: return None
	informacoes = json.loads(getInformacoes(cabecalho))
	if informacoes == None: return None
	login = informacoes['nome_usual'].replace(' ','_') # Ex.: nome_usual = 'Lucas Schneider'; login = 'Lucas_Schneider'
	return login

def setLogin(con, cliente):
	msg = ''
	while msg != 'OK':
		login = con.recv(1024).decode('utf-8') # Receber login
		if not login: return 0
		time.sleep(0.1)
		senha = con.recv(1024).decode('utf-8') # Receber senha
		if not senha: return 0
		if (login == '\x00' or senha == '\x00'):
			msg = 'A matrícula e senha não podem ficar em branco. Tente novamente.'
		else:
			try:
				login = autentica(login,senha) # Tentativa de login no SUAP
				msg = 'OK'
			except:
				return 0
			if msg != 'OK' or login == None:
				msg = 'Não foi possível realizar o login. Verifique se seu usuário e senha estão corretos.'
		#if login in logins.values(): # Se houver alguém online com aquele login
		#	msg = 'Já há um usuário com esse login online. Tente novamente.'
		# As linhas acima estão comentadas para permitir varios usuários com o mesmo login
		try: con.send(msg.encode('utf-8'))
		except: return 0
	
	time.sleep(2)
	try: con.send(login.encode('utf-8'))
	except: return 0

	logins[cliente] = login
	conexoes[cliente] = con
	horaInicio[cliente] = agora()
	return 1

def sendMsgs(con, cliente):
	msgs = msg_retrieve()
	if not msgs: num = '0'
	else: num = len(msgs)
	try:
		con.send(str(num).encode('utf-8'))
		if not msgs: return 1
		for i in msgs:
			msg = '{0} {1}: {2}'.format(i[1], i[2], i[4])
			con.send(msg.encode('utf-8'))
			time.sleep(0.2)
	except: return 0
	return 1

def inicioConexao(con, cliente):
	OK_login = setLogin(con, cliente)
	print('teste')
	if OK_login: # Se o cliente se autenticou no SUAP com sucesso
		OK_send = sendMsgs(con, cliente)
		if OK_send: # Se o histórico de mensagens foi enviado com sucesso
			msg = logins[cliente] + ' entrou.'
			_thread.start_new_thread(envioBroadcast, tuple([agora(),servername,msg]))
			OK_conexao = conexao(con,cliente)
			if OK_conexao == 0: # Se a conexão foi encerrada abruptamente
				msg = 'Algo deu errado ao conectar com o cliente ' + str(cliente)
				logAdd(agora(),servername, msg)
		else:
			msg = 'Não foi possível enviar o histórico de mensagens para o cliente ' + str(cliente)
			logAdd(agora(),servername, msg)
	else:
		msg = 'Não foi possível autenticar o cliente ' + str(cliente)
		logAdd(agora(),servername, msg)
	fimConexao(con, cliente)
	con.close()
	_thread.exit()

def conexao(con,cliente):
	msg = ''
	while msg != 'exit': # 'exit' = Comando utilizado pelo cliente para encerrar a conexão
		msg = con.recv(1024).decode('utf-8')
		if not msg: return 0
		if not msg == 'exit': _thread.start_new_thread(envioBroadcast, tuple([agora(),cliente,msg]))
	return 1

def fimConexao(con, cliente):
	if cliente in logins.keys():
		msg = logins[cliente] + ' saiu.'
		_thread.start_new_thread(envioBroadcast, tuple([agora(), servername, msg]))
		del logins[cliente]
	if cliente in conexoes.keys():
		del conexoes[cliente]
	if cliente in horaInicio.keys():
		del horaInicio[cliente]


def main():
	os.system('clear')



	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	try:
		server.bind((HOST, PORT))
		server.listen(1)
	except:
		print('\nNão foi possível iniciar o servidor.\n')
		os._exit(0)
	if db_exists():
		print("O banco existe!")
		pass
	else:
		print("Criando o banco...")
		db_create()
	if table_exists():
		print("A tabela usuario existe!")
		pass
	else:
		print("Criando tabela usuario...")
		table_create()
	m = 'Servidor TCP-THREAD iniciado no IP %s na porta %d às %s'%(HOST,PORT,agora())
	logAdd(agora(),servername,m)
	print('\n%s'%m)

	while True: # Loop para sempre aceitar novas conexões.
		try:
			con, cliente = server.accept()
		except KeyboardInterrupt:
			break
		msg = 'Nova thread iniciada para o cliente ' + str(cliente)
		logAdd(agora(),servername, msg)
		_thread.start_new_thread(inicioConexao, tuple([con, cliente]))
	m = 'Encerrando servidor às %s...'%agora()
	logAdd(agora(),servername,m)
	logRec() # Grava o log em um arquivo de texto.
	print('\n%s'%m)
	server.close()
	
if __name__ == '__main__': main()
