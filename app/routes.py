import itertools
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
def generate_next_question(game):
    if len(game.questions.all()) < game.max_questions:
        facts = Fact.query.filter_by(theme_id=game.theme_id).all()
        used_facts = list(map(lambda question: list(map(lambda option: option.fact, question.options)), game.questions.all()))
        used_facts = list(itertools.chain(*used_facts))
        used_facts_ids = list(map(lambda fact: fact.id, used_facts))
        unused_facts = list(filter(lambda fact: fact.id not in used_facts_ids, facts))
        unused_facts_ids = list(map(lambda unused_fact: unused_fact.id, unused_facts))

        question = Question(text='¿Qué fue primero?', game_id=game.id)

        db.session.add(question)
        db.session.commit()
        facts_options = random.sample(unused_facts_ids, 2)
        for fact_id in facts_options:
            option = Option(fact_id=fact_id, question_id=question.id, is_answer=False)
            db.session.add(option)
            db.session.commit()
        
        answer = Question.define_answer(question.options)        
        answer.is_answer = True
        db.session.add(answer)
        db.session.commit()
    else:
        game.completed = True
        db.session.commit()
        response = {
            'message': 'No more questions',
            'status': 'success',
        }
        return make_response(jsonify(response)), 200
        

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


@api.route('/')
def index():
    print(request.json)

    return 'Hello, World!'


@api.route('/api/sign-in', methods=['POST'])
def sign_in():
    """
    Sign in user route. If everything is ok, returns a json with the user and an access token.
    """
    print(request.json)
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
                print(f'ERROR A => {e}')
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
        print(f'ERROR B: {error}')
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

        try:
            game = Game(user_id=userId, theme_id=themeId, completed=False)
            game.set_max_questions()
            db.session.add(game)
            db.session.commit()
            generate_next_question(game)

            response = {
                'status': 'success',
                'message': 'Game created.',
                'game': game.to_json(),
            }
            return make_response(jsonify(response)), 200

        except Exception as error:
            print(f'ERROR C: {error}')
            return 'Something went wrong', 500


@api.route('/api/games/<game_id>', methods=['GET'])
def get_game(game_id):
    """
    Get game route.
    """
    if validate_token():
        try:
            game = Game.query.filter_by(id=game_id).first()
            if game:
                response = {
                    'status': 'success',
                    'message': 'Game found.',
                    'game': game.to_json(),
                }
                return make_response(jsonify(response)), 200
            else:
                response = {
                    'status': 'fail',
                    'message': 'Game not found.',
                }
                return make_response(jsonify(response)), 404

        except Exception as error:
            print(f'ERROR D: {error}')
            return 'Something went wrong', 500


@api.route('/api/games/<game_id>/questions/next', methods=['GET'])
def next_question(game_id):
    """
    Get next question route.
    """
    if validate_token():
        try:
            game = Game.query.filter_by(id=game_id).first()
            generate_next_question(game)
            response = {
                'status': 'success',
                'message': 'Next question generated.',
                'game': game.to_json(),
            }
            return make_response(jsonify(response)), 200
        except Exception as error:
            print(f'ERROR E: {error}')
            return 'Something went wrong', 500


# @api.route('/api/games/<game_id>/questions', methods=['GET'])
# def get_questions(game_id):
#     pass

@api.route('/api/questions/answer', methods=['POST'])
def answer():
    if validate_token():
        try:
            params = request.get_json()
            questionId = params['questionId']
            optionId = params['optionId']
            question = Question.query.filter_by(id=questionId).first()
            question.completed = True
            db.session.add(question)
            answer = Answer(question_id=questionId, option_id=optionId)
            db.session.add(answer)
            db.session.commit()

            response = {
                'status': 'success',
                'message': 'Answer added.',
                'answer': answer.to_json(),
            }
            return make_response(jsonify(response)), 200

        except Exception as error:
            print(f'ERROR F: {error}')
            return 'Something went wrong', 500


@api.route('/api/games/<game_id>/summary', methods=['GET'])
def get_summary(game_id):
    if validate_token():
        try:
            game = Game.query.filter_by(id=game_id).first()
            response = {
                'status': 'success',
                'message': 'Game summary found.',
                'summary': game.summary_to_json(),
            }
            return make_response(jsonify(response)), 200
        except Exception as error:
            print(f'ERROR G: {error}')
            return 'Something went wrong', 500
