import os
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, render_template
from flask_socketio import SocketIO

from config import Config
from routes.ai_routes import ai_bp
from routes.interview_routes import interview_bp
from webrtc.signaling import register_signaling_events

app = Flask(__name__)
app.config.from_object(Config)

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading",
    logger=False,
    engineio_logger=False
)

app.register_blueprint(ai_bp)
app.register_blueprint(interview_bp)
register_signaling_events(socketio)


@app.route("/")
def home():
    return render_template("index.html")


@app.errorhandler(404)
def not_found(e):
    return render_template("index.html"), 404


if __name__ == "__main__":
    os.makedirs(Config.AUDIO_FOLDER, exist_ok=True)
    os.makedirs(Config.ANSWERS_FOLDER, exist_ok=True)

    print("InterviewOS - AI Cohort Interview Agent")
    print(f"Running at http://{Config.HOST}:{Config.PORT}")
    print(f"Local Access: http://localhost:{Config.PORT}")

    socketio.run(
        app,
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
