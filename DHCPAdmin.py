#DHCPAdmin.py


from socket import *
import re, uuid
import sys

serverName = 'localhost'
serverPort = 12001
clientSocket = socket(AF_INET, SOCK_DGRAM)
clientMacAddr =  macAddr = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
clientBroadCast = '255.255.255'
currClientIPAddr = '0.0.0.0'

def sendMessage(outgoingMessage):
    clientSocket.sendto(outgoingMessage.encode(),(serverName, serverPort))

#get computers MAC Address
def getMACAddr():
    macAddr = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
    return macAddr

#checks if the entered mac address is its own mac address
def checkMACAddr(address):
    if address == clientMacAddr:
        return True
    else:
        return False

#receive message and figure out what kind it is (ACK or OFFER)
def receiveMessage():
    serverMessage, serverAddress = clientSocket.recvfrom(2048)
    serverMessage = serverMessage.decode()
    serverMessage = serverMessage.split(',')    
    msg_type = serverMessage[0]
    msg_mac_addr = serverMessage[1]
    msg_IP = serverMessage[2]
    print(serverMessage)
    if 'END' in serverMessage:
        sys.exit()
    else:
        pass

outmessage = 'LIST' + ',' + clientMacAddr + ',' + currClientIPAddr
sendMessage(outmessage)
while 1:
    receiveMessage()