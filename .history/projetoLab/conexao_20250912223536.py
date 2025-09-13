from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
CORS(app)  # Habilita CORS para evitar problemas com requisições de outros domínios

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='equilibrio',
            user='root',
            password='sua_senha_aqui'  # Substitua pela senha correta do MySQL
        )
        print("Conexão com MySQL estabelecida!")
        return connection
    except Error as e:
        print(f"Erro detalhado ao conectar: {e}")
        return None

@app.route('/')
@app.route('/index.html')
def home():
    return send_file('index.html')  # Serve o index.html

@app.route('/conexao', methods=['GET'])
def testar_conexao():
    connection = get_db_connection()
    if connection is None:
        return jsonify({'error': 'Erro ao conectar ao banco'}), 500
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        return jsonify({'message': 'Conexão com o banco bem-sucedida!'}), 200
    except Error as e:
        return jsonify({'error': f'Erro ao executar query: {e}'}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/salvar-diagnostico', methods=['POST'])
def salvar_diagnostico():
    dados = request.json
    if not dados:
        return jsonify({'error': 'Nenhum dado recebido'}), 400
    connection = get_db_connection()
    if connection is None:
        return jsonify({'error': 'Erro de conexão com o banco'}), 500
    try:
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
        connection.commit()
        return jsonify({'message': 'Diagnóstico salvo com sucesso!', 'id': cursor.lastrowid}), 200
    except Error as e:
        print(f"Erro ao inserir: {e}")
        return jsonify({'error': 'Erro ao salvar no banco'}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)