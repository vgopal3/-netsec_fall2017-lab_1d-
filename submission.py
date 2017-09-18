import playground
import asyncio
import io 
from playground.network.packet.fieldtypes import UINT16, STRING, BOOL, UINT32, BUFFER
from playground.network.packet import PacketType
from playground.asyncio_lib.testing import TestLoopEx
from playground.network.testing import MockTransportToProtocol



class testpacket(PacketType):
	DEFINITION_IDENTIFIER = "lab1b.sidd.testpacket"
	DEFINITION_VERSION = "1.0"	
	FIELDS = [ 
		("counter1", UINT32),
		("data", BUFFER)
		]

class testpacket2(PacketType):
	DEFINITION_IDENTIFIER = "lab1b.sidd.testpacket2"
	DEFINITION_VERSION = "1.0"
	FIELDS = [
		("counter1", UINT32),
		("data", BUFFER)
		]

class testpacket3(PacketType):
	DEFINITION_IDENTIFIER = "lab1b.sidd.testpacket3"
	DEFINITION_VERSION = "1.0"
	FIELDS = [
		("counter1", UINT32),
		("data", BUFFER)
		]

class testpacket4(PacketType):
	DEFINITION_IDENTIFIER = "lab1b.sidd.testpacket4"
	DEFINITION_VERSION = "1.0"
	FIELDS = [
		("counter1", UINT32),
		("data", BUFFER)
		]

class ClientSide(asyncio.Protocol):

    def __init__(self):
        print("Client : Connected")
        print("")
        self.transport = None #set the transport to none

    def connection_made(self, transport):
        self.transport = transport
        self.deserializer = PacketType.Deserializer()
        self.transport.write(pack())
        print ('Client : The data has been sent')

    def data_received(self, data):
        print ('Client : The data has been recieved')
        self.deserializer = PacketType.Deserializer()        
        self.deserializer.update(data)
        for pkt in self.deserializer.nextPackets():
            print (pkt)
            if (pkt.counter1 == 2):
                print ('Client:Received Packet 2 Successfully')
                packet_t3 = testpacket()
                packet_t3.counter1 = 3
                packet_t3.data = b"Hello"
                packet_t3bytes = packet_t3.__serialize__()	
                #ClientSide.connection_made(MockTransportToProtocol(ServerSide()),packet_t3bytes)
                self.transport.write(packet_t3bytes)
                #ServerSide.data_received(ServerSide(),packet_t3bytes)
            elif (pkt.counter1 == 4):
                print ('Client : Recieved Packet 4 Successfully.')
		
    def connection_lost(self, exc):
        print ('Client : Connection Lost because')

class ServerSide(asyncio.Protocol):

    def __init__(self):
        print("Server: Connected")
        print("")
        self.transport = None

    def connection_made(self,transport):
        self.transport = transport
        self.deserializer = PacketType.Deserializer()
        print ('Server: The data has been sent')

    def data_received(self,data):
        print ('Server: The data has been recieved')
        #print (data)
        self.deserializer = PacketType.Deserializer()
        self.deserializer.update(data)
        for pkt in self.deserializer.nextPackets():
            print (pkt)
            if (pkt.counter1 == 1):
                print ('Server: Received Packet 1 Successfully. ')	
                packet_t2 = testpacket()
                packet_t2.counter1 = 2
                packet_t2.data = b"Send PassPhrase"
                packet_t2bytes = packet_t2.__serialize__()
                #ServerSide.connection_made(MockTransportToProtocol(ClientSide()), packet_t2bytes)
                self.transport.write(packet_t2bytes)
                #ClientSide.data_received(ClientSide(),packet_t2bytes)
            elif (pkt.counter1 == 3):
                print ('Server: Recieved Packet 3 Successfully.')
                if (pkt.data == b"Hello"):
                    print ('Server: The Passphrase is correct. ')
                    packet_t4 = testpacket()
                    packet_t4.counter1 = 4
                    packet_t4.data = b"Connection Handshake Complete. Start with Payload"
                    packet_t4bytes = packet_t4.__serialize__()
                    #ServerSide.connection_made(MockTransportToProtocol(ClientSide()), packet_t4bytes)
                    #ClientSide.data_received(ClientSide(),packet_t4bytes)
                    self.transport.write(packet_t4bytes)
                else:
                    print ('Server: Sorry! Wrong passphrase')

    def connection_lost(self, exc):
        print ("Server : Connection Lost {}")

def pack():
    packet_t1 = testpacket()
    packet_t1.counter1=1
    packet_t1.data = b"hello Server"
    packet_t1bytes = packet_t1.__serialize__()
    return packet_t1bytes
    
def UnitTest():
    asyncio.set_event_loop(TestLoopEx())
    clientProtocol = ClientSide()
    serverProtocol = ServerSide()
    cTransport, sTransport = MockTransportToProtocol.CreateTransportPair(clientProtocol, serverProtocol)
    serverProtocol.connection_made(sTransport)
    clientProtocol.connection_made(cTransport)
    
if __name__=="__main__":
	UnitTest()
	print("Test Success")
	
	
"""if __name__=="__main__":
	UnitTest()
	print("Test Success")"""
	
	
class EchoControl:
    def __init__(self):
        self.txProtocol = None
        
    def buildProtocol(self):
        return ClientSide(self.callback)
        
    def connect(self, txProtocol):
        self.txProtocol = txProtocol
        print("Echo Connection to Server Established!")
        self.txProtocol = txProtocol
        '''sys.stdout.write("Enter Message: ")
        sys.stdout.flush()
        asyncio.get_event_loop().add_reader(sys.stdin, self.stdinAlert)'''
	
    def callback(self, message):
        print("Server Response: {}".format(message))
        sys.stdout.write("\nEnter Message: ")
        sys.stdout.flush()
        
    def stdinAlert(self):
       data = sys.stdin.readline()
       if data and data[-1] == "\n":
            data = data[:-1] # strip off \n
            
       self.txProtocol.send(data)
    
if __name__=="__main__":
    echoArgs = {}
    
    args= sys.argv[1:]
    i = 0
    for arg in args:
        if arg.startswith("-"):
            k,v = arg.split("=")
            echoArgs[k]=v
        else:
            echoArgs[i] = arg
            i+=1
    
    if not 0 in echoArgs:
        sys.exit(USAGE)

    mode = echoArgs[0]
    loop = asyncio.get_event_loop()
    loop.set_debug(enabled=True)
    
    if mode.lower() == "server":
        coro = playground.getConnector().create_playground_server(lambda: ServerSide(), 101)
        server = loop.run_until_complete(coro)
        print("Echo Server Started at {}".format(server.sockets[0].gethostname()))
        loop.run_forever()
        loop.close()
        
        
    else:
        remoteAddress = mode
        control = ClientSide()
        coro = playground.getConnector().create_playground_connection(lambda: ClientSide(), remoteAddress, 101)
        transport, protocol = loop.run_until_complete(coro)
        print("Echo Client Connected. Starting UI t:{}. p:{}".format(transport, protocol))
        control.connect(protocol)
        loop.run_forever()
        loop.close()	
