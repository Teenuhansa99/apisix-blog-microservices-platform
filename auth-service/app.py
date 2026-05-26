import os
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
import jwt
from passlib.hash import bcrypt
from email_validator import validate_email, EmailNotValidError

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/blogdb')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'default-secret-key')
app.config['JWT_ALGORITHM'] = os.getenv('JWT_ALGORITHM', 'HS256')
app.config['JWT_ACCESS_EXPIRE_MINUTES'] = int(os.getenv('JWT_ACCESS_EXPIRE_MINUTES', 30))
app.config['JWT_REFRESH_EXPIRE_DAYS'] = int(os.getenv('JWT_REFRESH_EXPIRE_DAYS', 7))

db = SQLAlchemy(app)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    refresh_tokens = db.relationship('RefreshToken', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = bcrypt.hash(password)

    def check_password(self, password):
        return bcrypt.verify(password, self.password_hash)

class RefreshToken(db.Model):
    __tablename__ = 'refresh_tokens'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(512), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def is_valid(self):
        return datetime.utcnow() < self.expires_at

def generate_tokens(user):
    access_payload = {
        'user_id': user.id,
        'username': user.username,
        'exp': datetime.utcnow() + timedelta(minutes=app.config['JWT_ACCESS_EXPIRE_MINUTES']),
        'type': 'access'
    }
    access_token = jwt.encode(access_payload, app.config['JWT_SECRET_KEY'], algorithm=app.config['JWT_ALGORITHM'])

    refresh_payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(days=app.config['JWT_REFRESH_EXPIRE_DAYS']),
        'type': 'refresh'
    }
    refresh_token = jwt.encode(refresh_payload, app.config['JWT_SECRET_KEY'], algorithm=app.config['JWT_ALGORITHM'])

    return access_token, refresh_token

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request', 'message': str(error)}), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized', 'message': 'Invalid credentials'}), 401

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f'Internal error: {error}')
    return jsonify({'error': 'Internal server error'}), 500

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        username = data.get('username', '').strip()
        password = data.get('password', '')
        email = data.get('email', '').strip() if data.get('email') else None

        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400

        if len(username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters'}), 400

        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400

        if email:
            try:
                validate_email(email)
            except EmailNotValidError:
                return jsonify({'error': 'Invalid email format'}), 400

        user = User(username=username, email=email)
        user.set_password(password)

        try:
            db.session.add(user)
            db.session.commit()
            logger.info(f'User registered: {username}')
            return jsonify({'message': 'User registered successfully'}), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({'error': 'Username already exists'}), 409

    except Exception as e:
        logger.error(f'Registration error: {e}')
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        username = data.get('username', '')
        password = data.get('password', '')

        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400

        user = User.query.filter_by(username=username, is_active=True).first()

        if not user or not user.check_password(password):
            logger.warning(f'Failed login attempt for: {username}')
            return jsonify({'error': 'Invalid credentials'}), 401

        access_token, refresh_token = generate_tokens(user)

        db.session.add(RefreshToken(user_id=user.id, token=refresh_token,
                                    expires_at=datetime.utcnow() + timedelta(days=app.config['JWT_REFRESH_EXPIRE_DAYS'])))
        db.session.commit()

        logger.info(f'User logged in: {username}')
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'bearer',
            'expires_in': app.config['JWT_ACCESS_EXPIRE_MINUTES'] * 60
        })

    except Exception as e:
        logger.error(f'Login error: {e}')
        return jsonify({'error': 'Login failed'}), 500

@app.route('/refresh', methods=['POST'])
def refresh_token():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        refresh_token = data.get('refresh_token')
        if not refresh_token:
            return jsonify({'error': 'Refresh token required'}), 400

        try:
            payload = jwt.decode(refresh_token, app.config['JWT_SECRET_KEY'], algorithms=[app.config['JWT_ALGORITHM']])
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Refresh token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid refresh token'}), 401

        stored_token = RefreshToken.query.filter_by(token=refresh_token, user_id=payload['user_id']).first()
        if not stored_token or not stored_token.is_valid():
            return jsonify({'error': 'Invalid or expired refresh token'}), 401

        user = User.query.get(payload['user_id'])
        if not user or not user.is_active:
            return jsonify({'error': 'User not found or inactive'}), 404

        db.session.delete(stored_token)
        access_token, new_refresh_token = generate_tokens(user)
        db.session.add(RefreshToken(user_id=user.id, token=new_refresh_token,
                                    expires_at=datetime.utcnow() + timedelta(days=app.config['JWT_REFRESH_EXPIRE_DAYS'])))
        db.session.commit()

        return jsonify({
            'access_token': access_token,
            'refresh_token': new_refresh_token,
            'token_type': 'bearer'
        })

    except Exception as e:
        logger.error(f'Refresh token error: {e}')
        return jsonify({'error': 'Token refresh failed'}), 500

@app.route('/logout', methods=['POST'])
def logout():
    try:
        data = request.get_json()
        refresh_token = data.get('refresh_token') if data else None

        if refresh_token:
            stored_token = RefreshToken.query.filter_by(token=refresh_token).first()
            if stored_token:
                db.session.delete(stored_token)
                db.session.commit()

        return jsonify({'message': 'Logged out successfully'})
    except Exception as e:
        logger.error(f'Logout error: {e}')
        return jsonify({'error': 'Logout failed'}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'auth-service'})

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
