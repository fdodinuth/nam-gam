from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
import random

# Initialize Flask app and SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Store game data (in memory for this example)
games = {}

# Hardcoded questions (fixed questions)
questions = [
    "Nam?",
    "Gam?",
    "Pala?",
    "Ela?",
    "Sathu?",
    "Mal?",
    "Rata?",
    "Sindu?"
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/host_game', methods=['POST'])
def host_game():
    username = request.form['username']
    game_id = str(random.randint(1000, 9999))  # Generate a random game ID

    # Create a game room with the game ID and store the player's info
    games[game_id] = {
        'players': [username],
        'game_started': False,
        'timer': 100,  # Initial timer (100 seconds)
        'questions': questions,  # Fixed list of questions
        'answers': {},
        'game_over': False
    }

    return render_template('game_lobby.html', game_id=game_id, players=[username], is_host=True)

@app.route('/join_game', methods=['POST'])
def join_game():
    username = request.form['username']
    game_id = request.form['game_id']

    # Check if the game exists
    if game_id not in games:
        return "Game not found!", 404

    # Add the player to the game
    games[game_id]['players'].append(username)

    return render_template('game_lobby.html', game_id=game_id, players=games[game_id]['players'], is_host=False)

@app.route('/game/<game_id>', methods=['GET'])
def game(game_id):
    if game_id not in games:
        return "Game not found!", 404

    # Check if game started
    if not games[game_id]['game_started']:
        return redirect(url_for('index'))  # Redirect to index if the game hasn't started

    return render_template('game.html', game_id=game_id, players=games[game_id]['players'])

# Handle socket connection
@socketio.on('join_game')
def handle_join_game(data):
    username = data['username']
    room = data['room']

    # Join the room
    join_room(room)

    # Add player to the game's player list
    games[room]['players'].append(username)

    # Emit the updated player list to everyone in the room
    emit('update_player_list', {'players': games[room]['players']}, room=room)

@socketio.on('start_game')
def start_game(data):
    room = data['room']

    # Ensure the game exists and hasn't already started
    if room in games and not games[room]['game_started']:
        games[room]['game_started'] = True

        # Emit game start to all players in the room
        emit('game_started', {'message': 'Game has started!'}, room=room)

        # Send the fixed questions to players
        emit('send_questions', {'questions': games[room]['questions']}, room=room)

        # Optionally, start a timer for 100 seconds
        emit('start_timer', {'time': games[room]['timer']}, room=room)

@socketio.on('submit_answer')
def submit_answer(data):
    room = data['room']
    username = data['username']
    answer = data['answer']

    # Save the answer for the player
    if room in games and not games[room]['game_over']:
        if username not in games[room]['answers']:
            games[room]['answers'][username] = []

        games[room]['answers'][username].append(answer)
        emit('update_answers', {'answers': games[room]['answers']}, room=room)

@socketio.on('end_game')
def end_game(data):
    room = data['room']

    if room in games:
        games[room]['game_over'] = True
        emit('game_over', {'message': 'Game Over!'}, room=room)
        emit('show_answers', {'answers': games[room]['answers']}, room=room)

@socketio.on('restart_game')
def restart_game(data):
    room = data['room']

    if room in games:
        # Reset game state
        games[room]['game_started'] = False
        games[room]['timer'] = 100
        games[room]['answers'] = {}
        games[room]['game_over'] = False

        emit('game_restarted', {'message': 'Game has been restarted!'}, room=room)
        emit('start_timer', {'time': games[room]['timer']}, room=room)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
