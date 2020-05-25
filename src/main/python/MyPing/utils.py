#!/usr/bin/python
import argparse
import time
import struct
import socket
import select
import sys
from .opts import PingOptions


class PingUtil(object):

    def __init__(self):
        pass

    def chesksum(self, data):
        n = len(data)
        m = n % 2
        sum = 0 
        for i in range(0, n - m ,2):
            sum += (data[i]) + ((data[i+1]) << 8)
        if m:
            sum += (data[-1])

        sum = (sum >> 16) + (sum & 0xffff)
        sum += (sum >> 16)
        answer = ~sum & 0xffff

        answer = answer >> 8 | (answer << 8 & 0xff00)
        return answer 

    def raw_socket(self, dst_addr,imcp_packet):
        rawsocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
        send_request_ping_time = time.time()
        #send data to the socket
        rawsocket.sendto(imcp_packet, (dst_addr, 80))
        return send_request_ping_time, rawsocket, dst_addr

    def request_ping(self, data_type, data_code, data_checksum, data_ID, data_Sequence, payload_body):
        '''
        request ping
        '''
        icmp_packet = struct.pack('>BBHHH{}s'.format(self.packet_size), data_type, data_code,
            data_checksum, data_ID, data_Sequence, payload_body)
        icmp_chesksum = self.chesksum(icmp_packet)
        icmp_packet = struct.pack('>BBHHH{}s'.format(self.packet_size), data_type, data_code,
            icmp_chesksum, data_ID, data_Sequence, payload_body)
        return icmp_packet

    def reply_ping(self, send_request_ping_time,rawsocket,data_Sequence,timeout = 2):
        '''
        reply ping
        '''
        while True:
            started_select = time.time()
            what_ready = select.select([rawsocket], [], [], timeout)
            wait_for_time = (time.time() - started_select)
            if what_ready[0] == []:  # Timeout
                return -1

            time_received = time.time()
            buf_size = 2048 if self.packet_size < 2048 else int(self.packet_size * 1.5)
            received_packet, addr = rawsocket.recvfrom(buf_size)
            icmpHeader = received_packet[20:28]
            type, code, checksum, packet_id, sequence = struct.unpack(
                ">BBHHH", icmpHeader
            )
            if type == 0 and sequence == data_Sequence:
                return time_received - send_request_ping_time
            timeout = timeout - wait_for_time
            if timeout <= 0:
                return -1

    def ping(self, opt):
        host = opt.host
        self.packet_size = opt.packet_size
        ping_times = opt.ping_times

        data_type = 8 # ICMP Echo Request
        data_code = 0 # must be zero
        data_checksum = 0 # "...with value 0 substituted for this field..."
        data_ID = 0 #Identifier
        data_Sequence = 1 #Sequence number
        payload_body = b'abcdefghijklmnopqrstuvwabcdefghi0123456789' #data

        dst_addr = socket.gethostbyname(host)
        print("now Ping {0} [{1}] with {2} bytes of data:".format(host, dst_addr, self.packet_size))
        for i in range(0, ping_times):
            icmp_packet = self.request_ping(data_type, data_code, data_checksum,
                data_ID, data_Sequence + i, payload_body)
            send_request_ping_time,rawsocket,addr = self.raw_socket(dst_addr, icmp_packet)
            times = self.reply_ping(send_request_ping_time, rawsocket, data_Sequence + i)
            if times > 0:
                print("{0}/{1}: reply from {2} bytes = {3} time ={4}ms" \
                    .format(i+1, ping_times, addr, self.packet_size, int(times * 1000)))
                time.sleep(0.7)
            else:
                print("request time out")
        print()


if __name__ == "__main__":

    opt = PingOptions().parse()

    ping_util = PingUtil()
    ping_util.ping(opt)
