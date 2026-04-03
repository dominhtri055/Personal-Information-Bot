from flask import Flask, render_template, request
from Bot import search_person

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        hint = request.form.get("hint", "").strip()

        if not name:
            error = "Please enter a name."
        else:
            try:
                person = search_person(name, hint)
                result = person
            except Exception as e:
                error = f"Error: {str(e)}"

    return render_template("index.html", result=result, error=error)

if __name__ == "__main__":
    app.run(debug=True)