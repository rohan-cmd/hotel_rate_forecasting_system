from flask import Flask, render_template, redirect, url_for, request
from db import get_connection
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# ------------------------------
# DATABASE SETUP
# ------------------------------
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    IF NOT EXISTS (
        SELECT * FROM sys.tables WHERE name = 'user_registrations'
    )
    BEGIN
        CREATE TABLE user_registrations (
            id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWSEQUENTIALID(),
            username NVARCHAR(100) UNIQUE NOT NULL,
            email NVARCHAR(255) UNIQUE NOT NULL,
            password_hash NVARCHAR(255) NOT NULL
        );
    END
    """)

    conn.commit()
    conn.close()

# init_db()   # Run at startup

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about") 
def about():
    return render_template("about.html")

@app.route("/predict")
def predict():
    return render_template("predict.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        # generating hashed_password
        hashed_password = generate_password_hash(password)

        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO user_registrations (username, email, password_hash) VALUES (?, ?, ?)",
                           (username, email, hashed_password))
            conn.commit()
            conn.close()
            return redirect(url_for("login"))
        except:
            conn.close()
            return "Username already exists. Try another."
        
    return render_template("register.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

if __name__ == "__main__":
    app.run(debug=True)