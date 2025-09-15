# Flask API Guide
https://chatgpt.com/share/68c75aa9-059c-8010-b159-979a208615fd

Got it 👍 Let’s create a **simple Flask API project** that serves data from an **SQLite database**.

We’ll include:

* SQLite `CREATE TABLE` script
* Sample data insertion
* A small Flask app with routes to get data

---

## 1. SQLite Table Script

```sql
-- create a sample database schema
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL
);

CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL
);

-- insert sample data
INSERT INTO users (name, email) VALUES 
('Alice', 'alice@example.com'),
('Bob', 'bob@example.com'),
('Charlie', 'charlie@example.com');

INSERT INTO products (name, price) VALUES
('Laptop', 1200.50),
('Phone', 650.00),
('Headphones', 85.75);
```

Run this in `sqlite3` to create a `database.db` file.

---

## 2. Flask API Project

**File structure**

```
flask_api/
│── app.py
│── database.db   (generated after running sqlite scripts)
│── requirements.txt
```

**requirements.txt**

```
flask
flask_sqlalchemy
```

---

**app.py**

```python
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
```

---

## 3. Running the API

1. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```
2. Create the database (`database.db`) using the SQL scripts above.

   ```bash
   sqlite3 database.db < schema.sql
   ```
3. Run the Flask app

   ```bash
   python app.py
   ```

---

## 4. Test the API

* `GET /` → Welcome message
* `GET /users` → List all users
* `GET /users/1` → Get user by ID
* `GET /products` → List all products
* `GET /products/1` → Get product by ID

---

## CRUD

Perfect 👍 let’s extend it to a **full CRUD API** using **Flask + SQLite**.

We’ll add `POST`, `PUT`, and `DELETE` routes for **users** and **products**.

---

## 1. Updated `app.py`

```python
from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)
DB_NAME = "database.db"


# ---------- Helper Functions ----------
def query_db(query, args=(), one=False, commit=False):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query, args)
    
    if commit:
        conn.commit()
        conn.close()
        return cur.lastrowid

    rows = cur.fetchall()
    conn.close()
    return (rows[0] if rows else None) if one else rows


# ---------- Routes ----------
@app.route("/")
def home():
    return {"message": "Welcome to the Flask SQLite API"}


# ---------------- USERS ----------------
@app.route("/users", methods=["GET"])
def get_users():
    rows = query_db("SELECT * FROM users")
    return jsonify([dict(row) for row in rows])


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    row = query_db("SELECT * FROM users WHERE id = ?", (user_id,), one=True)
    return jsonify(dict(row)) if row else ({"error": "User not found"}, 404)


@app.route("/users", methods=["POST"])
def add_user():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    if not name or not email:
        return {"error": "Name and email required"}, 400

    try:
        new_id = query_db(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            (name, email),
            commit=True
        )
        return {"message": "User created", "id": new_id}, 201
    except sqlite3.IntegrityError:
        return {"error": "Email must be unique"}, 400


@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.json
    name = data.get("name")
    email = data.get("email")

    query_db(
        "UPDATE users SET name = ?, email = ? WHERE id = ?",
        (name, email, user_id),
        commit=True
    )
    return {"message": "User updated"}


@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    query_db("DELETE FROM users WHERE id = ?", (user_id,), commit=True)
    return {"message": "User deleted"}


# ---------------- PRODUCTS ----------------
@app.route("/products", methods=["GET"])
def get_products():
    rows = query_db("SELECT * FROM products")
    return jsonify([dict(row) for row in rows])


@app.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    row = query_db("SELECT * FROM products WHERE id = ?", (product_id,), one=True)
    return jsonify(dict(row)) if row else ({"error": "Product not found"}, 404)


@app.route("/products", methods=["POST"])
def add_product():
    data = request.json
    name = data.get("name")
    price = data.get("price")
    if not name or price is None:
        return {"error": "Name and price required"}, 400

    new_id = query_db(
        "INSERT INTO products (name, price) VALUES (?, ?)",
        (name, price),
        commit=True
    )
    return {"message": "Product created", "id": new_id}, 201


@app.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    data = request.json
    name = data.get("name")
    price = data.get("price")

    query_db(
        "UPDATE products SET name = ?, price = ? WHERE id = ?",
        (name, price, product_id),
        commit=True
    )
    return {"message": "Product updated"}


@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    query_db("DELETE FROM products WHERE id = ?", (product_id,), commit=True)
    return {"message": "Product deleted"}


# ---------- Run ----------
if __name__ == "__main__":
    app.run(debug=True)
```

---

## 2. Example Requests (using `curl`)

* **Create user**

  ```bash
  curl -X POST http://127.0.0.1:5000/users \
       -H "Content-Type: application/json" \
       -d '{"name": "David", "email": "david@example.com"}'
  ```

* **Update user**

  ```bash
  curl -X PUT http://127.0.0.1:5000/users/1 \
       -H "Content-Type: application/json" \
       -d '{"name": "Alice Updated", "email": "alice_new@example.com"}'
  ```

* **Delete user**

  ```bash
  curl -X DELETE http://127.0.0.1:5000/users/3
  ```

* **Create product**

  ```bash
  curl -X POST http://127.0.0.1:5000/products \
       -H "Content-Type: application/json" \
       -d '{"name": "Tablet", "price": 300.0}'
  ```

---

👉 Now you have a **complete CRUD API with Flask + SQLite** 🎉


## AUTOMATICALY CREATING SQLITE DATABASE

Let’s make it even easier by **automatically creating the SQLite database and seeding sample data** when it doesn’t exist.

We’ll add a small **database initialization function** inside the Flask project.

---

## 1. Updated `app.py` (with auto DB + seed)

```python
from flask import Flask, jsonify, request
import sqlite3
import os

app = Flask(__name__)
DB_NAME = "database.db"


# ---------- Database Setup ----------
def init_db():
    """Create tables and seed data if database does not exist"""
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()

        # create tables
        cur.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
        """)

        cur.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL
        )
        """)

        # insert seed data
        cur.executemany(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            [
                ("Alice", "alice@example.com"),
                ("Bob", "bob@example.com"),
                ("Charlie", "charlie@example.com"),
            ]
        )

        cur.executemany(
            "INSERT INTO products (name, price) VALUES (?, ?)",
            [
                ("Laptop", 1200.50),
                ("Phone", 650.00),
                ("Headphones", 85.75),
            ]
        )

        conn.commit()
        conn.close()
        print("✅ Database created and seeded!")


# ---------- Helper Function ----------
def query_db(query, args=(), one=False, commit=False):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query, args)
    
    if commit:
        conn.commit()
        conn.close()
        return cur.lastrowid

    rows = cur.fetchall()
    conn.close()
    return (rows[0] if rows else None) if one else rows


# ---------- Routes ----------
@app.route("/")
def home():
    return {"message": "Welcome to the Flask SQLite API"}


# ---------------- USERS ----------------
@app.route("/users", methods=["GET"])
def get_users():
    rows = query_db("SELECT * FROM users")
    return jsonify([dict(row) for row in rows])


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    row = query_db("SELECT * FROM users WHERE id = ?", (user_id,), one=True)
    return jsonify(dict(row)) if row else ({"error": "User not found"}, 404)


@app.route("/users", methods=["POST"])
def add_user():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    if not name or not email:
        return {"error": "Name and email required"}, 400

    try:
        new_id = query_db(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            (name, email),
            commit=True
        )
        return {"message": "User created", "id": new_id}, 201
    except sqlite3.IntegrityError:
        return {"error": "Email must be unique"}, 400


@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.json
    name = data.get("name")
    email = data.get("email")

    query_db(
        "UPDATE users SET name = ?, email = ? WHERE id = ?",
        (name, email, user_id),
        commit=True
    )
    return {"message": "User updated"}


@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    query_db("DELETE FROM users WHERE id = ?", (user_id,), commit=True)
    return {"message": "User deleted"}


# ---------------- PRODUCTS ----------------
@app.route("/products", methods=["GET"])
def get_products():
    rows = query_db("SELECT * FROM products")
    return jsonify([dict(row) for row in rows])


@app.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    row = query_db("SELECT * FROM products WHERE id = ?", (product_id,), one=True)
    return jsonify(dict(row)) if row else ({"error": "Product not found"}, 404)


@app.route("/products", methods=["POST"])
def add_product():
    data = request.json
    name = data.get("name")
    price = data.get("price")
    if not name or price is None:
        return {"error": "Name and price required"}, 400

    new_id = query_db(
        "INSERT INTO products (name, price) VALUES (?, ?)",
        (name, price),
        commit=True
    )
    return {"message": "Product created", "id": new_id}, 201


@app.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    data = request.json
    name = data.get("name")
    price = data.get("price")

    query_db(
        "UPDATE products SET name = ?, price = ? WHERE id = ?",
        (name, price, product_id),
        commit=True
    )
    return {"message": "Product updated"}


@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    query_db("DELETE FROM products WHERE id = ?", (product_id,), commit=True)
    return {"message": "Product deleted"}


# ---------- Run ----------
if __name__ == "__main__":
    init_db()  # create DB if not exists
    app.run(debug=True)
```

---

## 2. How It Works

* The first time you run `python app.py`, it will:
  ✅ Create `database.db`
  ✅ Create tables (`users`, `products`)
  ✅ Insert sample rows

* On next runs, it just uses the existing database.

---

## 3. Quick Test

```bash
# Get all users
curl http://127.0.0.1:5000/users

# Add new user
curl -X POST http://127.0.0.1:5000/users \
     -H "Content-Type: application/json" \
     -d '{"name":"David","email":"david@example.com"}'

# Get all products
curl http://127.0.0.1:5000/products
```

---

👉 Now you don’t need to manually run `sqlite3` scripts — it **auto-builds the DB with sample data**.

Do you also want me to **add Swagger/OpenAPI docs** so you can test endpoints from a browser UI (like `/docs`)?

## An API Client

Let’s make the **Flask client** more user-friendly by adding a **simple HTML frontend** (with forms and tables) to interact with the API.

We’ll extend the client to:

* Show a table of **Users** and **Products**
* Add new records via **HTML forms**
* Use `requests` under the hood to call the API

---

## 1. Project Structure

```
flask_client/
│── client.py
│── templates/
│     ├── base.html
│     ├── users.html
│     └── products.html
```

---

## 2. Updated `client.py`

```python
from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)
API_URL = "http://127.0.0.1:5000"  # Flask API server


@app.route("/")
def home():
    return render_template("base.html")


# ---------------- USERS ----------------
@app.route("/users")
def show_users():
    r = requests.get(f"{API_URL}/users")
    users = r.json()
    return render_template("users.html", users=users)


@app.route("/users/add", methods=["POST"])
def add_user():
    name = request.form["name"]
    email = request.form["email"]
    requests.post(f"{API_URL}/users", json={"name": name, "email": email})
    return redirect(url_for("show_users"))


@app.route("/users/delete/<int:user_id>")
def delete_user(user_id):
    requests.delete(f"{API_URL}/users/{user_id}")
    return redirect(url_for("show_users"))


# ---------------- PRODUCTS ----------------
@app.route("/products")
def show_products():
    r = requests.get(f"{API_URL}/products")
    products = r.json()
    return render_template("products.html", products=products)


@app.route("/products/add", methods=["POST"])
def add_product():
    name = request.form["name"]
    price = request.form["price"]
    requests.post(f"{API_URL}/products", json={"name": name, "price": float(price)})
    return redirect(url_for("show_products"))


@app.route("/products/delete/<int:product_id>")
def delete_product(product_id):
    requests.delete(f"{API_URL}/products/{product_id}")
    return redirect(url_for("show_products"))


if __name__ == "__main__":
    app.run(port=6000, debug=True)
```

---

## 3. Templates

### `templates/base.html`

```html
<!DOCTYPE html>
<html>
<head>
    <title>Flask Client</title>
    <link rel="stylesheet" href="https://cdn.simplecss.org/simple.min.css">
</head>
<body>
    <header>
        <h1>Flask Client for API</h1>
        <nav>
            <a href="{{ url_for('show_users') }}">Users</a> |
            <a href="{{ url_for('show_products') }}">Products</a>
        </nav>
    </header>
    <main>
        {% block content %}{% endblock %}
    </main>
</body>
</html>
```

---

### `templates/users.html`

```html
{% extends "base.html" %}
{% block content %}
<h2>Users</h2>

<form method="POST" action="{{ url_for('add_user') }}">
    <input type="text" name="name" placeholder="Name" required>
    <input type="email" name="email" placeholder="Email" required>
    <button type="submit">Add User</button>
</form>

<table>
    <thead>
        <tr><th>ID</th><th>Name</th><th>Email</th><th>Actions</th></tr>
    </thead>
    <tbody>
    {% for user in users %}
        <tr>
            <td>{{ user.id }}</td>
            <td>{{ user.name }}</td>
            <td>{{ user.email }}</td>
            <td>
                <a href="{{ url_for('delete_user', user_id=user.id) }}">Delete</a>
            </td>
        </tr>
    {% endfor %}
    </tbody>
</table>
{% endblock %}
```

---

### `templates/products.html`

```html
{% extends "base.html" %}
{% block content %}
<h2>Products</h2>

<form method="POST" action="{{ url_for('add_product') }}">
    <input type="text" name="name" placeholder="Product Name" required>
    <input type="number" step="0.01" name="price" placeholder="Price" required>
    <button type="submit">Add Product</button>
</form>

<table>
    <thead>
        <tr><th>ID</th><th>Name</th><th>Price</th><th>Actions</th></tr>
    </thead>
    <tbody>
    {% for product in products %}
        <tr>
            <td>{{ product.id }}</td>
            <td>{{ product.name }}</td>
            <td>${{ "%.2f"|format(product.price) }}</td>
            <td>
                <a href="{{ url_for('delete_product', product_id=product.id) }}">Delete</a>
            </td>
        </tr>
    {% endfor %}
    </tbody>
</table>
{% endblock %}
```

---

## 4. How to Run

1. Start your **API server** (port `5000`):

   ```bash
   cd flask_api
   python app.py
   ```

2. Start the **client app** (port `6000`):

   ```bash
   cd flask_client
   python client.py
   ```

3. Open browser at:

   * `http://127.0.0.1:6000/users` → manage users
   * `http://127.0.0.1:6000/products` → manage products

---

👉 Now you have a **client with HTML frontend** that can:
✔ List Users & Products
✔ Add new ones via form
✔ Delete existing ones

Do you also want me to add **Update (edit) forms** for users/products, so you can change values directly from the frontend?

