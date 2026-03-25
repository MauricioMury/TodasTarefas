"""
notificacoes.py
================
Módulo responsável pelo envio de notificações por e-mail via Gmail SMTP.
Mantido separado do app.py para facilitar troca de provedor no futuro.

Configuração necessária (variáveis de ambiente ou direto no código):
    NOTIF_EMAIL_REMETENTE  — seu Gmail, ex: seuemail@gmail.com
    NOTIF_EMAIL_SENHA_APP  — senha de app gerada no Google
                             (Conta Google → Segurança → Senhas de app)
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

logger = logging.getLogger(__name__)

# ── Configuração do remetente ─────────────────────────────────────
# Prefira variáveis de ambiente em produção.
# Em desenvolvimento, pode preencher diretamente.
SMTP_HOST      = 'smtp.gmail.com'
SMTP_PORT      = 587
EMAIL_REMETENTE = os.environ.get('NOTIF_EMAIL_REMETENTE', 'seuemail@gmail.com')
EMAIL_SENHA_APP = os.environ.get('NOTIF_EMAIL_SENHA_APP', 'sua_senha_de_app_aqui')


def enviar_email(destinatario: str, assunto: str, corpo_texto: str) -> bool:
    """
    Envia um e-mail via Gmail SMTP.

    Parâmetros:
        destinatario — endereço de e-mail do usuário
        assunto      — linha de assunto do e-mail
        corpo_texto  — corpo em texto puro (também gerado em HTML simples)

    Retorna:
        True  — envio confirmado
        False — falha (credenciais, timeout, destinatário inválido, etc.)

    Nunca lança exceção — erros são logados e retornam False.
    """
    if not destinatario:
        logger.warning('enviar_email: destinatário não configurado.')
        return False

    if not EMAIL_REMETENTE or EMAIL_REMETENTE == 'seuemail@gmail.com':
        logger.warning('enviar_email: remetente não configurado.')
        return False

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = assunto
        msg['From']    = f'Controle de Tarefas <{EMAIL_REMETENTE}>'
        msg['To']      = destinatario

        # Parte texto puro
        parte_texto = MIMEText(corpo_texto, 'plain', 'utf-8')

        # Parte HTML — mesmo conteúdo, formatado
        corpo_html = _texto_para_html(corpo_texto)
        parte_html = MIMEText(corpo_html, 'html', 'utf-8')

        # Anexar ambas (cliente usa a última que suportar)
        msg.attach(parte_texto)
        msg.attach(parte_html)

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as servidor:
            servidor.ehlo()
            servidor.starttls()
            servidor.login(EMAIL_REMETENTE, EMAIL_SENHA_APP)
            servidor.sendmail(EMAIL_REMETENTE, destinatario, msg.as_string())

        logger.info(f'E-mail enviado para {destinatario}')
        return True

    except smtplib.SMTPAuthenticationError:
        logger.error('enviar_email: falha de autenticação — verifique o Gmail e a senha de app.')
        return False

    except smtplib.SMTPException as e:
        logger.warning(f'enviar_email: erro SMTP para {destinatario}: {e}')
        return False

    except TimeoutError:
        logger.warning(f'enviar_email: timeout ao enviar para {destinatario}')
        return False

    except Exception as e:
        logger.error(f'enviar_email: erro inesperado: {e}')
        return False


def montar_notificacao(tarefa) -> tuple[str, str]:
    """
    Monta assunto e corpo do e-mail de notificação.

    Retorna:
        (assunto, corpo_texto)
    """
    hora_fim = ''
    if tarefa.hora_fim:
        hora_fim = f' — {tarefa.hora_fim.strftime("%H:%M")}'

    assunto = f'🔔 Lembrete: {tarefa.tarefa}'

    linhas = [
        '🔔 Lembrete de Tarefa',
        '',
        f'📌 {tarefa.tarefa}',
        f'📅 {tarefa.data_meta.strftime("%d/%m/%Y")} às '
        f'{tarefa.hora_inicio.strftime("%H:%M")}{hora_fim}',
        f'🏷️  Categoria: {tarefa.categoria}',
        f'⚡ Prioridade: {tarefa.prioridade}',
    ]

    if tarefa.comentario:
        linhas.append(f'💬 {tarefa.comentario}')

    linhas += [
        '',
        '—',
        'Controle de Tarefas',
    ]

    return assunto, '\n'.join(linhas)


def _texto_para_html(texto: str) -> str:
    """Converte texto puro em HTML simples para melhor renderização."""
    linhas_html = []
    for linha in texto.split('\n'):
        if linha.strip() == '—':
            linhas_html.append('<hr style="border:none;border-top:1px solid #ddd;margin:16px 0;">')
        elif linha == '':
            linhas_html.append('<br>')
        else:
            linha_escaped = (linha
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;'))
            linhas_html.append(f'<p style="margin:4px 0;">{linha_escaped}</p>')

    return f"""
    <div style="font-family: Arial, sans-serif; max-width: 480px;
                padding: 24px; border: 1px solid #e0e0e0; border-radius: 8px;">
        {''.join(linhas_html)}
    </div>
    """