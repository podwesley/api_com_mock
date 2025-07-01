from src.database_config import db
from src.models.auth import Usuario, Token
from src.models.pessoa import Pessoa
from src.models.endereco import Endereco
from datetime import datetime, date
import random

def seed_database():
    """Popula o banco de dados com dados mockados"""
    
    # Limpa dados existentes
    db.session.query(Token).delete()
    db.session.query(Endereco).delete()
    db.session.query(Pessoa).delete()
    db.session.query(Usuario).delete()
    
    # Cria usuário padrão para testes
    usuario = Usuario(
        username='admin',
        email='admin@api.com',
        ativo=True
    )
    usuario.set_password('123456')
    db.session.add(usuario)
    
    # Dados mockados para pessoas
    nomes = [
        'Ana Silva', 'João Santos', 'Maria Oliveira', 'Pedro Costa', 'Carla Souza',
        'Lucas Pereira', 'Fernanda Lima', 'Rafael Alves', 'Juliana Rocha', 'Bruno Martins',
        'Camila Ferreira', 'Diego Ribeiro', 'Larissa Gomes', 'Thiago Barbosa', 'Natália Cardoso',
        'Gabriel Nascimento', 'Priscila Araújo', 'Rodrigo Dias', 'Vanessa Castro', 'Felipe Moreira',
        'Amanda Ramos', 'Gustavo Teixeira', 'Isabela Correia', 'Marcelo Vieira', 'Patrícia Mendes',
        'André Cavalcanti', 'Renata Freitas', 'Leonardo Pinto', 'Cristina Lopes', 'Fábio Monteiro'
    ]
    
    profissoes = [
        'Desenvolvedor', 'Designer', 'Analista', 'Gerente', 'Vendedor',
        'Professor', 'Médico', 'Advogado', 'Engenheiro', 'Contador',
        'Arquiteto', 'Psicólogo', 'Enfermeiro', 'Jornalista', 'Administrador'
    ]
    
    # Cria pessoas
    pessoas = []
    for i, nome in enumerate(nomes, 1):
        pessoa = Pessoa(
            nome=nome,
            email=f'{nome.lower().replace(" ", ".")}@email.com',
            telefone=f'(11) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}',
            cpf=f'{random.randint(100, 999)}.{random.randint(100, 999)}.{random.randint(100, 999)}-{random.randint(10, 99)}',
            data_nascimento=date(
                random.randint(1970, 2000),
                random.randint(1, 12),
                random.randint(1, 28)
            ),
            profissao=random.choice(profissoes),
            salario=round(random.uniform(2000, 15000), 2),
            ativo=random.choice([True, True, True, False])  # 75% ativo
        )
        pessoas.append(pessoa)
        db.session.add(pessoa)
    
    db.session.commit()
    
    # Dados para endereços
    logradouros = [
        'Rua das Flores', 'Avenida Paulista', 'Rua Augusta', 'Alameda Santos',
        'Rua Oscar Freire', 'Avenida Faria Lima', 'Rua Consolação', 'Avenida Rebouças',
        'Rua Teodoro Sampaio', 'Avenida Ibirapuera', 'Rua Haddock Lobo', 'Avenida Europa',
        'Rua Bela Cintra', 'Avenida Brigadeiro Faria Lima', 'Rua Estados Unidos'
    ]
    
    bairros = [
        'Vila Madalena', 'Pinheiros', 'Jardins', 'Itaim Bibi', 'Moema',
        'Vila Olímpia', 'Brooklin', 'Morumbi', 'Perdizes', 'Higienópolis',
        'Liberdade', 'Bela Vista', 'Consolação', 'Santa Cecília', 'Barra Funda'
    ]
    
    cidades = [
        'São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Salvador', 'Brasília',
        'Fortaleza', 'Curitiba', 'Recife', 'Porto Alegre', 'Manaus'
    ]
    
    estados = ['SP', 'RJ', 'MG', 'BA', 'DF', 'CE', 'PR', 'PE', 'RS', 'AM']
    
    tipos_endereco = ['residencial', 'comercial', 'correspondência']
    
    # Cria endereços (1-3 por pessoa)
    for pessoa in pessoas:
        num_enderecos = random.randint(1, 3)
        for i in range(num_enderecos):
            endereco = Endereco(
                pessoa_id=pessoa.id,
                tipo=random.choice(tipos_endereco),
                logradouro=random.choice(logradouros),
                numero=str(random.randint(1, 9999)),
                complemento=random.choice([None, 'Apto 101', 'Casa 2', 'Bloco A', 'Sala 205']) if random.random() < 0.3 else None,
                bairro=random.choice(bairros),
                cidade=random.choice(cidades),
                estado=random.choice(estados),
                cep=f'{random.randint(10000, 99999)}-{random.randint(100, 999)}',
                pais='Brasil',
                principal=(i == 0),  # Primeiro endereço é principal
                ativo=random.choice([True, True, True, False])  # 75% ativo
            )
            db.session.add(endereco)
    
    db.session.commit()
    
    print(f"✅ Banco populado com sucesso!")
    print(f"   - {len(pessoas)} pessoas criadas")
    print(f"   - {Endereco.query.count()} endereços criados")
    print(f"   - Usuário padrão: admin / 123456")

if __name__ == '__main__':
    from flask import Flask
    import os
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        seed_database()

