import datetime
import itertools
import jwt
from flask import current_app
from .extensions import db

class Game(db.Model):
    """
    A game is a single instance of a game based on a theme.
    """
    id = db.Column(db.Integer, primary_key=True)
    completed = db.Column(db.Boolean, default=False)
    questions = db.relationship('Question', backref='game', lazy='dynamic')
    max_questions = db.Column(db.Integer, default=20)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    theme_id = db.Column(db.Integer, db.ForeignKey('theme.id'))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def set_max_questions(self):
        facts = Fact.query.filter_by(theme_id=self.theme_id).all()
        questions_len = round(len(facts) / 2)
        self.max_questions = questions_len
        db.session.commit()

    def current_question(self):
        return self.questions.filter(Question.completed == False).first()

    def __repr__(self):
        return '<Game %r>' % self.id

    def to_json(self):
        question = self.questions.filter(Question.completed == False).first()
        if question:
            question = question.to_json()

        return {
            'id': self.id,
            'max_questions': self.max_questions,
            'completed': self.completed,
            'question': question,
            'questions_completed': self.questions.filter(Question.completed == True).count()
        }

    def summary_to_json(self):
        complited_questions = self.questions.filter(Question.completed == True).all()
        answers = list(map(lambda q: q.answer, complited_questions))
        answers = itertools.chain(*answers)
        answers_options = list(map(lambda a: a.option, answers))
        correct_answers = list(filter(lambda a: a.is_answer, answers_options))
        return {
            'id': self.id,
            'total_questions': self.max_questions,
            'complited_questions': len(complited_questions),
            'correct_answers_count': len(correct_answers),
            'wrong_answers_count': len(complited_questions) - len(correct_answers),
        }



class Theme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    title = db.Column(db.String, unique=True, nullable=False)
    games = db.relationship('Game', backref='theme', lazy=True)
    facts = db.relationship('Fact', backref='theme', lazy=True)


    def __init__(self, name, title):
        self.name = name
        self.title = title

    def __repr__(self):
        return '<Theme %r>' % self.name

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'title': self.title,
        }

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    options = db.relationship('Option', backref='question', lazy=True)
    answer = db.relationship('Answer', backref='question', lazy=True)

    def to_json(self):
        return {
            'id': self.id,
            'text': self.text,
            'completed': self.completed,
            'options': [option.to_json() for option in self.options]
        }

    @staticmethod
    def define_answer(options):
        return sorted(options, key=lambda option: option.fact.year)[0]


class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fact_id = db.Column(db.Integer, db.ForeignKey('fact.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    is_answer = db.Column(db.Boolean, default=False)
    answer = db.relationship('Answer', backref='option', lazy=True)
    

    def __repr__(self):
        return '<Option %r>' % self.fact.year

    def to_json(self):
        return {
            'id': self.id,
            'fact': self.fact.to_json(),
            'is_answer': self.is_answer,
        }


class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    option_id = db.Column(db.Integer, db.ForeignKey('option.id'))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<Answer %r>' % self.option.fact.name

    def to_json(self):
        return {
            'id': self.id,
            'is_correct': self.option.is_answer,
        }
class Fact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    info_link = db.Column(db.String, nullable=False)
    options = db.relationship('Option', backref='fact', lazy=True)
    theme_id = db.Column(db.Integer, db.ForeignKey('theme.id'))

    def __repr__(self):
        return '<Fact %r>' % self.name
    
    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'year': self.year,
            'info_link': self.info_link,
        }

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String, unique=True)
    email = db.Column(db.String(254), unique=True)
    username = db.Column(db.String, unique=True)
    photoURL = db.Column(db.String)
    providerId = db.Column(db.String)
    games = db.relationship('Game', backref='user', lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __init__(self, uid, providerId, photoURL, username, email):
        """
        Initializes the User object
        """
        self.uid = uid
        self.providerId = providerId
        self.photoURL = photoURL
        self.username = username
        self.email = email

    def __repr__(self):
        """
        String representation of the User object
        :return: string
        """
        return '<User %r>' % self.username

    def encode_auth_token(self, user_id):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=5),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id,
            }
            return jwt.encode(
                payload,
                current_app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e


    def to_json(self):
        """
        Serializes the User object to JSON
        :return: string
        """
        return {
            'id': self.id,
            'uid': self.uid,
            'email': self.email,
            'photoURL': self.photoURL,
            'username': self.username,
        }


    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(
                auth_token,
                options={"verify_signature": False},
            )
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'

