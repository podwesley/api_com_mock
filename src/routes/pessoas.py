from flask import Blueprint, request, jsonify
from src.database_config import db
from src.models.pessoa import Pessoa
from src.routes.auth import token_required
from datetime import datetime
import random

pessoas_bp = Blueprint('pessoas', __name__)

@pessoas_bp.route('/pessoas', methods=['GET'])
@token_required
def listar_pessoas():
    """Lista todas as pessoas com paginação e filtros"""
    try:
        # Simula erro 500 ocasionalmente (3% das vezes)
        if random.random() < 0.03:
            return jsonify({'error': 'Erro interno do servidor'}), 500
        
        # Query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        nome = request.args.get('nome', '')
        email = request.args.get('email', '')
        ativo = request.args.get('ativo', '')
        profissao = request.args.get('profissao', '')
        
        # Limita per_page para evitar sobrecarga
        per_page = min(per_page, 100)
        
        # Query base
        query = Pessoa.query
        
        # Filtros
        if nome:
            query = query.filter(Pessoa.nome.ilike(f'%{nome}%'))
        if email:
            query = query.filter(Pessoa.email.ilike(f'%{email}%'))
        if ativo:
            ativo_bool = ativo.lower() in ['true', '1', 'sim', 'yes']
            query = query.filter(Pessoa.ativo == ativo_bool)
        if profissao:
            query = query.filter(Pessoa.profissao.ilike(f'%{profissao}%'))
        
        # Paginação
        pessoas_paginated = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'pessoas': [pessoa.to_dict_simple() for pessoa in pessoas_paginated.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pessoas_paginated.total,
                'pages': pessoas_paginated.pages,
                'has_next': pessoas_paginated.has_next,
                'has_prev': pessoas_paginated.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@pessoas_bp.route('/pessoas/<int:pessoa_id>', methods=['GET'])
@token_required
def obter_pessoa(pessoa_id):
    """Obtém uma pessoa específica"""
    try:
        # Simula erro 404 para IDs específicos
        if pessoa_id in [999, 1000, 9999]:
            return jsonify({'error': 'Pessoa não encontrada'}), 404
        
        # Simula erro 500 ocasionalmente
        if random.random() < 0.03:
            return jsonify({'error': 'Erro interno do servidor'}), 500
        
        pessoa = Pessoa.query.get(pessoa_id)
        
        if not pessoa:
            return jsonify({'error': 'Pessoa não encontrada'}), 404
        
        return jsonify(pessoa.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@pessoas_bp.route('/pessoas', methods=['POST'])
@token_required
def criar_pessoa():
    """Cria uma nova pessoa"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados JSON são obrigatórios'}), 400
        
        # Validações obrigatórias
        required_fields = ['nome', 'email', 'cpf']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        # Verifica se email já existe
        if Pessoa.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email já cadastrado'}), 409
        
        # Verifica se CPF já existe
        if Pessoa.query.filter_by(cpf=data['cpf']).first():
            return jsonify({'error': 'CPF já cadastrado'}), 409
        
        # Cria nova pessoa
        pessoa = Pessoa(
            nome=data['nome'],
            email=data['email'],
            telefone=data.get('telefone'),
            cpf=data['cpf'],
            data_nascimento=datetime.strptime(data['data_nascimento'], '%Y-%m-%d').date() if data.get('data_nascimento') else None,
            profissao=data.get('profissao'),
            salario=data.get('salario'),
            ativo=data.get('ativo', True)
        )
        
        db.session.add(pessoa)
        db.session.commit()
        
        return jsonify({
            'message': 'Pessoa criada com sucesso',
            'pessoa': pessoa.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({'error': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@pessoas_bp.route('/pessoas/<int:pessoa_id>', methods=['PUT'])
@token_required
def atualizar_pessoa(pessoa_id):
    """Atualiza uma pessoa existente"""
    try:
        pessoa = Pessoa.query.get(pessoa_id)
        
        if not pessoa:
            return jsonify({'error': 'Pessoa não encontrada'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados JSON são obrigatórios'}), 400
        
        # Verifica se email já existe (exceto para a própria pessoa)
        if data.get('email') and data['email'] != pessoa.email:
            if Pessoa.query.filter_by(email=data['email']).first():
                return jsonify({'error': 'Email já cadastrado'}), 409
        
        # Verifica se CPF já existe (exceto para a própria pessoa)
        if data.get('cpf') and data['cpf'] != pessoa.cpf:
            if Pessoa.query.filter_by(cpf=data['cpf']).first():
                return jsonify({'error': 'CPF já cadastrado'}), 409
        
        # Atualiza campos
        if 'nome' in data:
            pessoa.nome = data['nome']
        if 'email' in data:
            pessoa.email = data['email']
        if 'telefone' in data:
            pessoa.telefone = data['telefone']
        if 'cpf' in data:
            pessoa.cpf = data['cpf']
        if 'data_nascimento' in data:
            pessoa.data_nascimento = datetime.strptime(data['data_nascimento'], '%Y-%m-%d').date() if data['data_nascimento'] else None
        if 'profissao' in data:
            pessoa.profissao = data['profissao']
        if 'salario' in data:
            pessoa.salario = data['salario']
        if 'ativo' in data:
            pessoa.ativo = data['ativo']
        
        pessoa.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Pessoa atualizada com sucesso',
            'pessoa': pessoa.to_dict()
        }), 200
        
    except ValueError as e:
        return jsonify({'error': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@pessoas_bp.route('/pessoas/<int:pessoa_id>', methods=['PATCH'])
@token_required
def atualizar_pessoa_parcial(pessoa_id):
    """Atualiza parcialmente uma pessoa existente"""
    # Reutiliza a lógica do PUT
    return atualizar_pessoa(pessoa_id)

@pessoas_bp.route('/pessoas/<int:pessoa_id>', methods=['DELETE'])
@token_required
def deletar_pessoa(pessoa_id):
    """Deleta uma pessoa"""
    try:
        pessoa = Pessoa.query.get(pessoa_id)
        
        if not pessoa:
            return jsonify({'error': 'Pessoa não encontrada'}), 404
        
        # Simula erro 500 ocasionalmente
        if random.random() < 0.02:
            return jsonify({'error': 'Erro interno do servidor'}), 500
        
        db.session.delete(pessoa)
        db.session.commit()
        
        return jsonify({'message': 'Pessoa deletada com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@pessoas_bp.route('/pessoas/stats', methods=['GET'])
@token_required
def estatisticas_pessoas():
    """Retorna estatísticas das pessoas"""
    try:
        total = Pessoa.query.count()
        ativas = Pessoa.query.filter_by(ativo=True).count()
        inativas = total - ativas
        
        # Profissões mais comuns
        profissoes = db.session.query(
            Pessoa.profissao, 
            db.func.count(Pessoa.profissao).label('count')
        ).filter(
            Pessoa.profissao.isnot(None)
        ).group_by(
            Pessoa.profissao
        ).order_by(
            db.func.count(Pessoa.profissao).desc()
        ).limit(5).all()
        
        return jsonify({
            'total_pessoas': total,
            'pessoas_ativas': ativas,
            'pessoas_inativas': inativas,
            'profissoes_mais_comuns': [
                {'profissao': p.profissao, 'count': p.count} 
                for p in profissoes
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

