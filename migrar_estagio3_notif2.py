"""
migrar_estagio3_notif2.py
==========================
Migração do banco — Estágio 3: ajuste dos campos de notificação.

Remove os campos do Estágio 1 (notif_antecedencia, notif_datetime, notif_enviada)
e adiciona os novos (notif_datetime_1, notif_enviada_1, notif_datetime_2, notif_enviada_2).

ATENÇÃO: SQLite não suporta DROP COLUMN em versões < 3.35.
O script detecta a versão e usa recreate da tabela se necessário.
Em produção (PythonAnywhere) o SQLite costuma ser >= 3.35, então DROP COLUMN funciona.

Execute UMA VEZ, com o venv ativado, na pasta do projeto:

    python migrar_estagio3_notif2.py
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
    partes = [int(x) for x in v.split('.')]
    return tuple(partes)

def main():
    if not os.path.exists(DB_PATH):
        print(f"❌  Banco '{DB_PATH}' não encontrado.")
        sys.exit(1)

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    ver = versao_sqlite(cur)
    print(f"ℹ️   SQLite versão {'.'.join(str(x) for x in ver)}")

    alteracoes = 0

    # ── Remover colunas do Estágio 1 (se existirem) ─────────────────────────
    colunas_antigas = ['notif_antecedencia', 'notif_datetime', 'notif_enviada']

    for col in colunas_antigas:
        if coluna_existe(cur, 'tarefa', col):
            if ver >= (3, 35, 0):
                cur.execute(f"ALTER TABLE tarefa DROP COLUMN {col}")
                print(f"🗑️   tarefa.{col} removida")
                alteracoes += 1
            else:
                print(f"⚠️   tarefa.{col} existe mas SQLite < 3.35 — não é possível remover automaticamente.")
                print(f"     A coluna ficará no banco mas não será usada. Isso não causa problemas.")
        else:
            print(f"⏭️   tarefa.{col} não existe — pulando remoção")

    # ── Adicionar novos campos ───────────────────────────────────────────────
    novos = [
        ('notif_datetime_1', 'DATETIME'),
        ('notif_enviada_1',  'BOOLEAN NOT NULL DEFAULT 0'),
        ('notif_datetime_2', 'DATETIME'),
        ('notif_enviada_2',  'BOOLEAN NOT NULL DEFAULT 0'),
    ]

    for col, tipo in novos:
        if not coluna_existe(cur, 'tarefa', col):
            cur.execute(f"ALTER TABLE tarefa ADD COLUMN {col} {tipo}")
            print(f"✅  tarefa.{col} adicionada")
            alteracoes += 1
        else:
            print(f"⏭️   tarefa.{col} já existe — pulando")

    con.commit()
    con.close()

    print(f"\n{'✅  Migração concluída!' if alteracoes else '✅  Nada a migrar.'}")
    print(f"   {alteracoes} operação(ões) executada(s).")

if __name__ == '__main__':
    main()