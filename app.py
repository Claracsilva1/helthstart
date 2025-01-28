import sqlite3
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder=".")
CORS(app)

# Criar o banco de dados SQLite
def criar_banco():
    conn = sqlite3.connect("exames.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS exames (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cpf TEXT NOT NULL,
        tipo TEXT NOT NULL,
        data TEXT NOT NULL,
        hospital TEXT NOT NULL,
        link TEXT NOT NULL
    )
    """)

    cursor.execute("SELECT COUNT(*) FROM exames")
    total = cursor.fetchone()[0]

    if total == 0:
        cursor.executemany("""
        INSERT INTO exames (cpf, tipo, data, hospital, link) VALUES (?, ?, ?, ?, ?)
        """, [
            ("123.456.789-00", "Hemograma Completo", "2024-01-15", "Fleury", "https://exemplo.com/hemograma.pdf"),
            ("123.456.789-00", "Ressonância Magnética", "2023-10-20", "Hospital Einstein", "https://exemplo.com/ressonancia.pdf"),
            ("987.654.321-11", "Raio-X do Tórax", "2024-02-05", "Sírio-Libanês", "https://exemplo.com/raiox.pdf")
        ])
        print("Banco de dados criado com sucesso!")

    conn.commit()
    conn.close()

criar_banco()

@app.route("/")
def serve_index():
    return send_from_directory(".", "index.html")

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    crm = data.get("crm")
    senha = data.get("password")

    medicos = {
        "123456-SP": {"senha": "senha123", "nome": "Dr. João"},
        "654321-RJ": {"senha": "senha456", "nome": "Dra. Maria"}
    }

    if crm in medicos and medicos[crm]["senha"] == senha:
        return jsonify({"message": "Login bem-sucedido!", "nome": medicos[crm]["nome"]}), 200
    else:
        return jsonify({"error": "Credenciais inválidas"}), 401

@app.route('/exams', methods=['GET'])
def buscar_exames():
    cpf = request.args.get("cpf_paciente")

    conn = sqlite3.connect("exames.db")
    cursor = conn.cursor()

    cursor.execute("SELECT tipo, data, hospital, link FROM exames WHERE cpf = ?", (cpf,))
    exames = cursor.fetchall()
    conn.close()

    if exames:
        exames_formatados = [{"tipo": e[0], "data": e[1], "hospital": e[2], "link": e[3]} for e in exames]
        return jsonify({"paciente": cpf, "exames": exames_formatados}), 200
    else:
        return jsonify({"error": "Nenhum exame encontrado"}), 404

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
