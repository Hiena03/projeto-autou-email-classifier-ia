import os
from flask import Flask, render_template, request, jsonify, session
import PyPDF2 # Para ler PDF
from openai import OpenAI # Para a nova versão da biblioteca OpenAI (versão >= 1.0.0)
import json # Para lidar com JSON

app = Flask(__name__)

# --- CONFIGURAÇÃO PARA PRODUÇÃO E SEGURANÇA ---

# 1. SECRET_KEY: ESSENCIAL para segurança de sessões e cookies.
#    Em produção, deve ser uma string longa e aleatória, armazenada como variável de ambiente.
#    No Render, você DEVE DEFINIR 'SESSION_SECRET' NAS VARIÁVEIS DE AMBIENTE.
#    Gere uma string como esta no terminal: python -c "import os; print(os.urandom(32).hex())"
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'uma_chave_secreta_padrao_muito_insegura_apenas_para_desenvolvimento_local')

# 2. Desabilitar modo de DEBUG em produção
app.config['DEBUG'] = False # Sempre False para deploy de produção

# 3. Carregar Chaves de API (OpenAI) de variáveis de ambiente
#    No Render, você DEVE DEFINIR 'OPENAI_API_KEY' NAS VARIÁVEIS DE AMBIENTE.
openai_api_key = os.environ.get('OPENAI_API_KEY')

# --- DEBUGGING: Verificar Variáveis de Ambiente (estes prints aparecerão nos logs do Render) ---
print(f"DEBUG: Ambiente 'SECRET_KEY' configurado? {'Sim' if app.config['SECRET_KEY'] != 'uma_chave_secreta_padrao_muito_insegura_apenas_para_desenvolvimento_local' else 'Não (usando padrão inseguro)'}")
print(f"DEBUG: Ambiente 'OPENAI_API_KEY' presente? {'Sim' if openai_api_key else 'Não'}")

# --- INICIALIZAÇÃO DA API DA OPENAI ---
client = None # Inicializa client como None
if openai_api_key:
    try:
        client = OpenAI(api_key=openai_api_key)
        print("DEBUG: Cliente OpenAI inicializado com sucesso.")
    except Exception as e:
        print(f"ERRO CRÍTICO: Falha ao inicializar o cliente OpenAI: {e}")
        # Em produção, você pode querer levantar uma exceção aqui para impedir o deploy de um app disfuncional
        # raise ValueError(f"Falha na inicialização da OpenAI: {e}")
else:
    print("AVISO: A variável de ambiente OPENAI_API_KEY não está definida no ambiente. As chamadas à API da OpenAI falharão.")

# --- ROTAS DA SUA APLICAÇÃO ---

@app.route('/')
def home():
    print("DEBUG: Rota '/' acessada. Renderizando index.html")
    return render_template('index.html')

@app.route('/processar_email', methods=['POST'])
def processar_email():
    print("DEBUG: Rota '/processar_email' acessada.")

    if not client: # Verifica se o cliente OpenAI foi inicializado com sucesso
        print("ERRO: Cliente OpenAI não inicializado. Verifique a OPENAI_API_KEY nas variáveis de ambiente.")
        return jsonify({"error": "O serviço de IA não está disponível (API Key ausente ou inválida)."}), 500

    email_content = ""
    # Verifica se há um arquivo sendo enviado
    if 'email_file' in request.files and request.files['email_file'].filename != '':
        file = request.files['email_file']
        print(f"DEBUG: Arquivo recebido: {file.filename}")
        if file.filename.lower().endswith('.txt'):
            email_content = file.read().decode('utf-8')
        elif file.filename.lower().endswith('.pdf'):
            try:
                reader = PyPDF2.PdfReader(file)
                for page_num in range(len(reader.pages)):
                    email_content += reader.pages[page_num].extract_text() + "\n"
                print("DEBUG: PDF processado.")
            except Exception as e:
                print(f"ERRO: Erro ao processar PDF: {str(e)}")
                return jsonify({"error": f"Erro ao processar PDF: {str(e)}"}), 400
        else:
            print(f"ERRO: Formato de arquivo não suportado: {file.filename}")
            return jsonify({"error": "Formato de arquivo não suportado. Use .txt ou .pdf."}), 400
    # Se não houver arquivo, verifica o campo de texto (text_area)
    elif 'email_text' in request.form:
        email_content = request.form['email_text']
        print("DEBUG: Texto de e-mail recebido via formulário.")
    else:
        print("ERRO: Nenhum conteúdo de e-mail fornecido (nem arquivo, nem texto).")
        return jsonify({"error": "Nenhum conteúdo de e-mail fornecido."}), 400

    if not email_content.strip():
        print("ERRO: Conteúdo do e-mail vazio ou apenas espaços em branco.")
        return jsonify({"error": "O conteúdo do e-mail não pode estar vazio."}), 400

    try:
        print("DEBUG: Iniciando chamada à API da OpenAI...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # Você pode usar "gpt-4", se preferir e tiver acesso
            messages=[
                {"role": "system", "content": "Você é um assistente que classifica e-mails como 'Produtivo' ou 'Improdutivo' e gera uma resposta adequada. Responda APENAS no formato JSON com as chaves 'classificacao' e 'resposta'."},
                {"role": "user", "content": f"Classifique o seguinte e-mail: '{email_content}'. Gere também uma resposta curta e profissional para ele. Ambas as saídas devem estar em português."}
            ],
            max_tokens=200, # Aumente conforme a necessidade de respostas mais longas
            temperature=0.7,
            response_format={ "type": "json_object" } # Garante que a resposta venha em JSON
        )
        ai_response_content = response.choices[0].message.content
        print(f"DEBUG: Resposta bruta da OpenAI recebida: {ai_response_content}")
        
        # Tenta carregar a resposta JSON
        ai_data = json.loads(ai_response_content) 

        return jsonify({
            "classificacao": ai_data.get("classificacao", "Desconhecida"),
            "resposta_sugerida": ai_data.get("resposta", "Não foi possível gerar uma resposta.")
        })
    except json.JSONDecodeError as e:
        print(f"ERRO: json.JSONDecodeError da OpenAI: {e}. Resposta bruta recebida: '{ai_response_content}'")
        return jsonify({"error": f"A IA não retornou um JSON válido. Detalhes: {e}. Resposta da IA: {ai_response_content[:100]}..."}), 500
    except Exception as e:
        print(f"ERRO: Erro geral ao processar com OpenAI: {e}")
        return jsonify({"error": f"Erro ao processar e-mail com a IA: {str(e)}"}), 500

# --- PONTO DE ENTRADA PARA DESENVOLVIMENTO LOCAL ---
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    print(f"DEBUG: Rodando em modo de desenvolvimento local. DEBUG={app.config['DEBUG']} na porta {port}")
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])