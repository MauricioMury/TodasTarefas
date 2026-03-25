# 🗺️ Mapa do Projeto - Controle de Tarefas

**Versão:** 4.0
**Data:** Março 2026
**Tecnologias:** Flask 3.0, SQLite, Bootstrap 5, Python 3.11+, Syne + DM Sans (Google Fonts)

---

## 📑 Índice

### 🏗️ [1. Estrutura do Projeto](#1-estrutura-do-projeto)
### 🎯 [2. Funcionalidades Implementadas](#2-funcionalidades-implementadas)
### 🗄️ [3. Banco de Dados](#3-banco-de-dados)
### 🛣️ [4. Rotas da Aplicação](#4-rotas-da-aplicação)
### 🎨 [5. Interface do Usuário (V4)](#5-interface-do-usuário-v4)
### 🚀 [6. Guia de Instalação](#6-guia-de-instalação)
### 🔒 [7. Segurança](#7-segurança)
### 🔧 [8. Manutenção e Desenvolvimento](#8-manutenção-e-desenvolvimento)
### 🎯 [9. Roadmap Futuro](#9-roadmap-futuro)

---

## 1. Estrutura do Projeto

### 1.1 Arquivos Principais

```
controle_tarefas/
├── app.py                         # 🔥 Aplicação Flask principal
├── models.py                      # 📊 Modelos de banco de dados
├── requirements.txt               # 📦 Dependências de produção
├── requirements-dev.txt           # 🧪 Dependências de desenvolvimento
├── pytest.ini                     # ⚙️ Configuração de testes
├── tarefas.db                     # 💾 Banco de dados SQLite (gerado)
├── GUIA_ATUALIZACAO_V4.md         # 📖 Guia de atualização V3→V4
├── mapa_projetoV4.md              # 🗺️ Este arquivo
└── README.md                      # 📖 Documentação principal
```

### 1.2 Diretório templates/

```
templates/
├── base.html                      # 🎨 Template base (navbar, tema, footer)
├── login.html                     # 🔐 Página de login (standalone)
├── register.html                  # ✏️ Página de cadastro
├── index.html                     # 🏠 Dashboard com stats
├── cadastro_tarefa.html           # ➕ Formulário de nova tarefa
├── editar_tarefa.html             # ✏️ Formulário de edição
├── lista_tarefas.html             # 📋 Lista paginada + filtros + busca
├── cadastro_categoria.html        # 🏷️ Formulário de nova categoria
├── editar_categoria.html          # ✏️ Formulário de edição de categoria
└── lista_categorias.html          # 🏷️ Lista de categorias
```

**Hierarquia de Templates:**

```
base.html (tema dark/light, navbar com toggle, footer)
├── register.html
└── [templates autenticados]
    ├── index.html          (dashboard com stats)
    ├── cadastro_tarefa.html
    ├── editar_tarefa.html
    ├── lista_tarefas.html  (busca + filtros)
    ├── cadastro_categoria.html
    ├── editar_categoria.html
    └── lista_categorias.html

login.html (standalone - toggle próprio, não estende base.html)
```

---

## 2. Funcionalidades Implementadas

### 2.1 Autenticação

#### ✅ Login
- Rota: `/login`
- Método: GET, POST
- Validações: usuário existe, senha correta (bcrypt), sessão Flask-Login
- Interface standalone com toggle dark/light próprio

#### ✅ Registro
- Rota: `/register`
- Validações: username único, senhas coincidem, hash automático (bcrypt)
- Cria categorias padrão automaticamente para o novo usuário

#### ✅ Logout
- Rota: `/logout` — encerra sessão Flask-Login

**Credenciais Padrão:**
- Username: `admin` / Password: `admin`

---

### 2.2 Gestão de Tarefas

#### ✅ Cadastro de Tarefa
- **Rota:** `/cadastro_tarefa`
- **Campos:** Tarefa, Comentário, Data Meta, Data Realizado, Hora Início, Hora Fim (opcional), Prioridade, Recorrência (15 opções), Categoria (dinâmica do banco)
- **Validação:** Hora Fim > Hora Início

#### ✅ Lista de Tarefas
- **Rota:** `/lista_tarefas`
- **Features:**
  - Paginação (5, 10, 20, 50, 100 itens)
  - **🆕 Filtro de busca por texto** (Tarefa + Comentário, debounce 400ms, backend)
  - Filtros por categoria, prioridade, status, data
  - Filtros persistentes (mantidos na URL e sessão)
  - Indicador visual de filtros ativos com badges
  - Botão "Limpar Filtros" funcionando
  - Ordenação automática (data + hora)
  - Tabela responsiva Bootstrap

#### ✅ Edição de Tarefa
- **Rota:** `/editar_tarefa/<id>` — todos os campos editáveis, apenas dono

#### ✅ Exclusão de Tarefa
- **Rota:** `/deletar_tarefa/<id>` (POST) — confirmação JS, apenas dono

#### ✅ Marcar como Concluída
- **Rota:** `/marcar_concluida/<id>` (POST) — Status → "Concluída", Data Realizado → hoje

#### ✅ Duplicar Tarefa
- **Rota:** `/duplicar_tarefa/<id>` — copia campos, limpa datas, redireciona para formulário pré-preenchido

---

### 2.3 Gestão de Categorias

#### ✅ CRUD Completo
- `/categorias` — lista categorias do usuário
- `/cadastro_categoria` — criar nova categoria com nome e cor
- `/editar_categoria/<id>` — editar nome e cor
- `/deletar_categoria/<id>` — deletar (bloqueado se em uso)

#### ✅ Cores Disponíveis
`primary`, `success`, `danger`, `warning`, `info`, `secondary`, `dark`, `light`

---

### 2.4 Interface — Novidades V4

#### ✅ Tema Dark / Light
- Toggle ☀️/🌙 no canto superior esquerdo da navbar
- Preferência salva em `localStorage` (persiste entre sessões)
- Modo escuro padrão
- Transições suaves (0.25s) ao trocar tema
- Disponível em todas as telas, incluindo login

#### ✅ Design System V4
- **Tipografia:** Syne (títulos, navbar) + DM Sans (corpo)
- **Cores:** Sistema de variáveis CSS com `--accent` (#7c6af7 dark / #6355e8 light)
- **Cards:** border-radius 14px, sombras sutis
- **Tabelas:** cabeçalhos em uppercase com letter-spacing
- **Badges:** border-radius 6px, tipografia compacta
- **Scrollbar:** customizada com variáveis do tema

#### ✅ Dashboard com Estatísticas
- 5 cards: Total, Pendentes, Concluídas, Alta Prioridade, Hoje
- Valores carregados dinamicamente via JavaScript (fetch)
- 4 cards de ações rápidas com hover animado

#### ✅ Filtro de Busca por Texto
- Campo com ícone de lupa
- Debounce de 400ms (submete ao servidor ao parar de digitar)
- Busca em `tarefa` e `comentario` (case-insensitive, `ilike`)
- `coalesce` para tratar `comentario = NULL` sem erros
- Persiste na paginação e ao mudar itens por página
- Botão ✕ para limpar individualmente

---

## 3. Banco de Dados

### 3.1 Modelo User

```python
class User(UserMixin, db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # bcrypt
    tarefas  = db.relationship('Tarefa', backref='usuario', cascade='all, delete-orphan')
```

### 3.2 Modelo Tarefa

```python
class Tarefa(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    tarefa        = db.Column(db.String(200), nullable=False)
    comentario    = db.Column(db.Text, nullable=True)
    data_meta     = db.Column(db.Date, nullable=False)
    data_realizado= db.Column(db.Date, nullable=True)
    hora_inicio   = db.Column(db.Time, nullable=False)
    hora_fim      = db.Column(db.Time, nullable=True)
    prioridade    = db.Column(db.String(20), nullable=False)
    recorrencia   = db.Column(db.String(50), nullable=False)
    categoria     = db.Column(db.String(50), nullable=False)
    status        = db.Column(db.String(20), default='Pendente')
    user_id       = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
```

### 3.3 Modelo Categoria

```python
class Categoria(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    nome       = db.Column(db.String(50), nullable=False)
    cor        = db.Column(db.String(20), default='info')
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### 3.4 Relacionamentos

```
User (1) ↔ (N) Tarefa    — cascade delete
User (1) ↔ (N) Categoria — cascade delete
```

---

## 4. Rotas da Aplicação

### 4.1 Rotas Públicas

| Rota | Método | Descrição |
|------|--------|-----------|
| `/login` | GET, POST | Página de login |
| `/register` | GET, POST | Cadastro de usuário |

### 4.2 Rotas Protegidas

| Rota | Método | Descrição |
|------|--------|-----------|
| `/` | GET | Dashboard com stats |
| `/logout` | GET | Encerrar sessão |
| `/cadastro_tarefa` | GET, POST | Criar nova tarefa |
| `/lista_tarefas` | GET | Lista + filtros + busca |
| `/editar_tarefa/<id>` | GET, POST | Editar tarefa |
| `/deletar_tarefa/<id>` | POST | Deletar tarefa |
| `/marcar_concluida/<id>` | POST | Marcar como concluída |
| `/duplicar_tarefa/<id>` | GET | Duplicar tarefa |
| `/categorias` | GET | Lista de categorias |
| `/cadastro_categoria` | GET, POST | Nova categoria |
| `/editar_categoria/<id>` | GET, POST | Editar categoria |
| `/deletar_categoria/<id>` | POST | Deletar categoria |

---

## 5. Interface do Usuário (V4)

### 5.1 Sistema de Cores (CSS Variables)

| Variável | Dark | Light | Uso |
|----------|------|-------|-----|
| `--bg-primary` | `#0f1117` | `#f0f2fa` | Fundo da página |
| `--bg-card` | `#1e2130` | `#ffffff` | Cards e modais |
| `--bg-input` | `#252840` | `#f5f6ff` | Inputs e botões secundários |
| `--accent` | `#7c6af7` | `#6355e8` | Cor principal, botões |
| `--accent-glow` | `rgba(124,106,247,.2)` | `rgba(99,85,232,.12)` | Hover, focus glow |
| `--text-primary` | `#e8eaf6` | `#1a1d2e` | Texto principal |
| `--text-secondary` | `#8b90b8` | `#5a5f85` | Nav links, labels |
| `--text-muted` | `#555a7a` | `#9499bb` | Placeholders, hints |
| `--border-color` | `#2e3250` | `#dde1f5` | Bordas de cards e inputs |

### 5.2 Tipografia

| Fonte | Uso | Pesos |
|-------|-----|-------|
| Inter | Títulos (h1-h6), navbar brand, labels de cards | 400, 600, 700, 800 |
| DM Sans | Corpo do texto, inputs, botões | 300, 400, 500 |

### 5.3 Toggle Dark/Light

- **Localização:** Canto superior direito da navbar (antes do Usuário)
- **Persistência:** `localStorage` key `ct-theme`
- **Padrão:** `dark`
- **Login:** Toggle próprio (posição fixed top-left, não usa base.html)

---

## 6. Guia de Instalação

### 6.1 Requisitos

- Python 3.8+
- pip
- Ambiente virtual (recomendado)

### 6.2 Instalação

```bash
mkdir controle_tarefas && cd controle_tarefas
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Acesse: `http://localhost:5050`

### 6.3 Primeiro Acesso

- **Usuário:** `admin` / **Senha:** `admin`
- ⚠️ Altere a senha após o primeiro login!

---

## 7. Segurança

| Vulnerabilidade | Proteção |
|-----------------|----------|
| SQL Injection | ✅ SQLAlchemy ORM |
| XSS | ✅ Jinja2 auto-escape |
| CSRF | ⚠️ Recomendado adicionar Flask-WTF |
| Session Fixation | ✅ Flask-Login |
| Brute Force | ⏳ Não implementado |
| Rate Limiting | ⏳ Não implementado |

---

## 8. Manutenção e Desenvolvimento

### 8.1 Adicionar Novo Tema de Cor

Edite as variáveis no `base.html`:

```css
[data-theme="dark"] {
    --accent: #sua-cor-aqui;
    --accent-hover: #sua-cor-hover;
    --accent-glow: rgba(r,g,b,0.2);
}
```

### 8.2 Adicionar Novo Filtro

1. Adicionar campo no formulário de filtros em `lista_tarefas.html`
2. Capturar em `get_filtros_ativos()` no `app.py`
3. Adicionar `session.pop` em `limpar_filtros_sessao()`
4. Adicionar filtro na query em `lista_tarefas()`
5. Passar para `render_template`
6. Incluir nos `hidden inputs` do form de per_page
7. Incluir nos links de paginação

### 8.3 Troubleshooting

| Problema | Solução |
|----------|---------|
| Porta 5050 ocupada | Alterar `port` no `app.py` |
| Banco não criado | `python` → `from app import app,db` → `with app.app_context(): db.create_all()` |
| Tema não salva | Verificar `localStorage` no DevTools |
| Stats não carregam | JavaScript habilitado? Servidor rodando? |
| Fonts sem efeito | Google Fonts bloqueado — usa fallback automático |

---

## 9. Roadmap Futuro

### 9.1 Funcionalidades Planejadas

#### Curto Prazo:
- [ ] Completar testes restantes (60 pendentes)
- [ ] Dashboard com gráficos Chart.js (pizza de status, barras por categoria)
- [ ] Exportar lista em PDF
- [ ] Campo de observações expandido

#### Médio Prazo:
- [ ] Sistema de notificações/lembretes
- [ ] API REST para integração
- [ ] Dark/light mode por rota (preferência persistente já implementada)
- [ ] Compartilhamento de tarefas entre usuários

#### Longo Prazo:
- [ ] Integração com Google Calendar
- [ ] Subtarefas
- [ ] Aplicativo Android/iOS nativo
- [ ] Colaboração em tempo real

### 9.2 Melhorias Técnicas

- [ ] CSRF protection (Flask-WTF)
- [ ] Rate limiting (Flask-Limiter)
- [ ] CI/CD com GitHub Actions
- [ ] Docker containerization
- [ ] Migrations (Alembic)
- [ ] Cache (Redis)

---

## 📊 Histórico de Versões

| Versão | Data | Destaques |
|--------|------|-----------|
| V1 | Jan 2026 | CRUD de tarefas, autenticação básica |
| V2 | Jan 2026 | Filtros, paginação, categorias fixas |
| V3 | Fev 2026 | Categorias dinâmicas, comentários, filtros persistentes |
| V4 | Mar 2026 | Tema dark/light, redesign completo, filtro de busca por texto |

---

**Última atualização:** Março 2026
**Versão do documento:** 4.0
**Mantido por:** Mauricio
