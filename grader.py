import requests

token = "1726~bpIkiAOKiYLhv0KOfX7ScaX0ggeK0qEliRh34tqIjnPintrBLLX7nfe6cXEx1uF7"
endpoint = "https://k-state.instructure.com/api/v1/courses/89156/"

users_response = requests.get(
    "{0}/users?access_token={1}&per_page=1000".format(endpoint, token))


print(users_response.status_code)
