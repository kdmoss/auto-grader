# Author: Kaid Mossburgh

import requests
import pandas
import math
import json
import re

# [TODO] Add support for Text and Excel files
# [TODO] Use multiple query search terms if the previous failed
# [TODO] Handle cases for attendees with middle names

# Canvas API endpoint for the CIS 018 course
endpoint = "https://k-state.instructure.com/api/v1/courses/89156"

# Change string to lowercase and remove non-alphabetic characters
def format_header(header):

	return "".join(re.findall('[a-z]', header.lower()))

# Combine first and last name
def format_fullname(firstname, lastname):

	# We will try to find the user given only a first or last name, but there is no guarantees
	if type(lastname) is float and math.isnan(lastname):
		return firstname.capitalize()
		
	if type(firstname) is float and math.isnan(firstname):
		return lastname.capitalize()
		
	return "{} {}".format(firstname, lastname).title()
	
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
	
# Gets all students from the attendance file (CSV)
def get_attendees(file):
	
	headers = ["eid", "email", "fullname", "firstname", "lastname", "major"]

	attendees = pandas.read_csv(file, header = 0, usecols = lambda header : format_header(header) in headers)
	attendees.columns = map(format_header, attendees.columns)
	
	return attendees

# Grades the given users (assignment) attendance 
def grade_attendance(asgmt_id, uid):

	# Requires a valid Canvas authentication token
	with open("token.txt") as token_file:

		token = token_file.readline()
		form = {"submission": {"posted_grade": "complete"}, "access_token": token}
		content = {"Content-Type": "application/json"}
		
		submission = requests.put("{}/assignments/{}/submissions/{}".format(endpoint, asgmt_id, uid), data = json.dumps(form), headers = content)

# Get a unique attribute by order of priority
def get_unique_attribute(student):
	
	headers = ["eid", "email", "fullname", "firstname", "lastname"]

	for header in headers:
		if header in student:
		
			# Worst case scenario the only unique attribute is their name
			if header == "firstname" and "lastname" in student:
				return format_fullname(student["firstname"], student["lastname"])
				
			return student[header]
	return None

# Verify attendance for all users in the attendance file
def verify_attendance(file, asgmt_id):
	
	# We cut query time down significantly by only validating CS majors
	# However, there are a few foreseen issues with this method
	# Therefore, it is NOT recommended unless you know what you are doing
	for index, student in get_attendees(file).iterrows():
			
		# Search for user using some unique attribute
		print(get_unique_attribute(student))
		user = search_users(get_unique_attribute(student))
		print(user)
		
		# If the attendee isn't unique then we need more information
		if len(user) == 1 and "id" in user[0]:
			grade_attendance(asgmt_id, user[0]["id"])
			print("\n")
	
	
verify_attendance("attendance.csv", asgmt_id = 999361, only_cs = False)
