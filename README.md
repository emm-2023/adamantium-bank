# adamantium-bank

A simple banking app that processes form data safely, validating input in the form and also on the server,
makes an API call to the financial institution to submit the form as an application to apply for 
financing, and then, depending on the API response, dynamically displays a message to the user.

The form takes a base_64 encoded string that will come from properly encoding a key:secret set of credentials
which are authorized to call the API endpoint.