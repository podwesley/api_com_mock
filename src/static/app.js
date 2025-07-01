// Estado global da aplicação
let currentToken = '';
let requestHistory = [];

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    // Configurar eventos
    setupEventListeners();
    
    // Carregar token salvo
    const savedToken = localStorage.getItem('apiToken');
    if (savedToken) {
        currentToken = savedToken;
        document.getElementById('bearerToken').value = savedToken;
        updateTokenDisplay();
    }
    
    // Carregar histórico
    loadHistory();
});

function setupEventListeners() {
    // Auth type change
    document.getElementById('authType').addEventListener('change', function() {
        toggleAuthFields();
    });
    
    // Enter key para enviar requisição
    document.getElementById('urlInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendRequest();
        }
    });
    
    // Auto-format JSON
    document.getElementById('jsonBody').addEventListener('blur', function() {
        formatJSON();
    });
}

function toggleAuthFields() {
    const authType = document.getElementById('authType').value;
    const bearerDiv = document.getElementById('bearerTokenDiv');
    const basicDiv = document.getElementById('basicAuthDiv');
    
    if (authType === 'bearer') {
        bearerDiv.style.display = 'block';
        basicDiv.style.display = 'none';
    } else if (authType === 'basic') {
        bearerDiv.style.display = 'none';
        basicDiv.style.display = 'block';
    } else {
        bearerDiv.style.display = 'none';
        basicDiv.style.display = 'none';
    }
}

async function login() {
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    
    if (!username || !password) {
        alert('Por favor, preencha username e password');
        return;
    }
    
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentToken = data.token;
            document.getElementById('bearerToken').value = currentToken;
            localStorage.setItem('apiToken', currentToken);
            updateTokenDisplay();
            
            // Mostrar resposta
            displayResponse(response, data);
            
            alert('Login realizado com sucesso!');
        } else {
            alert('Erro no login: ' + data.error);
            displayResponse(response, data);
        }
    } catch (error) {
        alert('Erro de conexão: ' + error.message);
        console.error('Login error:', error);
    }
}

function updateTokenDisplay() {
    const tokenDisplay = document.getElementById('tokenDisplay');
    if (currentToken) {
        tokenDisplay.style.display = 'block';
        tokenDisplay.textContent = `Token: ${currentToken.substring(0, 20)}...`;
    } else {
        tokenDisplay.style.display = 'none';
    }
}

function loadRequest(method, url, name) {
    // Remover classe active de todos os itens
    document.querySelectorAll('.collection-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Adicionar classe active ao item clicado
    event.target.closest('.collection-item').classList.add('active');
    
    // Configurar método e URL
    document.getElementById('methodSelect').value = method;
    document.getElementById('urlInput').value = `http://localhost:5001${url}`;
    
    // Configurar body baseado no método e endpoint
    const jsonBody = document.getElementById('jsonBody');
    
    if (method === 'POST' || method === 'PUT') {
        if (url.includes('/pessoas')) {
            jsonBody.value = JSON.stringify({
                "nome": "João Silva",
                "email": "joao.silva@email.com",
                "telefone": "(11) 99999-9999",
                "cpf": "123.456.789-00",
                "data_nascimento": "1990-01-01",
                "profissao": "Desenvolvedor",
                "salario": 5000.00,
                "ativo": true
            }, null, 2);
        } else if (url.includes('/enderecos')) {
            jsonBody.value = JSON.stringify({
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
            }, null, 2);
        } else if (url.includes('/auth/login')) {
            jsonBody.value = JSON.stringify({
                "username": "admin",
                "password": "123456"
            }, null, 2);
        }
    } else {
        jsonBody.value = '';
    }
    
    // Configurar parâmetros baseado no endpoint
    clearParams();
    if (method === 'GET' && url.includes('/pessoas') && !url.includes('/stats')) {
        addParamRow('page', '1');
        addParamRow('per_page', '10');
        if (url === '/api/pessoas') {
            addParamRow('nome', '');
            addParamRow('ativo', 'true');
        }
    } else if (method === 'GET' && url.includes('/enderecos')) {
        addParamRow('page', '1');
        addParamRow('per_page', '10');
        addParamRow('cidade', '');
        addParamRow('estado', '');
    }
}

function clearParams() {
    document.getElementById('paramsContainer').innerHTML = '';
}

function addParamRow(key = '', value = '') {
    const container = document.getElementById('paramsContainer');
    const row = document.createElement('div');
    row.className = 'param-row';
    row.innerHTML = `
        <input type="text" class="param-input" placeholder="Key" value="${key}">
        <input type="text" class="param-input" placeholder="Value" value="${value}">
        <button class="remove-btn" onclick="removeParamRow(this)">
            <i class="fas fa-trash"></i>
        </button>
    `;
    container.appendChild(row);
}

function removeParamRow(button) {
    button.parentElement.remove();
}

function addHeaderRow(key = '', value = '') {
    const container = document.getElementById('headersContainer');
    const row = document.createElement('div');
    row.className = 'header-row';
    row.innerHTML = `
        <input type="text" class="header-input" placeholder="Key" value="${key}">
        <input type="text" class="header-input" placeholder="Value" value="${value}">
        <button class="remove-btn" onclick="removeHeaderRow(this)">
            <i class="fas fa-trash"></i>
        </button>
    `;
    container.appendChild(row);
}

function removeHeaderRow(button) {
    button.parentElement.remove();
}

function formatJSON() {
    const textarea = document.getElementById('jsonBody');
    try {
        if (textarea.value.trim()) {
            const parsed = JSON.parse(textarea.value);
            textarea.value = JSON.stringify(parsed, null, 2);
        }
    } catch (e) {
        // Ignore formatting errors
    }
}

function buildQueryString() {
    const params = [];
    const paramRows = document.querySelectorAll('#paramsContainer .param-row');
    
    paramRows.forEach(row => {
        const inputs = row.querySelectorAll('.param-input');
        const key = inputs[0].value.trim();
        const value = inputs[1].value.trim();
        
        if (key && value) {
            params.push(`${encodeURIComponent(key)}=${encodeURIComponent(value)}`);
        }
    });
    
    return params.length > 0 ? '?' + params.join('&') : '';
}

function buildHeaders() {
    const headers = {};
    
    // Headers customizados
    const headerRows = document.querySelectorAll('#headersContainer .header-row');
    headerRows.forEach(row => {
        const inputs = row.querySelectorAll('.header-input');
        const key = inputs[0].value.trim();
        const value = inputs[1].value.trim();
        
        if (key && value) {
            headers[key] = value;
        }
    });
    
    // Autenticação
    const authType = document.getElementById('authType').value;
    if (authType === 'bearer') {
        const token = document.getElementById('bearerToken').value.trim();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
    } else if (authType === 'basic') {
        const username = document.getElementById('basicUsername').value.trim();
        const password = document.getElementById('basicPassword').value.trim();
        if (username && password) {
            const credentials = btoa(`${username}:${password}`);
            headers['Authorization'] = `Basic ${credentials}`;
        }
    }
    
    return headers;
}

async function sendRequest() {
    const method = document.getElementById('methodSelect').value;
    const baseUrl = document.getElementById('urlInput').value;
    const queryString = buildQueryString();
    const url = baseUrl + queryString;
    const headers = buildHeaders();
    const body = document.getElementById('jsonBody').value.trim();
    
    // Mostrar loading
    const sendBtn = document.querySelector('.send-btn');
    const originalText = sendBtn.innerHTML;
    sendBtn.innerHTML = '<span class="spinner"></span> Sending...';
    sendBtn.classList.add('loading');
    
    try {
        const requestOptions = {
            method: method,
            headers: headers
        };
        
        // Adicionar body se necessário
        if ((method === 'POST' || method === 'PUT' || method === 'PATCH') && body) {
            requestOptions.body = body;
        }
        
        console.log('Sending request:', { url, requestOptions });
        
        const startTime = Date.now();
        const response = await fetch(url, requestOptions);
        const endTime = Date.now();
        const responseTime = endTime - startTime;
        
        let responseData;
        const contentType = response.headers.get('content-type');
        
        if (contentType && contentType.includes('application/json')) {
            responseData = await response.json();
        } else {
            responseData = await response.text();
        }
        
        // Salvar no histórico
        saveToHistory(method, url, response.status, responseTime);
        
        // Mostrar resposta
        displayResponse(response, responseData, responseTime);
        
    } catch (error) {
        console.error('Request error:', error);
        displayError(error);
    } finally {
        // Remover loading
        sendBtn.innerHTML = originalText;
        sendBtn.classList.remove('loading');
    }
}

function displayResponse(response, data, responseTime = 0) {
    // Status
    const statusElement = document.getElementById('responseStatus');
    const statusClass = `status-${Math.floor(response.status / 100) * 100}`;
    statusElement.innerHTML = `
        <span class="status-badge ${statusClass}">
            ${response.status} ${response.statusText}
        </span>
        <small class="text-muted ms-2">${responseTime}ms</small>
    `;
    
    // Body
    const responseJson = document.getElementById('responseJson');
    if (typeof data === 'object') {
        responseJson.textContent = JSON.stringify(data, null, 2);
    } else {
        responseJson.textContent = data;
    }
    
    // Headers
    const responseHeaders = document.getElementById('responseHeaders');
    const headersObj = {};
    response.headers.forEach((value, key) => {
        headersObj[key] = value;
    });
    responseHeaders.textContent = JSON.stringify(headersObj, null, 2);
    
    // Syntax highlighting
    Prism.highlightElement(responseJson);
    Prism.highlightElement(responseHeaders);
}

function displayError(error) {
    const statusElement = document.getElementById('responseStatus');
    statusElement.innerHTML = `
        <span class="status-badge status-500">
            Error
        </span>
    `;
    
    const responseJson = document.getElementById('responseJson');
    responseJson.textContent = `Erro de conexão: ${error.message}`;
    
    const responseHeaders = document.getElementById('responseHeaders');
    responseHeaders.textContent = 'Nenhum header disponível';
}

function saveToHistory(method, url, status, responseTime) {
    const historyItem = {
        method,
        url,
        status,
        responseTime,
        timestamp: new Date().toISOString()
    };
    
    requestHistory.unshift(historyItem);
    
    // Manter apenas os últimos 50 itens
    if (requestHistory.length > 50) {
        requestHistory = requestHistory.slice(0, 50);
    }
    
    localStorage.setItem('requestHistory', JSON.stringify(requestHistory));
}

function loadHistory() {
    const saved = localStorage.getItem('requestHistory');
    if (saved) {
        requestHistory = JSON.parse(saved);
    }
}

// Exemplos de requisições pré-configuradas
const requestExamples = {
    'GET /api/pessoas': {
        method: 'GET',
        url: 'http://localhost:5000/api/pessoas',
        params: [
            { key: 'page', value: '1' },
            { key: 'per_page', value: '10' },
            { key: 'nome', value: '' },
            { key: 'ativo', value: 'true' }
        ]
    },
    'POST /api/pessoas': {
        method: 'POST',
        url: 'http://localhost:5000/api/pessoas',
        body: {
            "nome": "João Silva",
            "email": "joao.silva@email.com",
            "telefone": "(11) 99999-9999",
            "cpf": "123.456.789-00",
            "data_nascimento": "1990-01-01",
            "profissao": "Desenvolvedor",
            "salario": 5000.00,
            "ativo": true
        }
    }
};

// Função para testar erros específicos
function testError(errorType) {
    switch (errorType) {
        case '404':
            loadRequest('GET', '/api/pessoas/999', 'Teste 404');
            break;
        case '500':
            // A API tem 3-5% de chance de retornar erro 500
            loadRequest('GET', '/api/pessoas', 'Teste 500 (aleatório)');
            break;
        case '401':
            // Limpar token e tentar acessar endpoint protegido
            document.getElementById('bearerToken').value = '';
            loadRequest('GET', '/api/pessoas', 'Teste 401');
            break;
    }
}

// Função para popular dados de teste
function populateTestData() {
    const testPerson = {
        "nome": "Maria Teste",
        "email": "maria.teste@email.com",
        "telefone": "(11) 88888-8888",
        "cpf": "987.654.321-00",
        "data_nascimento": "1985-05-15",
        "profissao": "Designer",
        "salario": 4500.00,
        "ativo": true
    };
    
    document.getElementById('jsonBody').value = JSON.stringify(testPerson, null, 2);
}

// Atalhos de teclado
document.addEventListener('keydown', function(e) {
    // Ctrl+Enter para enviar requisição
    if (e.ctrlKey && e.key === 'Enter') {
        e.preventDefault();
        sendRequest();
    }
    
    // Ctrl+L para focar na URL
    if (e.ctrlKey && e.key === 'l') {
        e.preventDefault();
        document.getElementById('urlInput').focus();
        document.getElementById('urlInput').select();
    }
});

// Auto-save do token
document.getElementById('bearerToken').addEventListener('input', function() {
    currentToken = this.value;
    if (currentToken) {
        localStorage.setItem('apiToken', currentToken);
    }
    updateTokenDisplay();
});

console.log('API Tester carregado com sucesso!');
console.log('Atalhos disponíveis:');
console.log('- Ctrl+Enter: Enviar requisição');
console.log('- Ctrl+L: Focar na URL');
console.log('- Enter na URL: Enviar requisição');

