"""
migrar_estagio1_whatsapp.py
============================
Migração do banco de dados — Estágio 1: campos de notificação WhatsApp.

Execute UMA VEZ, com o venv ativado, na pasta do projeto:

    python migrar_estagio1_whatsapp.py

O script é seguro para rodar múltiplas vezes (verifica colunas antes de adicionar).
"""

import sqlite3
import os
import sys

DB_PATH = os.path.join('instance/tarefas.db')   # ajuste se seu banco estiver em outro caminho

def coluna_existe(cursor, tabela, coluna):
    cursor.execute(f"PRAGMA table_info({tabela})")
    return any(row[1] == coluna for row in cursor.fetchall())

def main():
    if not os.path.exists(DB_PATH):
        print(f"❌  Banco '{DB_PATH}' não encontrado. Verifique o caminho.")
        sys.exit(1)

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    alteracoes = 0

    # ── Tabela: user ────────────────────────────────────────────────────────────
    if not coluna_existe(cur, 'user', 'whatsapp_numero'):
        cur.execute("ALTER TABLE user ADD COLUMN whatsapp_numero VARCHAR(30)")
        print("✅  user.whatsapp_numero adicionada")
        alteracoes += 1
    else:
        print("⏭️   user.whatsapp_numero já existe — pulando")

    if not coluna_existe(cur, 'user', 'whatsapp_apikey'):
        cur.execute("ALTER TABLE user ADD COLUMN whatsapp_apikey VARCHAR(100)")
        print("✅  user.whatsapp_apikey adicionada")
        alteracoes += 1
    else:
        print("⏭️   user.whatsapp_apikey já existe — pulando")

    # ── Tabela: tarefa ───────────────────────────────────────────────────────────
    if not coluna_existe(cur, 'tarefa', 'notif_antecedencia'):
        cur.execute("ALTER TABLE tarefa ADD COLUMN notif_antecedencia INTEGER")
        print("✅  tarefa.notif_antecedencia adicionada")
        alteracoes += 1
    else:
        print("⏭️   tarefa.notif_antecedencia já existe — pulando")

    if not coluna_existe(cur, 'tarefa', 'notif_datetime'):
        cur.execute("ALTER TABLE tarefa ADD COLUMN notif_datetime DATETIME")
        print("✅  tarefa.notif_datetime adicionada")
        alteracoes += 1
    else:
        print("⏭️   tarefa.notif_datetime já existe — pulando")

    if not coluna_existe(cur, 'tarefa', 'notif_enviada'):
        cur.execute("ALTER TABLE tarefa ADD COLUMN notif_enviada BOOLEAN NOT NULL DEFAULT 0")
        print("✅  tarefa.notif_enviada adicionada")
        alteracoes += 1
    else:
        print("⏭️   tarefa.notif_enviada já existe — pulando")

    con.commit()
    con.close()

    print(f"\n{'✅  Migração concluída!' if alteracoes else '✅  Nada a migrar — banco já estava atualizado.'}")
    print(f"   {alteracoes} coluna(s) adicionada(s).")

if __name__ == '__main__':
    main()