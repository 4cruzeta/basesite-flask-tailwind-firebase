# Quadro de Missões - EdCat

Este documento é a nossa fonte única de verdade para as próximas missões de desenvolvimento. Ele registra as funcionalidades planejadas, as decisões de arquitetura e as tarefas a serem executadas.

---

## Missão 1: Centro de Comando de Usuários (Admin Dashboard)

**Status:** Planejamento Concluído

**Objetivo:** Transformar a página `admin_home` em um painel funcional para gerenciar perfis de usuários, implementando um sistema de roles e status.

### Tarefa 1.1: Fundação de Dados (Firestore)
- [ ] **Criar Coleção `users`:** No Firestore, estabelecer uma coleção para armazenar perfis de usuários.
- [ ] **Estrutura do Documento:** Para cada usuário, o documento (usando o `uid` como ID) deve conter:
    - `role` (string: "adm", "user", "viewer")
    - `status` (string: "active", "inactive")
    - `name` (string)
    - `email` (string)
- [ ] **Refatorar Backend:** Modificar o backend para, após a autenticação, buscar o perfil do usuário (roles, status) no Firestore.

### Tarefa 1.2: Interface de Gerenciamento (admin_home.html)
- [ ] **Design Moderno:** Redesenhar a página `admin_home.html` com Tailwind CSS, com um design "tableless" (lista de cards ou tabela estilizada).
- [ ] **Tabela de Usuários:** Exibir os usuários em uma tabela estilizada e responsiva.
- [ ] **Controles Interativos:** Para cada usuário na tabela, implementar:
    - Um **dropdown** para selecionar e alterar a `role`.
    - Um **checkbox** ou **toggle switch** para alterar o `status`.

---

## Missão 2: Sistema de Auditoria de Sessão

**Status:** Planejamento Concluído

**Objetivo:** Rastrear o tempo de uso da aplicação por cada usuário, criando um histórico de sessões.

### Tarefa 2.1: Arquitetura de Logout
- [ ] **Criar Endpoint de Logout:** Desenvolver uma nova rota no Flask (ex: `/session_logout`) que será responsável por registrar o fim de uma sessão.
- [ ] **Modificar Lógica do Cliente:** Atualizar o JavaScript de logout no frontend para que, antes de apagar o cookie `__session`, ele faça uma chamada para o novo endpoint `/session_logout`.

### Tarefa 2.2: Lógica de Histórico (Backend)
- [ ] **Criar Coleção `session_history`:** No Firestore, estabelecer uma nova coleção para armazenar os registros de cada sessão.
- [ ] **Estrutura do Documento:** Cada documento deve conter:
    - `userId` (string)
    - `login_timestamp` (timestamp)
    - `logout_timestamp` (timestamp)
    - `duration_seconds` (number)
- [ ] **Implementar Lógica no Endpoint:** No endpoint `/session_logout`, calcular a duração da sessão e criar um novo documento na coleção `session_history`.

---

## Missão 3: Melhoria da Experiência de Edição (UX)

**Status:** Planejamento Concluído

**Objetivo:** Ao editar um registro de usuário, os campos do formulário devem ser pré-carregados com os dados existentes.

### Tarefa 3.1: Carregamento de Dados no Formulário
- [ ] **Criar Endpoint de Dados do Usuário:** Desenvolver uma rota de API no Flask (ex: `/api/user/<uid>`) que retorna os dados de um usuário específico do Firestore.
- [ ] **Lógica de Fetch no Cliente:** Quando o botão "Editar" é clicado, o JavaScript deve:
    - Chamar o novo endpoint com o `uid` do usuário.
    - Receber os dados do usuário (nome, email, role, status).
    - Popular os campos do formulário de edição com os dados recebidos antes de exibi-lo.

---
