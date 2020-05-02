import socket
import sys
import os
import logging
import random
import _thread
from checksum import Checksum
from packet import Packet

logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

UDP_IP_ADDRESS = "127.0.0.1"
UDP_PORT_NO = 6789


class GBN:
    def __init__(self, windowSize, sequenceBit):
        self.sequence_bits = sequenceBit
        self.window_size = windowSize
        self.expected_seq_number = 1
        self.once = True

    def receive_packet(self, packet):
        if packet.sequenceNumber == 4 and self.once:
            self.once = False
            return self.expected_seq_number, True
        if packet.sequenceNumber == self.expected_seq_number:
            self.expected_seq_number += 1
            return self.expected_seq_number, False
        else:
            return self.expected_seq_number, True  # to discard because the packet is either out of order or duplicate


class SR:
    def __init__(self, windowSize, sequenceBit):
        self.window_size = windowSize
        self.sequence_bits = sequenceBit
        self.r_base = 1
        self.sequence_max = 2 ** self.sequence_bits
        self.queue = {}
        self.next_seq_num = 1
        self.mutex = _thread.allocate_lock()  # slide window mutex

    def is_packet_in_order(self, sequenceNumber):
        if sequenceNumber in self.queue:
            return True
        elif sequenceNumber < self.next_seq_num:
            return True
        else:
            return False

    def add_one_to_queue(self):
        self.queue[self.next_seq_num] = 'waiting'
        self.next_seq_num += 1

    def slide_window(self):
        for key in self.queue:
            if self.queue[key] == 'rcvd':
                del self.queue[key]
                self.add_one_to_queue()
            else:
                return

    def init_queue(self):
        for i in range(self.r_base, self.window_size + 1):
            self.add_one_to_queue()

    def receive_packet(self, packet):
        self.mutex.acquire()
        if self.is_packet_in_order(packet.sequenceNumber):
            self.queue[packet.sequenceNumber] = 'rcvd'
            self.slide_window()
            self.mutex.release()
            return packet.sequenceNumber, False
        else:
            self.mutex.release()
            return packet.sequenceNumber, True  # to discard because the packet is out of order


class UDPHelper:
    def __init__(self, protocol_name, windowSize, sequenceBit):
        self.ip_address = '127.0.0.1'
        self.port_number = 6789
        self.serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.serverSock.bind((UDP_IP_ADDRESS, UDP_PORT_NO))
        self.receiver_running = False
        self.receiver = None
        self.protocol = None
        self.packets = 0
        self.selectedPacket = 5
        if protocol_name == "GBN":
            self.protocol = GBN(windowSize, sequenceBit)
        elif protocol_name == "SR":
            self.protocol = SR(windowSize, sequenceBit)
            self.protocol.init_queue()
        else:
            raise Exception('***** Invalid protocol name *****')

    def simulatePacketLoss(self):
        self.packets += 1
        if self.packets == 10:
            self.packets = 0
            self.selectedPacket = random.randint(0, 10)
        if self.selectedPacket == self.packets:
            self.selectedPacket = None
            return True
        return False

    def startListening(self):
        while True:
            try:
                data, addr = self.serverSock.recvfrom(1024)
                packet = Packet()
                packet.deserializePacket(data)

                if self.simulatePacketLoss():
                    print("!!!!! Packet: ", packet.sequenceNumber, " lost :(   !!!!!")
                    continue

                if Checksum.verify(packet.data, packet.checksum):
                    ack_num, discard = self.protocol.receive_packet(packet)
                    if discard:
                        print("!!!!! Discarding packet: " + str(packet.sequenceNumber), " !!!!!")
                    else:
                        print("!!!!! Received Segment: ", str(packet.sequenceNumber), " !!!!!")
                    _ = self.serverSock.sendto(str(ack_num).encode(), addr)  # sending ack with ack_num
                    print("!!!!! ACK Sent: ", str(ack_num) ,"!!!!!")
                else:
                    print("!!!!! Checksum Error!!!!! Packet: ", packet.sequenceNumber, " discarded !!!!!")

            except KeyboardInterrupt:
                print('*****Interrupted*****')
                os._exit(0)
            except ConnectionResetError:
                pass  # Do nothing.
            except Exception:
                raise Exception
        return

    def waitToReceive(self):
        self.receiver.join()
        return


if __name__ == "__main__":
    if len(sys.argv) is not 3:
        print("***** Please insert 4 arguments! ***** ")
        print("***** Syntax *****")
        print("***** Receiver.py inputfile(GBN/SR) portNumber *****")
    else:
        try:
            UDP_PORT_NO = int(sys.argv[2])
            file = open(sys.argv[1]).readlines()
            protocol = file[0].strip()
            sequence_bits = int(file[1].strip().split(' ')[0])
            window_size = int(file[1].strip().split(' ')[1])
            timeout_period = float(file[2].strip())
            segment_size = int(file[3].strip())

            if protocol == "GBN":
                udp_helper = UDPHelper('GBN', window_size, sequence_bits)
            elif protocol == "SR":
                udp_helper = UDPHelper('SR', window_size, sequence_bits)

            udp_helper.startListening()

        except Exception:
            raise Exception
