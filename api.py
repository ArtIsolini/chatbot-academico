from flask import Flask, request, jsonify
from flask_cors import CORS
from chatbot.chatbot import ChatbotAcademico

app = Flask(__name__)
CORS(app)  # Permite que o JavaScript acesse a API sem erros de segurança

# Inicializa o chatbot global
bot = ChatbotAcademico()
bot.conectar_bd()

@app.route('/login', methods=['POST'])
def login():
    dados = request.json
    usuario = dados.get('usuario')
    senha = dados.get('senha')
    
    sucesso = bot.autenticar(usuario, senha)
    if sucesso:
        return jsonify({"status": "sucesso", "aluno": bot.aluno_logado})
    return jsonify({"status": "erro", "mensagem": "Usuário ou senha inválidos"}), 401

@app.route('/perguntar', methods=['POST'])
def perguntar():
    dados = request.json
    pergunta = dados.get('pergunta')
    
    if not bot.aluno_logado:
        return jsonify({"status": "erro", "mensagem": "Aluno não autenticado"}), 401
        
    resposta = bot.consultar_gemini(pergunta)
    return jsonify({"resposta": resposta})

if __name__ == '__main__':
    app.run(port=5000, debug=True)