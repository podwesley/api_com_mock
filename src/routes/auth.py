from flask import Blueprint, request, jsonify
from src.database_config import db
from src.models.auth import Usuario, Token
from functools import wraps
import random

auth_bp = Blueprint('auth', __name__)

def token_required(f):
    """Decorator para verificar autenticação"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Verifica se o token está no header Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Token malformado'}), 401
        
        if not token:
            return jsonify({'error': 'Token de acesso necessário'}), 401
        
        # Simula erro 500 ocasionalmente (5% das vezes)
        if random.random() < 0.05:
            return jsonify({'error': 'Erro interno do servidor'}), 500
        
        try:
            # Busca o token no banco
            token_obj = Token.query.filter_by(token=token).first()
            
            if not token_obj or not token_obj.is_valid():
                return jsonify({'error': 'Token inválido ou expirado'}), 401
            
            # Adiciona o usuário atual ao contexto
            current_user = token_obj.usuario
            request.current_user = current_user
            
        except Exception as e:
            return jsonify({'error': 'Token inválido'}), 401
        
        return f(*args, **kwargs)
    
    return decorated

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    """
    Endpoint de login para autenticação de usuários.
    ---
    tags:
      - Autenticação
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
              description: Nome de usuário.
              example: "admin"
            password:
              type: string
              description: Senha do usuário.
              example: "admin"
    responses:
      200:
        description: Login realizado com sucesso.
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Login realizado com sucesso"
            token:
              type: string
              example: "..."
            expires_at:
              type: string
              example: "..."
            user:
              type: object
              properties:
                id:
                  type: integer
                  example: 1
                username:
                  type: string
                  example: "admin"
                email:
                  type: string
                  example: "admin@example.com"
                ativo:
                  type: boolean
                  example: true
      400:
        description: "Username e password são obrigatórios"
      401:
        description: "Credenciais inválidas ou usuário inativo"
      500:
        description: "Erro interno do servidor"
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username e password são obrigatórios'}), 400
        
        username = data.get('username')
        password = data.get('password')
        
        # Busca o usuário
        usuario = Usuario.query.filter_by(username=username).first()
        
        if not usuario or not usuario.check_password(password):
            return jsonify({'error': 'Credenciais inválidas'}), 401
        
        if not usuario.ativo:
            return jsonify({'error': 'Usuário inativo'}), 401
        
        # Cria um novo token
        token = Token.create_token(usuario.id)
        db.session.add(token)
        db.session.commit()
        
        return jsonify({
            'message': 'Login realizado com sucesso',
            'token': token.token,
            'expires_at': token.expires_at.isoformat(),
            'user': usuario.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@auth_bp.route('/auth/logout', methods=['POST'])
@token_required
def logout():
    """
    Endpoint de logout para invalidar o token de acesso.
    ---
    tags:
      - Autenticação
    security:
      - Bearer: []
    responses:
      200:
        description: "Logout realizado com sucesso"
      500:
        description: "Erro interno do servidor"
    """
    try:
        # Pega o token do header
        auth_header = request.headers.get('Authorization')
        token = auth_header.split(" ")[1]
        
        # Desativa o token
        token_obj = Token.query.filter_by(token=token).first()
        if token_obj:
            token_obj.ativo = False
            db.session.commit()
        
        return jsonify({'message': 'Logout realizado com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@auth_bp.route('/auth/me', methods=['GET'])
@token_required
def me():
    """
    Retorna informações do usuário autenticado.
    ---
    tags:
      - Autenticação
    security:
      - Bearer: []
    responses:
      200:
        description: "Informações do usuário"
        schema:
          $ref: '#/definitions/Usuario'
      401:
        description: "Token inválido ou expirado"
      500:
        description: "Erro interno do servidor"
    """
    try:
        return jsonify({
            'user': request.current_user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@auth_bp.route('/auth/refresh', methods=['POST'])
@token_required
def refresh_token():
    """
    Renova o token de acesso.
    ---
    tags:
      - Autenticação
    security:
      - Bearer: []
    responses:
      200:
        description: "Token renovado com sucesso"
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Token renovado com sucesso"
            token:
              type: string
            expires_at:
              type: string
      401:
        description: "Token inválido ou expirado"
      500:
        description: "Erro interno do servidor"
    """
    try:
        # Cria um novo token
        token = Token.create_token(request.current_user.id)
        db.session.add(token)
        
        # Desativa o token atual
        auth_header = request.headers.get('Authorization')
        current_token = auth_header.split(" ")[1]
        token_obj = Token.query.filter_by(token=current_token).first()
        if token_obj:
            token_obj.ativo = False
        
        db.session.commit()
        
        return jsonify({
            'message': 'Token renovado com sucesso',
            'token': token.token,
            'expires_at': token.expires_at.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

