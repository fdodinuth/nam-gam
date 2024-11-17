from flask import Flask, render_template, request, redirect, url_for, session
import random
import time

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Use a proper secret key in production.

# Store active games (In a real app, use a database)
active_games = {}

# Questions (Fixed for now)
QUESTIONS = [
    "Nam", "Gam", "Palathuru", "Elaulu", "Saththu", "Mal", "Rata", "Sindu"
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/host_game', methods=['POST'])
def host_game():
    username = request.form['username']
    session['username'] = username  # Store host's username in session
    game_id = str(random.randint(1000, 9999))  # Generate random game ID
    active_games[game_id] = {'host': username, 'players': [username], 'game_started': False, 'answers': {}}
    return render_template('game_lobby.html', game_id=game_id, players=[username], is_host=True)

@app.route('/join_game', methods=['POST'])
def join_game():
    username = request.form['username']
    game_id = request.form['game_id']
    
    if game_id in active_games:
        session['username'] = username
        active_games[game_id]['players'].append(username)
        return render_template('game_lobby.html', game_id=game_id, players=active_games[game_id]['players'], is_host=False)
    else:
        return "Game not found", 404

@app.route('/start_game', methods=['POST'])
def start_game():
    game_id = request.form['game_id']
    if game_id in active_games:
        game_data = active_games[game_id]
        # Allow any player to start the game, not just the host
        game_data['game_started'] = True
        active_games[game_id] = game_data
        # Start the game with a timer for answering (e.g., 30 seconds per question)
        return render_template('game.html', game_id=game_id, questions=QUESTIONS, timer=30)
    return "Game ID not found", 404

@app.route('/submit_answers', methods=['POST'])
def submit_answers():
    game_id = request.form['game_id']
    if game_id in active_games:
        game_data = active_games[game_id]
        if session.get('username') in game_data['players']:
            answers = {f"answer{i}": request.form[f"answer{i}"] for i in range(len(QUESTIONS))}
            game_data['answers'][session['username']] = answers
            active_games[game_id] = game_data
            return redirect(url_for('reveal_answers', game_id=game_id))
    return "Error submitting answers", 400

@app.route('/reveal_answers/<game_id>')
def reveal_answers(game_id):
    if game_id in active_games:
        game_data = active_games[game_id]
        if all(player in game_data['answers'] for player in game_data['players']):
            return render_template('reveal_answers.html', game_id=game_id, answers=game_data['answers'])
    return "Waiting for all players to answer", 200

@app.route('/restart_game', methods=['POST'])
def restart_game():
    game_id = request.form['game_id']
    if game_id in active_games:
        game_data = active_games[game_id]
        if game_data['host'] == session.get('username'):
            game_data['game_started'] = False
            game_data['answers'] = {}
            active_games[game_id] = game_data
            return redirect(url_for('game_lobby', game_id=game_id))
    return "Only the host can restart the game", 403

if __name__ == '__main__':
    app.run(debug=True)
