import os
import io
import re
import string
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import PyPDF2
from openai import OpenAI, OpenAIError, RateLimitError, APIConnectionError, AuthenticationError

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Inicializa a aplicação Flask
app = Flask(__name__)

# Instancia o cliente da OpenAI
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Verifique se a chave de API está definida
if not os.getenv("OPENAI_API_KEY"):
    print("AVISO: Variável de ambiente OPENAI_API_KEY não definida. As chamadas à API da OpenAI podem falhar.")

# --- Função de Pré-processamento NLP (ADICIONADO) ---
def preprocess_text(text):
    """
    Aplica técnicas básicas de NLP para pré-processar o texto.
    Remove pontuações, converte para minúsculas, remove stop words básicas.
    """
    if not text or not text.strip():
        return ""
    
    # Converter para minúsculas
    text = text.lower()
    
    # Remover pontuações
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Remover números isolados
    text = re.sub(r'\b\d+\b', '', text)
    
    # Stop words básicas em português (lista simplificada para não depender do NLTK)
    stop_words = {
        'a', 'o', 'e', 'é', 'de', 'do', 'da', 'em', 'um', 'uma', 'para', 'com', 'não', 'na', 'no',
        'se', 'que', 'por', 'mais', 'as', 'os', 'como', 'mas', 'foi', 'ao', 'ele', 'das', 'tem',
        'à', 'seu', 'sua', 'ou', 'ser', 'quando', 'muito', 'há', 'nos', 'já', 'está', 'eu', 'também',
        'só', 'pelo', 'pela', 'até', 'isso', 'ela', 'entre', 'era', 'depois', 'sem', 'mesmo', 'aos',
        'ter', 'seus', 'suas', 'numa', 'pelos', 'pelas', 'esse', 'esses', 'essa', 'essas', 'meu',
        'minha', 'teu', 'tua', 'nosso', 'nossa', 'dele', 'dela', 'deles', 'delas', 'este', 'esta',
        'estes', 'estas', 'aquele', 'aquela', 'aqueles', 'aquelas', 'isto', 'aquilo', 'estou',
        'está', 'estamos', 'estão', 'estive', 'esteve', 'estivemos', 'estiveram', 'estava', 'estávamos',
        'estavam', 'estivera', 'estivéramos', 'esteja', 'estejamos', 'estejam', 'estivesse', 'estivéssemos',
        'estivessem', 'estiver', 'estivermos', 'estiverem', 'hei', 'há', 'havemos', 'hão', 'houve',
        'houvemos', 'houveram', 'houvera', 'houvéramos', 'haja', 'hajamos', 'hajam', 'houvesse',
        'houvéssemos', 'houvessem', 'houver', 'houvermos', 'houverem', 'houverei', 'houverá',
        'houveremos', 'houverão', 'houveria', 'houveríamos', 'houveriam', 'sou', 'somos', 'são',
        'era', 'éramos', 'eram', 'fui', 'foi', 'fomos', 'foram', 'fora', 'fôramos', 'seja',
        'sejamos', 'sejam', 'fosse', 'fôssemos', 'fossem', 'for', 'formos', 'forem', 'serei',
        'será', 'seremos', 'serão', 'seria', 'seríamos', 'seriam'
    }
    
    # Tokenização simples e remoção de stop words
    words = text.split()
    filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Remover espaços extras
    processed_text = ' '.join(filtered_words)
    
    return processed_text.strip()

# --- Funções de IA (Classificação e Geração de Resposta) ---

def classify_email(email_text):
    """Classifica o e-mail como 'Produtivo' ou 'Improdutivo' usando a API da OpenAI."""
    
    # Aplicar pré-processamento NLP
    processed_text = preprocess_text(email_text)
    
    prompt = f"""
    Classifique o seguinte e-mail como 'Produtivo' ou 'Improdutivo'.
    
    Definições:
    - 'Produtivo': Requer uma ação específica, resposta ou acompanhamento. Exemplos: solicitação de suporte técnico, atualização sobre casos em aberto, dúvidas sobre sistema, pedidos de informação, reclamações, solicitações de documentos, questões financeiras.
    - 'Improdutivo': Não requer ação imediata ou é apenas informativo/cortesia. Exemplos: felicitações, agradecimentos, mensagens genéricas como "Bom dia!", "Obrigado!", "Feliz Natal", cumprimentos.

    Email original:
    "{email_text}"
    
    Email processado (após NLP):
    "{processed_text}"

    Responda APENAS com 'Produtivo' ou 'Improdutivo'.
    """
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente especializado em classificação de e-mails corporativos. Analise o conteúdo e responda apenas com 'Produtivo' ou 'Improdutivo'."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,
            temperature=0,
        )
        classification = response.choices[0].message.content.strip()
        
        # Validação da resposta
        if "Produtivo" in classification:
            return "Produtivo"
        elif "Improdutivo" in classification:
            return "Improdutivo"
        else:
            # Fallback: se a IA não retornar uma classificação clara
            app.logger.warning(f"Classificação inesperada da IA: {classification}")
            return "Inconclusivo"
            
    except Exception as e:
        app.logger.error(f"Erro na classificação: {e}")
        raise

def generate_auto_reply(email_text, classification):
    """Gera uma resposta automática baseada na classificação do e-mail."""
    
    if classification == "Produtivo":
        prompt = f"""
        Gere uma resposta automática cordial e profissional para o seguinte e-mail classificado como 'Produtivo'.
        
        A resposta deve:
        - Confirmar o recebimento da mensagem
        - Informar que a equipe responsável entrará em contato em breve
        - Ser concisa e profissional
        - Incluir um prazo estimado de resposta (ex: "em até 24 horas úteis")
        - Ter um tom amigável mas corporativo
        
        Email original:
        "{email_text}"

        Gere apenas a resposta automática, sem cabeçalhos ou assinaturas:
        """
    elif classification == "Improdutivo":
        prompt = f"""
        Gere uma resposta automática cordial para o seguinte e-mail classificado como 'Improdutivo'.
        
        A resposta deve:
        - Agradecer pela mensagem
        - Ser cordial e amigável
        - Informar que a mensagem foi recebida
        - Ser concisa
        - Retribuir o sentimento quando apropriado (ex: se for felicitação, retribuir)
        
        Email original:
        "{email_text}"

        Gere apenas a resposta automática, sem cabeçalhos ou assinaturas:
        """
    else:
        return "Não foi possível gerar uma resposta automática devido a uma classificação inconclusiva."

    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente de atendimento ao cliente cordial e profissional. Gere respostas automáticas apropriadas para e-mails corporativos."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=250,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        app.logger.error(f"Erro na geração de resposta: {e}")
        raise

# --- Rotas da Aplicação Flask ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/processar_email', methods=['POST'])
def processar_email():
    email_content = ""

    try:
        # Tenta pegar o texto digitado primeiro
        if 'email_text' in request.form and request.form['email_text']:
            email_content = request.form['email_text'].strip()
        # Se não houver texto, tenta pegar um arquivo
        elif 'email_file' in request.files and request.files['email_file']:
            file = request.files['email_file']
            
            if file.filename == '':
                return jsonify({"status": "error", "message": "Nenhum arquivo selecionado."}), 400

            # Verificar tamanho do arquivo (máximo 10MB)
            file.seek(0, 2)  # Vai para o final do arquivo
            file_size = file.tell()
            file.seek(0)  # Volta para o início
            
            if file_size > 10 * 1024 * 1024:  # 10MB
                return jsonify({"status": "error", "message": "Arquivo muito grande. Máximo permitido: 10MB."}), 400

            if file.filename.lower().endswith('.txt'):
                try:
                    email_content = file.read().decode('utf-8')
                except UnicodeDecodeError:
                    return jsonify({"status": "error", "message": "Erro ao decodificar arquivo .txt. Certifique-se de que está em UTF-8."}), 400
                    
            elif file.filename.lower().endswith('.pdf'):
                try:
                    reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
                    email_content = ""
                    for page_num in range(len(reader.pages)):
                        page_text = reader.pages[page_num].extract_text()
                        if page_text:
                            email_content += page_text + "\n"
                    
                    if not email_content.strip():
                        return jsonify({"status": "error", "message": "O arquivo PDF está vazio ou não contém texto legível."}), 400
                        
                except Exception as e:
                    app.logger.error(f"Erro ao ler PDF: {e}")
                    return jsonify({"status": "error", "message": "Erro ao ler o arquivo PDF. Certifique-se de que é um PDF válido."}), 400
            else:
                return jsonify({"status": "error", "message": "Formato de arquivo não suportado. Use .txt ou .pdf."}), 400
        else:
            return jsonify({"status": "error", "message": "Por favor, forneça o texto do e-mail ou faça upload de um arquivo."}), 400

        # Validar conteúdo
        if not email_content or not email_content.strip():
            return jsonify({"status": "error", "message": "O conteúdo fornecido está vazio."}), 400

        # Validar tamanho do conteúdo
        if len(email_content) > 10000:  # 10k caracteres
            return jsonify({"status": "error", "message": "Conteúdo muito longo. Máximo permitido: 10.000 caracteres."}), 400

        # Processar o email
        classification = classify_email(email_content)
        auto_reply = generate_auto_reply(email_content, classification)

        return jsonify({
            "status": "success",
            "classification": classification,
            "auto_reply": auto_reply,
            "original_email": email_content[:500] + "..." if len(email_content) > 500 else email_content,  # Limitar retorno
            "processed_text": preprocess_text(email_content)[:300] + "..." if len(preprocess_text(email_content)) > 300 else preprocess_text(email_content)
        }), 200
    
    except AuthenticationError:
        return jsonify({"status": "error", "message": "Erro de autenticação com a OpenAI. Verifique sua chave de API."}), 401
    except RateLimitError:
        return jsonify({"status": "error", "message": "Limite de uso da OpenAI excedido. Tente novamente em alguns minutos."}), 429
    except APIConnectionError:
        return jsonify({"status": "error", "message": "Não foi possível conectar à API da OpenAI. Verifique sua conexão."}), 500
    except OpenAIError as e:
        app.logger.error(f"Erro na API da OpenAI: {e}")
        return jsonify({"status": "error", "message": f"Erro na API da OpenAI: {str(e)}"}), 500
    except Exception as e:
        app.logger.error(f"Erro inesperado: {e}")
        return jsonify({"status": "error", "message": "Erro interno do servidor. Tente novamente."}), 500

# Rota para verificar saúde da aplicação (útil para monitoramento)
@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "message": "Aplicação funcionando corretamente"}), 200

if __name__ == '__main__':
    # Configuração para desenvolvimento local
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))