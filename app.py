import os
from flask import Flask, render_template, request, jsonify, session
import PyPDF2 # Certifique-se de que PyPDF2 esteja no seu requirements.txt
# import openai # Se você estiver usando o SDK openai, descomente e use aqui
import json # Necessário para o jsonify, mas geralmente já é importado pelo Flask

app = Flask(__name__)

# --- Configurações para Produção ---

# 1. SECRET_KEY: ESSENCIAL para segurança de sessões e cookies.
#    Em produção, deve ser uma string longa e aleatória, armazenada como variável de ambiente.
#    'your_insecure_default_secret_for_dev_only' é um fallback MUITO INSEGURO para desenvolvimento.
#    NO RENDER, VOCÊ IRÁ DEFINIR 'SESSION_SECRET' NAS VARIÁVEIS DE AMBIENTE.
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'your_insecure_default_secret_for_dev_only')

# 2. Desabilitar modo de DEBUG em produção
#    NO RENDER, NÓS IREMOS GARANTIR QUE ISSO ESTEJA DESATIVADO.
app.config['DEBUG'] = False # Sempre False para deploy de produção

# 3. Carregar Chaves de API (OpenAI) de variáveis de ambiente
#    NO RENDER, VOCÊ IRÁ DEFINIR 'OPENAI_API_KEY' NAS VARIÁVEIS DE AMBIENTE.
openai_api_key = os.environ.get('OPENAI_API_KEY')

if not openai_api_key:
    # Em produção, é melhor levantar um erro se a chave não estiver definida
    # para garantir que o aplicativo não inicie com funcionalidades críticas desabilitadas.
    # No desenvolvimento, você pode ter um aviso ou um fallback.
    print("AVISO: A variável de ambiente OPENAI_API_KEY não está definida.")
    # No Render, se isso acontecer, o deploy vai falhar, o que é o comportamento desejado.
    # raise ValueError("OPENAI_API_KEY não definida. O aplicativo não pode iniciar em produção.")

# --- Configuração do OpenAI (se estiver usando o SDK) ---
# Se você estiver usando o SDK da OpenAI (versão >= 1.0.0), a chave é configurada assim:
# from openai import OpenAI
# client = OpenAI(api_key=openai_api_key)

# Se estiver usando a versão antiga do SDK (0.x.x):
# import openai
# openai.api_key = openai_api_key


# --- Suas Rotas e Lógica de Aplicativo ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/classify-email', methods=['POST'])
def classify_email():
    email_content = ""
    if 'email_file' in request.files and request.files['email_file'].filename != '':
        file = request.files['email_file']
        if file.filename.endswith('.txt'):
            email_content = file.read().decode('utf-8')
        elif file.filename.endswith('.pdf'):
            try:
                reader = PyPDF2.PdfReader(file)
                for page_num in range(len(reader.pages)):
                    email_content += reader.pages[page_num].extract_text() + "\n"
            except Exception as e:
                return jsonify({"error": f"Erro ao processar PDF: {str(e)}"}), 400
        else:
            return jsonify({"error": "Formato de arquivo não suportado. Use .txt ou .pdf."}), 400
    elif 'email_text' in request.form:
        email_content = request.form['email_text']
    else:
        return jsonify({"error": "Nenhum conteúdo de e-mail fornecido."}), 400

    if not email_content.strip():
        return jsonify({"error": "O conteúdo do e-mail não pode estar vazio."}), 400

    try:
        # AQUI VOCÊ INTEGRARÁ COM A API DO OPENAI
        # Estou usando um placeholder para simular a resposta,
        # substitua pela sua lógica real da OpenAI.
        # Exemplo com o novo SDK (se client estiver definido globalmente):
        # response = client.chat.completions.create(
        #     model="gpt-3.5-turbo",
        #     messages=[
        #         {"role": "system", "content": "Você é um assistente que classifica e-mails como 'Produtivo' ou 'Improdutivo' e gera uma resposta."},
        #         {"role": "user", "content": f"Classifique este e-mail: '{email_content}' e gere uma resposta para ele. Responda no formato JSON com 'classificacao' e 'resposta'."}
        #     ]
        # )
        # ai_response_content = response.choices[0].message.content
        # ai_data = json.loads(ai_response_content) # Assumindo que a IA responde em JSON

        # Placeholder da resposta da IA:
        ai_data = {
            "classificacao": "Produtivo" if "urgente" in email_content.lower() else "Improdutivo",
            "resposta": f"Olá! Recebi seu e-mail e ele foi classificado como '{'Produtivo' if 'urgente' in email_content.lower() else 'Improdutivo'}'. Sua resposta será processada em breve. O conteúdo do e-mail é: {email_content[:100]}..."
        }

        return jsonify({
            "classificacao": ai_data.get("classificacao", "Desconhecida"),
            "resposta_sugerida": ai_data.get("resposta", "Não foi possível gerar uma resposta.")
        })

    except Exception as e:
        print(f"Erro ao processar com OpenAI: {e}")
        return jsonify({"error": f"Erro ao processar e-mail com a IA: {str(e)}"}), 500

# --- Ponto de Entrada para Desenvolvimento Local ---
# Este bloco 'if __name__ == "__main__":' só será executado quando você rodar
# 'python app.py' diretamente. Em produção, um servidor WSGI (como Gunicorn)
# importará o objeto 'app' diretamente, ignorando este bloco.
if __name__ == "__main__":
    # Para desenvolvimento local, use a porta 5000 por padrão, mas permita que uma variável de ambiente PORT a substitua.
    port = int(os.environ.get('PORT', 5000))
    print(f"Rodando em modo de desenvolvimento local. DEBUG={app.config['DEBUG']} na porta {port}")
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])