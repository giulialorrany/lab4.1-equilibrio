import mysql.connector
from mysql.connector import Error

try:
    # Configurações de conexão
    connection = mysql.connector.connect(
        host='localhost',          # Ou IP do servidor MySQL
        database='equilibrio',     # Nome do banco criado anteriormente
        user='root',               # Seu usuário MySQL (mude se necessário)
        password='sua_senha_aqui'  # Senha do MySQL (NUNCA commite isso em git!)
    )

    if connection.is_connected():
        print("Conexão bem-sucedida!")
        
        # Exemplo: Inserir um dado de teste
        cursor = connection.cursor()
        sql = """
        INSERT INTO diagnosticos (nome, genero, idade) 
        VALUES (%s, %s, %s)
        """
        valores = ('Exemplo Python', 'Masculino', 30)
        cursor.execute(sql, valores)
        connection.commit()  # Confirma a inserção
        print(f"{cursor.rowcount} registro inserido. ID: {cursor.lastrowid}")
        
        # Verificar dados
        cursor.execute("SELECT * FROM diagnosticos LIMIT 1")
        resultado = cursor.fetchone()
        print("Dado de exemplo:", resultado)

except Error as e:
    print(f"Erro ao conectar: {e}")

finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("Conexão fechada.")