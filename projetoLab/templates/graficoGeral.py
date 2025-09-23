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
            password='senac',            # Senha do usuário do MySQL
            port='3306'
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
    connection = get_db_connection()
    if connection is None:
        return jsonify({'error': 'Erro de conexão com o banco'}), 500
    try:
        cursor = connection.cursor()

        # total de formulários
        cursor.execute("SELECT COUNT(id) FROM diagnosticos;")
        totalFormularios = cursor.fetchone()[0]

        # necessitam terapia
        cursor.execute("SELECT COUNT(id) FROM diagnosticos WHERE diagnostico_previsto = 'Possível depressão';")
        necessitamTerapia = cursor.fetchone()[0]

        naoNecessitam = totalFormularios - necessitamTerapia

        # evolução temporal (últimos 7 dias)
        cursor.execute("""
            SELECT DATE(created_at) AS dia,
                   COUNT(id) as formularios,
                   SUM(CASE WHEN diagnostico_previsto = 'Possível depressão' THEN 1 ELSE 0 END) AS terapia
            FROM diagnosticos
            GROUP BY dia
            ORDER BY dia DESC
            LIMIT 7;
        """)
        tempos = cursor.fetchall()
        et_labels = []
        et_formularios = []
        et_terapia = []
        for tempo in reversed(tempos):  # inverter ordem p/ cronológica
            et_labels.append(tempo[0].strftime('%d/%m'))
            et_formularios.append(tempo[1])
            et_terapia.append(tempo[2])

        # distribuição por gênero
        cursor.execute("""
            SELECT genero,
                   COUNT(*) AS total,
                   SUM(CASE WHEN diagnostico_previsto = 'Possível depressão' THEN 1 ELSE 0 END) AS terapia
            FROM diagnosticos
            GROUP BY genero;
        """)
        genero_rows = cursor.fetchall()
        genero = {}
        for row in genero_rows:
            genero[row[0] if row[0] else "Não Informado"] = {
                "total": row[1],
                "terapia": row[2]
            }

        # campos críticos (exemplo com alguns campos principais)
        camposCriticos = []

        # pressão acadêmica alta
        cursor.execute("""
            SELECT COUNT(*) FROM diagnosticos 
            WHERE diagnostico_previsto = 'Possível depressão' AND pressao_academica >= 4;
        """)
        freq = cursor.fetchone()[0]
        percentual = (freq / necessitamTerapia * 100) if necessitamTerapia else 0
        camposCriticos.append({"campo": "Pressão Acadêmica", "frequencia": freq, "percentual": round(percentual, 1)})

        # pensamento suicida = Sim
        cursor.execute("""
            SELECT COUNT(*) FROM diagnosticos 
            WHERE diagnostico_previsto = 'Possível depressão' AND pensamento_suicida = 'Sim';
        """)
        freq = cursor.fetchone()[0]
        percentual = (freq / necessitamTerapia * 100) if necessitamTerapia else 0
        camposCriticos.append({"campo": "Pensamento Suicida", "frequencia": freq, "percentual": round(percentual, 1)})

        # pressão financeira alta (>=7)
        cursor.execute("""
            SELECT COUNT(*) FROM diagnosticos 
            WHERE diagnostico_previsto = 'Possível depressão' AND pressao_financeira >= 7;
        """)
        freq = cursor.fetchone()[0]
        percentual = (freq / necessitamTerapia * 100) if necessitamTerapia else 0
        camposCriticos.append({"campo": "Pressão Financeira", "frequencia": freq, "percentual": round(percentual, 1)})

        # sono baixo (<6h)
        cursor.execute("""
            SELECT COUNT(*) FROM diagnosticos 
            WHERE diagnostico_previsto = 'Possível depressão' AND duracao_sono < 6;
        """)
        freq = cursor.fetchone()[0]
        percentual = (freq / necessitamTerapia * 100) if necessitamTerapia else 0
        camposCriticos.append({"campo": "Duração do Sono", "frequencia": freq, "percentual": round(percentual, 1)})

        # satisfação estudo baixa (<=2)
        cursor.execute("""
            SELECT COUNT(*) FROM diagnosticos 
            WHERE diagnostico_previsto = 'Possível depressão' AND satisfacao_estudo <= 2;
        """)
        freq = cursor.fetchone()[0]
        percentual = (freq / necessitamTerapia * 100) if necessitamTerapia else 0
        camposCriticos.append({"campo": "Satisfação no Estudo", "frequencia": freq, "percentual": round(percentual, 1)})

        return jsonify({
            "totalFormularios": totalFormularios,
            "necessitamTerapia": necessitamTerapia,
            "naoNecessitam": naoNecessitam,
            "evolucaoTemporal": {
                "labels": et_labels,
                "formularios": et_formularios,
                "terapia": et_terapia
            },
            "genero": genero,
            "camposCriticos": camposCriticos
        }), 200

    except Error as e:
        print(f"Erro ao consultar: {e}")
        return jsonify({"error": "Erro ao salvar no banco"}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# Inicia o servidor Flask na porta 5000 com modo debug ativado
if __name__ == '__main__':
    app.run(debug=True, port=5000)