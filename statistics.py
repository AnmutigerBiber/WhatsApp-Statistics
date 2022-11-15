import os
import sys

from datetime import datetime as DateClass, timedelta

class Chat():
	def __init__(self, input_file):
		self.messages = []
		self.messages_with_sender = {}
		self.messages_per_day = {}
		self.last_date = None
		self.day_with_most_messages = None
		self.most_messages_number = None
		self.first_day = DateClass.today()
		self.days_where_messages_were_sent = 0
		self.sent_bytes = 0
	
		self.start_parsing(input_file)
		
		self.calculate_day_with_most_messages()
		self.calculate_first_day()
		
		self.calculate_bytes()
		
	def start_parsing(self, input_file):
		for line in input_file:
			#print(ord(line[0]))
		
			if line[0] == "[" or ord(line[0]) == 8206:
				self.parse_normal_line(line)
			else:
				self.append_line_to_last_message(line)
				
	def parse_normal_line(self, line):
		date_and_time = line[line.find("[")+1:line.find("]")]
		message_itself = line[line.find(": ")+2:]
		
		sender = line[21:line.find(": ")].strip()
		
		date, time = date_and_time.replace(",", "").split(" ")
		self.messages.append(message_itself)
		
		if sender in self.messages_with_sender:
			self.messages_with_sender[sender]["total"] += 1
			
			if date in self.messages_with_sender[sender]["messages_per_day"]:
				self.messages_with_sender[sender]["messages_per_day"][date] += 1
			else:
				self.messages_with_sender[sender]["messages_per_day"][date] = 1
		else:
			self.messages_with_sender[sender] = {"total" : 1, "messages_per_day" : {date : 1}}
		
		if date in self.messages_per_day:
			self.messages_per_day[date] += 1
		else:
			self.messages_per_day[date] = 1
			
		self.last_date = date
		
	def append_line_to_last_message(self, line):
		self.messages[-1] += line
	
	def calculate_bytes(self):
		for message in self.messages:
			self.sent_bytes += len(message)
	
	def calculate_day_with_most_messages(self):
		max_messages = 0
		max_messages_date = None

		for day in self.messages_per_day:
			if self.messages_per_day[day] > max_messages:
				max_messages = self.messages_per_day[day]
				max_messages_date = day
				
		self.most_messages_number = max_messages
		self.day_with_most_messages = max_messages_date
		
	def calculate_first_day(self):
		for day in self.messages_per_day:
			d, m, y = day.split(".")
			
			if DateClass(2000 + int(y), int(m), int(d)) < self.first_day:
				self.first_day = DateClass(2000 + int(y), int(m), int(d))
			
	def print_statistic(self):
		one_day = timedelta(days=1)
		current_day = self.first_day
		
		max_length_of_bar = 100
		
		while current_day.strftime("%d.%m.%y") != DateClass.today().strftime("%d.%m.%y"):
			formatted = current_day.strftime("%d.%m.%y")

			weekday = current_day.weekday()
			
			weekday = {0:"Mon ", 1:"Tue ", 2:"Wed ", 3:"Thu ", 4:"Fri ", 5:"Sat ", 6:"Sun "}[weekday]

			print(weekday + formatted + ": ", end="")

			# days without messages don't need a bar
			if formatted in self.messages_per_day:
				print(str(self.messages_per_day[formatted]) + "\t", end="")
				self.days_where_messages_were_sent += 1
				
				portion = self.messages_per_day[formatted] / self.most_messages_number * 100
		
				# calculate the part, which can't be representated by a full box
				remainder = portion - int(portion)
	
				# printing the bar
				for i in range(-1, int(portion) - 1):
					print("\u2589", end="")
			
				# printing the remainder
				if remainder > 0 and remainder <= 1/5:
					print("\u258f", end="")
				elif remainder <= 2/5:
					print("\u258e", end="")
				elif remainder <= 3/5:
					print("\u258d", end="")
				elif remainder <= 4/5:
					print("\u258b", end="")
				elif remainder <= 5/5:
					print("\u258a", end="")
	
			print()
			current_day += one_day
			
	def print_overall_results(self):
		print("\n========== General Statistics ==========")
		print(" A total of " + str(len(self.messages)) + " messages were sent")
		print(" This is " + str(self.sent_bytes / 1000) + "kB of data")
		print(" On average " + str(int(len(self.messages) / self.days_where_messages_were_sent)) + " messages were sent per day (excluding message-free days)")
		print(" The maximum number of messages in a day was " + str(self.most_messages_number) + " on " + self.day_with_most_messages)
		print("\n Written by Leon Maier")
		
	def print_sender_statistics(self):
		print("\n========== Sender Statistics ==========")
		
		for day in self.messages_per_day:
			print(day + ":", end="")
			
			for sender in self.messages_with_sender:
				print("\t" + sender + " (" + str(self.messages_with_sender[sender]["messages_per_day"][day]) + ")", end="")
				
			print()

# analyze a file, where an exported whatsapp conversation is saved
def analyze(input_file_name, output_file_name):
	file = open(input_file_name, "r")
	
	try:
		# redirect print statements to logfile
		original_stdout = sys.stdout
		output_file = open(output_file_name, "w")
		sys.stdout = output_file

		chat = Chat(file)
		
		chat.print_statistic()
		chat.print_overall_results()
		
		#if detailed:
		#	chat.print_sender_statistics()
	except Exception as e:
		print(e)
	finally:
		# stdout now points back to its former stream
		output_file.close()
		sys.stdout = original_stdout
		file.close()

if len(sys.argv) < 3:
	print("missing arguments:")
	
	print(sys.argv[0] + " <input-filename> <output-filename> [--detailed]")
else:
	if os.path.exists(sys.argv[1]):
		analyze(sys.argv[1], sys.argv[2])#, detailed=len(sys.argv)==4)
	else:
		print("The file does not exist")