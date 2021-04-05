# TCPsocketchat

Esse foi um trabalho realizado na disciplina `Programação para Redes` do segundo período (2018.2) do curso
superior de `Tecnologia em Redes de Computadores` no IFRN (Campus CNAT).

O objetivo do trabalho foi implementar um servidor e um cliente de um chat, no qual
o usuário realizaria o login utilizando suas credenciais do [SUAP](suap.ifrn.edu.br).


## Tecnologias utilizadas

- Conexão TCP utilizando `websockets`
- Uso de `threads` no servidor para aceitar múltiplas conexões
- Uso de `threads` no cliente para enviar e receber mensagens simultaneamente
- Backup das mensagens em um banco de dados postgresql e em um arquivo de log
- Backup dos dados do usuário também no banco de dados
