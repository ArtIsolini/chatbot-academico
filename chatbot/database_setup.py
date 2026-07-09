"""
Configuração do Banco de Dados
"""

import psycopg2
from psycopg2 import sql
import hashlib
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

def hash_password(password):
    """Hash SHA-256 da senha"""
    return hashlib.sha256(password.encode()).hexdigest()

# Configurações de conexão PostgreSQL
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'chatbot_academico'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres'),
    'port': int(os.getenv('DB_PORT', 5432))
}

def get_connection():
    """Cria conexão com PostgreSQL"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar ao PostgreSQL: {e}")
        raise

def create_students_db():
    """Cria banco de dados de alunos"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Tabela de alunos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alunos (
                id SERIAL PRIMARY KEY,
                nome_completo TEXT NOT NULL,
                cpf TEXT UNIQUE NOT NULL,
                login_blackboard TEXT UNIQUE NOT NULL,
                senha_hash TEXT NOT NULL,
                email TEXT,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de sessões/histórico de login
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessoes (
                id SERIAL PRIMARY KEY,
                aluno_id INTEGER NOT NULL REFERENCES alunos(id),
                data_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 5 alunos genéricos
        alunos = [
            ("João Silva Santos", "12345678901", "joao.silva", "senha123", "joao@email.com"),
            ("Maria Oliveira Costa", "23456789012", "maria.oliveira", "senha456", "maria@email.com"),
            ("Pedro Ferreira Gomes", "34567890123", "pedro.ferreira", "senha789", "pedro@email.com"),
            ("Ana Paula Martins", "45678901234", "ana.paula", "senhaABC", "ana@email.com"),
            ("Carlos Alberto Mendes", "56789012345", "carlos.mendes", "senhaXYZ", "carlos@email.com"),
        ]
        
        for nome, cpf, login, senha, email in alunos:
            try:
                cursor.execute('''
                    INSERT INTO alunos (nome_completo, cpf, login_blackboard, senha_hash, email)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (nome, cpf, login, hash_password(senha), email))
                print(f"✓ Aluno criado: {nome}")
            except psycopg2.IntegrityError:
                conn.rollback()
                print(f"⚠ Aluno já existe: {nome}")
        
        conn.commit()
        print("\n✅ Banco de dados de alunos criado com sucesso!")
        
    finally:
        cursor.close()
        conn.close()

def create_blackboard_db():
    """Cria banco de dados do Blackboard"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Tabela de cursos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cursos (
                id TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                codigo_curso TEXT,
                data_inicio TIMESTAMP,
                data_fim TIMESTAMP,
                descricao TEXT
            )
        ''')
        
        # Tabela de avisos (announcements)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS avisos (
                id TEXT PRIMARY KEY,
                curso_id TEXT NOT NULL REFERENCES cursos(id),
                titulo TEXT NOT NULL,
                corpo TEXT,
                data_criacao TIMESTAMP,
                data_modificacao TIMESTAMP,
                autor TEXT
            )
        ''')
        
        # Tabela de conteúdos (atividades, materiais, etc)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conteudos (
                id TEXT PRIMARY KEY,
                curso_id TEXT NOT NULL REFERENCES cursos(id),
                titulo TEXT NOT NULL,
                tipo TEXT,
                descricao TEXT,
                data_criacao TIMESTAMP,
                data_modificacao TIMESTAMP,
                tem_subconteudos BOOLEAN DEFAULT false
            )
        ''')
        
        # Tabela de atividades avaliativas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS atividades_avaliativas (
                id TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                descricao TEXT,
                data_criacao TIMESTAMP,
                data_vencimento TIMESTAMP,
                pontos_possiveis REAL,
                tipo_avaliacao TEXT,
                disponivel BOOLEAN DEFAULT true,
                tentativas_permitidas INTEGER
            )
        ''')
        
        # Tabela de matrículas do aluno
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS matriculas_aluno (
                id SERIAL PRIMARY KEY,
                aluno_login TEXT NOT NULL,
                curso_id TEXT NOT NULL REFERENCES cursos(id),
                data_matricula TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de notas/avaliações
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notas (
                id SERIAL PRIMARY KEY,
                aluno_login TEXT NOT NULL,
                atividade_id TEXT NOT NULL REFERENCES atividades_avaliativas(id),
                nota REAL,
                data_entrega TIMESTAMP,
                feedback TEXT
            )
        ''')
        
        # Inserir cursos usando OS NOVOS NOMES DAS PASTAS como ID
        cursos_mock = [
            ('Inteligencia_Artificial', 'Inteligência Artificial', 'RS-20261-FSPOA-INT-PRE-ADS5N26-1'),
            ('Analise_Ciencia_Dados', 'Análise e Ciência de Dados', 'ACD-MK3N26-1C'),
            ('Estruturas_Dados', 'Estruturas de Dados para Ciência de Dados', 'EDC-IA2N26-1'),
            ('Manipulacao_Visualizacao_Dados', 'Manipulação e Visualização de Dados', 'MVD-IA1N26-1')
        ]
        
        for c_id, c_nome, c_codigo in cursos_mock:
            try:
                cursor.execute('''
                    INSERT INTO cursos (id, nome, codigo_curso, data_inicio, data_fim)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (c_id, c_nome, c_codigo, '2026-03-02T03:00:00.000Z', '2027-01-20T02:59:59.000Z'))
                print(f"✓ Curso criado: {c_nome}")
            except psycopg2.IntegrityError:
                conn.rollback()
                print(f"⚠ Curso já existe: {c_nome}")
        
        # Inserir matrículas de exemplo para os 5 alunos em TODAS as disciplinas
        alunos_logins = ['joao.silva', 'maria.oliveira', 'pedro.ferreira', 'ana.paula', 'carlos.mendes']
        for login in alunos_logins:
            for c_id, _, _ in cursos_mock:
                try:
                    cursor.execute('''
                        INSERT INTO matriculas_aluno (aluno_login, curso_id)
                        VALUES (%s, %s)
                    ''', (login, c_id))
                except psycopg2.IntegrityError:
                    conn.rollback()
        
        conn.commit()
        print("✅ Banco de dados do Blackboard criado com sucesso!")
        
    finally:
        cursor.close()
        conn.close()

def setup_all():
    """Executa setup completo"""
    print("=" * 50)
    print("Criando Bancos de Dados do Chatbot - PostgreSQL")
    print("=" * 50)
    print()
    
    try:
        create_students_db()
        print()
        create_blackboard_db()
        
        print("\n" + "=" * 50)
        print("✅ Setup concluído! Bancos criados com sucesso.")
        print("=" * 50)
    except Exception as e:
        print(f"\n❌ Erro durante setup: {e}")
        print("\nVerifique:")
        print("1. PostgreSQL está rodando?")
        print("2. Banco de dados 'chatbot_academico' existe?")
        print("3. Arquivo .env tem credenciais corretas?")

if __name__ == "__main__":
    setup_all()