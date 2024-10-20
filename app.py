import sqlite3
import logging
from flask_cors import CORS
from flask import Flask, request, jsonify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = Flask(__name__)
CORS(app)

def init_db():
    logger.info('>>>>>>>>>>> Initializando la base de datos')
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS game_info (
                    match_number INTEGER PRIMARY KEY,
                    player1_name TEXT,
                    player1_points INTEGER,
                    player2_name TEXT,
                    player2_points INTEGER,
                    playing BOOLEAN,
                    match_date TEXT
                )''')
    conn.commit()
    conn.close()

@app.route('/game-info/<int:match_number>', methods=['GET'])
def get_game_info(match_number):
    logger.info(f">>>>>>>>>>> Entrando a get_game_info con match_number: {match_number}")
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute('SELECT * FROM game_info WHERE match_number = ?', (match_number,))
    game_info = c.fetchone()
    conn.close()
    if game_info:
        return jsonify({
            "player1": {"name": game_info[1], "points": game_info[2]},
            "player2": {"name": game_info[3], "points": game_info[4]},
            "matchNumber": game_info[0],
            "playing": bool(game_info[5]),
            "matchDate": game_info[6]
        })
    else:
        return jsonify({"error": "No se encontró información del juego para el número de partido"}), 404

@app.route('/game-info', methods=['POST'])
def update_game_info():
    logger.info(">>>>>>>>>>> Entering update_game_info")
    data = request.get_json()
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute('''INSERT INTO game_info (match_number, player1_name, player1_points, player2_name, player2_points, playing, match_date)
                 VALUES (?, ?, ?, ?, ?, ?, ?)
                 ON CONFLICT(match_number) DO UPDATE SET
                 player1_name=excluded.player1_name,
                 player1_points=excluded.player1_points,
                 player2_name=excluded.player2_name,
                 player2_points=excluded.player2_points,
                 playing=excluded.playing,
                 match_date=excluded.match_date''',
              (data['matchNumber'], data['player1']['name'], data['player1']['points'], data['player2']['name'], data['player2']['points'], data['playing'], data['matchDate']))
    conn.commit()
    conn.close()
    return jsonify({"message": "Información del juego actualizada exitosamente"}), 201

@app.route('/game-ids', methods=['GET'])
def get_game_ids():
    logger.info(">>>>>>>>>>> Entrando a get_game_ids")
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute('SELECT match_number FROM game_info')
    game_ids = [row[0] for row in c.fetchall()]
    conn.close()
    return jsonify({"matchNumbers": game_ids})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)