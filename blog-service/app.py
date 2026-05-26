import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/blogdb')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'default-secret-key')

db = SQLAlchemy(app)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'created_date': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_date': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request', 'message': str(error)}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f'Internal error: {error}')
    return jsonify({'error': 'Internal server error'}), 500

@app.route('/posts', methods=['GET'])
def get_posts():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        category = request.args.get('category')

        query = Post.query
        if category:
            query = query.filter(Post.category == category)

        posts = query.order_by(Post.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'posts': [post.to_dict() for post in posts.items],
            'total': posts.total,
            'page': page,
            'pages': posts.pages
        })
    except Exception as e:
        logger.error(f'Get posts error: {e}')
        return jsonify({'error': 'Failed to fetch posts'}), 500

@app.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    try:
        post = Post.query.get_or_404(post_id)
        return jsonify(post.to_dict())
    except Exception as e:
        logger.error(f'Get post error: {e}')
        return jsonify({'error': 'Post not found'}), 404

@app.route('/posts', methods=['POST'])
def create_post():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        title = data.get('title', '').strip()
        description = data.get('description', '')
        category = data.get('category', '')

        if not title:
            return jsonify({'error': 'Title is required'}), 400

        post = Post(title=title, description=description, category=category)
        db.session.add(post)
        db.session.commit()

        logger.info(f'Post created: {title}')
        return jsonify({'message': 'Post created successfully', 'post': post.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f'Create post error: {e}')
        return jsonify({'error': 'Failed to create post'}), 500

@app.route('/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    try:
        post = Post.query.get_or_404(post_id)
        data = request.get_json()

        if data.get('title'):
            post.title = data['title'].strip()
        if data.get('description') is not None:
            post.description = data['description']
        if data.get('category') is not None:
            post.category = data['category']

        db.session.commit()
        logger.info(f'Post updated: {post.title}')
        return jsonify({'message': 'Post updated successfully', 'post': post.to_dict()})
    except Exception as e:
        db.session.rollback()
        logger.error(f'Update post error: {e}')
        return jsonify({'error': 'Failed to update post'}), 500

@app.route('/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    try:
        post = Post.query.get_or_404(post_id)
        db.session.delete(post)
        db.session.commit()
        logger.info(f'Post deleted: {post.title}')
        return jsonify({'message': 'Post deleted successfully'})
    except Exception as e:
        db.session.rollback()
        logger.error(f'Delete post error: {e}')
        return jsonify({'error': 'Failed to delete post'}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'blog-service'})

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
