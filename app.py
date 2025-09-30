import os
import io
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import PyPDF2
# Importe a classe OpenAI e as exceções específicas
from openai import OpenAI, OpenAIError, RateLimitError, APIConnectionError, AuthenticationError

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Inicializa a aplicação Flask
app = Flask(__name__)

# Instancia o cliente da OpenAI GLOBLAMENTE
# Isso é crucial para a nova versão da biblioteca OpenAI (v1.x.x)
# A chave da API é passada diretamente para o construtor do cliente
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Verifique se a chave de API está definida após a criação do cliente
if not os.getenv("OPENAI_API_KEY"):
    # Loga um aviso se a chave não for encontrada, útil para depuração
    print("AVISO: Variável de ambiente OPENAI_API_KEY não definida. As chamadas à API da OpenAI podem falhar.")


# --- Funções de IA (Classificação e Geração de Resposta) ---

def classify_email(email_text):
    """Classifica o e-mail como 'Produtivo' ou 'Improdutivo' usando a API da OpenAI."""
    prompt = f"""
    Classifique o seguinte e-mail como 'Produtivo' ou 'Improdutivo'.
    - 'Produtivo': Requer uma ação específica, resposta ou acompanhamento (ex: solicitação de suporte, atualização de caso, dúvida sobre sistema, pedido de informação).
    - 'Improdutivo': Não requer ação imediata ou é apenas informativo/cortesia (ex: felicitações, agradecimentos, mensagens genéricas, "Bom dia!", "Obrigado!").

    Email:
    "{email_text}"

    Classificação:
    """
    try:
        response = openai_client.chat.completions.create( # Usando o objeto cliente instanciado
            model="gpt-3.5-turbo", # Modelo da OpenAI
            messages=[
                {"role": "system", "content": "Você é um assistente de classificação de e-mails para um ambiente corporativo. Responda apenas com 'Produtivo' ou 'Improdutivo'."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=20, # Suficiente para "Produtivo" ou "Improdutivo"
            temperature=0, # Queremos uma resposta consistente e determinística
        )
        classification = response.choices[0].message.content.strip()
        if "Produtivo" in classification:
            return "Produtivo"
        elif "Improdutivo" in classification:
            return "Improdutivo"
        else:
            # Caso a IA retorne algo inesperado
            return "Inconclusivo"
    except Exception as e:
        # Erros aqui serão capturados pela função processar_email
        raise # Re-lança a exceção para ser tratada no nível superior

def generate_auto_reply(email_text, classification):
    """Gera uma resposta automática baseada na classificação do e-mail."""
    if classification == "Produtivo":
        prompt = f"""
        Gere uma resposta automática para o seguinte e-mail classificado como 'Produtivo'.
        A resposta deve ser cordial, confirmar o recebimento e informar que a equipe responsável ou de suporte entrará em contato em breve para tratar a solicitação. Mantenha a resposta concisa, profissional e adicione um toque amigável.
        Apresente a resposta como se fosse um rascunho de e-mail pronto para ser enviado.

        Email Original:
        "{email_text}"

        Resposta Automática Sugerida:
        """
    elif classification == "Improdutivo":
        prompt = f"""
        Gere uma resposta automática para o seguinte e-mail classificado como 'Improdutivo'.
        A resposta deve ser cordial, agradecer a mensagem e informar que ela foi recebida e que nenhuma ação adicional é necessária. Mantenha a resposta concisa e amigável.
        Apresente a resposta como se fosse um rascunho de e-mail pronto para ser enviado.

        Email Original:
        "{email_text}"

        Resposta Automática Sugerida:
        """
    else: # Classificação 'Inconclusivo' ou 'Erro'
        return "Não foi possível gerar uma resposta automática devido a uma classificação inconclusiva ou erro."

    try:
        response = openai_client.chat.completions.create( # Usando o objeto cliente instanciado
            model="gpt-3.5-turbo", # Ou outro modelo da OpenAI que você prefira
            messages=[
                {"role": "system", "content": "Você é um assistente de e-mail cordial e profissional que gera rascunhos de respostas automáticas."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200, # Ajuste conforme o tamanho desejado da resposta
            temperature=0.7, # Permite um pouco mais de criatividade na resposta
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        # Erros aqui serão capturados pela função processar_email
        raise # Re-lança a exceção para ser tratada no nível superior


# --- Rotas da Aplicação Flask ---

# Rota principal - Serve o seu arquivo index.html
@app.route('/')
def home():
    return render_template('index.html')

# Rota para processar a análise - será acionada pelo formulário ou JS
@app.route('/processar_email', methods=['POST'])
def processar_email():
    email_content = ""

    # Tenta pegar o texto digitado primeiro
    if 'email_text' in request.form and request.form['email_text']:
        email_content = request.form['email_text']
    # Se não houver texto, tenta pegar um arquivo
    elif 'email_file' in request.files and request.files['email_file']:
        file = request.files['email_file']
        if file.filename == '': # Nenhum arquivo selecionado
            return jsonify({"status": "error", "message": "Nenhum arquivo selecionado."}), 400

        if file.filename.endswith('.txt'):
            email_content = file.read().decode('utf-8')
        elif file.filename.endswith('.pdf'):
            try:
                # PyPDF2 requer um objeto de arquivo binário
                reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
                for page_num in range(len(reader.pages)):
                    email_content += reader.pages[page_num].extract_text() or ""
                if not email_content.strip(): # Verifica se o PDF não tinha texto
                     return jsonify({"status": "error", "message": "O arquivo PDF está vazio ou não contém texto legível."}), 400
            except Exception as e:
                app.logger.error(f"Erro ao ler PDF: {e}")
                return jsonify({"status": "error", "message": "Erro ao ler o arquivo PDF. Certifique-se de que é um PDF válido e não está corrompido."}), 400
        else:
            return jsonify({"status": "error", "message": "Formato de arquivo não suportado. Use .txt ou .pdf."}), 400
    else:
        # Esta validação é mais um fallback, o frontend já deve impedir isso.
        return jsonify({"status": "error", "message": "Por favor, forneça o texto do e-mail ou faça upload de um arquivo."}), 400

    if not email_content.strip():
        return jsonify({"status": "error", "message": "O conteúdo fornecido está vazio após a leitura."}), 400

    try:
        classification = classify_email(email_content)
        auto_reply = generate_auto_reply(email_content, classification)

        return jsonify({
            "status": "success",
            "classification": classification,
            "auto_reply": auto_reply,
            "original_email": email_content
        }), 200 # Status 200 para sucesso
    
    except AuthenticationError:
        return jsonify({"status": "error", "message": "Erro de autenticação com a OpenAI. Verifique sua chave de API (OPENAI_API_KEY)."}), 401
    except RateLimitError:
        return jsonify({"status": "error", "message": "Limite de uso da OpenAI excedido. Por favor, verifique seu plano e saldo na plataforma OpenAI."}), 429
    except APIConnectionError:
        return jsonify({"status": "error", "message": "Não foi possível conectar à API da OpenAI. Verifique sua conexão de internet ou as configurações da API."}), 500
    except OpenAIError as e:
        # Captura outros erros da API OpenAI (ex: erros de validação de modelo, etc.)
        app.logger.error(f"Erro na API da OpenAI: {e}")
        return jsonify({"status": "error", "message": f"Erro na API da OpenAI: {str(e)}"}), 500
    except Exception as e:
        # Captura quaisquer outros erros inesperados
        app.logger.error(f"Erro inesperado no processamento: {e}")
        return jsonify({"status": "error", "message": "Ocorreu um erro inesperado ao processar sua requisição."}), 500


# Bloco para rodar a aplicação quando o script é executado diretamente
if __name__ == '__main__':
    # debug=True ativa o modo de depuração (útil para desenvolvimento)
    # Não use debug=True em produção
    app.run(debug=True)