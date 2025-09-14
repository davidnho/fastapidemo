from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)
DB_NAME = "database.db"

def query_db(query, args=(), one=False):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query, args)
    rows = cur.fetchall()
    conn.close()
    return (rows[0] if rows else None) if one else rows

@app.route("/")
def home():
    return {"message": "Welcome to the Flask SQLite API"}

@app.route("/users")
def get_users():
    rows = query_db("SELECT * FROM users")
    return jsonify([dict(row) for row in rows])

@app.route("/users/<int:user_id>")
def get_user(user_id):
    row = query_db("SELECT * FROM users WHERE id = ?", (user_id,), one=True)
    return jsonify(dict(row)) if row else ({"error": "User not found"}, 404)

@app.route("/products")
def get_products():
    rows = query_db("SELECT * FROM products")
    return jsonify([dict(row) for row in rows])

@app.route("/products/<int:product_id>")
def get_product(product_id):
    row = query_db("SELECT * FROM products WHERE id = ?", (product_id,), one=True)
    return jsonify(dict(row)) if row else ({"error": "Product not found"}, 404)

if __name__ == "__main__":
    app.run(debug=True)
