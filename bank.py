from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/apply', methods=['POST'])
def apply():
    response = "submitted!"
    return render_template("response_area.html", response=response)
    # if request.method == 'POST':
    #     #obtain the relevant form data
    #     lastname = request.form.get('')

if __name__ == '__main__':
    app.run(
        port=8080,
        debug=True
        )