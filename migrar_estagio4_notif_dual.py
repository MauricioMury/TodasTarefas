"""
migrar_estagio4_notif_dual.py
==============================
Migração do banco — Estágio 4: suporte a notificações por e-mail E WhatsApp.

O que este script faz:
  - Tabela user:   adiciona whatsapp_numero e whatsapp_apikey
  - Tabela user:   adiciona email_notif (caso não exista)
  - Tabela tarefa: adiciona notif_datetime_1, notif_datetime_2
  - Tabela tarefa: adiciona notif_email_enviada_1 / notif_whatsapp_enviada_1
  - Tabela tarefa: adiciona notif_email_enviada_2 / notif_whatsapp_enviada_2
  - Tabela tarefa: renomeia notif_enviada_1 → notif_email_enviada_1
                   e       notif_enviada_2 → notif_email_enviada_2
                   (se existirem com o nome antigo)

Execute UMA VEZ, com o venv ativado, na pasta do projeto:

    python migrar_estagio4_notif_dual.py

O script é seguro para rodar múltiplas vezes (verifica colunas antes de agir).
"""

import sqlite3
import os
import sys

DB_PATH = os.path.join('instance', 'tarefas.db')


def coluna_existe(cursor, tabela, coluna):
    cursor.execute(f"PRAGMA table_info({tabela})")
    return any(row[1] == coluna for row in cursor.fetchall())


def versao_sqlite(cursor):
    cursor.execute("SELECT sqlite_version()")
    v = cursor.fetchone()[0]
    return tuple(int(x) for x in v.split('.'))


def main():
    if not os.path.exists(DB_PATH):
        print(f"❌  Banco '{DB_PATH}' não encontrado. Verifique o caminho.")
        sys.exit(1)

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    ver = versao_sqlite(cur)
    print(f"ℹ️   SQLite versão {'.'.join(str(x) for x in ver)}")

    alteracoes = 0

    # ── Tabela: user ─────────────────────────────────────────────────────────

    if not coluna_existe(cur, 'user', 'email_notif'):
        cur.execute("ALTER TABLE user ADD COLUMN email_notif VARCHAR(120)")
        print("✅  user.email_notif adicionada")
        alteracoes += 1
    else:
        print("⏭️   user.email_notif já existe — pulando")

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

    # ── Tabela: tarefa — campos datetime ─────────────────────────────────────

    if not coluna_existe(cur, 'tarefa', 'notif_datetime_1'):
        cur.execute("ALTER TABLE tarefa ADD COLUMN notif_datetime_1 DATETIME")
        print("✅  tarefa.notif_datetime_1 adicionada")
        alteracoes += 1
    else:
        print("⏭️   tarefa.notif_datetime_1 já existe — pulando")

    if not coluna_existe(cur, 'tarefa', 'notif_datetime_2'):
        cur.execute("ALTER TABLE tarefa ADD COLUMN notif_datetime_2 DATETIME")
        print("✅  tarefa.notif_datetime_2 adicionada")
        alteracoes += 1
    else:
        print("⏭️   tarefa.notif_datetime_2 já existe — pulando")

    # ── Tabela: tarefa — flags de envio ──────────────────────────────────────
    # Se existirem colunas com nome antigo (notif_enviada_1/2), elas são
    # renomeadas para notif_email_enviada_1/2 (requer SQLite >= 3.25).
    # Caso a versão seja menor, mantém o nome antigo e avisa.

    for idx in ('1', '2'):
        col_antiga = f'notif_enviada_{idx}'
        col_email  = f'notif_email_enviada_{idx}'
        col_zap    = f'notif_whatsapp_enviada_{idx}'

        # Renomear coluna antiga → email, se aplicável
        if coluna_existe(cur, 'tarefa', col_antiga) and not coluna_existe(cur, 'tarefa', col_email):
            if ver >= (3, 25, 0):
                cur.execute(f"ALTER TABLE tarefa RENAME COLUMN {col_antiga} TO {col_email}")
                print(f"✅  tarefa.{col_antiga} renomeada para {col_email}")
                alteracoes += 1
            else:
                print(f"⚠️   SQLite < 3.25 — não é possível renomear {col_antiga}.")
                print(f"     Criando {col_email} separado; {col_antiga} ficará ignorada.")
                cur.execute(
                    f"ALTER TABLE tarefa ADD COLUMN {col_email} BOOLEAN NOT NULL DEFAULT 0"
                )
                alteracoes += 1
        elif not coluna_existe(cur, 'tarefa', col_email):
            cur.execute(
                f"ALTER TABLE tarefa ADD COLUMN {col_email} BOOLEAN NOT NULL DEFAULT 0"
            )
            print(f"✅  tarefa.{col_email} adicionada")
            alteracoes += 1
        else:
            print(f"⏭️   tarefa.{col_email} já existe — pulando")

        # Adicionar coluna WhatsApp
        if not coluna_existe(cur, 'tarefa', col_zap):
            cur.execute(
                f"ALTER TABLE tarefa ADD COLUMN {col_zap} BOOLEAN NOT NULL DEFAULT 0"
            )
            print(f"✅  tarefa.{col_zap} adicionada")
            alteracoes += 1
        else:
            print(f"⏭️   tarefa.{col_zap} já existe — pulando")

    con.commit()
    con.close()

    print(f"\n{'✅  Migração concluída!' if alteracoes else '✅  Nada a migrar — banco já estava atualizado.'}")
    print(f"   {alteracoes} operação(ões) executada(s).")


if __name__ == '__main__':
    main()
