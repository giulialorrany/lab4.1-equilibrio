from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
CORS(app)

# Função para estabelecer conexão com o banco de dados MySQL
def get_db_connection():
    try:
        # Configura a conexão com o banco de dados
        connection = mysql.connector.connect(
            host='localhost',               # Endereço do servidor MySQL
            database='project_equilibrio',  # Nome do banco de dados
            user='root',                   # Usuário do MySQL
            password='',            # Senha do usuário do MySQL
            port='3307'
        )
        print("Conexão com MySQL estabelecida!")
        return connection
    except Error as e:
        # Registra erros de conexão
        print(f"Erro detalhado ao conectar: {e}")
        return None
    
# Define rotas para a raiz ('/') e '/graficoGeral.html'
@app.route('/')
@app.route('/graficoGeral.html')
def home():
    # Serve o arquivo graficoGeral.html
    return send_file('graficoGeral.html')

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

# Rota para receber dados do banco
@app.route('/get_all', methods=['GET'])
def get_all():
     # Tenta estabelecer conexão com o banco
    connection = get_db_connection()
    if connection is None:
        # Retorna erro 500 se a conexão falhar
        return jsonify({'error': 'Erro de conexão com o banco'}), 500
    try:
# ----------------------------------------------------------------
        # Prepara e executa a query de consulta
        cursor = connection.cursor()
        sql = "SELECT count(id) AS qtd FROM diagnosticos;"
        cursor.execute(sql)
        totalFormularios = cursor.fetchone()[0]
        return jsonify({'totalFormularios': totalFormularios}), 200
# ----------------------------------------------------------------
    except Error as e:
        # Registra e retorna erro 500 se a inserção falhar
        print(f"Erro ao consultar: {e}")
        return jsonify({'error': 'Erro ao salvar no banco'}), 500
    finally:
        # Fecha a conexão e o cursor, se abertos
        if connection.is_connected():
            cursor.close()
            connection.close()

# Inicia o servidor Flask na porta 5000 com modo debug ativado
if __name__ == '__main__':
    app.run(debug=True, port=5000)