document.addEventListener('DOMContentLoaded', () => {
    // Seleção de elementos DOM
    const emailForm = document.getElementById('emailForm');
    const emailTextInput = document.getElementById('emailTextInput');
    const emailFileInput = document.getElementById('emailFileInput');
    const processButton = document.getElementById('processButton');
    const fileDisplay = document.querySelector('.file-input-display');
    const filePlaceholder = document.querySelector('.file-placeholder');
    
    // Elementos de feedback
    const loadingIndicator = document.getElementById('loadingIndicator');
    const errorMessageDiv = document.getElementById('errorMessage');
    const successMessageDiv = document.getElementById('successMessage');
    
    // Elementos de resultado
    const resultsDiv = document.getElementById('results');
    const classificationResult = document.getElementById('classification_result');
    const autoReplyResult = document.getElementById('auto_reply_result');
    const processedTextResult = document.getElementById('processed_text_result');
    const charCountResult = document.getElementById('char_count_result');
    const additionalInfo = document.querySelector('.additional-info');
    
    // Contador de caracteres
    const charCount = document.getElementById('charCount');
    const charCounter = document.querySelector('.char-counter');

    // --- Funções Utilitárias ---

    function showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.add('fade-out');
            setTimeout(() => {
                if (document.body.contains(toast)) {
                    document.body.removeChild(toast);
                }
            }, 300);
        }, 3000);
    }

    function showFeedbackMessage(element, message, type) {
        element.innerHTML = type === 'loading' 
            ? `<div class="spinner"></div><p>${message}</p>`
            : `<p>${message}</p>`;
        element.className = `feedback-message ${type}`;
        element.style.display = 'flex';
    }

    function hideFeedbackMessage(element) {
        element.style.display = 'none';
        element.innerHTML = '';
    }

    function resetUI() {
        hideFeedbackMessage(errorMessageDiv);
        hideFeedbackMessage(successMessageDiv);
        hideFeedbackMessage(loadingIndicator);
        resultsDiv.style.display = 'none';
        additionalInfo.style.display = 'none';
        classificationResult.textContent = '';
        classificationResult.className = 'classification-badge';
        autoReplyResult.value = '';
        processButton.disabled = false;
        
        // Reset file input display
        filePlaceholder.textContent = 'Nenhum arquivo selecionado';
        fileDisplay.style.borderColor = '#e1e8ed';
    }

    function updateCharCounter() {
        const count = emailTextInput.value.length;
        charCount.textContent = count;
        
        if (count > 8000) {
            charCounter.className = 'char-counter danger';
        } else if (count > 6000) {
            charCounter.className = 'char-counter warning';
        } else {
            charCounter.className = 'char-counter';
        }
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // --- Event Listeners ---

    // Contador de caracteres em tempo real
    if (emailTextInput) {
        emailTextInput.addEventListener('input', updateCharCounter);
        updateCharCounter(); // Inicializar
    }

    // Atualização do display do arquivo
    if (emailFileInput) {
        emailFileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                const fileName = file.name;
                const fileSize = formatFileSize(file.size);
                filePlaceholder.textContent = `${fileName} (${fileSize})`;
                fileDisplay.style.borderColor = '#667eea';
                
                // Limpar textarea quando arquivo é selecionado
                emailTextInput.value = '';
                updateCharCounter();
            } else {
                filePlaceholder.textContent = 'Nenhum arquivo selecionado';
                fileDisplay.style.borderColor = '#e1e8ed';
            }
        });
    }

    // Limpar arquivo quando texto é digitado
    if (emailTextInput) {
        emailTextInput.addEventListener('input', (e) => {
            if (e.target.value.trim() && emailFileInput.files[0]) {
                emailFileInput.value = '';
                filePlaceholder.textContent = 'Nenhum arquivo selecionado';
                fileDisplay.style.borderColor = '#e1e8ed';
            }
        });
    }

    // Submissão do formulário
    if (emailForm) {
        emailForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            resetUI();

            const text = emailTextInput.value.trim();
            const file = emailFileInput.files[0];

            // Validação frontend
            if (!text && !file) {
                showFeedbackMessage(errorMessageDiv, 'Por favor, insira um texto ou selecione um arquivo para processar.', 'error');
                return;
            }

            if (text && file) {
                showFeedbackMessage(errorMessageDiv, 'Por favor, insira texto OU selecione um arquivo, não ambos.', 'error');
                return;
            }

            // Validação de tamanho do texto
            if (text && text.length > 10000) {
                showFeedbackMessage(errorMessageDiv, 'Texto muito longo. Máximo permitido: 10.000 caracteres.', 'error');
                return;
            }

            // Validação de tamanho do arquivo
            if (file && file.size > 10 * 1024 * 1024) {
                showFeedbackMessage(errorMessageDiv, 'Arquivo muito grande. Máximo permitido: 10MB.', 'error');
                return;
            }

            // Feedback visual
            showFeedbackMessage(loadingIndicator, 'Analisando e processando seu e-mail...', 'loading');
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

                const data = await response.json();

                if (response.ok && data.status === 'success') {
                    // Sucesso
                    classificationResult.textContent = data.classification;
                    classificationResult.className = `classification-badge ${data.classification.toLowerCase()}`;
                    autoReplyResult.value = data.auto_reply;
                    
                    // Informações adicionais
                    if (processedTextResult && data.processed_text) {
                        processedTextResult.textContent = data.processed_text;
                    }
                    if (charCountResult) {
                        const originalLength = text ? text.length : 'N/A (arquivo)';
                        charCountResult.textContent = originalLength;
                    }
                    
                    resultsDiv.style.display = 'block';
                    showFeedbackMessage(successMessageDiv, '✅ Processamento concluído com sucesso!', 'success');
                    showToast('E-mail processado com sucesso!', 'success');
                    
                    // Scroll suave para os resultados
                    resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    
                } else {
                    // Erro do backend
                    const errorMsg = data.message || 'Ocorreu um erro desconhecido no servidor.';
                    showFeedbackMessage(errorMessageDiv, `❌ ${errorMsg}`, 'error');
                    showToast(errorMsg, 'error');
                    console.error('Erro do backend:', data);
                }
            } catch (error) {
                // Erro de rede
                console.error('Erro de conexão:', error);
                const networkError = 'Não foi possível conectar ao servidor. Verifique sua conexão e tente novamente.';
                showFeedbackMessage(errorMessageDiv, `🌐 ${networkError}`, 'error');
                showToast('Erro de conexão com o servidor', 'error');
            } finally {
                hideFeedbackMessage(loadingIndicator);
                processButton.disabled = false;
            }
        });
    }

    // --- Funções Globais ---

    window.copyToClipboard = () => {
        if (!autoReplyResult.value.trim()) {
            showToast('Nenhuma resposta para copiar', 'error');
            return;
        }

        autoReplyResult.select();
        autoReplyResult.setSelectionRange(0, 99999);
         try {
            document.execCommand('copy');
            showToast('Resposta copiada para a área de transferência!', 'success');
            
            // Feedback visual no botão
            const copyButton = document.querySelector('.copy-button');
            const originalText = copyButton.innerHTML;
            copyButton.innerHTML = '✅ Copiado!';
            copyButton.style.background = '#28a745';
            
            setTimeout(() => {
                copyButton.innerHTML = originalText;
                copyButton.style.background = '#28a745';
            }, 2000);
            
        } catch (err) {
            console.error('Erro ao copiar:', err);
            showToast('Erro ao copiar. Tente selecionar manualmente.', 'error');
        }
        
        // Deselecionar o texto
        window.getSelection().removeAllRanges();
    };

    window.clearResults = () => {
        if (confirm('Tem certeza que deseja limpar todos os resultados?')) {
            resetUI();
            emailTextInput.value = '';
            emailFileInput.value = '';
            updateCharCounter();
            showToast('Resultados limpos com sucesso', 'success');
        }
    };

    window.toggleAdditionalInfo = () => {
        const button = document.querySelector('.toggle-info-button');
        if (additionalInfo.style.display === 'none' || !additionalInfo.style.display) {
            additionalInfo.style.display = 'block';
            button.innerHTML = '👁️ Ocultar Detalhes Técnicos';
        } else {
            additionalInfo.style.display = 'none';
            button.innerHTML = '👁️ Mostrar Detalhes Técnicos';
        }
    };

    // --- Funcionalidades Extras ---

    // Atalhos de teclado
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + Enter para processar
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            if (!processButton.disabled) {
                emailForm.dispatchEvent(new Event('submit'));
            }
        }
        
        // Escape para limpar resultados
        if (e.key === 'Escape' && resultsDiv.style.display === 'block') {
            clearResults();
        }
    });

    // Drag and drop para arquivos
    const dropZone = document.querySelector('.file-input-wrapper');
    
    if (dropZone) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, unhighlight, false);
        });

        function highlight() {
            dropZone.classList.add('drag-over');
            fileDisplay.style.borderColor = '#667eea';
            fileDisplay.style.background = '#f8f9ff';
        }

        function unhighlight() {
            dropZone.classList.remove('drag-over');
            fileDisplay.style.borderColor = '#e1e8ed';
            fileDisplay.style.background = '#fafbfc';
        }

        dropZone.addEventListener('drop', handleDrop, false);

        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;

            if (files.length > 0) {
                const file = files[0];
                
                // Verificar tipo de arquivo
                if (file.name.toLowerCase().endsWith('.txt') || file.name.toLowerCase().endsWith('.pdf')) {
                    emailFileInput.files = files;
                    emailFileInput.dispatchEvent(new Event('change'));
                    showToast('Arquivo carregado com sucesso!', 'success');
                } else {
                    showToast('Tipo de arquivo não suportado. Use .txt ou .pdf', 'error');
                }
            }
        }
    }

    // Auto-save no localStorage (opcional)
    const STORAGE_KEY = 'autou_email_draft';
    
    // Carregar rascunho salvo
    const savedDraft = localStorage.getItem(STORAGE_KEY);
    if (savedDraft && !emailTextInput.value) {
        emailTextInput.value = savedDraft;
        updateCharCounter();
    }

    // Salvar rascunho automaticamente
    let saveTimeout;
    emailTextInput.addEventListener('input', () => {
        clearTimeout(saveTimeout);
        saveTimeout = setTimeout(() => {
            if (emailTextInput.value.trim()) {
                localStorage.setItem(STORAGE_KEY, emailTextInput.value);
            } else {
                localStorage.removeItem(STORAGE_KEY);
            }
        }, 1000);
    });

    // Limpar rascunho quando formulário é enviado com sucesso
    emailForm.addEventListener('submit', () => {
        localStorage.removeItem(STORAGE_KEY);
    });
});