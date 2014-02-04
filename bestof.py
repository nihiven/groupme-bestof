# configuration
group_ids = ["1516779", "1435713"]
base_url = "https://api.groupme.com/v3/"
access_token = "19a5dd8070060131ed2c727e4f5cb2e5"
like_threshold = 3
context_lines = 3 # x before and x after
forty_eight_hours_ago = int(time.time() - 86400)

# required libraries
import sys
import time
import json
import urllib2
from urllib2 import urlopen
from time import sleep

# base groupme api call
def api_call(command, parms=None):
	command_string = base_url + command + "?token=" + access_token

	if parms:
		for parm in parms:
			command_string += "&"+parm
#	print command_string

	data = urlopen(command_string).read()
	obj = json.loads(data)

	return_code = obj["meta"]["code"]
	if not return_code == 200:
		print "api error: " + str(return_code)
		print obj["meta"]["errors"]
		return None

	return obj

# get group info
def get_group(group_id):
	command_string = "groups/"+group_id
	return api_call(command_string)

def get_messages(group_id, before_id=False):
	command_string = "groups/"+group_id+"/messages"
	parms = None

	# add parameters as array
	if before_id:
		parms = {"before_id=" + before_id}

	return api_call(command_string, parms)

#def get_context(message_id, lines):
	# get x lines before and after favorite

for group_id in group_ids:
	best_of = []

	# get latest message id
	data = get_group(group_id)
	latest_message = data["response"]["messages"]["last_message_id"]
	created_at = data["response"]["messages"]["last_message_created_at"]

	print "Analyzing: " + data["response"]["name"]

	# go back through every message in the last 48 hours
	while created_at > forty_eight_hours_ago:
		messages = get_messages(group_id, latest_message)["response"]["messages"]
		message_ids = []
		
		# no messages returned, continue looping
		if not messages:
			continue

		for message in messages:
			likes = len(message["favorited_by"])
			message_ids.append([message["id"],message["created_at"],likes])

			# is this a best of?
			if likes >= like_threshold:
				best_of.append(message)
				print message["name"] + "("+str(likes)+"):", message["text"]

		# find oldest message in this group of messages
		oldest_message = sorted(message_ids, key=lambda created: created[0])[0]
		latest_message = oldest_message[0]
		created_at = oldest_message[1]

		# wait, so we don't kill the api
		sleep(5)

	# end while

	# do something with results
	# print best_of
	
# end for