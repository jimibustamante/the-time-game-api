import random
from .extensions import db
from flask import Blueprint, request, jsonify, make_response
import firebase_admin
from firebase_admin import credentials, auth
from .models import User, Theme, Game, Fact, Question, Option, Answer

cred = credentials.Certificate('./servicesAccountKey.json')
firebase_admin.initialize_app(cred)

api = Blueprint('api', __name__)


"""
Generates a list of questions for a game according to the theme id
"""
def generate_game_questions(theme_id, game_id):
    facts = Fact.query.filter_by(theme_id=theme_id).all()
    questions_len = round(len(facts) / 2)

    for i in range(questions_len):
        question = Question(text='¿Qué fue primero?', game_id=game_id)
        db.session.add(question)
        db.session.commit()
        facts_options = random.sample(facts, 2)
        for fact in facts_options:
            option = Option(fact_id=fact.id, question_id=question.id, is_answer=False)
            db.session.add(option)
            db.session.commit()
            facts.remove(fact)
        
        answer = Question.define_answer(question.options)        
        answer.is_answer = True
        db.session.add(answer)
        db.session.commit()
        

def validate_token():
    try:
        authorization = request.headers.get('Authorization')
        if authorization:
            auth_token = authorization.split(' ')[1]
            return User.decode_auth_token(auth_token=auth_token)
        else:
            response = {
                'status': 'fail',
                'message': 'Unauthorized',
            }
            return make_response(jsonify(response)), 403
    except Exception as e:
        print(e)
        response = {
            'status': 'fail',
            'message': 'Unauthorized',
        }
        return make_response(jsonify(response)), 403


@api.route('/api/sign-in', methods=['POST'])
def sign_in():
    """
    Sign in user route. If everything is ok, returns a json with the user and an access token.
    """

    params = request.get_json()
    uid = params['uid']
    username = params['username']
    email = params['email']
    photoURL = params['photoURL']
    accessToken = params['accessToken']
    providerId = params['providerId']

    try:
        response = auth.verify_id_token(id_token=accessToken, check_revoked=True)
        user = User.query.filter_by(email=email).first()

        if not user:
            try:
                user = User(uid=uid, username=username, email=email, photoURL=photoURL, providerId=providerId)
                db.session.add(user)
                db.session.commit()
            except Exception as e:
                print(f'ERROR => {e}')
                return make_response(jsonify({'error': 'Something went wrong.'}), 401)

        auth_token = user.encode_auth_token(user.id)
        response = {
            'status': 'success',
            'message': 'Succeesfully logged in.',
            'auth_token': auth_token,
            'user': user.to_json(),
        }

        return make_response(jsonify(response)), 200

    except Exception as error:
        print(f'ERROR: {error}')
        return 'Something went wrong', 500


@api.route('/api/themes')
def themes():
    try:
        if validate_token():
            themes = Theme.query.all()
            users = User.query.all()
            response = {
                'status': 'success',
                'themes': [theme.to_json() for theme in themes],
            }
            return make_response(jsonify(response)), 200

    except Exception as error:
        print(f'ERROR: {error}')
        return 'Something went wrong', 500

@api.route('/api/games/new', methods=['POST'])
def new_game():
    """
    Create a new game route.
    """
    if validate_token():
        params = request.get_json()
        userId = params['userId']
        themeId = params['themeId']
        print(f'userId => {userId}')
        print(f'themeId => {themeId}')

        try:
            game = Game(user_id=userId, theme_id=themeId)
            db.session.add(game)
            db.session.commit()
            generate_game_questions(themeId, game.id)

            response = {
                'status': 'success',
                'message': 'Game created.',
                'game': game.to_json(),
            }
            return make_response(jsonify(response)), 200

        except Exception as error:
            print(f'ERROR: {error}')
            return 'Something went wrong', 500


@api.route('/api/questions/answer', methods=['POST'])
def answer():
    if validate_token():
        try:
            params = request.get_json()
            questionId = params['questionId']
            optionId = params['optionId']
            print(f'questionId => {questionId}')
            print(f'optionId => {optionId}')
            question = Question.query.filter_by(id=questionId).first()
            option = Option.query.filter_by(id=optionId).first()
            print(f'question => {question}')
            print(f'option => {option}')
            answer = Answer(question_id=questionId, option_id=optionId)
            db.session.add(answer)
            db.session.commit()
            print(f'answer => {answer}')
            response = {
                'status': 'success',
                'message': 'Answer added.',
                'answer': answer.to_json(),
            }
            return make_response(jsonify(response)), 200

        except Exception as error:
            print(f'ERROR: {error}')
            return 'Something went wrong', 500


