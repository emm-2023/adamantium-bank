from flask import Flask, render_template, request, jsonify
import re, us

app = Flask(__name__)
states = [state.abbr for state in us.states.STATES]

# i'm not a regex expert; i looked these up

def is_zip_formatted(zip_code):
    pattern = r'^\d{5}(?:-\d{4})?$'
    return bool(re.match(pattern, str(zip_code)))

def is_valid_ssn(ssn):
    pattern = r"^(?!000|666)[0-8]\d{2}-(?!00)\d{2}-(?!0000)\d{4}$"
    return bool(re.match(pattern,ssn))

def is_valid_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))

def is_valid_dob(dob):
    pattern = r"^\d{4}-\d{2}-\d{2}$"
    return bool(re.match(pattern, dob))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/apply', methods=['POST'])
def apply():
    if request.method=="POST":
        form_data = request.form.to_dict()
        #some input validations
        valid_us_state = form_data['addressstate'] in states
        valid_zip_code = is_zip_formatted(form_data['addresszip'])
        valid_ssn = is_valid_ssn(form_data['ssn'])
        valid_email = is_valid_email(form_data['email'])
        valid_dob = is_valid_dob(form_data['dob'])

        all_input_valid = [v for v in [valid_us_state,valid_zip_code,valid_ssn,valid_email,valid_dob]]
        print(all_input_valid)
        if all_input_valid:
            req_json_body = jsonify(form_data)
            print(req_json_body)






    return render_template("response_area.html", response="submitted - we're working")

if __name__ == '__main__':
    app.run(
        port=8080,
        debug=True
        )