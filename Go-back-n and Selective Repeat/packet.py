import pickle


class Packet:
    def __init__(self, data=None, checksum=None, sequenceNumber=None, lastPacket=None):
        self.data = data
        self.checksum = checksum
        self.sequenceNumber = sequenceNumber
        self.lastPacket = lastPacket

        self.serialized_form = None

    def getSerializedPacket(self):
        if not self.serialized_form:
            self.serialized_form = pickle.dumps(
                {'sequenceNumber': self.sequenceNumber, 'checksum': self.checksum, 'data': self.data, 'lastPacket': self.lastPacket})
        return self.serialized_form

    def deserializePacket(self, packet):
        deserialized_form = pickle.loads(packet)
        self.data = deserialized_form['data']
        self.checksum = deserialized_form['checksum']
        self.sequenceNumber = deserialized_form['sequenceNumber']
        self.lastPacket = deserialized_form['lastPacket']
