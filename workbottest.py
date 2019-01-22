from __future__ import print_function
import requests
from bs4 import BeautifulSoup
import datetime
import time
import re
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools



def main():
	n = 1
	CAL = gcal_login()
	with open('output.txt', 'wt') as clear:
		clear.write('Data:' + '\n')
	with open('case_number_list', 'r+') as inwards:
		for caseNO in inwards:
			caseNO = caseNO.rstrip()
			gather_soup(caseNO, n)
			trim_soup()
			with open('output.txt','at') as outwards:
				date_List = universalize(parse_chunk(chunk_creation()))
				outwards.write(caseNO + ': \n' + str(date_List) + '\n')
			event_creation(date_List, CAL, caseNO)




			time.sleep(1)

			n = n + 1


def gather_soup(caseNO, n):

	url = 'https://www.lacourt.org/casesummary/ui/' 				#destination url
	payload = {'CaseNumber':caseNO} 							#name of input field: input query



	print('contacting website for case no. ' + str(n) + ": " + caseNO + "...")
	r = requests.get(url, params=payload)							#results of query called 'r'


	#write html file. just in case
	print('contacted')
	with open("requests_results.html", "wb") as f:
		f.write(r.content)
	with open("requests_results.html", "r+b") as f:
		data = f.read()

	#parse for text only
	soup = BeautifulSoup(data, 'html.parser')
	soupText = soup.get_text()
	soupText = soupText.encode('utf-8')
	print ('text parsed')
	with open("text_only.txt", "wb") as f:
		f.write(soupText)




#remove chunk of irrelevant text
def trim_soup():													 
	with open("text_only.txt", "rt") as f:
		#begin loop through text
		for line in f:
			if "CASE INFORMATION" in line:
				#interrupt loop at start of key info
				break

		#write new file starting at interruption
		with open("relevant_text.txt","wt") as out:
			out.writelines(f)







# attempt to pull out key dates and info from relevant_text.txt
def chunk_creation():
	#create list of data chunks
	chunkL = []
	byWord = []
	with open("relevant_text.txt","rt+") as f:
		for line in f:
			#pull filing date
			if 'VS' in line:
				caseName = str(line)
				chunkL.append(caseName)
			if "Filing Date:" in line:
				Filing = str(line)
				#append list w filing date
				chunkL.append(Filing)
			# if "at" in line:
			# 	at = str(line)
			# 	chunkL.append(at)
			if "Final Status Conference" in line:
				'/n'
				FSC = str(line)
				#append list w data chunk
				chunkL.append(FSC)
				#break after first trigger
				break
		dataChunk = ''.join(chunkL)
		dataChunk = dataChunk.split()

		for item in dataChunk:
			byWord.append(item)
		#create final file, create list from dictionary, write list to file. Move this to parse_chunk later on
		with open("final_text.txt","wt+") as out:
			for x in byWord:
				out.writelines(x + '\n')

	return byWord




def parse_chunk(byWord):
	#modify byWord to break between info points
	indexFiling = byWord.index('Filing')
	Name = byWord[0:indexFiling]
	Name = "Name: " + ' '.join(Name)
	Filing = byWord[indexFiling:indexFiling + 3]

	filingDate = Filing[2].split('/')
	filingMonth = int(filingDate[0])
	filingDay = int(filingDate[1])
	filingYear = int(filingDate[2])

	filingDateTime = datetime.date(filingYear, filingMonth, filingDay).isoformat()
	Filing = "Filing Date: " + filingDateTime

	if 'Conference' and 'Trial' and 'Dismissal' in byWord:
		indexConference = byWord.index('Conference')
		indexTrial = byWord.index('Trial')
		indexDismissal = byWord.index('Dismissal')
		#indexName = byWord.index('VS')

		FSC = byWord[indexFiling+3:indexConference-1]
		Trial = byWord[indexConference:indexTrial]
		OSC = byWord[indexTrial:indexDismissal]



		#pull dates for gcal integration


		FSCdate = FSC[0].split('/')
		FSCmonth = int(FSCdate[0])
		FSCday = int(FSCdate[1])
		FSCyear = int(FSCdate[2])
		FSCtime = FSC[2].split(':')
		FSChour = int(FSCtime[0])
		FSCminute = int(FSCtime[1])

		trialDate = Trial[1].split('/')
		trialMonth = int(trialDate[0])
		trialDay = int(trialDate[1])
		trialYear = int(trialDate[2])
		trialTime = Trial[3].split(':')
		trialHour = int(trialTime[0])
		trialMinute = int(trialTime[1])

		OSCdate = OSC[1].split('/')
		OSCmonth = int(OSCdate[0])
		OSCday = int(OSCdate[1])
		OSCyear = int(OSCdate[2])
		OSCtime = OSC[3].split(':')
		OSChour = int(OSCtime[0])
		OSCminute = int(OSCtime[1])




		FSCdatetime = datetime.datetime(FSCyear, FSCmonth, FSCday, FSChour, FSCminute).isoformat()


		trialDateTime = datetime.datetime(trialYear, trialMonth, trialDay, trialHour, trialMinute).isoformat()


		OSCdatetime = datetime.datetime(OSCyear, OSCmonth, OSCday, OSChour, OSCminute).isoformat()






		#create return values for output to text file.

		Trial = "Trial: " + trialDateTime + ' ' + ' '.join(Trial[5:len(Trial)-2])
		FSC = "FSC: " + FSCdatetime + ' ' + ' '.join(FSC[5:len(FSC)-1])
		OSC = "OSC: " + OSCdatetime + ' ' + ' '.join(OSC[6:len(OSC)-3])




		parsed_data = Name + '\n' + Filing + '\n' + Trial + '\n' + FSC + '\n' + OSC
	else:
		for item in byWord:
			if item == 'at':
				atIndex = byWord.index(item)
				tempDate = byWord[atIndex-1]
				tempTime = byWord[atIndex+1]
				tempTime = tempTime.split(':')
				tempDate = tempDate.split('/')
				dateMonth = int(tempDate[0])
				dateDay = int(tempDate[1])
				dateYear = int(tempDate[2])
				dateHour = int(tempTime[0])
				dateMinute = int(tempTime[1])

				tempDateTime = datetime.datetime(dateYear, dateMonth, dateDay, dateHour, dateMinute)
				now = datetime.datetime.now()
				if tempDateTime > now:
					#keyWord =
					pass
				else:
					pass









		parsed_data = Name + '\n' + Filing + '\n'




	return parsed_data

def universalize(date_string):
	date_list = re.split('[ \n]', date_string)
	print(date_list)
	return date_list


# def event_creation(date_list):
SCOPES = 'https://www.googleapis.com/auth/calendar'

def gcal_login():
	store = file.Storage('token.json')
	creds = store.get()
	if not creds or creds.invalid:
		flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
		creds = tools.run_flow(flow, store)
	CAL = build('calendar', 'v3', http=creds.authorize(Http()))
	return CAL


def event_creation(date_list, CAL, caseNO):
	indexName = date_list.index('Name:')
	indexEndName = date_list.index('VS')
	caseName = date_list[indexName+1:indexEndName]
	caseName = ' '.join(caseName)
	for item in date_list:
		if item == 'FSC:':
			#define terms
			indexFSC = date_list.index('FSC:')
			FSCdate = date_list[indexFSC+1]
			keyWord = 'FSC'
			indexFSCend = date_list.index('OSC:')
			location = date_list[indexFSC+2:indexFSCend]

			#call check_event()
			result = check_event(caseName, keyWord, FSCdate, CAL)

			if result == 1:
				#preexisting event found on correct date
				#print('Preexisting event found for ' + keyWord + ' for ' + caseName + ' on correct date: ' + FSCdate)
				pass
			elif (result != 1) and (result != 2):
				#preexisting event found on incorrect date
				#change date function
				eventId = result
				change_event(eventId, FSCdate, CAL)
				print('Preexisting event found for ' + keyWord + ' for ' + caseName + ' on INCORRECT DATE. Date has been changed to ' + FSCdate)
			elif result == 2:
				#no preexisting event found
				#proceed to insert_event():

				# construct endTime
				dt = datetime.datetime.fromisoformat(FSCdate)
				enddateTime = dt + datetime.timedelta(hours=1)
				endTime = enddateTime.isoformat()

				# construct summaryString
				summaryString = keyWord + ' - ' + caseName

				# construct location

				insert_event(FSCdate, endTime, summaryString, location, caseNO, CAL)
				print('No event for ' + keyWord + ' for ' + caseName + ' found. Event created on ' + FSCdate)

		if item == 'OSC:':
			#define terms
			indexOSC = date_list.index('OSC:')
			OSCdate = date_list[indexOSC+1]
			keyWord = 'OSC'
			location = date_list[indexOSC+2:]

			#call check_event()
			result = check_event(caseName, keyWord, OSCdate, CAL)
			if result == 1:
				#preexisting event found on correct date
				#print('Preexisting event found for ' + keyWord + ' for ' + caseName + ' on correct date: ' + OSCdate)
				pass
			elif (result != 1) and (result != 2):
				#preexisting event found on incorrect date
				#change date function
				eventId = result
				change_event(eventId, OSCdate, CAL)
				print('Preexisting event found for ' + keyWord + ' for ' + caseName + ' on INCORRECT DATE. Date has been changed to ' + OSCdate)
			elif result == 2:
				#no preexisting event found
				#proceed to insert_event():
				# construct endTime
				dt = datetime.datetime.fromisoformat(OSCdate)
				enddateTime = dt + datetime.timedelta(hours=1)
				endTime = enddateTime.isoformat()

				# construct summaryString
				summaryString = keyWord + ' - ' + caseName

				# construct location

				insert_event(OSCdate, endTime, summaryString, location, caseNO, CAL)
				print('No event for ' + keyWord + ' for '+ caseName + ' found. Event created on ' + OSCdate)

		if item == 'Trial:':
			#define terms
			indexTrial = date_list.index('Trial:')
			Trialdate = date_list[indexTrial+1]
			keyWord = 'Trial'
			indexLocEnd = date_list.index('FSC:')
			location = date_list[indexTrial+2:indexLocEnd]

			#call check_event()
			result = check_event(caseName, keyWord, Trialdate, CAL)

			if result == 1:
				#preexisting event found on correct date
				#print('Preexisting event found for ' + keyWord + ' for ' + caseName + ' on correct date: ' + Trialdate)
				pass
			elif (result != 1) and (result) != 2:
				#preexisting event found on incorrect date
				#change date function
				print('Preexisting event found for ' + keyWord + ' for ' + caseName + ' on INCORRECT DATE. Changing event to ' + Trialdate)

				eventId = result
				change_event(eventId, Trialdate, CAL)
				print(keyWord + ' date has been changed to ' + Trialdate)
			elif result == 2:
				#no preexisting event found
				#proceed to insert_event():

				#construct endTime
				dt = datetime.datetime.fromisoformat(Trialdate)
				enddateTime = dt + datetime.timedelta(hours=1)
				endTime = enddateTime.isoformat()

				#construct summaryString
				summaryString = keyWord + ' - ' + caseName


				insert_event(Trialdate, endTime, summaryString, location, caseNO, CAL)
				print('No event for ' + keyWord + ' for '+ caseName + ' found. Event created on ' + Trialdate)

		# if item == 'Fee:':
		# 	indexJuryFee =  index.date_list('Fee:')
		# 	JuryFeeDate = date_list[indexJuryFee+1]
		# 	keyWord = 'Fee'
		# 	if check_event(caseName, keyWord, JuryFeeDate) == 1:
		# 		#preexisting event found on correct date
		# 		print('Preexisting event found for ' + caseName + ' on ' + JuryFeeDate)
		# 		return 0
		# 	elif check_event(caseName, keyWord, JuryFeeDate) != 1 or 2:
		# 		#preexisting event found on incorrect date
		# 		#change date function
		# 		print('Preexisting event found for ' + caseName + ' on INCORRECT DATE. Date has been changed to ' + JuryFeeDate)
		# 	elif check_event(caseName, keyWord, JuryFeeDate) == 2:
		# 		#no preexisting event found
		# 		#proceed to insert_event():
		# 		print('No event for ' + caseName + ' found. Event created on ' + JuryFeeDate)
		# 	else:
		# 		print('No Fee: found')




def insert_event(startTime, endTime, eventSummary, eventLocation, caseNO, CAL):

	now = str(datetime.datetime.now())
	eventLocation = ' '.join(eventLocation)
	event = {
		'summary': eventSummary,

		'description': 'Event created automatically using case no: ' + caseNO + ' on ' + now + '. Event located in ' + eventLocation,
		'start': {
			'dateTime': startTime,
			'timeZone': 'America/Los_Angeles',
		},
		'end': {
			'dateTime': endTime,
			'timeZone': 'America/Los_Angeles',
		},
		# 'attendees': [
		# 	{'email': 'molchanlaw@yahoo.com'},
		# ],
		'reminders': {
			'useDefault': False,
			'overrides': [
				{'method': 'email', 'minutes': 48 * 60},

			],
		},
	}

	event = CAL.events().insert(calendarId='greylawcalendar@gmail.com', body=event).execute()

	'Event created: %s' % (event.get('htmlLink'))

def check_event(caseName, keyWord, dateTime, CAL):

	page_token = None
	while True:
		dt = datetime.datetime.fromisoformat(dateTime)
		dt = re.split('[ -]', str(dt))
		dtYear = int(dt[0])
		dtMonth = int(dt[1])
		dtDay = int(dt[2])
		dt = datetime.date(dtYear, dtMonth, dtDay).isoformat()
		keyWord = keyWord.lower()
		events = CAL.events().list(calendarId='greylawcalendar@gmail.com', pageToken=page_token, q=keyWord).execute()
		#below are events with keyWord present in title
		for event in events['items']:
			summaryString = str(event['summary']).lower()
			summaryList = summaryString.split(' ')
			nameString = ''.join(caseName).lower()
			nameList = nameString.split(' ')


			#for each word in case name - if word present in title of event with keyWord in title:

			for item in nameList:
				if item in summaryList:
					#print title of all events with both word from case name and keyword
					print('Match Found: ' + str(item) + ' and ' + keyWord)


					try:
						start = event['start']['dateTime']


					except:
						start = event['start']['date']


					start = re.split('[- T:]', str(start))

					startMonth = int(start[1])
					startDay = int(start[2])
					startYear = int(start[0])
					start = datetime.date(startYear, startMonth, startDay).isoformat()


					if dt == start:

						print('correct date')
						return 1


					else:
						print('incorrect date')

						results = event['id']



				else:
					results = 2






					#check if startTime matches time
		return results

		page_token = events.get('nextPageToken')

		if not page_token:
			break



def change_event(eventId, dateTime, CAL):
	event = CAL.events().get(calendarId='greylawcalendar@gmail.com', eventId=eventId).execute()

	dt = datetime.datetime.fromisoformat(dateTime)
	enddateTime = dt + datetime.timedelta(hours=1)
	dtISO = enddateTime.isoformat()

	event['start']['dateTime'] = dateTime
	event['end']['dateTime'] = dtISO
	print(event)

	CAL.events().update(calendarId='greylawcalendar@gmail.com', eventId=eventId, body=event).execute()

main()