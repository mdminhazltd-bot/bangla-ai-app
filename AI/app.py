from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

# ডাটাবেজ কনফিগারেশন
database_url = os.environ.get('DATABASE_URL')

if database_url:
    # Render PostgreSQL দেয় postgres:// দিয়ে, SQLAlchemy চায় postgresql://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # লোকাল টেস্টের জন্য SQLite ব্যবহার হবে
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'database', 'users.db')}"

db = SQLAlchemy(app)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ইউজার টেবিল
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(300), nullable=False)

with app.app_context():
    db.create_all()

# হোমপেজ রুট
@app.route("/")
def home():
    return jsonify({"message": "বাংলা AI ব্যাকএন্ড চলছে ✅"})

# সাইনআপ রুট
@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not name or not email or not password:
        return jsonify({"error": "সব তথ্য পূরণ করুন"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "এই ইমেইল দিয়ে আগেই অ্যাকাউন্ট আছে"}), 400

    hashed_pw = generate_password_hash(password)
    new_user = User(name=name, email=email, password_hash=hashed_pw)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "অ্যাকাউন্ট তৈরি হয়েছে"}), 201

# লগইন রুট
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "ইমেইল বা পাসওয়ার্ড ভুল"}), 401

    return jsonify({
        "message": "লগইন সফল হয়েছে",
        "user": {"name": user.name, "email": user.email}
    }), 200

# AI প্রশ্নের রুট
@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    user_question = data.get("question", "")

    if not user_question:
        return jsonify({"error": "কোনো প্রশ্ন দেওয়া হয়নি"}), 400

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "তুমি একজন সহায়ক বাংলা AI অ্যাসিস্ট্যান্ট। সবসময় শুদ্ধ ও স্বাভাবিক বাংলায় উত্তর দেবে।"},
                {"role": "user", "content": user_question}
            ],
            temperature=0.7,
        )
        return jsonify({"answer": response.choices[0].message.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)