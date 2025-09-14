# 🏠 Sistema de Gestão de Condomínio

## 📋 Descrição do Projeto

Sistema web para gestão de condomínio desenvolvido com Python Flask, HTML, CSS e JavaScript.

## 🎯 Funcionalidades da AC1

### ✅ Implementadas
- **Cadastro de Unidades**: Registro de apartamento
- **Cadastro de Moradores**: Registro de proprietários e locatários 
- **Visualização de Dados**: Listagem organizada de unidades e moradores
- **Dashboard**: Estatísticas gerais do condomínio
- **Interface Responsiva**: Design moderno e adaptável a diferentes dispositivos

### 📊 Campos de Unidade
- Número da unidade
- Bloco
- Tipo (Apartamento, Casa, Loja, etc.)
- Área em m²
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

## 📁 Estrutura do Projeto

```
sistema-gestao-de-Condomínio/
│
├── app.py                 # Aplicação principal Flask
├── requirements.txt       # Dependências Python
├── README.md             # Documentação
├── condominio.db         # Banco de dados SQLite (criado automaticamente)
│
├── templates/            # Templates HTML
│   ├── base.html         # Template base
│   ├── index.html        # Página inicial
│   ├── cadastrar_unidade.html
│   ├── cadastrar_morador.html
│   ├── unidades.html     # Lista de unidades
│   └── moradores.html    # Lista de moradores
│
└── static/              # Arquivos estáticos
    ├── css/
    │   └── style.css    # Estilos customizados
    └── js/
        └── script.js    # JavaScript customizado
```

## 🎮 Como Usar

### 1. Página Inicial
- Visualize estatísticas gerais do condomínio
- Acesse ações disponíveis para cadastros
- Veja listas resumidas de unidades e moradores

### 2. Cadastrar Unidade
1. Clique em "Cadastrar Unidade" no menu
2. Preencha os dados da unidade
3. Clique em "Cadastrar Unidade"
4. A unidade será salva no banco de dados

### 3. Cadastrar Morador
1. Clique em "Cadastrar Morador" no menu
2. Preencha os dados do morador
3. Selecione a unidade onde reside
4. Clique em "Cadastrar Morador"

### 4. Visualizar Dados
- **Unidades**: Veja todas as unidades cadastradas com detalhes
- **Moradores**: Veja todos os moradores em formato de tabela

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