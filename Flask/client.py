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
