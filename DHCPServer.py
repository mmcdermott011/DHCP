#DHCP SERVER
#Michael McDermott

#We assume, the range of IP addresses available to the server is 192.168.1.0/24, a block of 256 IP addresses including Net ID and Broadcast IP address.
#This follows the steps of the DHCP protocol
#DISCOVER
#OFFER
#REQUEST
#ACK
from socket import *
import ipaddress
import sys

NETID = '192.168.1.0'
BROADCAST = '192.168.1.255'
serverPort = 12001
ipNet = ipaddress.ip_network('192.168.1.0/24') #list of all valid ip addresses for network
clientList = {} #dictionary for when we start adding clients and their IPs (macAddr, IP)
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))
ipList = []
for ip in ipNet:
    ipList.append(str(ip))
ipList.remove(NETID)
ipList.remove(BROADCAST)

def sendMessage(outgoingMessage,cAdd):
    print('Sending message to client: %s' % outgoingMessage)
    serverSocket.sendto(outgoingMessage.encode(), cAdd)

def sendACK(msg_mac_addr, msg_IP, cAdd): 
    print('Server is sending Acknowledge message to client')
    message = 'ACK,' + msg_mac_addr + ',' + msg_IP
    sendMessage(message,cAdd)

def sendOFFER(msg_mac_addr, msg_IP, cAdd):
    print('Server is sending Offer message to client')
    clientIP = ipList.pop()      
    message = 'OFFER,' + msg_mac_addr +','+ clientIP
    sendMessage(message, cAdd)
            

def sendDECLINE(msg_mac_addr, msg_IP, cAdd):
    print('Server is sending Decline message to client')
    outmsg = 'DECLINE,' + msg_mac_addr + ', ' 
    sendMessage(outmsg, cAdd )

#checks if the IP passed is available and valid  
def checkIPs(clientIP): 
    if clientIP in ipList:
        return True
    else:
        return False
  
#checks if the mac addr already has an IP 
def checkMACAddrs(msg_mac_addr):
    if msg_mac_addr in clientList:
        print('This MAC address already has an IP of ' + clientList.get(msg_mac_addr))
        return True
    else:
        print('This MAC address does not have an assigned IP yet')
        return False
   
def receiveDISCOVER(msg_mac_addr, msg_IP, cAdd): 
    print('Server received Discover message from client')
    #check list of IP address to see if any have already been assigned to client
    #ie check the list whether the MAC address in the message exists in list or not
    #if record found, reply indicating an IP has already been assigned to this client
    if checkMACAddrs(msg_mac_addr) == False:
        #if no record found, check if there are any available IP addrresses
        if len(ipList) == 0:
            #if all addresses taken, send DECLINE message to client
            sendDECLINE(msg_mac_addr, msg_IP, cAdd)
        else:
            #else, get next available IP and send OFFER message to client with their mac addr and offered IP addr
            sendOFFER(msg_mac_addr, msg_IP, cAdd)
    else:
        print('Client is already assigned an IP address')
        sendACK(msg_mac_addr, msg_IP, cAdd)
     

def receiveRELEASE(msg_mac_addr, msg_IP, cAdd): 
    print('Server received Release message from client')
    #release IP addr that is currently assigned to the client
    #remove client from list of current clients
    try:
        if  msg_IP not in ipList:
            ipList.append(msg_IP)
        del clientList[msg_mac_addr]
    except KeyError:
        print("Key  not found")
    #reply to client that release is done(send ACK)
    sendACK(msg_mac_addr, '0.0.0.0', cAdd)

def receiveRENEW(msg_mac_addr, msg_IP, cAdd): 
    #release IP addr that is currently assigned to the client
    #remove client from list of current clients
    try:
        if  msg_IP not in ipList:
            if msg_IP != '0.0.0.0':
                ipList.append(msg_IP)
                del clientList[msg_mac_addr]
    except KeyError:
        print("Key  not found")
    print('Server received Renew message from client')
    #check if any IP addr have been assigned to client
    #if yes, reply they already have an IP x.x.x.x.
    if checkMACAddrs(msg_mac_addr) == False:
        sendOFFER(msg_mac_addr, msg_IP, cAdd)
        #otherwise, reply with OFFER message


def receiveREQUEST(msg_mac_addr, msg_IP, cAdd):
    print('Server received a Request message from client')
    #check if offered IP addr is still available
    if msg_IP in clientList.values(): #the ip has already been assigned to someone
        #offer a new IP
        if len(ipList) > 0:
            sendOFFER(msg_mac_addr, msg_IP, cAdd)
        else:
            sendDECLINE(msg_mac_addr, msg_IP, cAdd)
    else:
        #if yes, assign IP to client and store in IP list
        clientList[msg_mac_addr] = msg_IP
        message = 'Client is assigned IP address:' + msg_IP
        print(message)
        #reply with ACKNOWLEDGE message containing MAC addr and offered IP addr
        sendACK(msg_mac_addr, msg_IP, cAdd)



#receives a list of devices on the network when logged in as an admin
def receiveList(msg_mac_addr, msg_IP, cAdd):    
    print('Server received List request from admin')

    for mac in clientList:
        outmsg = 'LIST,' + mac + ',' + clientList.get(mac) + ','
        sendMessage(outmsg, cAdd)
    outmsg = 'END, , ,'
  


def receiveMessage(): 
    clientMessage, clientAddress = serverSocket.recvfrom(2048)
    clientMessage = clientMessage.decode()
    clientMessage = str(clientMessage)
    print(clientMessage)
    clientMessages = clientMessage.split(',')    
    msg_type = clientMessages[0]
    msg_mac_addr = clientMessages[1]
    msg_IP = clientMessages[2]
    if msg_type == 'DISCOVER':
        receiveDISCOVER(msg_mac_addr, msg_IP, clientAddress)
    elif msg_type == 'RELEASE':
        receiveRELEASE(msg_mac_addr, msg_IP, clientAddress)
    elif msg_type == 'RENEW':
        receiveRENEW(msg_mac_addr, msg_IP, clientAddress)
    elif msg_type == 'REQUEST':
        receiveREQUEST(msg_mac_addr, msg_IP, clientAddress)
    elif msg_type == 'LIST':
        receiveList(msg_mac_addr, msg_IP, clientAddress)
    else:
        print('Message not recognized!')
        sendDECLINE(msg_mac_addr, msg_IP, clientAddress)

def main():
   print('DHCP Server started')
   print('-------------------')
   while 1:
        receiveMessage()
        print()

main()
