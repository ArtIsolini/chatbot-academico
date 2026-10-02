# 🎓 Chatbot Acadêmico Inteligente

Assistente virtual desenvolvido com frontend web moderno (HTML/JS) e backend em Python (Flask) integrado a um banco de dados PostgreSQL e Inteligência Artificial Generativa (Google Gemini API). O projeto simula o ambiente do Blackboard, permitindo aos alunos consultar avisos, cronogramas de disciplinas, materiais de aulas e turmas matriculadas utilizando linguagem natural.

## 📂 Estrutura do Projeto

Para que o sistema web e a leitura de dados funcionem corretamente, o projeto obedece à seguinte estrutura de pastas:

```text
📁 Projeto_Chatbot/
│
├── api.py                      # API Flask (Backend web / Endpoints)
├── index.html                  # Interface do usuário (Frontend web)
│
├── 📁 chatbot/                 # Lógica principal da aplicação
│   ├── chatbot.py              # Script principal de execução da IA
│   ├── database_setup.py       # Script de inicialização do banco e tabelas
│   └── .env                    # (Não versionado) Variáveis de ambiente
│
└── 📁 mocks/                   # Base de conhecimento e materiais dos professores
    ├── 📁 Analise_Ciencia_Dados/
    ├── 📁 Estruturas_Dados/
    ├── 📁 Inteligencia_Artificial/
    └── 📁 Manipulacao_Visualizacao_Dados/
```

## ⚙️ Pré-requisitos

Antes de iniciar, certifique-se de ter instalado em sua máquina:

* **Python 3.9+**
* **PostgreSQL** (Rodando localmente)
* **Git**
* **Navegador Web atualizado** (Chrome, Edge, Firefox, etc.)

## 🚀 Como Configurar e Rodar o Projeto

### Passo 1: Obter o Código

Faça o clone do repositório para o seu computador:

```bash
git clone [https://github.com/ArtIsolini/chatbot-academico.git](https://github.com/ArtIsolini/chatbot-academico.git)
cd chatbot-academico
```

### Passo 2: Criar o Banco de Dados

Abra o **pgAdmin 4** (ou terminal psql) e crie um banco de dados vazio com o nome exato:
`chatbot_academico`

### Passo 3: Configurar o Ambiente Virtual e Dependências

Abra o terminal **na raiz do projeto** e execute:

```bash
# 1. Criar o ambiente virtual
python -m venv venv

# 2. Ativar o ambiente virtual (Escolha o comando certo para o seu terminal):
# -> Se usar CMD ou PowerShell (Windows):
venv\Scripts\activate
# -> Se usar Git Bash, Linux ou Mac:
source venv/Scripts/activate

# 3. Instalar as bibliotecas necessárias (Com o venv ativado)
pip install psycopg2-binary google-generativeai python-dotenv flask flask-cors
```

### Passo 4: Obter a Chave da API e Configurar Variáveis de Ambiente

Cada membro da equipe precisará de uma chave gratuita da API do Gemini:

1. Acesse o [Google AI Studio](https://aistudio.google.com/).
2. Faça login com a sua conta Google e clique em **Get API key**.
3. Clique em **Create API key** e copie a chave gerada.

Como os dados sensíveis não vão para o GitHub (por segurança), você precisa criar manualmente um arquivo chamado **`.env`** dentro da pasta `chatbot/` (ou na raiz, conforme a sua configuração) e colar a sua chave lá dentro, junto com os dados do banco:

```env
GEMINI_API_KEY=cole_aqui_a_chave_que_copiou_do_ai_studio
DB_HOST=localhost
DB_NAME=chatbot_academico
DB_USER=postgres
DB_PASSWORD=sua_senha_do_postgres_aqui
DB_PORT=5432
```

### Passo 5: Inicializar as Tabelas (Setup)

No terminal (com o ambiente virtual ativado), popule a base de dados com as informações iniciais e matrículas rodando o comando:

```bash
python chatbot/database_setup.py
```

*(Deve aparecer a mensagem: "✅ Setup concluído! Bancos criados com sucesso.")*

### Passo 6: Iniciar o Servidor Backend (API Flask)

Agora, você precisa rodar a API que fará a ponte entre o site e a Inteligência Artificial:

```bash
python api.py
```

*(O terminal mostrará que o servidor está rodando na porta 5000. Não feche este terminal!)*

### Passo 7: Abrir a Interface Web (Frontend)

Com a API rodando no terminal, basta abrir o seu projeto no navegador:

1. Vá até a pasta do projeto pelo Explorador de Arquivos do seu computador.
2. Dê um duplo clique no arquivo **`index.html`** (ele abrirá no seu navegador padrão).
   *Dica: Se você usar o VS Code, pode também utilizar a extensão "Live Server" para abrir o arquivo.*

## 🔑 Acesso de Teste

Com a interface web aberta, utilize as credenciais do aluno principal cadastrado na base de dados para testar:

* **Usuário:** `joao.silva`
* **Senha:** `senha123`


*Desenvolvido como projeto acadêmico.* 
