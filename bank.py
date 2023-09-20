from flask import Flask, render_template, request, jsonify
import re, us, requests, json, os
from waitress import serve

app = Flask(__name__)
port = int(os.environ.get("PORT", 8080))
#a US states convenience
states = [state.abbr for state in us.states.STATES]

#for use in the API call
alloy_base_url = "https://sandbox.alloy.co/v1/evaluations"

# i'm not a regex expert; i looked these up

def is_zip_formatted(zip_code):
    pattern = r'^\d{5}(?:-\d{4})?$'
    return bool(re.match(pattern, str(zip_code)))

def is_valid_ssn(ssn):
    # return True if valid, False if not valid
    pattern = r"^\d{3}\d{2}\d{4}$"
    return bool(re.match(pattern,ssn))

def is_valid_email(email):
    # return True if valid, False if not valid
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))

def is_valid_dob(dob):
    # return True if valid, False if not valid
    pattern = r"^\d{4}-\d{2}-\d{2}$"
    return bool(re.match(pattern, dob))

def is_valid_country(country):
    # return True if valid, False if not valid
    pattern = r'[uU][sS]'
    return bool(re.match(pattern,country))

#make API call to evaluations endpoint
def evaluation_get(data_body):
    url = alloy_base_url
    #a dict
    payload = {
        "name_first": data_body["firstname"],
        "name_last": data_body["lastname"],
        "address_line_1": data_body["addressone"],
        "address_line_2": data_body["addresstwo"],
        "address_city": data_body["addresscity"],
        "address_state": data_body["addressstate"],
        "address_postal_code": data_body["addressstate"],
        "address_country_code": data_body["addresscountry"],
        "document_ssn": data_body["ssn"],
        "birth_date": data_body["dob"]
    }
    #turn that dict to json, which the endpoint expects
    payload_to_json = json.dumps(payload)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {data_body["base_64_str"]}'
    }

    response = requests.request("POST",url,headers=headers,data=payload_to_json)
    return response



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/apply', methods=['POST'])
def apply():
    return_str = ''
    if request.method=="POST":
        form_data = request.form.to_dict()

        #some input validations
        #equal True if valid, equal False if not valid
        valid_us_state = form_data['addressstate'] in states
        valid_zip_code = is_zip_formatted(form_data['addresszip'])
        valid_ssn = is_valid_ssn(form_data['ssn'])
        valid_email = is_valid_email(form_data['email'])
        valid_dob = is_valid_dob(form_data['dob'])
        valid_country_code = is_valid_country(form_data['addresscountry'])
        all_input_valid = False not in [v for v in [valid_us_state,valid_zip_code,valid_ssn,valid_email,valid_dob,valid_country_code]]

        if all_input_valid:
            #format req to json
            req_json_body = jsonify(form_data)
            
            #create and execute API call
            alloy_response = evaluation_get(req_json_body.json)

            #take the API response and do things
            if alloy_response.json()['status_code']==201|200:   
                #depending on the outcome value ('Approve', 'Deny', 'Manual Review'), render various things in the response area
                choice = alloy_response.json()['summary']['outcome']
                match choice:    
                    case 'Denied':
                        return_str = "We're sorry, your application was unsuccessful."
                    case 'Approved':
                        return_str = "Congratulations, you were approved!"
                    case 'Manual Review':
                        return_str = "Thanks for submitting your application, we’ll be in touch shortly."
            else:
                return_str = "Seems like there's some weirdness here on our end."
        else:
            return_str = "Looks like some input was not valid"
    else:
        return_str = "Seems like there's some weirdness here on our end."       
    
    return render_template("response_area.html", response=return_str)

if __name__ == '__main__':
    serve(
        app,
        host='0.0.0.0',
        port=8080
        )