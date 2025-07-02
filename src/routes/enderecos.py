from flask import Blueprint, request, jsonify
from src.database_config import db
from src.models.endereco import Endereco
from src.models.pessoa import Pessoa
from src.routes.auth import token_required
from datetime import datetime
import random

enderecos_bp = Blueprint('enderecos', __name__)

@enderecos_bp.route('/enderecos', methods=['GET'])
@token_required
def listar_enderecos():
    """
    Lista todos os endereços com paginação e filtros.
    ---
    tags:
      - Endereços
    security:
      - Bearer: []
    parameters:
      - name: page
        in: query
        type: integer
        description: "Número da página"
      - name: per_page
        in: query
        type: integer
        description: "Itens por página"
      - name: pessoa_id
        in: query
        type: integer
        description: "ID da pessoa para filtrar endereços"
      - name: cidade
        in: query
        type: string
        description: "Filtrar por cidade"
      - name: estado
        in: query
        type: string
        description: "Filtrar por estado"
      - name: tipo
        in: query
        type: string
        description: "Filtrar por tipo de endereço (e.g., Residencial, Comercial)"
      - name: ativo
        in: query
        type: boolean
        description: "Filtrar por status de atividade"
    responses:
      200:
        description: "Lista de endereços"
      500:
        description: "Erro interno do servidor"
    """
    try:
        # Simula erro 500 ocasionalmente (3% das vezes)
        if random.random() < 0.03:
            return jsonify({'error': 'Erro interno do servidor'}), 500
        
        # Query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        pessoa_id = request.args.get('pessoa_id', type=int)
        cidade = request.args.get('cidade', '')
        estado = request.args.get('estado', '')
        tipo = request.args.get('tipo', '')
        ativo = request.args.get('ativo', '')
        
        # Limita per_page para evitar sobrecarga
        per_page = min(per_page, 100)
        
        # Query base
        query = Endereco.query
        
        # Filtros
        if pessoa_id:
            query = query.filter(Endereco.pessoa_id == pessoa_id)
        if cidade:
            query = query.filter(Endereco.cidade.ilike(f'%{cidade}%'))
        if estado:
            query = query.filter(Endereco.estado.ilike(f'%{estado}%'))
        if tipo:
            query = query.filter(Endereco.tipo.ilike(f'%{tipo}%'))
        if ativo:
            ativo_bool = ativo.lower() in ['true', '1', 'sim', 'yes']
            query = query.filter(Endereco.ativo == ativo_bool)
        
        # Paginação
        enderecos_paginated = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'enderecos': [endereco.to_dict() for endereco in enderecos_paginated.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': enderecos_paginated.total,
                'pages': enderecos_paginated.pages,
                'has_next': enderecos_paginated.has_next,
                'has_prev': enderecos_paginated.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@enderecos_bp.route('/enderecos/<int:endereco_id>', methods=['GET'])
@token_required
def obter_endereco(endereco_id):
    """
    Obtém um endereço específico.
    ---
    tags:
      - Endereços
    security:
      - Bearer: []
    parameters:
      - name: endereco_id
        in: path
        type: integer
        required: true
        description: "ID do endereço"
    responses:
      200:
        description: "Detalhes do endereço"
      404:
        description: "Endereço não encontrado"
      500:
        description: "Erro interno do servidor"
    """
    try:
        # Simula erro 404 para IDs específicos
        if endereco_id in [999, 1000, 9999]:
            return jsonify({'error': 'Endereço não encontrado'}), 404
        
        # Simula erro 500 ocasionalmente
        if random.random() < 0.03:
            return jsonify({'error': 'Erro interno do servidor'}), 500
        
        endereco = Endereco.query.get(endereco_id)
        
        if not endereco:
            return jsonify({'error': 'Endereço não encontrado'}), 404
        
        return jsonify(endereco.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@enderecos_bp.route('/enderecos', methods=['POST'])
@token_required
def criar_endereco():
    """
    Cria um novo endereço.
    ---
    tags:
      - Endereços
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          $ref: '#/definitions/Endereco'
    responses:
      201:
        description: "Endereço criado com sucesso"
      400:
        description: "Dados inválidos"
      404:
        description: "Pessoa não encontrada"
      500:
        description: "Erro interno do servidor"
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados JSON são obrigatórios'}), 400
        
        # Validações obrigatórias
        required_fields = ['pessoa_id', 'tipo', 'logradouro', 'numero', 'bairro', 'cidade', 'estado', 'cep']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        # Verifica se a pessoa existe
        pessoa = Pessoa.query.get(data['pessoa_id'])
        if not pessoa:
            return jsonify({'error': 'Pessoa não encontrada'}), 404
        
        # Se for endereço principal, remove a flag dos outros endereços da pessoa
        if data.get('principal', False):
            Endereco.query.filter_by(pessoa_id=data['pessoa_id'], principal=True).update({'principal': False})
        
        # Cria novo endereço
        endereco = Endereco(
            pessoa_id=data['pessoa_id'],
            tipo=data['tipo'],
            logradouro=data['logradouro'],
            numero=data['numero'],
            complemento=data.get('complemento'),
            bairro=data['bairro'],
            cidade=data['cidade'],
            estado=data['estado'],
            cep=data['cep'],
            pais=data.get('pais', 'Brasil'),
            principal=data.get('principal', False),
            ativo=data.get('ativo', True)
        )
        
        db.session.add(endereco)
        db.session.commit()
        
        return jsonify({
            'message': 'Endereço criado com sucesso',
            'endereco': endereco.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@enderecos_bp.route('/enderecos/<int:endereco_id>', methods=['PUT'])
@token_required
def atualizar_endereco(endereco_id):
    """
    Atualiza um endereço existente.
    ---
    tags:
      - Endereços
    security:
      - Bearer: []
    parameters:
      - name: endereco_id
        in: path
        type: integer
        required: true
        description: "ID do endereço"
      - name: body
        in: body
        required: true
        schema:
          $ref: '#/definitions/Endereco'
    responses:
      200:
        description: "Endereço atualizado com sucesso"
      400:
        description: "Dados inválidos"
      404:
        description: "Endereço não encontrado"
      500:
        description: "Erro interno do servidor"
    """
    try:
        endereco = Endereco.query.get(endereco_id)
        
        if not endereco:
            return jsonify({'error': 'Endereço não encontrado'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados JSON são obrigatórios'}), 400
        
        # Se for endereço principal, remove a flag dos outros endereços da pessoa
        if data.get('principal', False) and not endereco.principal:
            Endereco.query.filter_by(pessoa_id=endereco.pessoa_id, principal=True).update({'principal': False})
        
        # Atualiza campos
        if 'tipo' in data:
            endereco.tipo = data['tipo']
        if 'logradouro' in data:
            endereco.logradouro = data['logradouro']
        if 'numero' in data:
            endereco.numero = data['numero']
        if 'complemento' in data:
            endereco.complemento = data['complemento']
        if 'bairro' in data:
            endereco.bairro = data['bairro']
        if 'cidade' in data:
            endereco.cidade = data['cidade']
        if 'estado' in data:
            endereco.estado = data['estado']
        if 'cep' in data:
            endereco.cep = data['cep']
        if 'pais' in data:
            endereco.pais = data['pais']
        if 'principal' in data:
            endereco.principal = data['principal']
        if 'ativo' in data:
            endereco.ativo = data['ativo']
        
        endereco.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Endereço atualizado com sucesso',
            'endereco': endereco.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@enderecos_bp.route('/enderecos/<int:endereco_id>', methods=['PATCH'])
@token_required
def atualizar_endereco_parcial(endereco_id):
    """
    Atualiza parcialmente um endereço existente.
    ---
    tags:
      - Endereços
    security:
      - Bearer: []
    parameters:
      - name: endereco_id
        in: path
        type: integer
        required: true
        description: "ID do endereço"
      - name: body
        in: body
        required: true
        schema:
          $ref: '#/definitions/Endereco'
    responses:
      200:
        description: "Endereço atualizado com sucesso"
      400:
        description: "Dados inválidos"
      404:
        description: "Endereço não encontrado"
      500:
        description: "Erro interno do servidor"
    """
    # Reutiliza a lógica do PUT
    return atualizar_endereco(endereco_id)

@enderecos_bp.route('/enderecos/<int:endereco_id>', methods=['DELETE'])
@token_required
def deletar_endereco(endereco_id):
    """
    Deleta um endereço.
    ---
    tags:
      - Endereços
    security:
      - Bearer: []
    parameters:
      - name: endereco_id
        in: path
        type: integer
        required: true
        description: "ID do endereço"
    responses:
      200:
        description: "Endereço deletado com sucesso"
      404:
        description: "Endereço não encontrado"
      500:
        description: "Erro interno do servidor"
    """
    try:
        endereco = Endereco.query.get(endereco_id)
        
        if not endereco:
            return jsonify({'error': 'Endereço não encontrado'}), 404
        
        # Simula erro 500 ocasionalmente
        if random.random() < 0.02:
            return jsonify({'error': 'Erro interno do servidor'}), 500
        
        db.session.delete(endereco)
        db.session.commit()
        
        return jsonify({'message': 'Endereço deletado com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@enderecos_bp.route('/pessoas/<int:pessoa_id>/enderecos', methods=['GET'])
@token_required
def listar_enderecos_pessoa(pessoa_id):
    """
    Lista todos os endereços de uma pessoa específica.
    ---
    tags:
      - Endereços
    security:
      - Bearer: []
    parameters:
      - name: pessoa_id
        in: path
        type: integer
        required: true
        description: "ID da pessoa"
    responses:
      200:
        description: "Lista de endereços da pessoa"
      404:
        description: "Pessoa não encontrada"
      500:
        description: "Erro interno do servidor"
    """
    try:
        # Verifica se a pessoa existe
        pessoa = Pessoa.query.get(pessoa_id)
        if not pessoa:
            return jsonify({'error': 'Pessoa não encontrada'}), 404
        
        enderecos = Endereco.query.filter_by(pessoa_id=pessoa_id).all()
        
        return jsonify({
            'pessoa_id': pessoa_id,
            'pessoa_nome': pessoa.nome,
            'enderecos': [endereco.to_dict() for endereco in enderecos]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@enderecos_bp.route('/enderecos/stats', methods=['GET'])
@token_required
def estatisticas_enderecos():
    """
    Retorna estatísticas dos endereços.
    ---
    tags:
      - Endereços
    security:
      - Bearer: []
    responses:
      200:
        description: "Estatísticas de endereços"
      500:
        description: "Erro interno do servidor"
    """
    try:
        total = Endereco.query.count()
        ativos = Endereco.query.filter_by(ativo=True).count()
        inativos = total - ativos
        
        # Cidades mais comuns
        cidades = db.session.query(
            Endereco.cidade, 
            db.func.count(Endereco.cidade).label('count')
        ).group_by(
            Endereco.cidade
        ).order_by(
            db.func.count(Endereco.cidade).desc()
        ).limit(5).all()
        
        # Estados mais comuns
        estados = db.session.query(
            Endereco.estado, 
            db.func.count(Endereco.estado).label('count')
        ).group_by(
            Endereco.estado
        ).order_by(
            db.func.count(Endereco.estado).desc()
        ).limit(5).all()
        
        return jsonify({
            'total_enderecos': total,
            'enderecos_ativos': ativos,
            'enderecos_inativos': inativos,
            'cidades_mais_comuns': [
                {'cidade': c.cidade, 'count': c.count} 
                for c in cidades
            ],
            'estados_mais_comuns': [
                {'estado': e.estado, 'count': e.count} 
                for e in estados
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

