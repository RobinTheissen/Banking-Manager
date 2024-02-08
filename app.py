from flask import Flask, render_template

app = Flask(__name__)

@app.route('/register', methods=['GET', 'POST'])
def register():


    return render_template("register.html")  # on server validation error