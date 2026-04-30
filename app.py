import os
import uuid
from flask import Flask, request, jsonify, render_template, redirect, url_for
from psycopg2.extras import RealDictCursor
from database import get_connection

app = Flask(__name__)

# --- CONFIGURAÇÕES DE UPLOAD ---
# Define a pasta onde os arquivos serão salvos
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Extensões permitidas
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Garante que a pasta static/uploads exista no servidor
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Função para checar a extensão
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# -------------------------------


# Teste API
@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "API de catalogo de filmes"}), 200


# Ping
@app.route('/ping', methods=['GET'])
def ping():
    conn = get_connection()
    conn.close()
    return jsonify({"message": "pong! API Rodando!", "db": str(conn)}), 200


# Listar todos os filmes
@app.route('/filmes', methods=['GET'])
def listar_filmes():
    sql = "SELECT * FROM filmes"
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(sql)
        filmes = cursor.fetchall()
        conn.close()
        return render_template("index.html", filmes=filmes)
    except Exception as ex:
        print('erro: ', str(ex))
        return jsonify({"message": "erro ao listar filmes"}), 500


@app.route("/novo", methods=["GET", "POST"])
def novo_filme():
    sql = "INSERT INTO filmes (titulo, genero, ano, url_capa) VALUES (%s, %s, %s, %s)"
    try:
        if request.method == "POST":
            titulo = request.form["titulo"]
            genero = request.form["genero"]
            ano = request.form["ano"]

            # 1. Recebe o arquivo através da requisição
            arquivo = request.files.get("capa")

            if arquivo and arquivo.filename != '':
                # 2. Permite apenas as extensões jpeg, jpg, png
                if allowed_file(arquivo.filename):
                    # Pega a extensão original do arquivo
                    extensao = arquivo.filename.rsplit('.', 1)[1].lower()

                    # 3. Renomeia para uma hash única
                    nome_unico = f"{uuid.uuid4().hex}.{extensao}"

                    # 4. Salva o arquivo na pasta static/uploads
                    caminho_salvar = os.path.join(app.config['UPLOAD_FOLDER'], nome_unico)
                    arquivo.save(caminho_salvar)

                    # 5. Caminho do arquivo para salvar no banco de dados
                    # Usamos barra normal (/) para funcionar bem na web
                    url_capa_banco = f"/uploads/{nome_unico}"
                else:
                    return jsonify({"message": "Extensão de arquivo não permitida. Use apenas JPG, JPEG ou PNG."}), 400
            else:
                return jsonify({"message": "Nenhuma imagem foi enviada."}), 400

            params = [titulo, genero, ano, url_capa_banco]

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            conn.close()
            return redirect(url_for("listar_filmes"))

        return render_template("novo_filme.html")
    except Exception as ex:
        print('erro: ', str(ex))
        return jsonify({"message": "erro ao cadastrar filme"}), 500


@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar_filme(id):
    try:
        conn = get_connection()
        if request.method == "POST":
            titulo = request.form["titulo"]
            genero = request.form["genero"]
            ano = request.form["ano"]

            # Aqui lidamos com a edição. Se o usuário mandar uma capa nova, processamos.
            arquivo = request.files.get("capa")
            url_capa_banco = None

            if arquivo and arquivo.filename != '':
                if allowed_file(arquivo.filename):
                    extensao = arquivo.filename.rsplit('.', 1)[1].lower()
                    nome_unico = f"{uuid.uuid4().hex}.{extensao}"
                    caminho_salvar = os.path.join(app.config['UPLOAD_FOLDER'], nome_unico)
                    arquivo.save(caminho_salvar)
                    url_capa_banco = f"static/uploads/{nome_unico}"
                else:
                    return jsonify({"message": "Extensão inválida"}), 400

            # Se não mandou imagem nova, precisamos manter a antiga no banco
            if url_capa_banco:
                sql_update = "UPDATE filmes SET titulo = %s, genero = %s, ano = %s, url_capa = %s WHERE id = %s"
                params = [titulo, genero, ano, url_capa_banco, id]
            else:
                sql_update = "UPDATE filmes SET titulo = %s, genero = %s, ano = %s WHERE id = %s"
                params = [titulo, genero, ano, id]

            cursor = conn.cursor()
            cursor.execute(sql_update, params)
            conn.commit()
            conn.close()
            return redirect(url_for("listar_filmes"))

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        sql = "SELECT * FROM filmes WHERE id = %s"
        params = [id]
        cursor.execute(sql, params)
        filme = cursor.fetchone()
        conn.close()

        if filme is None:
            return redirect(url_for("listar_filmes"))
        return render_template("editar_filme.html", filme=filme)
    except Exception as ex:
        print('erro: ', str(ex))
        return jsonify({"message": "erro ao editar filme"}), 500


@app.route("/deletar/<int:id>", methods=["POST"])
def deletar_filme(id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = "DELETE FROM filmes WHERE id = %s"
        params = [id]
        cursor.execute(sql, params)
        conn.commit()
        conn.close()
        return redirect(url_for("listar_filmes"))
    except Exception as ex:
        print('erro: ', str(ex))
        return jsonify({"message": "erro ao deletar filme"}), 500


if __name__ == '__main__':
    app.run(debug=True)