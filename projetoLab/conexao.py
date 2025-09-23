from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Inicializa a aplicação Flask
app = Flask(__name__)
# Configura CORS para permitir origens específicas e métodos
CORS(app 
# , resources={r"/*": {
#     "origins": ["http://localhost:5000", "http://127.0.0.1:5000"],
#     "methods": ["GET", "POST", "OPTIONS"],
#     "allow_headers": ["Content-Type"]
# }}
)

# Função para estabelecer conexão com o banco de dados MySQL
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='project_equilibrio',
            user='root',
            password='senac123',
            port='3306'
        )
        logging.info("Conexão com MySQL estabelecida!")
        return connection
    except Error as e:
        logging.error(f"Erro detalhado ao conectar: {e}")
        return None

# Função para carregar e treinar o modelo
def train_model():
    try:
        connection = get_db_connection()
        if connection is None:
            raise Exception("Erro ao conectar ao banco para treinar o modelo")
        
        # Carregar dados da tabela 'dados'
        query = "SELECT * FROM dados"
        df = pd.read_sql(query, connection)
        connection.close()
        logging.info("Dados carregados da tabela 'dados'")

        # Pré-processamento dos dados
        # Converter variáveis categóricas em numéricas
        label_encoders = {}
        categorical_columns = ['genero', 'horas_de_sono', 'habitos_alimentares', 'graduacao', 'pensamentos_suis', 'historico_familiar']
        
        for column in categorical_columns:
            le = LabelEncoder()
            df[column] = le.fit_transform(df[column].astype(str))
            label_encoders[column] = le
            logging.info(f"LabelEncoder aplicado na coluna: {column}")
        
        # Definir variáveis independentes (X) e dependente (y)
        X = df[['genero', 'idade', 'pressao_academica', 'IRA', 'satisfacao_estudo', 
                'horas_de_sono', 'habitos_alimentares', 'graduacao', 'pensamentos_suis', 
                'carga_horaria', 'estresse_finaneiro', 'historico_familiar']]
        y = df['depressao']

        # Dividir os dados em treino e teste (opcional, para validação)
        X_train, _, y_train, _ = train_test_split(X, y, test_size=0.2, random_state=42)

        # Treinar o modelo (usando Random Forest)
        model = RandomForestClassifier(random_state=42)
        model.fit(X_train, y_train)
        logging.info("Modelo treinado com sucesso")

        # Salvar o modelo e os encoders
        joblib.dump(model, 'modelo_depressao.pkl')
        joblib.dump(label_encoders, 'label_encoders.pkl')
        logging.info("Modelo e encoders salvos com sucesso")
        
        return model, label_encoders

    except Exception as e:
        logging.error(f"Erro ao treinar o modelo: {e}")
        return None, None

# Carregar o modelo treinado ou treinar se não existir
try:
    model = joblib.load('modelo_depressao.pkl')
    label_encoders = joblib.load('label_encoders.pkl')
    logging.info("Modelo e encoders carregados com sucesso")
except:
    model, label_encoders = train_model()

# Rotas existentes
@app.route('/')
@app.route('/index.html')
def home():
    logging.info("Rota / ou /index.html acessada")
    return send_file('index.html')

@app.route('/testar-conexao', methods=['GET', 'OPTIONS'])
def testar_conexao():
    logging.info("Rota /testar-conexao acessada")
    if request.method == 'OPTIONS':
        logging.info("Requisição OPTIONS recebida para /testar-conexao")
        return jsonify({}), 200

    connection = get_db_connection()
    if connection is None:
        logging.error("Erro ao conectar ao banco na rota /testar-conexao")
        return jsonify({'error': 'Erro ao conectar ao banco'}), 500
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        logging.info("Conexão com o banco testada com sucesso")
        return jsonify({'message': 'Conexão com o banco bem-sucedida!'}), 200
    except Error as e:
        logging.error(f"Erro ao executar query: {e}")
        return jsonify({'error': f'Erro ao executar query: {e}'}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/salvar-diagnostico', methods=['POST', 'OPTIONS'])
def salvar_diagnostico():
    logging.info("Rota /salvar-diagnostico acessada")
    if request.method == 'OPTIONS':
        logging.info("Requisição OPTIONS recebida para /salvar-diagnostico")
        return jsonify({}), 200

    dados = request.json
    if not dados:
        logging.error("Nenhum dado recebido na requisição")
        return jsonify({'error': 'Nenhum dado recebido'}), 400
    
    connection = get_db_connection()
    if connection is None:
        logging.error("Erro de conexão com o banco")
        return jsonify({'error': 'Erro de conexão com o banco'}), 500
    
    cursor = None  # Inicializar cursor como None para evitar UnboundLocalError
    try:
        # Validar campos obrigatórios
        required_fields = ['nome', 'genero', 'idade', 'pressaoAcademica', 'rendimentoAcademico',
                           'satisfacaoEstudo', 'duracaoSono', 'habitosAlimentares', 'grauAcademico',
                           'pensamentoSuicida', 'horasEstudando', 'pressaoFinanceira', 'historicoFamiliar']
        for field in required_fields:
            if field not in dados or dados[field] is None:
                logging.error(f"Campo obrigatório ausente: {field}")
                return jsonify({'error': f'Campo obrigatório ausente: {field}'}), 400

        # Converter duracaoSono (numérico) para horas_de_sono (categórico)
        try:
            duracao_sono = int(dados.get('duracaoSono'))
            if duracao_sono <= 4:
                horas_de_sono = 'Menos de 5 horas'
            elif duracao_sono <= 6:
                horas_de_sono = '5-6 horas'
            elif duracao_sono <= 8:
                horas_de_sono = '7-8 horas'
            else:
                horas_de_sono = 'Mais de 8 horas'
        except (ValueError, TypeError):
            logging.error("Valor inválido para duracaoSono")
            return jsonify({'error': 'Valor inválido para duracaoSono'}), 400

        # Preparar dados para predição
        dados_predicao = {
            'genero': dados.get('genero'),
            'idade': int(dados.get('idade')),  # Garantir que seja int
            'pressao_academica': int(dados.get('pressaoAcademica')),
            'IRA': float(dados.get('rendimentoAcademico')),  # Garantir que seja float
            'satisfacao_estudo': int(dados.get('satisfacaoEstudo')),
            'horas_de_sono': horas_de_sono,  # Usar valor categórico
            'habitos_alimentares': dados.get('habitosAlimentares'),
            'graduacao': dados.get('grauAcademico'),
            'pensamentos_suis': dados.get('pensamentoSuicida'),
            'carga_horaria': int(dados.get('horasEstudando')),
            'estresse_finaneiro': int(dados.get('pressaoFinanceira')),
            'historico_familiar': dados.get('historicoFamiliar')
        }
        logging.info(f"Dados preparados para predição: {dados_predicao}")
        
        # Converter para DataFrame
        df_novo = pd.DataFrame([dados_predicao])
        
        # Aplicar LabelEncoder nas variáveis categóricas
        for column in label_encoders:
            try:
                if df_novo[column].iloc[0] not in label_encoders[column].classes_:
                    logging.error(f"Valor inválido para {column}: {df_novo[column].iloc[0]}")
                    return jsonify({'error': f'Valor inválido para {column}: {df_novo[column].iloc[0]}'}), 400
                df_novo[column] = label_encoders[column].transform(df_novo[column].astype(str))
            except ValueError as e:
                logging.error(f"Erro ao aplicar LabelEncoder na coluna {column}: {e}")
                return jsonify({'error': f'Erro ao aplicar LabelEncoder na coluna {column}: {e}'}), 400
        logging.info("LabelEncoder aplicado com sucesso")
        
        # Selecionar as colunas para predição
        X_novo = df_novo[['genero', 'idade', 'pressao_academica', 'IRA', 'satisfacao_estudo', 
                          'horas_de_sono', 'habitos_alimentares', 'graduacao', 'pensamentos_suis', 
                          'carga_horaria', 'estresse_finaneiro', 'historico_familiar']]
        
        # Fazer a predição
        predicao = model.predict(X_novo)[0]
        probabilidade = model.predict_proba(X_novo)[0][1]  # Probabilidade de depressão (classe 1)
        logging.info(f"Predição realizada: {predicao}, Probabilidade: {probabilidade}")
        
        # Interpretar o resultado
        resultado = 'Possível depressão' if predicao == 1 else 'Sem indícios de depressão'
        
        # Inserir no banco, incluindo diagnostico_previsto
        cursor = connection.cursor()
        sql = """
        INSERT INTO diagnosticos 
        (nome, genero, idade, pressao_academica, rendimento_academico, satisfacao_estudo, 
         duracao_sono, habitos_alimentares, graduacao, pensamento_suicida, 
         horas_estudando, pressao_financeira, historico_familiar, diagnostico_previsto) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        valores = (
            dados.get('nome'),
            dados.get('genero'),
            int(dados.get('idade')),
            int(dados.get('pressaoAcademica')),
            float(dados.get('rendimentoAcademico')),
            int(dados.get('satisfacaoEstudo')),
            int(dados.get('duracaoSono')),
            dados.get('habitosAlimentares'),
            dados.get('grauAcademico'),
            dados.get('pensamentoSuicida'),
            int(dados.get('horasEstudando')),
            int(dados.get('pressaoFinanceira')),
            dados.get('historicoFamiliar'),
            resultado
        )
        logging.info(f"Executando query SQL com valores: {valores}")
        cursor.execute(sql, valores)
        connection.commit()
        logging.info("Dados inseridos no banco com sucesso")
        
        return jsonify({
            'message': 'Diagnóstico salvo com sucesso!',
            'id': cursor.lastrowid,
            'diagnostico': resultado,
            'probabilidade_depressao': round(probabilidade * 100, 2)
        }), 200

    except Error as e:
        logging.error(f"Erro ao inserir no banco: {e}")
        return jsonify({'error': f'Erro ao salvar no banco: {e}'}), 500
    except Exception as e:
        logging.error(f"Erro na predição: {e}")
        return jsonify({'error': f'Erro ao realizar a predição: {e}'}), 500
    finally:
        if cursor is not None and connection.is_connected():
            cursor.close()
            logging.info("Cursor fechado")
        if connection.is_connected():
            connection.close()
            logging.info("Conexão com o banco fechada")

if __name__ == '__main__':
    app.run(debug=True, port=5000)