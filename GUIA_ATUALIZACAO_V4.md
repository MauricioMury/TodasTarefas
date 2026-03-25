# 🚀 Guia de Atualização V3 → V4

## 📋 Índice
1. [Novidades da V4](#novidades-da-v4)
2. [Backup do Banco](#backup-do-banco)
3. [Atualização dos Arquivos](#atualização-dos-arquivos)
4. [Migração do Banco de Dados](#migração-do-banco-de-dados)
5. [Verificação Pós-Atualização](#verificação-pós-atualização)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 Novidades da V4

### ✅ Correções Implementadas

1. **Filtro de Busca por Texto**
   - Campo de busca que filtra em tempo real (debounce 400ms)
   - Busca simultânea em **Tarefa** e **Comentário**
   - Suporte a `coalesce` para tratar campos nulos sem erros
   - Busca funciona em todas as páginas (backend), não só na página atual
   - Botão ✕ para limpar busca individualmente
   - Badge "Busca: ..." no indicador de filtros ativos
   - Filtro de busca persiste na paginação e ao trocar itens por página

### 🆕 Novas Funcionalidades

1. **Tema Dark / Light com Toggle**
   - Botão de alternância no canto superior esquerdo da navbar
   - Ícone ☀️ no modo escuro, 🌙 no modo claro
   - Preferência salva no `localStorage` (persiste entre sessões)
   - Transições suaves ao trocar de tema
   - Disponível em **todas as telas**, incluindo login

2. **Interface Completamente Redesenhada (V4 Design)**
   - Novo sistema de cores com variáveis CSS (`--bg-primary`, `--accent`, etc.)
   - Tipografia: **Syne** (títulos/navbar) + **DM Sans** (corpo)
   - Tema escuro padrão inspirado no protótipo visual
   - Cards com bordas arredondadas e sombras refinadas
   - Tabelas com cabeçalhos estilizados e hover suave
   - Badges, botões e alertas totalmente adaptados ao tema
   - Scrollbar customizada
   - Navbar com backdrop blur

3. **Dashboard Reformulado**
   - 5 cards de estatísticas dinâmicas (Total, Pendentes, Concluídas, Alta Prioridade, Hoje)
   - Ícones coloridos por categoria de stat
   - 4 cards de ações rápidas com hover animado
   - Saudação personalizada com nome do usuário

4. **Login Redesenhado**
   - Card centralizado com logo e ícone
   - Campos com ícones internos
   - Botão de toggle dark/light próprio (não depende do base.html)
   - Mensagens de erro integradas ao card

---

## 💾 Backup do Banco

### ⚠️ MUITO IMPORTANTE!

A V4 **não altera o banco de dados** — é uma atualização apenas de interface. Mesmo assim, sempre faça backup antes de substituir arquivos.

#### Windows:
```cmd
copy tarefas.db tarefas_backup_v3.db
```

#### Linux/Mac:
```bash
cp tarefas.db tarefas_backup_v3.db
```

---

## 📁 Atualização dos Arquivos

### Arquivos a SUBSTITUIR (sem migração de banco)

```
controle_tarefas/
├── app.py                        ← SUBSTITUIR (filtro busca + coalesce)
└── templates/
    ├── base.html                 ← SUBSTITUIR (tema dark/light + toggle)
    ├── login.html                ← SUBSTITUIR (redesign completo)
    ├── index.html                ← SUBSTITUIR (dashboard com stats)
    ├── lista_tarefas.html        ← SUBSTITUIR (campo busca + tema)
    ├── cadastro_tarefa.html      ← SUBSTITUIR (adaptado ao tema)
    ├── editar_tarefa.html        ← SUBSTITUIR (adaptado ao tema)
    ├── cadastro_categoria.html   ← SUBSTITUIR (adaptado ao tema)
    ├── editar_categoria.html     ← SUBSTITUIR (adaptado ao tema)
    └── lista_categorias.html     ← SUBSTITUIR (adaptado ao tema)
```

### ✅ Checklist de Atualização

- [ ] Backup do banco criado (`tarefas_backup_v3.db`)
- [ ] `app.py` substituído
- [ ] `base.html` substituído
- [ ] `login.html` substituído
- [ ] `index.html` substituído
- [ ] `lista_tarefas.html` substituído
- [ ] `cadastro_tarefa.html` substituído
- [ ] `editar_tarefa.html` substituído
- [ ] `cadastro_categoria.html` substituído
- [ ] `editar_categoria.html` substituído
- [ ] `lista_categorias.html` substituído

---

## 🔄 Migração do Banco de Dados

**A V4 não requer migração de banco.** Nenhuma tabela ou coluna foi adicionada ou alterada.

Se estiver atualizando direto da V2 para V4, execute a migração da V3 antes:

```bash
python migrar_para_v3.py
```

---

## ✔️ Verificação Pós-Atualização

### 1. Iniciar o Servidor

```bash
python app.py
```

### 2. Checklist de Funcionalidades

Acesse `http://localhost:5050` e verifique:

#### Tema:
- [ ] Página carrega em modo escuro por padrão
- [ ] Botão ☀️/🌙 aparece no canto superior esquerdo da navbar
- [ ] Clicar no botão alterna entre dark e light
- [ ] Tema persiste ao recarregar a página (localStorage)
- [ ] Tela de login também tem o toggle de tema

#### Dashboard:
- [ ] 5 cards de estatísticas aparecem com valores
- [ ] 4 cards de ações rápidas funcionam como links
- [ ] Saudação mostra o nome do usuário logado

#### Filtro de Busca (lista_tarefas):
- [ ] Campo de busca aparece no topo dos filtros
- [ ] Digitar filtra automaticamente após 400ms
- [ ] Botão ✕ limpa o campo e refiltra
- [ ] Badge "Busca: ..." aparece nos filtros ativos
- [ ] Busca funciona em tarefas sem comentário (sem erro)
- [ ] Busca persiste ao trocar de página
- [ ] Busca persiste ao mudar itens por página

#### Interface Geral:
- [ ] Navbar com fundo adaptado ao tema
- [ ] Cards com bordas e sombras corretas
- [ ] Tabelas com hover funcionando
- [ ] Formulários com inputs estilizados
- [ ] Botões com cores corretas
- [ ] Alertas flash estilizados

---

## 🐛 Troubleshooting

### Problema: Tema não persiste ao recarregar

**Causa:** `localStorage` bloqueado ou script não carregado.

**Solução:**
- Verifique se o `base.html` foi atualizado
- Abra o DevTools → Application → Local Storage e confirme a chave `ct-theme`

### Problema: Filtro de busca não filtra tarefas sem comentário

**Causa:** Versão antiga do `app.py` sem `coalesce`.

**Solução:**
Certifique-se que o `app.py` da V4 está sendo usado. O trecho correto é:
```python
from sqlalchemy import func
query = query.filter(
    db.or_(
        Tarefa.tarefa.ilike(termo),
        func.coalesce(Tarefa.comentario, '').ilike(termo)
    )
)
```

### Problema: Fonts não carregam (Syne / DM Sans)

**Causa:** Sem acesso à internet ou CDN bloqueado.

**Solução:**
O sistema usa fallback automático para fontes do sistema. Nenhuma ação necessária — a interface funciona sem as fontes do Google Fonts.

### Problema: Botão de tema não aparece no login

**Causa:** `login.html` não foi substituído (não estende `base.html`).

**Solução:**
Substitua o `login.html` pelo arquivo da V4 (contém o toggle próprio).

### Problema: Dashboard mostra "—" nos stats

**Causa:** As requisições fetch para carregar stats falharam.

**Solução:**
- Verifique se o servidor está rodando
- Os stats são carregados via JavaScript — se o JS estiver bloqueado, os valores não aparecem
- Não afeta o funcionamento do sistema

### Problema: 500 Internal Server Error

**Solução:**
1. Verifique logs no terminal
2. Confirme que `app.py` foi substituído
3. Confirme que a migração V3 foi executada (se vindo da V2)
4. Reinicie o servidor

---

## 📊 Comparativo V3 vs V4

| Funcionalidade | V3 | V4 |
|----------------|----|----|
| Tema | ✅ Light fixo | ✅ Dark/Light com toggle |
| Tipografia | Bootstrap padrão | ✅ Syne + DM Sans |
| Dashboard | Cards simples | ✅ Stats dinâmicas + ações rápidas |
| Login | Glassmorphism | ✅ Card limpo com ícones |
| Filtro por texto | ❌ Não | ✅ Busca em Tarefa + Comentário |
| Busca com paginação | ❌ Não | ✅ Backend (todas as páginas) |
| Toggle dark/light | ❌ Não | ✅ Salvo em localStorage |
| Variáveis CSS de tema | ❌ Não | ✅ Sistema completo |
| Banco de dados | — | ✅ Sem alterações necessárias |

---

## 🎊 Novos Recursos Disponíveis

### Para Usuários:

1. **Alterne o tema a qualquer momento**
   - Clique no botão ☀️/🌙 no canto superior esquerdo
   - Sua preferência é salva automaticamente

2. **Busque tarefas por texto**
   - Digite qualquer palavra no campo de busca
   - Filtra em nome da tarefa e comentário simultaneamente
   - Funciona junto com os outros filtros

3. **Dashboard com visão geral**
   - Veja totais de tarefas por status em cards coloridos
   - Acesso rápido às principais seções

### Para Desenvolvedores:

1. **Sistema de temas via CSS variables**
   - Adicione novos componentes usando `var(--accent)`, `var(--bg-card)`, etc.
   - Automaticamente suporta dark e light mode

2. **Filtro de busca extensível**
   - Adicione mais campos ao `ilike` conforme necessário
   - Padrão `coalesce` previne erros com campos nulos

---

## 📞 Suporte

Em caso de problemas:

1. Verifique o checklist de atualização
2. Consulte a seção Troubleshooting
3. Revise os logs do servidor
4. Confirme que todos os 10 arquivos foram substituídos

---

**Versão:** 4.0
**Data:** Março 2026
**Mantido por:** Mauricio

---
linha 447 no base.html
<!-- Adicionar APÓS o link de Categorias no base.html -->
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('calendario') }}">
                            <i class="bi bi-calendar3"></i> Calendário
                        </a>
                    </li>

**🎉 Aproveite o novo visual da V4! 🎉**
