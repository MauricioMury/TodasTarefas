"""
Script de Migração V2 → V3
============================
Este script atualiza o banco de dados existente para incluir:
1. Tabela de Categorias
2. Campo comentario nas Tarefas
3. Categorias padrão para usuários existentes

IMPORTANTE: Faça backup do banco antes de executar!

Uso:
    python migrar_para_v3.py
"""

import sqlite3
from datetime import datetime

def migrar_banco():
    """Migra o banco de dados da V2 para V3"""
    
    print("="*60)
    print("MIGRAÇÃO V2 → V3 - Controle de Tarefas")
    print("="*60)
    print()
    
    # Conectar ao banco
    conn = sqlite3.connect('tarefas.db')
    cursor = conn.cursor()
    
    try:
        # ============================================
        # 1. CRIAR TABELA DE CATEGORIAS
        # ============================================
        print("📊 Criando tabela de categorias...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categoria (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome VARCHAR(50) NOT NULL,
                cor VARCHAR(20) DEFAULT 'info',
                user_id INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE
            )
        """)
        print("✅ Tabela 'categoria' criada com sucesso!")
        print()
        
        # ============================================
        # 2. ADICIONAR CAMPO COMENTARIO NA TAREFA
        # ============================================
        print("📝 Adicionando campo 'comentario' à tabela tarefa...")
        
        # Verificar se já existe
        cursor.execute("PRAGMA table_info(tarefa)")
        colunas = [col[1] for col in cursor.fetchall()]
        
        if 'comentario' not in colunas:
            cursor.execute("""
                ALTER TABLE tarefa 
                ADD COLUMN comentario TEXT
            """)
            print("✅ Campo 'comentario' adicionado com sucesso!")
        else:
            print("⚠️  Campo 'comentario' já existe!")
        print()
        
        # ============================================
        # 3. CRIAR CATEGORIAS PADRÃO PARA USUÁRIOS
        # ============================================
        print("🏷️  Criando categorias padrão para usuários existentes...")
        
        # Buscar todos os usuários
        cursor.execute("SELECT id, username FROM user")
        usuarios = cursor.fetchall()
        
        categorias_padrao = [
            ('Família', 'success'),
            ('Trabalho', 'primary'),
            ('Casa', 'warning'),
            ('Amigos', 'info'),
            ('Estudo', 'secondary'),
            ('Financeiro', 'danger'),
            ('Espiritual', 'light'),
            ('Saúde', 'success'),
        ]
        
        total_criadas = 0
        for user_id, username in usuarios:
            # Verificar se já tem categorias
            cursor.execute("SELECT COUNT(*) FROM categoria WHERE user_id = ?", (user_id,))
            count = cursor.fetchone()[0]
            
            if count == 0:
                print(f"   📌 Criando categorias para usuário: {username}")
                for nome, cor in categorias_padrao:
                    cursor.execute("""
                        INSERT INTO categoria (nome, cor, user_id, created_at)
                        VALUES (?, ?, ?, ?)
                    """, (nome, cor, user_id, datetime.utcnow()))
                    total_criadas += 1
            else:
                print(f"   ⏭️  Usuário {username} já possui categorias")
        
        print(f"✅ {total_criadas} categorias criadas!")
        print()
        
        # ============================================
        # 4. COMMIT E FINALIZAÇÃO
        # ============================================
        conn.commit()
        
        # Estatísticas finais
        cursor.execute("SELECT COUNT(*) FROM user")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tarefa")
        total_tarefas = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM categoria")
        total_categorias = cursor.fetchone()[0]
        
        print("="*60)
        print("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*60)
        print()
        print("📊 Estatísticas do Banco:")
        print(f"   👥 Usuários: {total_users}")
        print(f"   📋 Tarefas: {total_tarefas}")
        print(f"   🏷️  Categorias: {total_categorias}")
        print()
        print("🎉 Seu banco está pronto para a V3!")
        print()
        
    except Exception as e:
        print(f"❌ ERRO durante a migração: {str(e)}")
        conn.rollback()
        print("⏪ Rollback realizado. Banco mantido no estado anterior.")
        return False
        
    finally:
        conn.close()
    
    return True

def verificar_backup():
    """Verifica se usuário fez backup antes de migrar"""
    print()
    print("⚠️  ATENÇÃO: É ALTAMENTE RECOMENDADO fazer backup do banco antes de migrar!")
    print()
    print("Para fazer backup:")
    print("   Windows: copy tarefas.db tarefas_backup.db")
    print("   Linux/Mac: cp tarefas.db tarefas_backup.db")
    print()
    
    resposta = input("Você já fez backup do banco? (s/n): ").strip().lower()
    
    if resposta != 's':
        print()
        print("❌ Faça o backup primeiro e execute o script novamente!")
        return False
    
    return True

if __name__ == '__main__':
    print()
    
    if not verificar_backup():
        exit(1)
    
    print()
    input("Pressione ENTER para iniciar a migração...")
    print()
    
    sucesso = migrar_banco()
    
    if sucesso:
        print("="*60)
        print("PRÓXIMOS PASSOS:")
        print("="*60)
        print()
        print("1. ✅ Substitua os arquivos do projeto pelos novos:")
        print("   - models.py")
        print("   - app.py")
        print("   - base.html")
        print("   - cadastro_tarefa.html")
        print("   - editar_tarefa.html")
        print("   - lista_tarefas.html")
        print()
        print("2. ✅ Adicione os novos templates:")
        print("   - cadastro_categoria.html")
        print("   - lista_categorias.html")
        print("   - editar_categoria.html")
        print()
        print("3. ✅ Reinicie o servidor Flask")
        print()
        print("4. 🎊 Aproveite as novas funcionalidades da V3!")
        print()
    else:
        print()
        print("❌ Migração falhou. Verifique os erros acima.")
        print()
