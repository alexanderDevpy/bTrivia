from flask import render_template, flash, redirect, url_for, request
from app import app
from app.forms import LoginForm
from flask_login import current_user, login_user, login_required
from app.models import User, Questions
from flask_login import logout_user
from werkzeug.urls import url_parse
from app import db, socketio
from app.forms import RegistrationForm, QuestionForm
from flask_socketio import emit, send, join_room, leave_room
import random
import string
from app.game import Game


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if current_user.admin:
        form = QuestionForm()
        if form.validate_on_submit():
            question = Questions(question=form.question.data, answers=form.answers.data,
                                 correct_answer=form.correct.data, speed=form.speed.data)
            db.session.add(question)
            db.session.commit()
            return redirect(url_for('admin'))
        return render_template('admin.html', form=form)
    else:
        return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/finish/<score>')
def finish(score):
    id = current_user.get_id()
    user = User.query.get_or_404(id)
    print(user.score)
    print(f"{score}")
    user.score += int(score)
    db.session.commit()

    return redirect(url_for('index'))


@app.route('/game/<usernames>')
@login_required
def game(usernames):
    print(usernames)
    return render_template('game.html', user=usernames)


@app.route('/lobby')
@login_required
def lobby():
    return render_template('lobby.html')


def randomString(stringLength=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


# ------------------ LOBBY-----------------------------------------------

clients = []

count = 0


@socketio.on('connect', namespace='/lobby')
def connect():
    currentSocketId = request.sid
    clients.append(currentSocketId)
    print(currentSocketId, request.namespace)
    print(clients)
    user = current_user.username
    data = {'user': user}
    if len(clients) > 2:
        url = randomString()
        data = {'url': url}
        emit('start', data, room=clients[0])
        emit('start', data, room=clients[1])
        emit('start', data, room=clients[2])


@socketio.on('start', namespace='/lobby')
def start():
    emit('start', len(clients))


@socketio.on('disconnect', namespace='/lobby')
def disconnect():
    clients.remove(request.sid)
    print(clients)


# ------------------ GAME  -----------------------------------------------


roomsGame = {}


@socketio.on('join', namespace='/game')
def on_join(data):
    user = current_user.username
    id = request.sid
    room = data['room']
    join_room(room)
    if room in roomsGame:
        print(f' room{room}')
    else:
        print(f'Else om{room}')
        roomsGame[room] = Game(room)

    some = {'id': id, 'user': user, 'room': room}
    socketio.sleep(1)
    emit('count', some, room=id)


@socketio.on('leave', namespace='/game')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    send(username + ' has left the room.', room=room)


@socketio.on('update', namespace='/game')
def update(data):
    game = roomsGame[data['room']]
    sock = request.sid
    user = data['user']
    game.updateuser(user, sock)
    if len(game.sokid) == 3:
        startque = Questions.query.filter(Questions.speed.is_(False)).all()
        random.shuffle(startque)
        game.questions = startque
        print(f'Game begin {game}{startque[0].answers} {game.questions[0].question}')

        gamestart(game)
    print(f" update{game.sokid}")


@socketio.on('create', namespace='/game')
def create(data):
    print('game start')


@socketio.on('disconnect', namespace='/game')
def disconnect():
    pass


# ================== START =====================

def gamestart(data):
    print(f'game begin {data}')
    print(f'{data.sokid}')

    emit('g', {"user": [data.sokid[0][2], data.sokid[1][2], data.sokid[2][2]],
               "color": [data.sokid[0][0], data.sokid[1][0], data.sokid[2][0]], 'room': data.room}, room=data.room)


@socketio.on('speed', namespace='/game')
def speed(data):
    game = roomsGame[data['room']]
    game.rasp += 1
    if game.rasp == game.users:
        game.rasp = 0
        emit('time', room=game.room)
        answers = game.questions[game.count].answers.split(',')
        print(answers)
        print(game.gameround)
        print('speed')
        emit('first', {'questions': game.questions[game.count].question, 'answers': answers,
                       'corect': game.questions[game.count].correct_answer, 'round': game.gameround}, room=game.room)


@socketio.on('check', namespace="/game")
def check(data):
    game = roomsGame[data['room']]
    game.rasp += 1
    ans = game.questions[game.count].correct_answer

    for color, ids, username in game.sokid:
        print(f'color {color} , id {ids}  {username}, ')
        print(f'dataid {data["id"]}')
        if data['id'] == ids:
            print(f'for {game.corans}')
            print(data['ans'])

            game.corans.append((color, ids, data['ans']))

    if game.rasp == game.users:
        print(game.corans)
        game.gameround += 1
        game.rasp = 0
        upd = {}
        for x, y in enumerate(game.corans):
            upd[str(x)] = list(y)
        game.count += 1

        print(f'check{upd["0"]}')
        emit('uptable', upd, room=game.room)
        game.corans = []


@socketio.on('win', namespace="/game")
def win(data):
    print('finish', data['winer'])
    game = roomsGame[data['room']]
    game.rasp += 1
    if game.rasp == game.users:
        emit('finish', room=data['winer'])
        game.rasp = 0


@socketio.on('pleft', namespace="/game")
def pleft(data):
    print(f'pleft')
    game = roomsGame[data['room']]
    game.users -= 1

    print(f'pleft {game.users}')
