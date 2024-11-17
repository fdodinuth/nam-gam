const socket = io.connect('http://localhost:5000');  // Ensure this is the correct URL

let username = '';
let gameID = '';
let isHost = false;

// Enter name and show options to host/join game
document.getElementById('enterName').addEventListener('click', () => {
    username = document.getElementById('usernameInput').value.trim();
    if (username) {
        document.getElementById('nameEntry').classList.add('d-none');
        document.getElementById('gameOptions').classList.remove('d-none');
    } else {
        alert('Please enter a valid username');
    }
});

// Host game button - create a new game and display the game lobby
document.getElementById('hostGame').addEventListener('click', () => {
    fetch('/host_game', {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: `username=${username}`
    }).then(response => response.text())
      .then(html => {
          document.body.innerHTML = html;  // Replace the page with the game lobby
          gameID = document.getElementById('gameID').textContent;  // Get the generated game ID
          isHost = true;
          socket.emit('join_game', { username: username, room: gameID });  // Emit join game event
      });
});

// Join game button - enter game ID to join
document.getElementById('joinGame').addEventListener('click', () => {
    const gameIDInput = prompt("Enter the Game ID:");
    if (gameIDInput) {
        gameID = gameIDInput;
        fetch('/join_game', {
            method: 'POST',
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            body: `username=${username}&game_id=${gameID}`
        }).then(response => response.text())
          .then(html => {
              document.body.innerHTML = html;  // Replace the page with the game lobby
              isHost = false;
              socket.emit('join_game', { username: username, room: gameID });  // Emit join game event
          });
    }
});

// Handle player list updates
socket.on('update_player_list', (data) => {
    const playersList = data.players;
    const playersContainer = document.getElementById('playersList');

    // Clear existing list and update with new players
    playersContainer.innerHTML = '';
    playersList.forEach(player => {
        const playerItem = document.createElement('li');
        playerItem.classList.add('list-group-item');
        playerItem.textContent = player;
        playersContainer.appendChild(playerItem);
    });
});

// Start game only for the host
document.getElementById('startGame').addEventListener('click', () => {
    const timerValue = document.getElementById('timerInput').value || 100;
    socket.emit('start_game', { room: gameID });
    socket.emit('start_timer', { room: gameID, time: timerValue });
    document.getElementById('startGame').disabled = true;  // Disable start game button
});

// Handle timer countdown
socket.on('start_timer', (data) => {
    let timeLeft = data.time;
    const timerElement = document.getElementById('timer');

    const timerInterval = setInterval(() => {
        if (timeLeft <= 0) {
            clearInterval(timerInterval);
            socket.emit('finish_game', { room: gameID });
        } else {
            timerElement.textContent = timeLeft;
            timeLeft--;
        }
    }, 1000);
});

// Handle answer submission
document.getElementById('submitAnswers').addEventListener('click', () => {
    const answers = {};
    for (let i = 0; i < 7; i++) {
        const question = document.getElementById(`question${i}`).value;
        answers[i] = question;
    }
    socket.emit('submit_answer', { username: username, room: gameID, answers: answers });
});

// Display answers when the game finishes
socket.on('game_finished', (data) => {
    const answersContainer = document.getElementById('answersList');
    answersContainer.innerHTML = '';

    data.players.forEach(player => {
        const playerAnswers = data.answers[player];
        const answersElement = document.createElement('div');
        answersElement.innerHTML = `<h5>${player}'s Answers:</h5><ul>${Object.values(playerAnswers).map(answer => `<li>${answer}</li>`).join('')}</ul>`;
        answersContainer.appendChild(answersElement);
    });
});

// Reset the game (host can trigger this)
document.getElementById('resetGame').addEventListener('click', () => {
    socket.emit('reset_game', { room: gameID, host: username });
});
