# Projeto AutoU: Classificador e Gerador de Respostas para E-mails com IA

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Flask](https://img.shields.io/badge/Framework-Flask-black.svg)
![OpenAI API](https://img.shields.io/badge/AI%20API-OpenAI%20GPT-green.svg)
![Status](https://img.shields.io/badge/Status-Funcional-brightgreen.svg)
![Licença](https://img.shields.io/badge/License-MIT-purple.svg)

## 📝 Sobre o Projeto

Este projeto (`Projeto-AutoU`) tem como objetivo principal desenvolver uma **solução digital para automatizar a leitura, classificação e sugestão de respostas para e-mails**, especialmente útil para empresas que lidam com um alto volume de comunicações diárias.

A ideia é otimizar a gestão de caixas de entrada, **liberando tempo da equipe** que atualmente faz esse trabalho manualmente. A aplicação utiliza **Inteligência Artificial** para categorizar e-mails como "Produtivos" ou "Improdutivos" e, em seguida, gerar respostas automáticas contextuais, melhorando a eficiência e padronizando a comunicação.

## ✨ Funcionalidades

*   **Classificação de E-mails:** Categorização automática de e-mails em duas classes principais:
    *   **Produtivo:** Requer uma ação específica, resposta ou acompanhamento (ex: solicitação de suporte, atualização de caso, dúvida sobre sistema, pedido de informação).
    *   **Improdutivo:** Não requer ação imediata ou é apenas informativo/cortesia (ex: felicitações, agradecimentos, mensagens genéricas, "Bom dia!", "Obrigado!").
*   **Geração de Respostas Automáticas:** Criação inteligente de rascunhos de respostas para e-mails classificados, economizando tempo e mantendo a cordialidade e profissionalismo.
*   **Interface Web Intuitiva:** Uma aplicação web amigável para interagir com o classificador e o gerador de respostas.
*   **Múltiplas Formas de Entrada:** Permite inserir o conteúdo do e-mail diretamente via texto ou fazer upload de arquivos nos formatos `.txt` e `.pdf`.
*   **Feedback Visual e Tratamento de Erros:** Proporciona uma experiência de usuário fluida com indicadores de carregamento, validações de entrada e mensagens de erro claras.

## 🚀 Tecnologias Utilizadas

Este projeto utiliza uma combinação de tecnologias para o backend, o processamento de IA e a interface do usuário:

*   **Backend:**
    *   **Python 3.x:** Linguagem principal de desenvolvimento.
    *   **Flask:** Microframework web para construir a aplicação e gerenciar as rotas.
    *   **python-dotenv:** Para gerenciar variáveis de ambiente de forma segura.
*   **Inteligência Artificial & Machine Learning:**
    *   **OpenAI API:** Utilização do modelo `gpt-3.5-turbo` para as tarefas de classificação e geração de respostas, via `openai` SDK (versão 1.x.x).
    *   **Engenharia de Prompt:** Estratégia de "ajuste" da IA através de prompts cuidadosamente elaborados para direcionar a classificação e as respostas.
*   **Processamento de Arquivos:**
    *   **PyPDF2:** Biblioteca para extração de texto de arquivos PDF.
*   **Frontend:**
    *   **HTML5:** Estrutura das páginas web.
    *   **CSS3:** Estilização responsiva e moderna da interface do usuário.
    *   **JavaScript:** Interatividade na página, validações de formulário e feedback assíncrono ao usuário.

## ��️ Instalação Local

Siga os passos abaixo para configurar e executar o projeto em sua máquina local:

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/Hiena03/projeto-autou-email-classifier-ia.git
    cd projeto-autou-email-classifier-ia
    ```
    *(Substitua `Hiena03` pelo seu username no GitHub se for diferente)*

2.  **Crie e ative um ambiente virtual (recomendado):**
    ```bash
    python -m venv .venv
    # No Windows:
    .venv\Scripts\activate
    # No macOS/Linux:
    source .venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure a Chave da API da OpenAI:**
    *   Crie um arquivo chamado `.env` na raiz do projeto (na mesma pasta de `app.py`).
    *   Dentro do arquivo `.env`, adicione a sua chave da API da OpenAI no formato:
        ```
        OPENAI_API_KEY="sua_chave_secreta_aqui"
        ```
    *   Substitua `"sua_chave_secreta_aqui"` pela sua chave real da OpenAI (ex: `sk-xxxxxxxxxxxxxxxx`).

## 🏃 Como Executar Localmente

Após a instalação das dependências e configuração da chave da API, você pode iniciar o servidor Flask:

```bash
python app.py