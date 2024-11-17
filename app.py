from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import random
import time
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For session management
socketio = SocketIO(app)

# Predefined questions
QUESTIONS = [
    "nam", "gam", "pala", "ela", "sathu", "mal", "rata", "sindu"
]

# Store active game data
active_games = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/host_game', methods=['POST'])
def host_game():
    username = request.form['username']
    game_id = str(random.randint(1000, 9999))  # Generate a random game ID
    session['username'] = username
    active_games[game_id] = {
        'host': username,
        'players': [username],
        'game_started': False,
        'answers': {},
        'time_limit': 30  # Default answering time limit
    }
    return render_template('game_lobby.html', game_id=game_id, players=[username], is_host=True)

@app.route('/join_game', methods=['POST'])
def join_game():
    username = request.form['username']
    game_id = request.form['game_id']
    
    if game_id in active_games:
        game_data = active_games[game_id]
        game_data['players'].append(username)
        active_games[game_id] = game_data
        session['username'] = username
        return render_template('game_lobby.html', game_id=game_id, players=game_data['players'], is_host=False)
    else:
        return "Game not found!", 404

@app.route('/start_game', methods=['POST'])
def start_game():
    game_id = request.form['game_id']
    game_data = active_games.get(game_id)
    
    if game_data and game_data['host'] == session.get('username'):
        game_data['game_started'] = True
        active_games[game_id] = game_data
        # Start the timer (30 seconds for example)
        return render_template('game.html', game_id=game_id, questions=QUESTIONS, time_limit=game_data['time_limit'])
    
    return "Only the host can start the game", 403

@app.route('/submit_answers', methods=['POST'])
def submit_answers():
    game_id = request.form['game_id']
    answers = request.form.getlist('answers[]')  # Get answers from form
    
    if game_id in active_games:
        game_data = active_games[game_id]
        player = session.get('username')
        game_data['answers'][player] = answers
        active_games[game_id] = game_data
        
        # Check if all players have submitted answers
        if len(game_data['answers']) == len(game_data['players']):
            return render_template('results.html', game_id=game_id, answers=game_data['answers'])
    
    return "Error submitting answers", 500

@app.route('/restart_game', methods=['POST'])
def restart_game():
    game_id = request.form['game_id']
    game_data = active_games.get(game_id)
    
    if game_data and game_data['host'] == session.get('username'):
        # Reset the game state but keep the players
        game_data['game_started'] = False
        game_data['answers'] = {}
        active_games[game_id] = game_data
        return render_template('game_lobby.html', game_id=game_id, players=game_data['players'], is_host=True)
    
    return "Only the host can restart the game", 403

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000)
