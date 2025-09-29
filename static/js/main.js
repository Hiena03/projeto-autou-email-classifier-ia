// main.js
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('email-form');
    const emailTextArea = document.getElementById('email-text-area');
    const emailFileInput = document.getElementById('email-file-input');
    const classificationOutput = document.getElementById('classification-output');
    const responseOutput = document.getElementById('response-output');
    const resultDisplay = document.getElementById('result-display');

    if (form) {
        form.addEventListener('submit', async (event) => {
            event.preventDefault(); // Impede o envio padrão do formulário

            // Limpa mensagens anteriores e mostra status de processamento
            classificationOutput.textContent = 'Processando...';
            classificationOutput.style.color = '#555'; // Cor padrão
            responseOutput.textContent = '';
            resultDisplay.classList.remove('error'); // Remove classe de erro se existir

            const formData = new FormData();
            
            // Adiciona o conteúdo do textarea, se houver
            if (emailTextArea.value.trim() !== '') {
                formData.append('email_text', emailTextArea.value);
            }

            // Adiciona o arquivo, se um foi selecionado
            // Verifica também se o arquivo realmente tem um nome, para evitar envios vazios
            if (emailFileInput.files.length > 0 && emailFileInput.files[0].name) {
                formData.append('email_file', emailFileInput.files[0]);
            }

            // Verifica se algum conteúdo foi fornecido (texto ou arquivo)
            if (emailTextArea.value.trim() === '' && emailFileInput.files.length === 0) {
                classificationOutput.textContent = 'Por favor, insira o conteúdo do e-mail ou faça upload de um arquivo.';
                classificationOutput.style.color = 'red';
                return; // Interrompe a função se não há conteúdo
            }

            try {
                // *** ATENÇÃO: SUBSTITUA ESTA URL PELA SUA URL DO RENDER.COM ***
                const response = await fetch('https://projeto-autou-email-classifier-ia.onrender.com/', {
                    method: 'POST',
                    body: formData // FormData lida com arquivos e campos de texto
                });

                // Verifica se a resposta HTTP não foi OK (ex: 4xx, 5xx)
                if (!response.ok) {
                    let errorMessage = `Erro HTTP! Status: ${response.status}.`;
                    try {
                        const errorData = await response.json(); // Tenta ler o erro como JSON
                        errorMessage = errorData.error || errorMessage; // Usa a mensagem de erro do JSON, se disponível
                    } catch (e) {
                        // Se não for JSON, usa o status
                        errorMessage += " Resposta do servidor não foi um JSON válido.";
                    }
                    throw new Error(errorMessage); // Lança um erro para o bloco catch
                }

                // Se a resposta HTTP foi OK, tenta parsear como JSON
                const data = await response.json(); 

                if (data.error) { // Se o backend explicitamente enviou um objeto JSON com a chave 'error'
                    classificationOutput.textContent = `Erro do servidor: ${data.error}`;
                    classificationOutput.style.color = 'red';
                    responseOutput.textContent = '';
                    console.error("Erro retornado pelo backend:", data.error);
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
            }
        });
    }
});