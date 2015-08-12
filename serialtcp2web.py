# Serial (TCP/IP) wedge to Web App (HTTP POST)
# Tested with COGNEX Dataman 302X
# Version 1.01
# Sean Lam


import httplib, urllib,sys
import socket, select


def lookup(decode):
	decode = decode.replace("\n", "")
	params = urllib.urlencode({'scanner': '1', 'itemcode': decode})
	headers = {"Content-type": "application/x-www-form-urlencoded",
	            "Accept": "text/plain"}
	            
	conn = httplib.HTTPConnection("localhost:8888")
	conn.request("POST", "/add.php", params, headers)
	response = conn.getresponse()
	print response.status, response.reason
	data = response.read()
	conn.close()


if __name__ == "__main__":
    CONNECTION_LIST = []    # list of socket clients
    RECV_BUFFER = 1024
    PORT = 3131
         
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setblocking(0)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("localhost", PORT))
    server_socket.listen(10)
    
 
    # Add server socket to the list of readable connections
    CONNECTION_LIST.append(server_socket)

    print "Listener for Scanner 1 started on port " + str(PORT)

    while 1:
        # Get the list sockets which are ready to be read through select
        read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[],0.0)
 
        for sock in read_sockets:
            sock.setblocking(0)

            # Handle New Connections
            if sock == server_socket:
                # Handle the case in which there is a new connection recieved through server_socket
                sockfd, addr = server_socket.accept()

                CONNECTION_LIST.append(sockfd)
                print "Client (%s, %s) connected" % addr
                 
            #SHandle Incoming Comms
            else:
                try:
                    data = sock.recv(RECV_BUFFER)
                except socket.timeout, e:
                    err = e.args[0]

                    if err == 'timed out':
                        sleep(1)
                        print 'recv timed out, retry later'
                        continue
                    else:
                        print e
                        # Socket Error , close socket
                        sock.close()
                        CONNECTION_LIST.remove(sock)

                except socket.error, e:
                    # Socket Error , close socket
                    print e
                    sock.close()
                    CONNECTION_LIST.remove(sock)

                else:
                    if len(data) == 0:
                        print 'Shutdown by Client'
                        print "Client (%s, %s) disconnected" % addr
                        sock.close()
                        CONNECTION_LIST.remove(sock)
                    else:
                        
                        sock.send('OK ... ' + data) # remove if device does not respond
                        print "data %s " % data
                        print "len %s " % len(data)
                        lookup(data)
    server_socket.close()
