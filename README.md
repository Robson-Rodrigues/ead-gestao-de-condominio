# 🏠 Sistema de Gestão de Condomínio

## 📋 Descrição do Projeto

Sistema web para gestão de condomínio desenvolvido com Python Flask, HTML, CSS e JavaScript.

## 🎯 Funcionalidades

### ✅ AC1 - Implementadas
- **Cadastro de Unidades**: Registro de apartamento
- **Cadastro de Moradores**: Registro de proprietários e locatários 
- **Visualização de Dados**: Listagem organizada de unidades e moradores
- **Dashboard**: Estatísticas gerais do condomínio
- **Interface Responsiva**: Design moderno e adaptável

### ✅ AC2 - Implementadas
- **Sistema de Login**: Autenticação de usuários (Admin e Morador)
- **Perfil de Usuário**: Visualização de dados pessoais
- **Cadastro de Visitantes**: Controle de entrada e saída
- **Sistema de Multas**: Gestão de multas e cobranças
- **Controle de Acesso**: Diferentes permissões por tipo de usuário

### ✅ AC3 - Implementadas
- **Sistema de Reservas**: Moradores solicitam reservas de áreas comuns e administradores aprovam/rejeitam
- **Gestão de Funcionários**: Cadastro completo de colaboradores, inclusive ativação/inativação
- **Sistema de Notificações**: Envio de avisos gerais ou específicos com controle de leitura
- **Chat Interno**: Conversa em tempo real entre administradores e moradores com alerta de não lidas

### 📊 Campos de Unidade
- Número da unidade
- Bloco
- Tipo (Apartamento, Casa, Loja, etc.)
- Número de vagas de garagem

### 👥 Campos de Morador
- Nome completo
- CPF (com validação)
- Telefone (com máscara)
- E-mail (com validação)
- Tipo (Proprietário, Locatário, Síndico)
- Vinculação com unidade

## 🛠️ Tecnologias Utilizadas

### Backend
- **Python 3.8+**
- **Flask 2.3.3** - Framework web
- **Flask-SQLAlchemy 3.0.5** - ORM para banco de dados
- **SQLite** - Banco de dados (pode ser migrado para PostgreSQL)

### Frontend
- **HTML5** - Estrutura
- **CSS3** - Estilos customizados
- **JavaScript ES6** - Interatividade
- **Bootstrap 5.3.0** - Framework CSS
- **Font Awesome 6.4.0** - Ícones

## 🚀 Instalação e Execução

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Passo a Passo

1. **Clone ou baixe o projeto**
   ```bash
   # Se usando Git
   git clone [URL_DO_REPOSITORIO]
   cd sistema-gestao-de-Condomínio
   ```

2. **Crie um ambiente virtual (recomendado)**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Execute a aplicação**
   ```bash
   python app.py
   ```

5. **Acesse no navegador**
   ```
   http://localhost:5000
   ```

### 👤 Usuários de Exemplo
Para testar o sistema, você pode criar usuários manualmente através da interface ou usar as credenciais padrão:
- **Admin**: `admin` / `admin123`
- **Morador**: `joao.silva` / `123456`
- **Morador**: `maria.santos` / `123456`

## 📁 Estrutura do Projeto

```
sistema-gestao-de-Condomínio/
│
├── app.py                    # Aplicação principal Flask
├── requirements.txt          # Dependências Python
├── README.md                 # Documentação
├── condominio.db             # Banco de dados SQLite (criado automaticamente)
│
├── templates/               # Templates HTML
│   ├── base.html            # Template base
│   ├── index.html           # Página inicial
│   ├── login.html           # Página de login
│   ├── perfil.html          # Página de perfil
│   ├── cadastrar_unidade.html
│   ├── cadastrar_morador.html
│   ├── cadastrar_visitante.html
│   ├── cadastrar_multa.html
│   ├── cadastrar_reserva.html
│   ├── reservas.html
│   ├── unidades.html        # Lista de unidades
│   ├── moradores.html       # Lista de moradores
│   ├── visitantes.html      # Lista de visitantes
│   ├── multas.html          # Lista de multas
│   ├── funcionarios.html
│   ├── cadastrar_funcionario.html
│   ├── editar_funcionario.html
│   ├── notificacoes.html
│   ├── cadastrar_notificacao.html
│   └── chat.html
│
└── static/                 # Arquivos estáticos
    ├── css/
    │   └── style.css       # Estilos customizados
    └── js/
        └── script.js       # JavaScript customizado
```

## 🎮 Como Usar

### 1. Login (Tela Inicial)
1. Acesse o sistema - será redirecionado automaticamente para o login
2. Faça login com suas credenciais
3. Escolha entre Admin ou Morador

### 2. Dashboard
**Para Administradores:**
- Total de unidades do condomínio
- Total de moradores do condomínio
- Multas pendentes dos moradores
- Reservas pendentes aguardando aprovação
- Funcionários ativos e total de notificações enviadas
- Acesso completo a todas as funcionalidades

**Para Moradores:**
- Moradores na sua unidade
- Visitantes ativos da sua unidade
- Multas em aberto e valor total
- Minhas reservas realizadas
- Notificações recebidas da administração
- Cadastro de visitantes (apenas para sua unidade)
- Visualização das suas multas
- Acesso limitado às funcionalidades

### 3. Gestão de Unidades e Moradores
- **Cadastrar Unidade**: Registre novas unidades
- **Cadastrar Morador**: Vincule moradores às unidades
- **Visualizar Dados**: Consulte listas organizadas

### 4. Controle de Visitantes
- **Admin**: Pode cadastrar visitantes para qualquer unidade
- **Morador**: Pode cadastrar visitantes apenas para sua própria unidade
- **Registrar Saída**: Controle a saída dos visitantes
- **Histórico**: Veja todas as visitas realizadas

### 5. Sistema de Multas
- **Admin**: Pode cadastrar multas e marcar como pagas
- **Morador**: Pode apenas visualizar suas multas (sem opção de pagar)
- **Acompanhar Pagamentos**: Veja status das multas
- **Relatórios**: Consulte valores e pendências

### 6. Sistema de Reservas
- **Morador**: Solicita, acompanha e cancela reservas das áreas comuns do condomínio
- **Admin**: Aprova, rejeita ou cancela reservas; pode cadastrar reservas diretamente
- **Prevenção de Conflitos**: Bloqueio automático de horários sobrepostos para uma mesma área

### 7. Gestão de Funcionários (Admin)
- Cadastro completo com dados pessoais, contato, turno e observações
- Edição de informações, ativação/inativação e exclusão de colaboradores
- Indicadores de funcionários ativos e total geral

### 8. Sistema de Notificações
- Envio de avisos gerais ou direcionados a moradores específicos
- Indicador de notificações não lidas no menu e na listagem
- Marcação automática de leitura ao acessar a página de notificações

### 9. Chat Interno
- Conversas individuais entre administradores e moradores
- Badge no menu com quantidade de mensagens não lidas
- Restrição de permissão: moradores conversam apenas com administradores; administradores com qualquer usuário ativo

## 🔧 Configurações

### Banco de Dados
- O sistema usa SQLite por padrão
- O arquivo `condominio.db` é criado automaticamente
- Para usar PostgreSQL, altere a configuração em `app.py`:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://usuario:senha@localhost/condominio'
```

### Porta e Host
- Padrão: `http://localhost:5000`
- Para alterar, edite o final do arquivo `app.py`:

```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Porta 8080
```
## 🐛 Resolução de Problemas

### Erro de Dependências
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Erro de Banco de Dados
- Delete o arquivo `condominio.db` e execute novamente
- O banco será recriado automaticamente

### Erro de Porta em Uso
```bash
# Encontre o processo usando a porta 5000
netstat -ano | findstr :5000
# Finalize o processo ou mude a porta
```
