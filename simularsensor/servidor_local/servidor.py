from flask import Flask, request, jsonify
import oracledb
from datetime import datetime

app = Flask(__name__)

# *** Configurações do Banco de Dados Oracle ***
DB_USER = "system"  # Substitua pelo seu nome de usuário Oracle
DB_PASSWORD = "MinhaSenha123"  # Substitua pela sua senha Oracle
DB_DSN = "localhost/FREEPDB1"  # Substitua pela sua string de conexão DSN (e.g., "localhost/XEPDB1" ou "your_oracle_host:1521/your_service_name")

def conectar_db():
    """Conecta ao banco de dados Oracle."""
    try:
        # Para Thin mode (não requer Oracle Client), use:
        # conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
        # Para Thick mode (requer Oracle Client configurado no PATH ou via init_oracle_client):
        # Se o Oracle Client não estiver no PATH, você pode precisar inicializá-lo:
        # oracledb.init_oracle_client(lib_dir="/path/to/your/instantclient_XX_Y") # Ex: "/opt/oracle/instantclient_21_12"
        conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
        cursor = conn.cursor()
        print("Conectado ao Oracle DB com sucesso!")
        return conn, cursor
    except oracledb.Error as error:
        print(f"Erro ao conectar ao Oracle: {error}")
        return None, None

def criar_tabela_se_nao_existir():
    """Cria a tabela 'leituras_agua' no Oracle se ela não existir."""
    conn, cursor = conectar_db()
    if conn and cursor:
        try:
            cursor.execute("""
                CREATE TABLE leituras_agua (
                    timestamp VARCHAR2(255) PRIMARY KEY,
                    chlorine NUMBER,
                    turbidity NUMBER,
                    conductivity NUMBER,
                    ph NUMBER,
                    prediction VARCHAR2(20)
                )
            """)
            conn.commit()
            print("Tabela 'leituras_agua' criada (ou já existia e a criação foi ignorada se o erro for 'name is already used').")
        except oracledb.Error as error:
            # ORA-00955: nome já está sendo usado por um objeto existente
            if error.args[0].code == 955:
                print("A tabela 'leituras_agua' já existe.")
            else:
                print(f"Erro ao criar a tabela 'leituras_agua': {error}")
                if conn: # Rollback somente se a conexão for bem-sucedida
                    conn.rollback()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    else:
        print("Não foi possível conectar ao DB para criar a tabela.")

# Chama a função para garantir que a tabela exista ao iniciar o servidor
criar_tabela_se_nao_existir()

def inserir_dados_agua(chlorine, turbidity, conductivity, ph, prediction):
    """Insere uma nova leitura de dados de água na tabela 'leituras_agua'."""
    conn, cursor = conectar_db()
    if conn and cursor:
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f") # Adicionando milissegundos para unicidade
        try:
            cursor.execute("""
                INSERT INTO leituras_agua (timestamp, chlorine, turbidity, conductivity, ph, prediction)
                VALUES (:timestamp, :chlorine, :turbidity, :conductivity, :ph, :prediction)
            """,
            timestamp=timestamp_str, chlorine=chlorine, turbidity=turbidity,
            conductivity=conductivity, ph=ph, prediction=prediction
            )
            conn.commit()
            print(f"Dados inseridos no Oracle em {timestamp_str}!")
            return True
        except oracledb.Error as error:
            print(f"Erro ao inserir dados no Oracle: {error}")
            if conn: conn.rollback() # Rollback se ocorrer um erro durante a inserção
            return False
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
    else:
        print("Não foi possível conectar ao banco de dados para inserir dados.")
        return False

def simular_predicao_ml(chlorine, turbidity, conductivity, ph):
    """
    Simula um modelo de Machine Learning para prever a potabilidade da água.
    Retorna "POTAVEL", "SUSPEITA", ou "NAO_POTAVEL".
    ESTES SÃO APENAS VALORES DE EXEMPLO. SUBSTITUA PELA LÓGICA DO SEU MODELO REAL.
    """
    print(f"Simulando ML com: Cloro={chlorine}, Turbidez={turbidity}, Condut.={conductivity}, pH={ph}")
    
    # Exemplo de regras (muito simplificado):
    # pH ideal: 6.5 - 8.5
    # Turbidez ideal: < 5 NTU
    # Cloro residual livre ideal: 0.2 - 2.0 ppm (varia conforme regulamentação)
    # Condutividade: varia muito, mas valores extremos podem ser problemáticos.
    
    score = 0
    
    # pH
    if 6.5 <= ph <= 8.5:
        score += 2
    elif 6.0 <= ph < 6.5 or 8.5 < ph <= 9.0:
        score += 1
    else: # < 6.0 or > 9.0
        score -= 1

    # Turbidez (assumindo menor é melhor)
    if turbidity < 5: # Ideal
        score += 2
    elif turbidity < 25: # Aceitável/Suspeito
        score += 1
    elif turbidity < 100: # Suspeito Alto
        score += 0
    else: # > 100 NTU, Não potável
        score -= 2
        
    # Cloro Residual (exemplo de faixa)
    if 0.2 <= chlorine <= 2.0: # Ideal
        score += 2
    elif 0.1 <= chlorine < 0.2 or 2.0 < chlorine <= 4.0: # Limite / Excesso leve
        score += 1
    else: # Muito baixo ou muito alto
        score -=1

    # Condutividade (exemplo muito genérico, depende da fonte da água)
    if conductivity < 50: # Pode ser muito pura, potencialmente corrosiva ou sem minerais
        score +=0 
    elif conductivity < 1000: # Geralmente OK
        score += 1
    elif conductivity < 2500: # Limite para água potável em algumas normas
        score += 0
    else: # > 2500 uS/cm - provavelmente não potável
        score -=1

    print(f"Score de potabilidade (simulado): {score}")

    if score >= 5:
        return "POTAVEL"
    elif score >= 2:
        return "SUSPEITA"
    else:
        return "NAO_POTAVEL"


@app.route('/data', methods=['GET'])
def receive_data():
    try:
        chlorine_str = request.args.get('chlorine')
        turbidity_str = request.args.get('turbidity')
        conductivity_str = request.args.get('conductivity')
        ph_str = request.args.get('ph')

        if None in [chlorine_str, turbidity_str, conductivity_str, ph_str]:
            return "Erro: Parâmetros ausentes (chlorine, turbidity, conductivity, ph)", 400

        chlorine = float(chlorine_str)
        turbidity = float(turbidity_str)
        conductivity = float(conductivity_str)
        ph = float(ph_str)

        print("Dados Recebidos do ESP32:")
        print(f"  Cloro: {chlorine}")
        print(f"  Turbidez: {turbidity}")
        print(f"  Condutividade: {conductivity}")
        print(f"  pH: {ph}")

        # 2. Simular predição do modelo de Machine Learning
        prediction = simular_predicao_ml(chlorine, turbidity, conductivity, ph)
        print(f"Predição Simulada: {prediction}")

        # 3. Inserir dados no Oracle
        if not inserir_dados_agua(chlorine, turbidity, conductivity, ph, prediction):
            # Se a inserção falhar, ainda retorna a predição para o ESP32, mas loga o erro.
             print("ALERTA: Falha ao inserir dados no Oracle, mas a predição será enviada ao ESP32.")
        
        # 4. Retornar a predição para o ESP32 como texto plano
        return prediction, 200

    except ValueError:
        return "Erro: Parâmetros inválidos (devem ser números).", 400
    except Exception as e:
        print(f"Erro inesperado no servidor: {e}")
        return f"Erro interno no servidor: {str(e)}", 500

@app.route('/get_all_data', methods=['GET'])
def get_all_data_from_db():
    """Lista todas as leituras da tabela 'leituras_agua' do Oracle."""
    conn, cursor = conectar_db()
    registros = []
    if conn and cursor:
        try:
            cursor.execute("SELECT timestamp, chlorine, turbidity, conductivity, ph, prediction FROM leituras_agua ORDER BY timestamp DESC")
            colunas = [desc[0].lower() for desc in cursor.description] # Nomes das colunas em minúsculo
            for row in cursor:
                registros.append(dict(zip(colunas, row)))
        except oracledb.Error as error:
            print(f"Erro ao listar dados do Oracle: {error}")
            return jsonify({"error": str(error)}), 500
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
    else:
        return jsonify({"error": "Não foi possível conectar ao banco de dados para listar dados."}), 500
    return jsonify(registros)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
    print("Servidor Flask rodando em http://0.0.0.0:8000")