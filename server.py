import socket # for socket 
import sys  
import threading
import os

def init():
	# global declaration to allow its access via other functions too
	global s
	try: 
		# Create a socket object 
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		# Make the address reusable by other socket connections 
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
		#bind to the IP and port provided
		s.bind((IP,PORT))   
		#Handles 4 incoming connections in a queue
		s.listen(4)
		print ("Socket established")
	except socket.error as err: 
		print ("Socket could not be established, error %s" %(err)) 
  

def start_listen():
	# A loop to continously listen to the requests
	while True:
		# accept all incoming connections
		c, addr = s.accept()
		# Call a new thread and let this function run parallely
		thread = threading.Thread(target = proxy_or_server, args = (c, addr))
		thread.setDaemon(True) 
		# Branch a thread from here to run all threads parallely
		thread.start() 


# A function to decide on whether the server is a proxy or has to serve the file
# It decides on the basis of content length of the data received
# If size if 2 lines then it is the server else a proxy
def proxy_or_server(c, addr):
	# receive the request
	data = c.recv(1024)
	addrs = data.decode('utf-8').split('\n')

	if len(addrs) <= 2:
		# Acting as the server
		start_server(addrs, c, addr)
	else:
		#Acting as a proxy
		start_proxy(addrs, c, addr)

def start_server(addresses, c, addr):
	# Server processes
	print("I am a Server of address: " + addresses[1])

	try:
		# Send the size of file to client as client first requests the file_size.
		c.sendall(str(os.path.getsize(addresses[0])).encode('utf-8')) 
		# Waiting for the signal from client to start or Ack on that client has received the file size
		signal = c.recv(4)
		file = open(addresses[0], "rb", encoding=None, errors=None)
		data = file.read()
		c.sendall(data) 
		c.close()

	# Send NA if a file is not present at the server. NA will trigger the client to not receive the file and inform the user    
	except Exception as e:
		raise e    
		c.sendall(b"NA")
		c.close()

# For any proxy the following process is an invariant
# 1) First it sends client data to the server
# 2) Then server will send the file size to the client
# 3) Then client will send to the server notifying that it has received the size
# 4) Then server will send the file
# 5) Close
def start_proxy(addresses, c, addr):
	# Proxy process
	print ("I am a proxy server addresses: " + addresses[1])
	next_addr = addresses[2].split(' ')
	del addresses[1]
    
	# Building the data to forward.
	# Note we remove our own address so that at the final destination server can get to know by file_size
	data = str(addresses[0] + '\n')
	for line in addresses[1:-1]:
		data += line + '\n'
	data += str(addresses[-1])

	#-----------------------------------------------------------
	# Now we will establish a socket connection with the next proxy/server
	#-----------------------------------------------------------
	try:
		s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s2.connect((next_addr[0], int(next_addr[1])))
		# Step 1: Send data to server
		s2.sendall(data.encode('utf-8'))

		# step2: server to client size
		server_to_client_size = s2.recv(1024)
		c.send(server_to_client_size)

		# step 3: client to server ack
		client_to_server_ack = c.recv(4)
		s2.send(client_to_server_ack)
		
		# step 4: Continuously stream the data to the client. So send on c stream
		while True:
			# We read a fixed 1KB amount of data in the buffer and continuously transfer it to the client
			# We don't wait for the entire content to get downloaded
			file_data = s2.recv(1024)
			if len(file_data) > 0:
				c.sendall(file_data)
			else:
				break
		# step 5: Close the forward proxy connection 
		c.recv(4)
		# close sender's socket
		s2.close()
		# closing caller's socket 
		c.close() 
	except Exception as e:
		raise e
		print ("Forward socket connection error.") 
		if s2:
			s2.close()

		if c:
			c.sendall(b"Address not found")
			c.close()
    
  
if __name__ == "__main__":
	IP = input("IP: ")
	PORT = int(input("PORT: "))
	init()
	start_listen()