# API Mockada - Sistema de Pessoas e Endereços

## 📋 Descrição

API REST mockada completa com endpoints para gerenciamento de pessoas e endereços, incluindo autenticação, simulação de erros e interface web similar ao Postman para testes.


## 🚀 Funcionalidades

### ✅ **API Backend (Flask)**
- **Autenticação JWT** com Bearer Token
- **CRUD completo** para Pessoas e Endereços
- **30+ registros mockados** para testes
- **Simulação de erros** (404, 500, 401)
- **Query parameters** e filtros
- **Headers customizados**
- **Paginação** automática
- **CORS** habilitado

### ✅ **Interface Web (Postman-like)**
- **Design moderno** inspirado no Postman
- **Editor JSON** com syntax highlighting
- **Visualizador de resposta** com tabs
- **Gerenciamento de headers** e parâmetros
- **Autenticação integrada**
- **Histórico de requisições**
- **Responsivo** para desktop e mobile

## 🛠️ Tecnologias

- **Backend**: Python 3.11, Flask, SQLAlchemy, SQLite
- **Frontend**: HTML5, CSS3, JavaScript ES6, Bootstrap 5
- **Autenticação**: JWT (JSON Web Tokens)
- **Banco**: SQLite (em memória para testes)

## 📚 Endpoints da API

### 🔐 **Autenticação**

#### POST `/api/auth/login`
Realiza login e retorna token JWT.

**Body:**
```json
{
  "username": "admin",
  "password": "123456"
}
```

**Response (200):**
```json
{
  "message": "Login realizado com sucesso",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "expires_at": "2025-07-01T21:50:09.180860",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@api.com",
    "ativo": true
  }
}
```

#### POST `/api/auth/logout`
Invalida o token atual (requer autenticação).

#### GET `/api/auth/me`
Retorna informações do usuário logado (requer autenticação).

### 👥 **Pessoas**

#### GET `/api/pessoas`
Lista pessoas com paginação e filtros.

**Query Parameters:**
- `page` (int): Página (padrão: 1)
- `per_page` (int): Itens por página (padrão: 10, máx: 100)
- `nome` (string): Filtro por nome
- `ativo` (boolean): Filtro por status ativo

**Headers necessários:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "pagination": {
    "page": 1,
    "pages": 3,
    "per_page": 10,
    "total": 22,
    "has_next": true,
    "has_prev": false
  },
  "pessoas": [
    {
      "id": 1,
      "nome": "Ana Silva",
      "email": "ana.silva@email.com",
      "telefone": "(11) 96808-2668",
      "cpf": "863.249.580-32",
      "data_nascimento": "1974-03-12",
      "profissao": "Administrador",
      "salario": 14635.35,
      "ativo": true,
      "created_at": "2025-06-30T21:40:17.750106",
      "updated_at": "2025-06-30T21:40:17.750106",
      "enderecos": []
    }
  ]
}
```

#### GET `/api/pessoas/{id}`
Obtém uma pessoa específica.

**Response (200):** Objeto pessoa
**Response (404):** `{"error": "Pessoa não encontrada"}`

#### POST `/api/pessoas`
Cria uma nova pessoa.

**Body:**
```json
{
  "nome": "João Silva",
  "email": "joao.silva@email.com",
  "telefone": "(11) 99999-9999",
  "cpf": "123.456.789-00",
  "data_nascimento": "1990-01-01",
  "profissao": "Desenvolvedor",
  "salario": 5000.00,
  "ativo": true
}
```

#### PUT `/api/pessoas/{id}`
Atualiza uma pessoa existente.

#### DELETE `/api/pessoas/{id}`
Remove uma pessoa.

#### GET `/api/pessoas/stats`
Retorna estatísticas das pessoas.

### 🏠 **Endereços**

#### GET `/api/enderecos`
Lista endereços com paginação e filtros.

**Query Parameters:**
- `page`, `per_page`: Paginação
- `cidade`, `estado`: Filtros por localização
- `tipo`: Filtro por tipo (residencial, comercial, etc.)

#### GET `/api/enderecos/{id}`
Obtém um endereço específico.

#### POST `/api/enderecos`
Cria um novo endereço.

**Body:**
```json
{
  "pessoa_id": 1,
  "tipo": "residencial",
  "logradouro": "Rua das Flores",
  "numero": "123",
  "complemento": "Apto 45",
  "bairro": "Centro",
  "cidade": "São Paulo",
  "estado": "SP",
  "cep": "01234-567",
  "pais": "Brasil",
  "principal": true,
  "ativo": true
}
```

#### PUT `/api/enderecos/{id}`
Atualiza um endereço existente.

#### DELETE `/api/enderecos/{id}`
Remove um endereço.

#### GET `/api/pessoas/{id}/enderecos`
Lista endereços de uma pessoa específica.

## 🔧 Como Usar

### Docker. configure a porta no compose - IMPORTANTEEEEE 

- **docker build -t api-mockada .** 
- **docker-compose up -d**
- **docker-compose logs api** - Dar uma bizulhada nos logs. 

### 3. **Fazer Login**
- **Username:** `admin`
- **Password:** `123456`




### 4. **Testar Endpoints**
Use a interface web ou ferramentas como curl/Postman:

```bash
# Login
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "123456"}'

# Listar pessoas (com token)
curl -X GET "http://localhost:5001/api/pessoas?page=1&per_page=5" \
  -H "Authorization: Bearer <seu_token>"
```

## 🎯 Recursos para Treinamento

### **Headers HTTP**
- `Authorization`: Bearer token para autenticação
- `Content-Type`: application/json para requisições POST/PUT
- `Accept`: application/json para respostas
- Headers customizados podem ser adicionados via interface

### **Query Parameters**
- Paginação: `page`, `per_page`
- Filtros: `nome`, `ativo`, `cidade`, `estado`
- Ordenação: `sort_by`, `order`

### **Status Codes**
- `200 OK`: Sucesso
- `201 Created`: Recurso criado
- `400 Bad Request`: Dados inválidos
- `401 Unauthorized`: Token inválido/ausente
- `404 Not Found`: Recurso não encontrado
- `500 Internal Server Error`: Erro do servidor (3-5% das requisições)

### **Simulação de Erros**
- **404**: Acesse `/api/pessoas/999` (ID inexistente)
- **401**: Remova o token de Authorization
- **500**: A API simula erros aleatórios em 3-5% das requisições
- **400**: Envie dados inválidos no body

## 📱 Interface Web

A interface web oferece:

### **Sidebar de Collections**
- Organização por categorias (Autenticação, Pessoas, Endereços)
- Requests pré-configurados
- Badges coloridos por método HTTP

### **Editor de Requisições**
- Seletor de método HTTP
- Campo de URL editável
- Abas para Params, Authorization, Headers, Body
- Editor JSON com syntax highlighting

### **Visualizador de Resposta**
- Status code com cores
- Tempo de resposta
- Abas para Body e Headers
- JSON formatado automaticamente

### **Recursos Avançados**
- Auto-save do token JWT
- Histórico de requisições
- Atalhos de teclado (Ctrl+Enter para enviar)
- Design responsivo

## 🔍 Dados Mockados

A API contém:
- **30 pessoas** com dados realistas
- **60+ endereços** distribuídos entre as pessoas
- **Relacionamentos** pessoa-endereço
- **Dados brasileiros** (CPF, telefones, CEPs)
- **Profissões variadas** e salários
- **Endereços** de diferentes tipos e cidades

## 🛡️ Segurança

- **JWT Tokens** com expiração de 24 horas
- **Middleware de autenticação** em endpoints protegidos
- **Validação de dados** de entrada
- **CORS** configurado para desenvolvimento
- **Rate limiting** simulado

## 🎨 Design

Interface inspirada no Postman com:
- **Tema escuro** moderno
- **Gradientes** e animações suaves
- **Ícones FontAwesome**
- **Bootstrap 5** para responsividade
- **Syntax highlighting** com Prism.js

## 📝 Notas Técnicas

- **Banco SQLite** em memória (dados resetam a cada reinício)
- **CORS** habilitado para todas as origens
- **Debug mode** ativo para desenvolvimento
- **Logs** detalhados no console
- **Estrutura modular** com blueprints Flask

---

**Desenvolvido para treinamento em APIs REST** 🚀

