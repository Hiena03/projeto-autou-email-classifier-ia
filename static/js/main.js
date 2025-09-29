// main.js
document.addEventListener('DOMContentLoaded', () => {
    console.log("main.js: Script carregado e DOMContentLoaded."); // DEBUG 1: Verifica se o script está sendo executado

    const form = document.getElementById('email-form');
    // Verifica se o formulário foi encontrado no DOM
    if (!form) {
        console.error("main.js: ERRO - Formulário com ID 'email-form' NÃO encontrado no DOM.");
        // Se o formulário não for encontrado, o script não pode anexar o event listener e a página vai recarregar.
        return; // Sai da função para evitar erros posteriores.
    }
    console.log("main.js: Formulário com ID 'email-form' encontrado."); // DEBUG 2: Confirma que o formulário foi encontrado

    const emailTextArea = document.getElementById('email-text-area');
    const emailFileInput = document.getElementById('email-file-input');
    const classificationOutput = document.getElementById('classification-output');
    const responseOutput = document.getElementById('response-output');
    const resultDisplay = document.getElementById('result-display');
    const processButton = form.querySelector('button[type="submit"]'); // Pega o botão dentro do formulário

    // Verificações adicionais para garantir que todos os elementos foram encontrados
    if (!emailTextArea) console.error("main.js: ERRO - Elemento com ID 'email-text-area' NÃO encontrado.");
    if (!emailFileInput) console.error("main.js: ERRO - Elemento com ID 'email-file-input' NÃO encontrado.");
    if (!classificationOutput) console.error("main.js: ERRO - Elemento com ID 'classification-output' NÃO encontrado.");
    if (!responseOutput) console.error("main.js: ERRO - Elemento com ID 'response-output' NÃO encontrado.");
    if (!resultDisplay) console.error("main.js: ERRO - Elemento com ID 'result-display' NÃO encontrado.");
    if (!processButton) console.error("main.js: ERRO - Botão de submit NÃO encontrado dentro do formulário.");


    form.addEventListener('submit', async (event) => {
        console.log("main.js: Evento de submit acionado. Prevenindo default..."); // DEBUG 3: Verifica se o evento foi interceptado
        event.preventDefault(); // ESSENCIAL: Impede o envio padrão do formulário (e a atualização da página)

        // Limpa mensagens anteriores e mostra status de processamento
        classificationOutput.textContent = 'Processando...';
        classificationOutput.style.color = '#555'; // Cor padrão
        responseOutput.textContent = '';
        resultDisplay.classList.remove('error'); // Remove classe de erro se existir

        if (processButton) {
            processButton.disabled = true; // Desabilita o botão para evitar múltiplos envios
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
            console.log("main.js: Nenhuma entrada fornecida pelo usuário."); // DEBUG: Nenhuma entrada
            return; // Interrompe a função se não há conteúdo
        }

        try {
            // *** ATENÇÃO: SUBSTITUA ESTA URL PELA SUA URL DO RENDER.COM ***
            const backendUrl = 'projeto-autou-email-classifier-ia-maykonjnerdl.replit.app';
            console.log(`main.js: Enviando requisição para: ${backendUrl}`); // DEBUG: Mostra para onde a requisição está indo

            const response = await fetch(backendUrl, {
                method: 'POST',
                body: formData // FormData lida com arquivos e campos de texto
            });

            // Tenta ler a resposta como JSON, mesmo em caso de erro, para obter detalhes
            let data = {};
            try {
                data = await response.json(); 
            } catch (jsonError) {
                console.error("main.js: Erro ao parsear JSON da resposta:", jsonError);
                // Se não conseguir parsear JSON, pode ser um erro HTTP sem corpo JSON
                data.error = data.error || `Resposta não JSON do servidor (Status: ${response.status})`;
            }

            if (!response.ok || data.error) { // Se a resposta HTTP não for OK ou se o JSON contiver um erro
                const errorMessage = data.error || `Erro HTTP! Status: ${response.status}. Por favor, tente novamente.`;
                classificationOutput.textContent = `Erro: ${errorMessage}`;
                classificationOutput.style.color = 'red';
                responseOutput.textContent = '';
                console.error("main.js: Erro do backend:", data);
            } else { // Se a resposta foi um sucesso, com classificação e sugestão
                classificationOutput.textContent = `Classificação: ${data.classificacao}`;
                classificationOutput.style.color = '#333'; // Resetar cor para sucesso
                responseOutput.textContent = `Resposta Sugerida: ${data.resposta_sugerida}`;
                console.log("main.js: Resposta completa da IA:", data);
            }

        } catch (error) {
            // Captura erros de rede ou erros lançados acima
            classificationOutput.textContent = `Não foi possível conectar ao servidor. Detalhes: ${error.message}`;
            classificationOutput.style.color = 'red';
            responseOutput.textContent = '';
            console.error("main.js: Erro na conexão ou processamento:", error);
        } finally {
            if (processButton) {
                processButton.disabled = false; // Reabilita o botão
                processButton.textContent = 'Processar E-mail'; // Restaura o texto
            }
        }
    });
});