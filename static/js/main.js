document.addEventListener('DOMContentLoaded', () => {
    const emailForm = document.getElementById('emailForm');
    const emailTextInput = document.getElementById('emailTextInput');
    const emailFileInput = document.getElementById('emailFileInput');
    const processButton = document.getElementById('processButton');
    
    const loadingIndicator = document.getElementById('loadingIndicator');
    const errorMessageDiv = document.getElementById('errorMessage');
    const successMessageDiv = document.getElementById('successMessage');
    const resultsDiv = document.getElementById('results');
    const classificationResult = document.getElementById('classification_result');
    const autoReplyResult = document.getElementById('auto_reply_result');

    // Função para exibir mensagens (erro, sucesso, carregamento)
    function showFeedbackMessage(element, message, type) {
        element.textContent = message;
        element.className = `feedback-message ${type}`; // Define a classe para estilização
        element.style.display = 'flex'; // Usar flex para alinhar spinner e texto
    }

    // Função para ocultar mensagens
    function hideFeedbackMessage(element) {
        element.style.display = 'none';
        element.textContent = '';
    }

    // Limpa todas as mensagens e resultados anteriores
    function resetUI() {
        hideFeedbackMessage(errorMessageDiv);
        hideFeedbackMessage(successMessageDiv);
        hideFeedbackMessage(loadingIndicator); // Garante que o loading também esteja oculto
        resultsDiv.style.display = 'none'; // Esconde a área de resultados
        classificationResult.textContent = '';
        autoReplyResult.value = '';
        processButton.disabled = false; // Garante que o botão esteja habilitado
    }

    // Event listener para o formulário
    if (emailForm) {
        emailForm.addEventListener('submit', async (event) => {
            event.preventDefault(); // Impede o envio padrão do formulário

            resetUI(); // Limpa a UI antes de um novo processamento

            const text = emailTextInput.value.trim();
            const file = emailFileInput.files[0];

            // --- Validação de Entrada Frontend ---
            if (!text && !file) {
                showFeedbackMessage(errorMessageDiv, 'Por favor, insira um texto ou selecione um arquivo para processar.', 'error');
                return; // Interrompe a função se a validação falhar
            }
            if (text && file) {
                showFeedbackMessage(errorMessageDiv, 'Por favor, insira texto OU selecione um arquivo, não ambos.', 'error');
                return; // Interrompe se ambos forem fornecidos
            }

            // --- Feedback Visual: Mostrar carregamento e desabilitar botão ---
            showFeedbackMessage(loadingIndicator, 'Processando, aguarde...', 'loading');
            processButton.disabled = true;

            const formData = new FormData();
            if (text) {
                formData.append('email_text', text);
            }
            if (file) {
                formData.append('email_file', file);
            }

            try {
                const response = await fetch('/processar_email', {
                    method: 'POST',
                    body: formData,
                });

                // Tenta parsear a resposta como JSON
                const data = await response.json(); 

                if (response.ok && data.status === 'success') {
                    // Requisição bem-sucedida (status 2xx) e status 'success' do backend
                    classificationResult.textContent = data.classification;
                    autoReplyResult.value = data.auto_reply;
                    resultsDiv.style.display = 'block';
                    showFeedbackMessage(successMessageDiv, 'Processamento concluído com sucesso!', 'success');
                } else {
                    // Backend retornou um erro (status 4xx ou 5xx) OU status 'error' no JSON (mesmo com 200 OK)
                    const errorMsg = data.message || 'Ocorreu um erro desconhecido no servidor.';
                    showFeedbackMessage(errorMessageDiv, `Erro: ${errorMsg}`, 'error');
                    console.error('Erro do backend:', data.message);
                }
            } catch (error) {
                // Erros de rede ou outros problemas que impedem o fetch
                console.error('Erro ao conectar ao servidor:', error);
                showFeedbackMessage(errorMessageDiv, 'Não foi possível conectar ao servidor. Verifique sua conexão ou tente novamente.', 'error');
            } finally {
                // --- Feedback Visual: Esconder carregamento e habilitar botão ---
                hideFeedbackMessage(loadingIndicator);
                processButton.disabled = false;
            }
        });
    }

    // Função para copiar o texto da resposta
    window.copyToClipboard = () => {
        autoReplyResult.select();
        autoReplyResult.setSelectionRange(0, 99999); // Para dispositivos móveis
        document.execCommand('copy');
        // Você pode adicionar um feedback visual aqui, como um tooltip "Copiado!"
        alert('Resposta copiada para a área de transferência!');
    };
});