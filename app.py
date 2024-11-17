from flask import Flask, render_template, request, redirect, url_for, session
import random
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key

# Predefined questions
QUESTIONS = [
    "What's your name?",
    "What's your game?",
    "What's your favorite dish?",
    "What's your hobby?",
    "What's your favorite animal?",
    "What's your favorite color?",
    "What's your country?",
    "What's your favorite song?"
]

# Active games stored in-memory
active_games = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/host_game', methods=['POST'])
def host_game():
    username = request.form.get('username')
    game_id = str(random.randint(1000, 9999))
    
    session['username'] = username
    session['game_id'] = game_id
    active_games[game_id] = {
        'host': username,
        'players': [username],
        'game_started': False,
        'answers': {},
        'timer': 30
    }
    return render_template('game_lobby.html', game_id=game_id, players=[username], is_host=True)

@app.route('/join_game', methods=['POST'])
def join_game():
    username = request.form.get('username')
    game_id = request.form.get('game_id')
    
    if game_id in active_games:
        session['username'] = username
        session['game_id'] = game_id
        active_games[game_id]['players'].append(username)
        return render_template('game_lobby.html', game_id=game_id, players=active_games[game_id]['players'], is_host=False)
    return "Game not found!", 404

@app.route('/start_game', methods=['POST'])
def start_game():
    game_id = session.get('game_id')
    
    if game_id and game_id in active_games:
        active_games[game_id]['game_started'] = True
        active_games[game_id]['timer'] = 30  # Reset timer to 30 seconds
        
        # Redirect to the game page where the questions will be asked
        return render_template('game.html', game_id=game_id, questions=QUESTIONS, timer=30)

    return "Unable to start game.", 400

@app.route('/submit_answers', methods=['POST'])
def submit_answers():
    game_id = session.get('game_id')
    answers = request.form.to_dict()
    
    if game_id in active_games:
        active_games[game_id]['answers'][session['username']] = answers
        return redirect(url_for('show_answers', game_id=game_id))

    return "Error submitting answers", 400

@app.route('/show_answers/<game_id>')
def show_answers(game_id):
    if game_id in active_games:
        game_data = active_games[game_id]
        return render_template('show_answers.html', game_data=game_data)

    return "Game not found.", 404

@app.route('/restart_game/<game_id>')
def restart_game(game_id):
    if game_id in active_games and active_games[game_id]['host'] == session['username']:
        # Reset game state
        active_games[game_id] = {
            'host': active_games[game_id]['host'],
            'players': active_games[game_id]['players'],
            'game_started': False,
            'answers': {},
            'timer': 30
        }
        return redirect(url_for('game_lobby', game_id=game_id))

    return "Only the host can restart the game.", 403

if __name__ == '__main__':
    app.run(debug=True)
