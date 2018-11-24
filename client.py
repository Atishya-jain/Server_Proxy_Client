# Import socket module 
import socket                
import sys

def client(in_filename):
	# Create a socket object 
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   
	# Make the address reusable by other socket connections 
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 

	#--------------------------------------------
	# First read the input file and store it properly 
	#--------------------------------------------

	# Open the input file to read and parse information
	try:
		file = open(in_filename, "r")    
		out_file = file.readline()
		# Address of server the client will send to
		addr_to_send = file.readline()
		addr_to = addr_to_send.split(' ')
		IP = addr_to[0]
		PORT = int(addr_to[1])
		# Reading whole data
		data_to_send = out_file
		data_to_send += addr_to_send
		for l in file:
			data_to_send += l
	except:
		print ("Error with input file")
	  
	# connect to the server on local computer
	try:
		s.connect((IP, PORT)) 
	except Exception as e:
		raise e
		print ("Connection couldn't be established at: " + IP + ":" + PORT)
		sys.exit()  

	# Send data
	s.send(data_to_send.encode('utf-8'));

	#--------------------------------------------
	# Now, first I will send the data inquiring it about the size of the file. This is so that file 
	# can be received till the end and client knows when to stop
	#--------------------------------------------

	# receive data from the server 
	file_size = s.recv(1024).decode('utf-8')
	if file_size == "NA":
		print ("File not present")
		sys.exit()
	else:
		file_size = int(file_size)
	
	# signalling the server to start sending
	s.send(b'ack_to_send')

	# Start receiving
	start = 0
	output = open(out_file[:-1], "wb")
	while start < file_size:
		try:
			data = s.recv(file_size)
		except Exception as e:
			raise e
	
		if data == '':
			break
		output.write(data)
		start += len(data)
		print (str(len(data)) + " received " + str((file_size-start)/file_size*100) + "% remaining")
	output.close() 

if __name__ == '__main__':
	in_filename = input("Enter input filename: ")
	client(in_filename)