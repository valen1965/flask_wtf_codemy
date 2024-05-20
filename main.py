from flask import Flask, render_template

# Create Flask Instance
app = Flask(__name__)

# FILTERS !!!!!!

# safe
# capitalize
# lower
# upper
# title
# trim
# striptags
# '''


# Create a route decorator
@app.route("/")
def index():
    first_name = "John"
    stuff = "This is <strong>Bold</strong> Text"

    favorite_pizza = ["Pepperoni", "Cheese", "Mushrooms", 41]

    return render_template("index.html",
                           first_name=first_name,
                           stuff=stuff,
                           favorite_pizza=favorite_pizza)


@app.route("/user/<name>")
def user(name):
    return render_template("/user.html", user_name=name)


# Create Custom Error Pages

# Invalid URL

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def page_not_found(error):
    render_template("500.html"), 500


if __name__ == "__main__":
    app.run(debug=True)
