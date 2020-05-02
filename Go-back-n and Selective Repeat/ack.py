import pickle

class Ack:
    def __init__(self, checksum = None, ackNumber = None):
        self.ackNumber = ackNumber
        self.serialized_ack = None
        
    def getSerializedAck(self):
        if(not self.serialized_ack):
            self.serialized_ack = pickle.dumps({'ackNumber': self.ackNumber})
        return self.serialized_ack

    def deserializeAck(self, ack):
        deserialized_ack = pickle.loads(ack)
        print("!!!!! Deserialized ACK: ", deserialized_ack, " !!!!!")
        self.ackNumber = deserialized_ack['ackNumber']
        print("!!!!! Data: ", self.ackNumber, " !!!!!")