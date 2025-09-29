import os
from flask import Flask, render_template, request, jsonify, session
import PyPDF2 # Para ler PDF
from openai import OpenAI # Para a nova versão da biblioteca OpenAI (versão >= 1.0.0)
import json # Para lidar com JSON

app = Flask(__name__)

# --- CONFIGURAÇÃO PARA PRODUÇÃO E SEGURANÇA ---

# 1. SECRET_KEY: ESSENCIAL para segurança de sessões e cookies.
#    Em produção, deve ser uma string longa e aleatória, armazenada como variável de ambiente.
#    Use o comando Python: import os; print(os.urandom(24).hex()) para gerar um valor.
#    No Render, você irá DEFINIR 'SESSION_SECRET' NAS VARIÁVEIS DE AMBIENTE.
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'sua_chave_secreta_padrao_muito_insegura_apenas_para_desenvolvimento_local')

# 2. Desabilitar modo de DEBUG em produção
#    No Render, isso será automaticamente tratado, mas é bom ter no código.
app.config['DEBUG'] = False # Sempre False para deploy de produção

# 3. Carregar Chaves de API (OpenAI) de variáveis de ambiente
#    No Render, você irá DEFINIR 'OPENAI_API_KEY' NAS VARIÁVEIS DE AMBIENTE.
openai_api_key = os.environ.get('OPENAI_API_KEY')

# --- INICIALIZAÇÃO DA API DA OPENAI ---
client = None # Inicializa client como None
if openai_api_key:
    client = OpenAI(api_key=openai_api_key)
else:
    print("AVISO: A variável de ambiente OPENAI_API_KEY não está definida.")
    print("As chamadas à API da OpenAI falharão até que seja configurada no ambiente.")
    # Em um ambiente de produção crítico, considere lançar uma exceção:
    # raise ValueError("OPENAI_API_KEY não definida. O aplicativo não pode iniciar sem ela.")

# --- ROTAS DA SUA APLICAÇÃO ---

@app.route('/')
def home():
    # A rota principal deve renderizar seu HTML (geralmente index.html)
    return render_template('index.html')

@app.route('/processar_email', methods=['POST'])
def processar_email():
    if not openai_api_key or not client:
        return jsonify({"error": "Configuração da OpenAI API key está faltando no servidor."}), 500

    email_content = ""
    # Verifica se há um arquivo sendo enviado
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
    # Se não houver arquivo, verifica o campo de texto (text_area)
    elif 'email_text' in request.form:
        email_content = request.form['email_text']
    else:
        return jsonify({"error": "Nenhum conteúdo de e-mail fornecido."}), 400

    if not email_content.strip():
        return jsonify({"error": "O conteúdo do e-mail não pode estar vazio."}), 400

    try:
        # Chamada à API da OpenAI para classificação e resposta
        # A linha com o exemplo JSON foi removida para evitar problemas de sintaxe.
        # A instrução 'response_format' garante a resposta JSON.
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # Ou "gpt-4", se preferir
            messages=[
                {"role": "system", "content": "Você é um assistente que classifica e-mails como 'Produtivo' ou 'Improdutivo' e gera uma resposta adequada. Responda no formato JSON com as chaves 'classificacao' e 'resposta'."},
                {"role": "user", "content": f"Classifique o seguinte e-mail: '{email_content}'. Gere também uma resposta curta e profissional para ele. Ambas as saídas devem estar em português."}
            ],
            max_tokens=200, # Aumente conforme a necessidade de respostas mais longas
            temperature=0.7,
            response_format={ "type": "json_object" } # Garante que a resposta venha em JSON
        )
        ai_response_content = response.choices[0].message.content
        ai_data = json.loads(ai_response_content) # Converte a string JSON para um dicionário Python

        return jsonify({
            "classificacao": ai_data.get("classificacao", "Desconhecida"),
            "resposta_sugerida": ai_data.get("resposta", "Não foi possível gerar uma resposta.")
        })
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON da OpenAI: {e}")
        print(f"Resposta bruta da OpenAI: {ai_response_content}")
        return jsonify({"error": f"Erro de formato na resposta da IA. Tente novamente ou ajuste o prompt. Detalhes: {e}"}), 500
    except Exception as e:
        print(f"Erro geral ao processar com OpenAI: {e}")
        return jsonify({"error": f"Erro ao processar e-mail com a IA: {str(e)}"}), 500

# --- PONTO DE ENTRADA PARA DESENVOLVIMENTO LOCAL ---
# Este bloco 'if __name__ == "__main__":' só será executado quando você rodar
# 'python app.py' diretamente. Em produção, um servidor WSGI (como Gunicorn)
# importará o objeto 'app' diretamente, ignorando este bloco.
if __name__ == "__main__":
    # Para desenvolvimento local, use a porta 5000 por padrão, mas permita que uma variável de ambiente PORT a substitua.
    port = int(os.environ.get('PORT', 5000))
    print(f"Rodando em modo de desenvolvimento local. DEBUG={app.config['DEBUG']} na porta {port}")
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])
