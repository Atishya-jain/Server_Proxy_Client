# Server_Proxy_Client

This is an implementation of a server-client architecture under TCP protocol. Multiple clients can request the server for different files and all the requests are handled parallely. Client request passes through a system of proxy servers. Both proxy servers and main server can be interchanged as the implementation is identical for both of them. 

## Communication
1. Client reads a file provided as input. File contains the file requested and a list of proxy servers to pass through to reach the final server
2. Client passes this information to the first proxy server in the list.
3. Proxy server in turn accepts the request and strips of its address from the data and passes the remaining to further proxy servers again making a TCP connection.
4. When data reaches the server, it consists of just the 2 lines. Server's address and the requested file
5. Server returns the size of the file if exists else returns a string signifying file not found to which client shuts down.
6. Request travels back the same path as TCP connections are already maintained and alive.
7. Then if the file was present, client allocates appropriate buffers as per the file size and requests the server to start sending the file
8. Server streams the file to the client, which means that at no point the file is downloaded and forwarded, but received and sent in small chunks
9. Client simultaneously writes the file received on its disk and at the end shuts down after closing the connections. Connections are also closed by each server and proxy servers.

## How to run?
Follow the steps:

1. Currently uploaded input.txt consists entries for 2 proxy servers and 1 server.
2. Open 4 terminal sessions
3. On 2 of them write **python server.py**.
   - Enter IP and PORT of the server as indicated in the input file for proxy servers (last entry denotes main server)
4. On 3rd teminal, change its location from the current working directory and from there write **python server.py** and enter the IP and PORT of the main server. (The last entry in input.txt file)
5. Put a file of your choice at the location of 3rd terminal as we will be transferring that to our current working directory
6. On the 4th terminal, write **proxy client.py**. Enter input.txt as filename
7. Hit enter. File will be transferred.

**Note** - It may happen that your system requires the files to be run in root priveledges to open up socket connections. Please use sudo before each command in that case.

## Author

* **Atishya Jain** 