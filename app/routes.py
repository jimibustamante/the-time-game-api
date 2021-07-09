from .extensions import db
from flask import Blueprint, request, jsonify, make_response
import firebase_admin
from firebase_admin import credentials, auth
from .models import User, Theme

cred = credentials.Certificate('./servicesAccountKey.json')
firebase_admin.initialize_app(cred)

api = Blueprint('api', __name__)


@api.route('/api/sign-in', methods=['POST'])
def sign_in():
    # print(f'REQUEST: {request.get_json()}')
    params = request.get_json()
    uid = params['uid']
    username = params['username']
    email = params['email']
    photoURL = params['photoURL']
    accessToken = params['accessToken']
    providerId = params['providerId']

    try:
        response = auth.verify_id_token(id_token=accessToken, check_revoked=True)
        # print(f'\n\nRESPONSE =>{response}\n\n')
        user = User.query.filter_by(email=email).first()
        print(f'USER => {user}')

        if not user:
            try:
                user = User(uid=uid, username=username, email=email, photoURL=photoURL, providerId=providerId)
                db.session.add(user)
                db.session.commit()
                print(f'USER => {user}')
            except Exception as e:
                print('ERRRRRRRRRRRORRRRRRR !!!')
                response = {
                    'status': 'fail',
                    'message': 'Some error curred. Please try again.'
                }
                return make_response(jsonify(response)), 401
        auth_token = user.encode_auth_token(user.id)
        # print(auth_token)
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
    authorization = request.headers.get('Authorization')
    print(f'authorization => {authorization}')
    try:
        if authorization:
            auth_token = authorization.split(' ')[1]
            resp = User.decode_auth_token(auth_token=auth_token)
            # print(f'resp => {resp}')
            if resp:
                themes = Theme.query.all()
                users = User.query.all()
                print(f'USER => {users}')
                print(f'THEMES => {themes}')
                response = {
                    'status': 'success',
                    'themes': [theme.to_json() for theme in themes],
                }
                # result = [theme.to_json() for theme in themes]
                return make_response(jsonify(response)), 200
            else:
                response = {
                    'status': 'fail',
                    'message': 'Unauthorized',
                }
                return make_response(jsonify(response)), 403

    except Exception as error:
        print(f'ERROR: {error}')
        return 'Something went wrong', 500