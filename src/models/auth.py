from src.database_config import db
from datetime import datetime, timedelta
import secrets
import hashlib

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento com tokens
    tokens = db.relationship('Token', backref='usuario', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash da senha"""
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password):
        """Verifica a senha"""
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'ativo': self.ativo,
            'created_at': self.created_at.isoformat()
        }

class Token(db.Model):
    __tablename__ = 'tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    token = db.Column(db.String(128), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @staticmethod
    def generate_token():
        """Gera um token único"""
        return secrets.token_urlsafe(64)
    
    @classmethod
    def create_token(cls, usuario_id, expires_in_hours=24):
        """Cria um novo token para o usuário"""
        token = cls(
            usuario_id=usuario_id,
            token=cls.generate_token(),
            expires_at=datetime.utcnow() + timedelta(hours=expires_in_hours)
        )
        return token
    
    def is_valid(self):
        """Verifica se o token é válido"""
        return self.ativo and self.expires_at > datetime.utcnow()
    
    def to_dict(self):
        return {
            'token': self.token,
            'expires_at': self.expires_at.isoformat(),
            'ativo': self.ativo
        }

