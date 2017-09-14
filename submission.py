import playground
import asyncio
import io 
from playground.network.packet.fieldtypes import UINT16, STRING, BOOL, UINT32, BUFFER
from playground.network.devices.vnic import connect
from playground.network.devices.vnic import VNIC
from playground.network.packet import PacketType
from playground.asyncio_lib.testing import TestLoopEx
from playground.network.testing import MockTransportToStorageStream
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
        self._transport = None

    def connection_made(self, transport):
        self._transport = transport
        print ('Client : The data has been sent')

    def data_received(self, data):
        print ('Client : The data has been recieved')
        deserializer = testpacket.Deserializer()
        
        deserializer.update(data)
        for packet in deserializer.nextPackets():
            print (packet)
	         	
            if (packet.counter1 == 2):
                print ('Client:Received Packet 2 Successfully')
                packet_t3 = testpacket()
                packet_t3.counter1 = 3
                packet_t3.data = b"Hello"
                packet_t3bytes = packet_t3.__serialize__()	
                ClientSide.connection_made(MockTransportToProtocol(ServerSide()),packet_t3bytes)
                ServerSide.data_received(ServerSide(),packet_t3bytes)
            elif (packet.counter1 == 4):
                print ('Client : Recieved Packet 4 Successfully.')
		
    def connection_lost(self, exc):
        print ('Client : Connection Lost because')

class ServerSide(asyncio.Protocol):

    def __init__(self):
        self._transport = None

    def connection_made(self, transport):
        self._transport = transport
        self._deserializer = PacketType.Deserializer()
        print ('Server: The data has been sent')

    def data_received(self, data):
        print ('Server: The data has been recieved')
        deserializer = testpacket.Deserializer()
        deserializer.update(data)
        for packet in deserializer.nextPackets():
            print (packet)
            if (packet.counter1 == 1):
                print ('Server: Received Packet 1 Successfully. ')	
                packet_t2 = testpacket()
                packet_t2.counter1 = 2
                packet_t2.data = b"Send PassPhrase"
                packet_t2bytes = packet_t2.__serialize__()
                ServerSide.connection_made(MockTransportToProtocol(ClientSide()), packet_t2bytes)
                ClientSide.data_received(ClientSide(),packet_t2bytes)
            elif (packet.counter1 == 3):
                print ('Server: Recieved Packet 3 Successfully.')
                if (packet.data == b"Hello"):
                    print ('Server: The Passphrase is correct. ')
                    packet_t4 = testpacket()
                    packet_t4.counter1 = 4
                    packet_t4.data = b"Connection Handshake Complete. Start with Payload"
                    packet_t4bytes = packet_t4.__serialize__()
                    ServerSide.connection_made(MockTransportToProtocol(ClientSide()), packet_t4bytes)
                    ClientSide.data_received(ClientSide(),packet_t4bytes)
                else:
                    print ('Server: Sorry! Wrong passphrase')

    def connection_lost(self, exc):
        print ("Server : Connection Lost {}")

def UnitTest():

    
    asyncio.get_event_loop()
    playground.getConnector().create_playground_server(ServerSide(), 9999)
    playground.getConnector().create_playground_connection(ClientSide(),"20174.1.1.4", 9999)
    client = ClientSide()
    server = ServerSide()
    transportToServer = MockTransportToProtocol(server)
    transportToClient = MockTransportToProtocol(client)
    
    print('')
    packet_t1 = testpacket()
    packet_t1.counter1= 1
    packet_t1.data = b"Hello Sever"
    packet_t1bytes = packet_t1.__serialize__()	
    ClientSide.connection_made(transportToServer,packet_t1bytes)
    ServerSide.data_received(server,packet_t1bytes)
    
if __name__=="__main__":
	UnitTest()
