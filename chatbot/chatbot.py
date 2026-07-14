"""
Chatbot Acadêmico Inteligente
Consulta dados do Blackboard e responde com linguagem natural via Gemini API
"""

import psycopg2
from psycopg2.extras import DictCursor
import hashlib
from datetime import datetime
import os
import json
import time
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

class ChatbotAcademico:
    def __init__(self):
        self.aluno_logado = None
        self.aluno_login_bb = None
        self.aluno_id = None
        
        # Configurar Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ ERRO: GEMINI_API_KEY não encontrada no arquivo .env")
            
        genai.configure(api_key=api_key)
        
        try:
            modelos_suportados = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            preferencias = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-1.0-pro', 'models/gemini-pro']
            
            modelo_escolhido = None
            for pref in preferencias:
                if pref in modelos_suportados:
                    modelo_escolhido = pref
                    break
                    
            if not modelo_escolhido and modelos_suportados:
                modelo_escolhido = modelos_suportados[0]
                
            if modelo_escolhido:
                nome_modelo = modelo_escolhido.replace("models/", "")
                self.modelo = genai.GenerativeModel(nome_modelo)
            else:
                self.modelo = genai.GenerativeModel("gemini-1.5-flash")
                
        except Exception as e:
            print(f"⚠️ Aviso ao verificar modelos disponíveis: {e}")
            self.modelo = genai.GenerativeModel("gemini-1.5-flash")
        # -----------------------------------------
        
        self.historico_conversa = []
        self.chat_session = None
        
        # Configurações PostgreSQL
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'database': os.getenv('DB_NAME', 'chatbot_academico'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'postgres'),
            'port': int(os.getenv('DB_PORT', 5432))
        }
        self.conn = None
    
    def conectar_bd(self):
        try:
            self.conn = psycopg2.connect(**self.db_config)
            print("✅ Conectado ao PostgreSQL")
        except Exception as e:
            print(f"❌ Erro ao conectar ao PostgreSQL: {e}")
            raise
    
    def fechar_bd(self):
        if self.conn:
            self.conn.close()
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def autenticar(self, login, senha):
        try:
            cursor = self.conn.cursor(cursor_factory=DictCursor)
            
            cursor.execute('''
                SELECT id, nome_completo FROM alunos 
                WHERE login_blackboard = %s AND senha_hash = %s
            ''', (login, self.hash_password(senha)))
            
            resultado = cursor.fetchone()
            
            if resultado:
                self.aluno_logado = resultado['nome_completo']
                self.aluno_login_bb = login
                self.aluno_id = resultado['id']
                
                # Registrar login
                cursor.execute('''
                    INSERT INTO sessoes (aluno_id) VALUES (%s)
                ''', (self.aluno_id,))
                self.conn.commit()
                
                cursor.close()
                return True
            
            cursor.close()
            return False
        except Exception as e:
            self.conn.rollback() # Evita que o erro quebre o banco de dados
            print(f"Erro na autenticação: {e}")
            return False
    
    def obter_cursos(self):
        """Obtém cursos que o aluno está matriculado pelo Banco de Dados"""
        try:
            cursor = self.conn.cursor(cursor_factory=DictCursor)
            cursor.execute('''
                SELECT DISTINCT c.id, c.nome 
                FROM cursos c
                JOIN matriculas_aluno m ON c.id = m.curso_id
                WHERE m.aluno_login = %s
            ''', (self.aluno_login_bb,))
            
            cursos = cursor.fetchall()
            cursor.close()
            return cursos
        except Exception as e:
            self.conn.rollback()
            print(f"Erro ao obter cursos: {e}")
            return []
    
    def obter_atividades_pendentes(self):
        """Obtém atividades com vencimento pendente do aluno pelo Banco de Dados"""
        try:
            cursor = self.conn.cursor(cursor_factory=DictCursor)
            cursor.execute('''
                SELECT a.nome, a.data_vencimento, a.pontos_possiveis
                FROM atividades_avaliativas a
                WHERE a.disponivel = true AND a.data_vencimento IS NOT NULL
                AND a.data_vencimento > CURRENT_TIMESTAMP
                ORDER BY a.data_vencimento ASC
                LIMIT 10
            ''')
            
            atividades = cursor.fetchall()
            cursor.close()
            return atividades
        except Exception as e:
            self.conn.rollback()
            print(f"Erro ao obter atividades: {e}")
            return []
    
    def obter_notas(self):
        """Obtém notas do aluno pelo Banco de Dados"""
        try:
            cursor = self.conn.cursor(cursor_factory=DictCursor)
            cursor.execute('''
                SELECT a.nome, n.nota, n.data_entrega, n.feedback
                FROM notas n
                JOIN atividades_avaliativas a ON n.atividade_id = a.id
                WHERE n.aluno_login = %s
                ORDER BY n.data_entrega DESC
                LIMIT 10
            ''', (self.aluno_login_bb,))
            
            notas = cursor.fetchall()
            cursor.close()
            return notas
        except Exception as e:
            self.conn.rollback()
            print(f"Erro ao obter notas: {e}")
            return []
    
    def obter_avisos_recentes(self):
        """Obtém avisos recentes do curso pelo Banco de Dados"""
        try:
            cursor = self.conn.cursor(cursor_factory=DictCursor)
            cursor.execute('''
                SELECT titulo, corpo, data_criacao
                FROM avisos
                WHERE curso_id IN (
                    SELECT curso_id FROM matriculas_aluno 
                    WHERE aluno_login = %s
                )
                ORDER BY data_criacao DESC
                LIMIT 5
            ''', (self.aluno_login_bb,))
            
            avisos = cursor.fetchall()
            cursor.close()
            return avisos
        except Exception as e:
            self.conn.rollback()
            print(f"Erro ao obter avisos: {e}")
            return []
    
    def buscar_conteudo(self, palavra_chave):
        """Busca conteúdo por palavra-chave no Banco de Dados"""
        try:
            cursor = self.conn.cursor(cursor_factory=DictCursor)
            cursor.execute('''
                SELECT titulo, tipo, descricao
                FROM conteudos
                WHERE titulo ILIKE %s OR descricao ILIKE %s
                LIMIT 5
            ''', (f'%{palavra_chave}%', f'%{palavra_chave}%'))
            
            conteudos = cursor.fetchall()
            cursor.close()
            return conteudos
        except Exception as e:
            self.conn.rollback()
            print(f"Erro ao buscar conteúdo: {e}")
            return []

    def carregar_dados_professor(self, curso_id_foco=None):
        """Lê os arquivos JSON e filtra usando o ID da disciplina (Nome da Pasta)"""
        dados_disciplinas = []
        todas_disciplinas = [] # Backup caso o filtro falhe
        
        diretorio_atual = os.path.dirname(os.path.abspath(__file__))
        caminhos_possiveis = [
            os.path.join(diretorio_atual, '..', 'mocks'),
            os.path.join(diretorio_atual, 'mocks')
        ]
        
        caminho_base = None
        for caminho in caminhos_possiveis:
            if os.path.exists(caminho):
                caminho_base = caminho
                break

        arquivos_esperados = {
            'curso': 'course.json',
            'avisos': 'announcements.json',
            'conteudos': 'contents.json',
            'notas_colunas': 'gradebook_columns.json'
        }

        if not caminho_base:
            print(f"⚠️ Aviso: Pasta 'mocks' não encontrada.")
            return dados_disciplinas

        try:
            pastas_disciplinas = [d for d in os.listdir(caminho_base) if os.path.isdir(os.path.join(caminho_base, d))]
            
            for pasta in pastas_disciplinas:
                if pasta.startswith('__') or pasta.startswith('.'):
                    continue
                    
                caminho_pasta_disciplina = os.path.join(caminho_base, pasta)
                dados_desta_disciplina = {}
                tem_dados = False
                
                for chave, arquivo in arquivos_esperados.items():
                    caminho_arquivo = os.path.join(caminho_pasta_disciplina, arquivo)
                    if os.path.exists(caminho_arquivo):
                        try:
                            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                                dados_desta_disciplina[chave] = json.load(f)
                                tem_dados = True
                        except Exception as e:
                            pass
                
                if tem_dados:
                    nome_exibicao = pasta
                    if 'curso' in dados_desta_disciplina and 'name' in dados_desta_disciplina['curso']:
                        nome_exibicao = dados_desta_disciplina['curso']['name']
                        
                    dados_desta_disciplina['nome_pasta'] = nome_exibicao
                    todas_disciplinas.append(dados_desta_disciplina)
                    
                    if curso_id_foco:
                        if curso_id_foco == pasta:
                            pass 
                        else:
                            continue 
                            
                    dados_disciplinas.append(dados_desta_disciplina)
                    
        except Exception as e:
            print(f"⚠️ Erro ao acessar as pastas: {e}")

        # Se o filtro falhou por algum motivo, retorna todas por segurança
        if curso_id_foco and not dados_disciplinas:
            return todas_disciplinas
            
        return dados_disciplinas
    
    def formatar_contexto_aluno(self, curso_id_foco=None):
        """Formata informações do aluno para contexto da IA"""
        cursos = self.obter_cursos()
        atividades_pendentes = self.obter_atividades_pendentes()
        notas = self.obter_notas()
        avisos = self.obter_avisos_recentes()
        
        contexto = f"""
CONTEXTO DO ALUNO:
- Nome: {self.aluno_logado}
- Login: {self.aluno_login_bb}

CURSOS MATRICULADOS (Dados do Banco):
"""
        for curso in cursos:
            contexto += f"  • {curso['nome']}\n"
        
        contexto += "\nATIVIDADES PENDENTES (Dados do Banco):\n"
        if atividades_pendentes:
            for ativ in atividades_pendentes:
                data = ativ['data_vencimento'].strftime('%d/%m/%Y') if ativ['data_vencimento'] else 'N/A'
                contexto += f"  • {ativ['nome']} - Vencimento: {data}\n"
        else:
            contexto += "  • Nenhuma atividade pendente\n"
        
        contexto += "\nÚLTIMAS NOTAS (Dados do Banco):\n"
        if notas:
            for nota in notas[:5]:
                contexto += f"  • {nota['nome']}: {nota['nota']}/100\n"
        else:
            contexto += "  • Nenhuma nota registrada\n"
        
        contexto += "\nAVISOS RECENTES (Dados do Banco):\n"
        if avisos:
            for aviso in avisos[:3]:
                corpo_resumido = aviso['corpo'][:100] if aviso['corpo'] else 'Sem conteúdo'
                contexto += f"  • {aviso['titulo']}: {corpo_resumido}...\n"
        else:
            contexto += "  • Nenhum aviso recente\n"
            
        dados_prof_multiplos = self.carregar_dados_professor(curso_id_foco)
        
        if dados_prof_multiplos:
            contexto += "\n\n=== MATERIAIS OFICIAIS DAS DISCIPLINAS (FONTE DO PROFESSOR/MOCKS) ===\n"
            contexto += "ATENÇÃO: Use primordialmente estas informações abaixo para responder. Extraia todo o cronograma, datas e conteúdos em detalhes das estruturas JSON fornecidas:\n"
            
            for disciplina in dados_prof_multiplos:
                nome = disciplina.get('nome_pasta', 'Disciplina Desconhecida')
                contexto += f"\n\n--- INÍCIO DOS DADOS DA DISCIPLINA: {nome} ---\n"
                
                if disciplina.get('curso'):
                    contexto += f"\nDADOS DO CURSO:\n{json.dumps(disciplina['curso'], ensure_ascii=False)}\n"
                if disciplina.get('avisos'):
                    contexto += f"\nAVISOS DA DISCIPLINA:\n{json.dumps(disciplina['avisos'], ensure_ascii=False)}\n"
                if disciplina.get('conteudos'):
                    contexto += f"\nCONTEÚDOS/MATERIAIS E CRONOGRAMA:\n{json.dumps(disciplina['conteudos'], ensure_ascii=False)}\n"
                if disciplina.get('notas_colunas'):
                    contexto += f"\nESTRUTURA DE NOTAS/ATIVIDADES:\n{json.dumps(disciplina['notas_colunas'], ensure_ascii=False)}\n"
                    
                contexto += f"--- FIM DOS DADOS DA DISCIPLINA: {nome} ---\n"
        
        return contexto
    
    def consultar_gemini(self, pergunta, curso_id_foco=None):
        
        contexto = self.formatar_contexto_aluno(curso_id_foco)

        # Obtém a data e hora atuais do computador para dar noção de tempo à IA
        data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        sistema_prompt = f"""Você é um assistente acadêmico inteligente para uma instituição educacional.
Você tem acesso aos dados do Blackboard do aluno e deve responder em português de forma natural e amigável.

INFORMAÇÃO TEMPORAL IMPORTANTE:
- Data e Hora atuais: {data_atual}
- Utilize esta data exata como referência (Hoje) para responder com precisão a perguntas sobre "última aula", "próxima aula", "na semana que vem", etc. Compare sempre as datas do cronograma com esta data atual.

{contexto}

INSTRUÇÕES:
- Responda sempre em português
- Use informações contextuais do aluno quando relevante
- Extraia os cronogramas das aulas (data e assunto) vasculhando os arquivos 'contents'
- Seja detalhista com datas e materiais de aulas
- Tom: profissional mas amigável"""

        max_tentativas = 3
        for tentativa in range(max_tentativas):
            try:
                if self.chat_session is None:
                    self.chat_session = self.modelo.start_chat(history=[])
                
                mensagem_completa = f"{sistema_prompt}\n\nPergunta do aluno: {pergunta}"
                
                resposta = self.chat_session.send_message(mensagem_completa)
                return resposta.text
                
            except Exception as e:
                erro_str = str(e)
                if "429" in erro_str or "quota" in erro_str.lower():
                    if tentativa < max_tentativas - 1:
                        tempo_espera = 45
                        print(f"\n⚠️ Limite gratuito da API atingido. A aguardar {tempo_espera} segundos antes de tentar novamente (Tentativa {tentativa+1}/{max_tentativas})...")
                        time.sleep(tempo_espera)
                        continue
                return f"❌ Erro ao consultar Gemini: {erro_str}"

    def exibir_menu(self):
        """Exibe menu de opções atualizado"""
        print("\n" + "=" * 50)
        print("🤖 CHATBOT ACADÊMICO INTELIGENTE")
        print("=" * 50)
        print("\n📌 Opções rápidas:")
        print("  1. Ver avisos recentes")
        print("  2. Ver cronograma de uma disciplina específica")
        print("  3. Buscar conteúdo")
        print("  4. Ver minhas disciplinas")
        print("  5. Fazer pergunta livre")
        print("  0. Sair")
        print()
    
    def processar_pergunta_rapida(self, opcao):
        """Processa opções de pergunta rápida com interatividade"""
        curso_id_foco = None
        
        if opcao == "1":
            pergunta = "Quais são os avisos recentes dos professores?"
            
        elif opcao == "2":
            cursos = self.obter_cursos()
            if not cursos:
                print("\n❌ Você não está matriculado em nenhuma disciplina.")
                return
                
            print("\n📚 De qual disciplina você deseja ver o cronograma?")
            for i, c in enumerate(cursos, 1):
                print(f"  {i}. {c['nome']}")
                
            escolha = input("\n👉 Escolha o número da disciplina: ").strip()
            
            try:
                idx = int(escolha) - 1
                if 0 <= idx < len(cursos):
                    curso_escolhido = cursos[idx]['nome']
                    curso_id_foco = cursos[idx]['id'] 
                    
                    pergunta = f"Verifique atentamente os arquivos fornecidos pelo professor. Me mostre o cronograma detalhado, aula por aula (com as datas e conteúdos de cada dia) da disciplina de {curso_escolhido}."
                else:
                    print("\n❌ Opção inválida. Retornando ao menu principal.")
                    return
            except ValueError:
                print("\n❌ Digite um número válido. Retornando ao menu principal.")
                return
                
        elif opcao == "3":
            tema = input("\n🔍 Digite o tema a buscar: ").strip()
            if tema:
                self.buscar_conteudo(tema)
                pergunta = f"Me resuma os principais conteúdos sobre {tema}"
            else:
                return
                
        elif opcao == "4":
            pergunta = "Quais são as disciplinas ou cursos em que estou matriculado atualmente?"
            
        elif opcao == "5":
            pergunta = input("\n💬 Faça sua pergunta: ").strip()
            if not pergunta:
                return
        else:
            return
        
        print("\n⏳ Processando sua pergunta...")
        resposta = self.consultar_gemini(pergunta, curso_id_foco) 
        
        print("\n" + "=" * 50)
        print("🤖 Resposta do Assistente:")
        print("=" * 50)
        print(f"\n{resposta}\n")
    
    def executar_login(self):
        """Fluxo de login"""
        print("\n" + "=" * 50)
        print("🔐 LOGIN - CHATBOT ACADÊMICO")
        print("=" * 50)
        
        while not self.aluno_logado:
            print("\n📝 Dados de login de exemplo:")
            print("  Usuário: joao.silva | Senha: senha123")
            print("  Usuário: maria.oliveira | Senha: senha456")
            print("  Usuário: pedro.ferreira | Senha: senha789")
            print()
            
            login = input("👤 Login (ou 'sair' para cancelar): ").strip()
            
            if login.lower() == 'sair':
                return False
            
            senha = input("🔑 Senha: ").strip()
            
            if self.autenticar(login, senha):
                print(f"\n✅ Bem-vindo(a), {self.aluno_logado}! 🎓")
                return True
            else:
                print("\n❌ Login inválido. Tente novamente.")
        
        return False
    
    def executar(self):
        """Executa o chatbot"""
        print("\n" + "=" * 70)
        print("  🎓 CHATBOT ACADÊMICO INTELIGENTE - PostgreSQL + Gemini 🤖")
        print("=" * 70)
        
        self.conectar_bd()
        
        try:
            if not self.executar_login():
                print("\n👋 Até logo!")
                return
            
            # Loop principal
            while True:
                self.exibir_menu()
                opcao = input("Escolha uma opção: ").strip()
                
                if opcao == "0":
                    print("\n👋 Até a próxima sessão!")
                    break
                elif opcao in ["1", "2", "3", "4", "5"]:
                    self.processar_pergunta_rapida(opcao)
                else:
                    print("\n❌ Opção inválida. Tente novamente.")
        
        finally:
            self.fechar_bd()

def main():
    """Função principal"""
    chatbot = ChatbotAcademico()
    chatbot.executar()

if __name__ == "__main__":
    main()