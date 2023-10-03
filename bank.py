from flask import Flask, render_template, request, jsonify
import re, us, requests, json, os
from waitress import serve
from requests.exceptions import HTTPError, InvalidHeader, InvalidURL

from fastapi import FastAPI
from pydantic import BaseModel, Field, constr, validator
from typing import List

app = FastAPI()

class FormEntry(BaseModel):
    # valid_us_state = form_data['addressstate'] in states
    # valid_zip_code = is_zip_formatted(form_data['addresszip'])
    # valid_ssn = is_valid_ssn(form_data['ssn'])
    # valid_email = is_valid_email(form_data['email'])
    # valid_dob = is_valid_dob(form_data['dob'])
    # valid_country_code = is_valid_country(form_data['addresscountry'])

    #a US states convenience
    states: List[str] = [state.abbr for state in us.states.STATES]

    #states validator
    @validator('valid_us_state')
    def validate_us_state(states, item):
        if item not in states:
            raise ValueError(f'Value {item} not a valid US state')
        
    #zip code validator
    valid_zip_code: str = Field(pattern=r'^\d{5}(?:-\d{4})?$')

    #ssn validator
    valid_ssn: str = Field(pattern=r"^\d{3}\d{2}\d{4}$")

    #email validator
    valid_email: str = Field(pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    #dob validator
    valid_dob: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")

    #valid country code
    # TODO etc

#heroku will need port 8000
port = int(os.environ.get("PORT", 8000))

#for use in the API call
alloy_base_url = "https://sandbox.alloy.co/v1/evaluations"

# i'm not a regex expert; i looked these up

# def is_zip_formatted(zip_code):
#     pattern = r'^\d{5}(?:-\d{4})?$'
#     return bool(re.match(pattern, str(zip_code)))

# def is_valid_ssn(ssn):
#     # return True if valid, False if not valid
#     pattern = r"^\d{3}\d{2}\d{4}$"
#     return bool(re.match(pattern,ssn))

# def is_valid_email(email):
#     # return True if valid, False if not valid
#     pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
#     return bool(re.match(pattern, email))

# def is_valid_dob(dob):
#     # return True if valid, False if not valid
#     pattern = r"^\d{4}-\d{2}-\d{2}$"
#     return bool(re.match(pattern, dob))

def is_valid_country(country):
    # return True if valid, False if not valid
    pattern = r'[uU][sS]'
    return bool(re.match(pattern,country))

# make API call to evaluations endpoint
# if this application was refactored using FastAPI [https://fastapi.tiangolo.com]
# we could make this function asyncronous. Flask requires it to be syncronous.
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
        #'request' here is an object of type Request containing all the data of the request we'll need
        form_data = request.form.to_dict()



        #some input validations
        #equal True if valid, equal False if not valid

        # 10/2 these will be undefined now.
        valid_us_state = form_data['addressstate'] in states
        valid_zip_code = is_zip_formatted(form_data['addresszip'])
        valid_ssn = is_valid_ssn(form_data['ssn'])
        valid_email = is_valid_email(form_data['email'])
        valid_dob = is_valid_dob(form_data['dob'])
        valid_country_code = is_valid_country(form_data['addresscountry'])
        
        ###
        # this can be refactored and optimized. 
        # This should move through a list of "keyname": form_data['keyname'],
        # passing each key:value to a function that contains a match:case block.
        # the match:case block should, depending on the keyname, validate the 
        # form_data['keyname'] against the requisite regex pattern, and then return
        # the boolean. the validations_list should still be a list of 
        # [False,True,False...] etc.
        ###

        ###
        # if this application were refactored using FastAPI, i think a lot of this validation work
        # could be handled by FastAPI's built-in use of Pydantic models (https://docs.pydantic.dev/latest/).
        # Going on this, there should probably be an Application model `class Application(BaseMdel)`
        # where the fields are defined. 
        ###
        validations_list = [v for v in [valid_us_state,valid_zip_code,valid_ssn,valid_email,valid_dob,valid_country_code]]
        
        #is the input all valid?
        all_input_valid = False not in validations_list

        #is the input not at all valid?
        no_input_valid = True not in validations_list

        if no_input_valid:
            return_str = 'Looks like there may be a few issues with your entries.'
        elif all_input_valid:
            #format req to json
            req_json_body = jsonify(form_data)
            
            try:
                #create and execute API call
                alloy_response = evaluation_get(req_json_body.json)
                alloy_response.raise_for_status()
                
                #take the API response and do things 
                #depending on the outcome value ('Approve', 'Deny', 'Manual Review'), render various things in the response area
                choice = alloy_response.json()['summary']['outcome']
                match choice:    
                    case 'Denied':
                        return_str = "We're sorry, your application was unsuccessful."
                    case 'Approved':
                        return_str = "Congratulations, you were approved!"
                    case 'Manual Review':
                        return_str = "Thanks for submitting your application, we’ll be in touch shortly."
            #handle http errors
            except HTTPError as e:
                print("Http error occured: ", e)
                return_str = "Apologies, it seems like there's an issue here on our end."
            except InvalidHeader as e:
                print("There was an invalid header: ", e)
                return_str = "Apologies, it seems like there's an issue here on our end."
            except InvalidURL as e:
                print("There was an issue with the URL validity: ", e)
                return_str = "Apologies, it seems like there's an issue here on our end."
        elif valid_us_state==False:
            return_str = "Please enter a valid US state code."
        #very unlikely scenario where niether all_input_valid nor no_input_valid resolved to True
        else:
            return_str = "Seems like there's some weirdness here on our end."       
    
    return render_template("response_area.html", response=return_str)

if __name__ == '__main__':
    serve(
        app,
        host='0.0.0.0',
        port=port
        )