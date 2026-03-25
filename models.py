from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """Modelo de usuário do sistema"""
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    # Notificações por e-mail
    email_notif = db.Column(db.String(120), nullable=True)

    # Notificações por WhatsApp (CallMeBot)
    whatsapp_numero = db.Column(db.String(30),  nullable=True)
    whatsapp_apikey = db.Column(db.String(100), nullable=True)

    tarefas    = db.relationship('Tarefa',    backref='usuario', lazy=True, cascade='all, delete-orphan')
    categorias = db.relationship('Categoria', backref='usuario', lazy=True, cascade='all, delete-orphan')


class Categoria(db.Model):
    """Modelo de categorias customizadas por usuário"""
    id         = db.Column(db.Integer, primary_key=True)
    nome       = db.Column(db.String(50), nullable=False)
    cor        = db.Column(db.String(20), default='info')
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Categoria {self.nome}>'


class Tarefa(db.Model):
    """Modelo de tarefas do usuário"""
    id             = db.Column(db.Integer, primary_key=True)
    tarefa         = db.Column(db.String(200), nullable=False)
    comentario     = db.Column(db.Text,        nullable=True)
    data_meta      = db.Column(db.Date,        nullable=False)
    data_realizado = db.Column(db.Date,        nullable=True)
    hora_inicio    = db.Column(db.Time,        nullable=False)
    hora_fim       = db.Column(db.Time,        nullable=True)
    prioridade     = db.Column(db.String(20),  nullable=False)
    recorrencia    = db.Column(db.String(50),  nullable=False)
    categoria      = db.Column(db.String(50),  nullable=False)
    status         = db.Column(db.String(20),  default='Pendente')
    user_id        = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at     = db.Column(db.DateTime,    default=datetime.utcnow)

    # Notificações — até 2 por tarefa
    # Cada notificação tem: datetime escolhido + flag individual por canal
    notif_datetime_1        = db.Column(db.DateTime, nullable=True)
    notif_email_enviada_1   = db.Column(db.Boolean,  default=False, nullable=False)
    notif_whatsapp_enviada_1= db.Column(db.Boolean,  default=False, nullable=False)

    notif_datetime_2        = db.Column(db.DateTime, nullable=True)
    notif_email_enviada_2   = db.Column(db.Boolean,  default=False, nullable=False)
    notif_whatsapp_enviada_2= db.Column(db.Boolean,  default=False, nullable=False)

    def get_prioridade_cor(self):
        cores = {
            'Muito Importante': 'danger',
            'Importante':       'warning',
            'Normal':           'primary'
        }
        return cores.get(self.prioridade, 'secondary')

    def get_dia_semana_ordem(self):
        dias = {
            'SEGUNDA': 1, 'TERÇA': 2, 'QUARTA': 3, 'QUINTA': 4,
            'SEXTA': 5,   'SÁBADO': 6, 'DOMINGO': 7
        }
        mapa_dias = {
            'MONDAY': 'SEGUNDA', 'TUESDAY': 'TERÇA', 'WEDNESDAY': 'QUARTA',
            'THURSDAY': 'QUINTA', 'FRIDAY': 'SEXTA',
            'SATURDAY': 'SÁBADO', 'SUNDAY': 'DOMINGO'
        }
        dia_nome = self.data_meta.strftime('%A').upper()
        dia_pt   = mapa_dias.get(dia_nome, 'SEGUNDA')
        return dias.get(dia_pt, 1)

    def __repr__(self):
        return f'<Tarefa {self.tarefa}>'