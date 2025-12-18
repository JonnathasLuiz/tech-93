# Guia de Instalação e Configuração do Projeto "The Architect"

Este guia detalha os passos necessários para configurar e executar os ambientes de frontend e backend do projeto.

## 1. Pré-requisitos

Antes de começar, certifique-se de que tem o seguinte software instalado na sua máquina:

*   **Node.js:** Versão 18 ou superior.
*   **Python:** Versão 3.10 ou superior.
*   **FFmpeg:** Uma ferramenta de linha de comando para processamento de áudio e vídeo.
    *   **macOS (via Homebrew):** `brew install ffmpeg`
    *   **Ubuntu/Debian:** `sudo apt update && sudo apt install ffmpeg`
    *   **Windows:** Pode ser descarregado a partir do site oficial e adicionado ao PATH.

## 2. Configuração do Backend (Python/FastAPI)

O backend é responsável por todo o processamento de áudio e pela comunicação com as APIs de IA.

### Passo 2.1: Criar o Ambiente Virtual e Instalar Dependências

1.  **Navegue para a pasta do backend:**
    ```bash
    cd backend
    ```

2.  **Crie um ambiente virtual:**
    ```bash
    python3 -m venv venv
    ```

3.  **Ative o ambiente virtual:**
    *   **macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```
    *   **Windows:**
        ```bash
        .\venv\Scripts\activate
        ```

4.  **Instale as dependências a partir do `requirements.txt`:**
    ```bash
    pip install -r requirements.txt
    ```

### Passo 2.2: Configurar as Chaves de API

1.  **Copie o ficheiro de exemplo `.env.example`:** Na raiz do projeto, copie o ficheiro `.env.example` para um novo ficheiro chamado `.env`.
    ```bash
    # Este comando deve ser executado a partir da raiz do projeto
    cp .env.example .env
    ```

2.  **Edite o ficheiro `.env`:** Abra o ficheiro `.env` com um editor de texto e substitua os valores de placeholder pelas suas chaves de API reais da Deepgram e do Google AI Studio.
    ```
    DEEPGRAM_API_KEY="SUA_CHAVE_DEEPGRAM_REAL"
    GEMINI_API_KEY="SUA_CHAVE_GEMINI_REAL"
    ```

## 3. Configuração do Frontend (Next.js)

O frontend é a interface do utilizador que corre no navegador, responsável por capturar o áudio.

1.  **Navegue para a pasta do frontend:**
    ```bash
    # A partir da raiz do projeto
    cd frontend
    ```

2.  **Instale as dependências do Node.js:**
    ```bash
    npm install
    ```

## 4. Como Executar o Projeto

Para que a aplicação funcione, ambos os servidores (backend e frontend) precisam de estar a correr em simultâneo.

### Passo 4.1: Iniciar o Servidor do Backend

1.  **Abra um terminal na raiz do projeto.**

2.  **Ative o ambiente virtual do backend:**
    ```bash
    source backend/venv/bin/activate
    ```

3.  **Inicie o servidor Uvicorn:**
    ```bash
    uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
    ```
    O servidor estará agora a correr em `http://localhost:8000`. A flag `--reload` faz com que o servidor reinicie automaticamente se fizer alterações no código.

### Passo 4.2: Iniciar o Servidor do Frontend

1.  **Abra um *outro* terminal na raiz do projeto.**

2.  **Navegue para a pasta do frontend:**
    ```bash
    cd frontend
    ```

3.  **Inicie o servidor de desenvolvimento do Next.js:**
    ```bash
    npm run dev
    ```
    O servidor estará agora a correr em `http://localhost:3000`.

### Passo 4.3: Utilizar a Aplicação

1.  **Abra o seu navegador** e vá para `http://localhost:3000`.
2.  **Use auscultadores (fones de ouvido)** para evitar eco, pois a aplicação irá capturar tanto o seu microfone como o áudio do sistema.
3.  **Clique em "Start Recording"** e dê as permissões necessárias.
4.  **Selecione o ecrã ou a aba** que contém o áudio que deseja capturar (por exemplo, uma chamada no Google Meet ou Zoom).
5.  Fale, e as transcrições e análises da IA (atualmente) serão impressas no log do terminal do **backend**.
