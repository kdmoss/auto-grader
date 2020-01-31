import requests

token = "1726~bpIkiAOKiYLhv0KOfX7ScaX0ggeK0qEliRh34tqIjnPintrBLLX7nfe6cXEx1uF7"
endpoint = "https://k-state.instructure.com/api/v1/courses/89156/"

request_data = {"access_token": token, "per_page": 400}
users_response = requests.get("{}/users".format(endpoint), data=request_data)

print(users_response.text)
