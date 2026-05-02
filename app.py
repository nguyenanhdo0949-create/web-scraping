from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

def query_db(keyword=None):
    conn = sqlite3.connect("database/products.db")
    cursor = conn.cursor()

    query = "SELECT title, price, source FROM products WHERE 1=1"
    params = []

    if keyword:
        query += " AND title LIKE ?"
        params.append(f"%{keyword}%")

    cursor.execute(query, params)
    data = cursor.fetchall()

    conn.close()
    return data


@app.route("/")
def home():
    data = query_db()
    return render_template("index.html", products=data)


@app.route("/search")
def search():
    keyword = request.args.get("keyword", "")
    data = query_db(keyword)
    return jsonify({"data": data})


if __name__ == "__main__":
    app.run(debug=True)