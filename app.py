from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from flask_session import Session
import piazza_conn
from main import process_question_from_web

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Flask-Session configuration
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user_email = data['email']
    user_password = data['password']
    print(user_email, user_password)
    
    # Here, you should authenticate with Piazza and store the session details.
    p = piazza_conn.create_piazza_object()
    success = piazza_conn.login_to_piazza(p, user_email, user_password)
    print(success)
    if success:
        session['email'] = user_email
        session['password'] = user_password
        session.modified = True
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'message': 'Login failed'}), 401


@app.route('/logout', methods=['POST'])
def logout():
    # Clear the session
    session.clear()
    return jsonify({'message': 'You have been logged out'}), 200


@app.route('/process-question', methods=['POST'])
def process_question():
    if 'email' in session and 'password' in session:
        data = request.get_json()
        question = data['question']
        
        # Here, use the session information instead of logging in each time
        email = session['email']
        password = session['password']
        final_response = process_question_from_web(question, email, password)
        return jsonify(final_response), 200
    else:
        print("Not logged in")
        return jsonify({'message': 'Unauthorized'}), 401


@app.route('/snapshots/<filename>')
def serve_snapshot(filename):
    return send_from_directory('snapshots', filename)


if __name__ == '__main__':
    app.run(debug=True)

