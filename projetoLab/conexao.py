from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error

# Inicializa a aplicação Flask
app = Flask(__name__)
# Habilita CORS para permitir requisições de origens diferentes
CORS(app)

# Função para estabelecer conexão com o banco de dados MySQL
def get_db_connection():
    try:
        # Configura a conexão com o banco de dados
        connection = mysql.connector.connect(
            host='localhost',               # Endereço do servidor MySQL
            database='project_equilibrio',  # Nome do banco de dados
            user='root',                   # Usuário do MySQL
            password='senac123'            # Senha do usuário do MySQL
        )
        print("Conexão com MySQL estabelecida!")
        return connection
    except Error as e:
        # Registra erros de conexão
        print(f"Erro detalhado ao conectar: {e}")
        return None

# Define rotas para a raiz ('/') e '/index.html'
@app.route('/')
@app.route('/index.html')
def home():
    # Serve o arquivo index.html
    return send_file('index.html')

# Rota para testar a conexão com o banco de dados
@app.route('/testar-conexao', methods=['GET'])
def testar_conexao():
    # Tenta estabelecer conexão com o banco
    connection = get_db_connection()
    if connection is None:
        # Retorna erro 500 se a conexão falhar
        return jsonify({'error': 'Erro ao conectar ao banco'}), 500
    try:
        # Executa uma query simples para verificar a conexão
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        # Retorna mensagem de sucesso com status 200
        return jsonify({'message': 'Conexão com o banco bem-sucedida!'}), 200
    except Error as e:
        # Retorna erro 500 se a query falhar
        return jsonify({'error': f'Erro ao executar query: {e}'}), 500
    finally:
        # Fecha a conexão e o cursor, se abertos
        if connection.is_connected():
            cursor.close()
            connection.close()

# Rota para salvar dados do formulário no banco
@app.route('/salvar-diagnostico', methods=['POST'])
def salvar_diagnostico():
    # Recebe os dados enviados no formato JSON
    dados = request.json
    if not dados:
        # Retorna erro 400 se nenhum dado for enviado
        return jsonify({'error': 'Nenhum dado recebido'}), 400
    # Tenta estabelecer conexão com o banco
    connection = get_db_connection()
    if connection is None:
        # Retorna erro 500 se a conexão falhar
        return jsonify({'error': 'Erro de conexão com o banco'}), 500
    try:
        # Prepara e executa a query de inserção
        cursor = connection.cursor()
        sql = """
        INSERT INTO diagnosticos 
        (nome, genero, idade, pressao_academica, rendimento_academico, satisfacao_estudo, 
         duracao_sono, habitos_alimentares, grau_academico, pensamento_suicida, 
         horas_estudando, pressao_financeira, historico_familiar) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        valores = (
            dados.get('nome'),
            dados.get('genero'),
            dados.get('idade'),
            dados.get('pressaoAcademica'),
            dados.get('rendimentoAcademico'),
            dados.get('satisfacaoEstudo'),
            dados.get('duracaoSono'),
            dados.get('habitosAlimentares'),
            dados.get('grauAcademico'),
            dados.get('pensamentoSuicida'),
            dados.get('horasEstudando'),
            dados.get('pressaoFinanceira'),
            dados.get('historicoFamiliar')
        )
        cursor.execute(sql, valores)
        # Confirma a inserção no banco
        connection.commit()
        # Retorna mensagem de sucesso com o ID do registro inserido
        return jsonify({'message': 'Diagnóstico salvo com sucesso!', 'id': cursor.lastrowid}), 200
    except Error as e:
        # Registra e retorna erro 500 se a inserção falhar
        print(f"Erro ao inserir: {e}")
        return jsonify({'error': 'Erro ao salvar no banco'}), 500
    finally:
        # Fecha a conexão e o cursor, se abertos
        if connection.is_connected():
            cursor.close()
            connection.close()

# Inicia o servidor Flask na porta 5000 com modo debug ativado
if __name__ == '__main__':
    app.run(debug=True, port=5000)