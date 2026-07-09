🎓 Chatbot Acadêmico Inteligente

Assistente virtual desenvolvido em Python com base de dados PostgreSQL e integração com a IA generativa (Google Gemini API). O projeto simula o ambiente do Blackboard, permitindo aos alunos consultar avisos, cronogramas de disciplinas, listas de exercícios e turmas matriculadas.

📂 Estrutura do Projeto

Para que o Chatbot consiga ler os dados corretamente, o projeto obedece a seguinte estrutura:

📁 Projeto_Chatbot/
│
├── 📁 chatbot/                 # Código-fonte da aplicação
│   ├── chatbot.py              # Script principal de execução do assistente
│   ├── database_setup.py       # Script de inicialização do banco e tabelas
│   └── .env                    # (Não versionado) Variáveis de ambiente
│
└── 📁 mocks/                   # Base de conhecimento e materiais dos professores
    ├── 📁 Analise_Ciencia_Dados/
    ├── 📁 Estruturas_Dados/
    ├── 📁 Inteligencia_Artificial/
    └── 📁 Manipulacao_Visualizacao_Dados/


⚙️ Pré-requisitos

Antes de iniciar, certifique-se de ter instalado em sua máquina:

Python 3.9+

PostgreSQL (Rodando localmente)

Git

🚀 Como Configurar e Rodar o Projeto

Passo 1: Obter o Código

Faça o clone do repositório para o seu computador:

git clone (https://github.com/SEU_UTILIZADOR/chatbot-academico.git)
cd chatbot-academico


Passo 2: Criar o Banco de Dados

Abra o pgAdmin 4 e crie um banco de dados vazio com o nome exato:
chatbot_academico

Passo 3: Configurar o Ambiente Virtual e Dependências

Abra o terminal dentro da pasta chatbot e execute:

# Criar e ativar o ambiente virtual (Windows)
python -m venv venv
venv\Scripts\activate

# Instalar as bibliotecas necessárias
pip install psycopg2-binary google-generativeai python-dotenv


Passo 4: Obter a Chave da API e Configurar Variáveis de Ambiente

Para que o assistente consiga responder usando Inteligência Artificial, cada membro da equipe precisará de uma chave gratuita da API do Gemini:

Acesse o Google AI Studio.

Faça login com a sua conta Google.

No menu lateral esquerdo, clique em Get API key (Obter chave da API).

Clique no botão azul Create API key.

Copie a chave gerada.

Como os dados sensíveis não vão para o GitHub (por segurança), você precisa criar manualmente um ficheiro chamado .env dentro da pasta chatbot/ e colar a sua chave lá dentro, junto com os dados do banco:

GEMINI_API_KEY=cole_aqui_a_chave_que_copiou_do_ai_studio
DB_HOST=localhost
DB_NAME=chatbot_academico
DB_USER=postgres
DB_PASSWORD=sua_senha_do_postgres_aqui
DB_PORT=5432


Passo 5: Inicializar as Tabelas (Setup)

Ainda no terminal dentro da pasta chatbot, popule a base de dados com as informações iniciais e matrículas rodando o comando:

python database_setup.py


(Deve aparecer a mensagem: "✅ Setup concluído! Bancos criados com sucesso.")

Passo 6: Iniciar o Assistente

Com o banco configurado, inicie o Chatbot:

python chatbot.py


🔑 Acesso de Teste

Utilize o aluno principal cadastrado na base de dados para testar todas as funcionalidades matriculadas:

Usuário: joao.silva

Senha: senha123


Desenvolvido como projeto acadêmico.