# adamantium-bank

https://adamantium-bank-267459cc5704.herokuapp.com

A banking app that processes form data safely, validating input in the form fields and also on the server,
makes an API call to the financial institution to submit the form as an application to apply for 
financing, and then, depending on the API response, dynamically displays informative messages to the user.

The form takes a base_64 encoded string that comes from properly encoding a `token:secret` set of credentials
which are authorized to call the API endpoint.

This application has a front end that utilizes [htmx](https://htmx.org) for the form action, and a python (Flask) back end to
handle request routing and validating user form input, make outgoing API calls, process the return data, and
display information to the user.


