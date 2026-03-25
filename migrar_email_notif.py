"""
migrar_email_notif.py
======================
Migração do banco — substitui campos WhatsApp por email_notif no User.

Execute UMA VEZ, com o venv ativado, na pasta do projeto:

    python migrar_email_notif.py

Seguro para rodar múltiplas vezes.
"""

import sqlite3
import os
import sys

DB_PATH = os.path.join('instance', 'tarefas.db')

def coluna_existe(cursor, tabela, coluna):
    cursor.execute(f"PRAGMA table_info({tabela})")
    return any(row[1] == coluna for row in cursor.fetchall())

def main():
    if not os.path.exists(DB_PATH):
        print(f"❌  Banco '{DB_PATH}' não encontrado.")
        sys.exit(1)

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    alteracoes = 0

    # ── Adicionar email_notif ────────────────────────────────────
    if not coluna_existe(cur, 'user', 'email_notif'):
        cur.execute("ALTER TABLE user ADD COLUMN email_notif VARCHAR(120)")
        print("✅  user.email_notif adicionada")
        alteracoes += 1
    else:
        print("⏭️   user.email_notif já existe — pulando")

    # ── Remover colunas WhatsApp (SQLite >= 3.35) ────────────────
    for col in ['whatsapp_numero', 'whatsapp_apikey']:
        if coluna_existe(cur, 'user', col):
            try:
                cur.execute(f"ALTER TABLE user DROP COLUMN {col}")
                print(f"🗑️   user.{col} removida")
                alteracoes += 1
            except Exception as e:
                print(f"⚠️   Não foi possível remover user.{col}: {e}")
                print(f"     A coluna ficará no banco mas não será usada.")
        else:
            print(f"⏭️   user.{col} não existe — pulando")

    con.commit()
    con.close()

    print(f"\n✅  Migração concluída. {alteracoes} operação(ões) executada(s).")

if __name__ == '__main__':
    main()