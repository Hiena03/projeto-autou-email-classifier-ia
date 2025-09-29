// main.js
document.addEventListener('DOMContentLoaded', () => {
    console.log("main.js carregado."); // DEBUG: Verifica se o script está sendo executado

    const form = document.getElementById('email-form');
    const emailTextArea = document.getElementById('email-text-area');
    const emailFileInput = document.getElementById('email-file-input');
    const classificationOutput = document.getElementById('classification-output');
    const responseOutput = document.getElementById('response-output');
    const resultDisplay = document.getElementById('result-display');
    const processButton = form ? form.querySelector('button[type="submit"]') : null; // Pega o botão

    console.log("Formulário encontrado:", form); // DEBUG: Verifica se o formulário foi encontrado

    if (form) {
        form.addEventListener('submit', async (event) => {
            console.log("Evento de submit acionado. Prevenindo default..."); // DEBUG: Verifica se o evento foi interceptado
            event.preventDefault(); // ESSENCIAL: Impede o envio padrão do formulário (e a atualização da página)

            // Limpa mensagens anteriores e mostra status de processamento
            classificationOutput.textContent = 'Processando...';
            classificationOutput.style.color = '#555'; // Cor padrão
            responseOutput.textContent = '';
            resultDisplay.classList.remove('error'); // Remove classe de erro se existir

            if (processButton) {
                processButton.disabled = true; // Desabilita o botão
                processButton.textContent = 'Processando...'; // Muda o texto do botão
            }

            const formData = new FormData();
            let hasContent = false;
            
            // Adiciona o conteúdo do textarea, se houver
            if (emailTextArea && emailTextArea.value.trim() !== '') {
                formData.append('email_text', emailTextArea.value);
                hasContent = true;
            }

            // Adiciona o arquivo, se um foi selecionado
            // Verifica também se o arquivo realmente tem um nome, para evitar envios vazios
            if (emailFileInput && emailFileInput.files.length > 0 && emailFileInput.files[0].name) {
                formData.append('email_file', emailFileInput.files[0]);
                hasContent = true;
            }

            // Verifica se algum conteúdo foi fornecido (texto ou arquivo)
            if (!hasContent) {
                classificationOutput.textContent = 'Por favor, insira o conteúdo do e-mail ou faça upload de um arquivo.';
                classificationOutput.style.color = 'red';
                if (processButton) {
                    processButton.disabled = false;
                    processButton.textContent = 'Processar E-mail';
                }
                return; // Interrompe a função se não há conteúdo
            }

            try {
                // *** ATENÇÃO: SUBSTITUA ESTA URL PELA SUA URL DO RENDER.COM ***
                const backendUrl = 'projeto-autou-email-classifier-ia-maykonjnerdl.replit.app';
                console.log(`Enviando requisição para: ${backendUrl}`); // DEBUG: Mostra para onde a requisição está indo

                const response = await fetch(backendUrl, {
                    method: 'POST',
                    body: formData // FormData lida com arquivos e campos de texto
                });

                // Tenta ler a resposta como JSON, mesmo em caso de erro, para obter detalhes
                let data = {};
                try {
                    data = await response.json(); 
                } catch (jsonError) {
                    // Se não conseguir parsear JSON, pode ser um erro HTTP sem corpo JSON
                    console.error("Erro ao parsear JSON da resposta:", jsonError);
                    data.error = data.error || `Resposta não JSON do servidor (Status: ${response.status})`;
                }

                if (!response.ok || data.error) { // Se a resposta HTTP não for OK ou se o JSON contiver um erro
                    const errorMessage = data.error || `Erro HTTP! Status: ${response.status}. Por favor, tente novamente.`;
                    classificationOutput.textContent = `Erro: ${errorMessage}`;
                    classificationOutput.style.color = 'red';
                    responseOutput.textContent = '';
                    console.error("Erro do backend:", data);
                } else { // Se a resposta foi um sucesso, com classificação e sugestão
                    classificationOutput.textContent = `Classificação: ${data.classificacao}`;
                    classificationOutput.style.color = '#333'; // Resetar cor para sucesso
                    responseOutput.textContent = `Resposta Sugerida: ${data.resposta_sugerida}`;
                    console.log("Resposta completa da IA:", data);
                }

            } catch (error) {
                // Captura erros de rede ou erros lançados acima
                classificationOutput.textContent = `Não foi possível conectar ao servidor. Detalhes: ${error.message}`;
                classificationOutput.style.color = 'red';
                responseOutput.textContent = '';
                console.error("Erro na conexão ou processamento:", error);
            } finally {
                if (processButton) {
                    processButton.disabled = false; // Reabilita o botão
                    processButton.textContent = 'Processar E-mail'; // Restaura o texto
                }
            }
        });
    }
});