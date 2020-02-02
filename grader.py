# Author: Kaid Mossburgh

import requests
import pandas
import json
import re

# [TODO] Add support for Text and Excel files
# [TODO] Use multiple query search terms if the previous failed

# Canvas API endpoint for the CIS 018 course
endpoint = "https://k-state.instructure.com/api/v1/courses/89156/"

# [Deprecated]
# Gets all users in CIS 018
def get_users():

	# Requires a valid Canvas authentication token
	with open("token.txt") as token_file:

		token = token_file.readline()
		request_data = {
		
			"access_token": token,
			"search_term": 100,
		}
		
		# Deal with pagination by reviewing the "link" response header
		users = requests.get("{}/search_users".format(endpoint), data = request_data)
		links = re.findall('\<(.*?)\>', users.headers['link'])
		
		# Append each user list corresponding to a page to a singular list of user pages
		pages = []
		for link in links:
		
			response = requests.get(link, data = {"access_token": token})
			pages.append(response.text)
		
		# Append each user into a singular list of users
		users = []
		for page in pages:
			for user in json.loads(page):
			
				users.append(user)
		
		return users

# Searches for a user using the provided search term
def search_users(term):

	# Requires a valid Canvas authentication token
	with open("token.txt") as token_file:

		token = token_file.readline()
		request_data = {
			"access_token": token,
			"search_term": term,
		}
		
		# Search for the user using the Canvas API
		user = requests.get("{}/search_users".format(endpoint), data = request_data)
		return json.loads(user.text)
		
# Change string to lowercase and remove non-alphabetic characters
def format_header(header):

	return "".join(re.findall('[a-z]', header.lower()))

# Gets all students from the attendance file (CSV)
def get_attendees(file):
	
	headers = ["eid", "email", "firstname", "lastname", "major"]
	attendees = pandas.read_csv(file, header = 0, usecols = lambda header : format_header(header) in headers)
	
	attendees.columns = map(format_header, attendees.columns)
	
	return attendees
	
def verify_attendance(file, only_cs = True):
	
	# We cut query time down significantly by only validating CS majors
	# However, there are a few foreseen issues with this method
	# Therefore, it is NOT recommended unless you know what you are doing
	for index, student in get_attendees(file).iterrows():
	
		if only_cs and format_header(student["major"]) == "computerscience" or not only_cs:
		
			user = search_users(student["eid"])
			print(user)			
	
	
#users = get_users("token.txt")	
verify_attendance("attendance.csv", only_cs = False)
