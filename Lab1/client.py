from socket import socket, AF_INET, SOCK_DGRAM, timeout
import sys

DEST_IP_ADDR = "127.0.0.1"
DEST_PORT = 65432
PORT = 65433
BUF_SIZE = 1024
SEQNO0 = 0
NUMBER_TRIALS = 5
TIMEOUT_TIME = 0.5


class NoServerResponseException(Exception):
    pass


class SmallServerBufferException(Exception):
    pass


def is_valid_start_message_format(data, seqno):
    #Check if the format of first message is ok
    if len(data.split("|")) != 3:
        return False
    a, next_seqno, maxsize = data.split("|")
    try:
        int(maxsize)
        if a == "a" and int(next_seqno) == seqno + 1:
            return True
    except ValueError:
        pass
    return False


def is_valid_data_message_format(data, seqno):
    # Check if the format of message is ok
    if len(data.split("|")) != 2:
        return False
    a, next_seqno = data.split("|")
    try:
        if a == "a" and int(next_seqno) == seqno + 1:
            return True
    except ValueError:
        pass
    return False


def send_start_message(s, seqno, extension, size):
    # Send the first start message
    trial = 1
    while trial <= NUMBER_TRIALS:
        s.settimeout(TIMEOUT_TIME)
        try:
            encoded_message = f"s|{seqno}|{extension}|{size}".encode()
            s.sendto(encoded_message, (DEST_IP_ADDR, DEST_PORT))
            data, addr = s.recvfrom(BUF_SIZE)
            data = data.decode()
            if is_valid_start_message_format(data, seqno):
                _, _, maxsize = data.split("|")
                return int(maxsize)
        except timeout:
            trial += 1
    raise NoServerResponseException


def send_data_packet(s, seqno, data_frame):
    #Send the data pack to the server
    trial = 1
    while trial <= NUMBER_TRIALS:
        s.settimeout(TIMEOUT_TIME)
        try:
            encoded_message = f"d|{seqno}|".encode() + data_frame
            s.sendto(encoded_message, (DEST_IP_ADDR, DEST_PORT))
            data, _ = s.recvfrom(BUF_SIZE)
            data = data.decode()
            if is_valid_data_message_format(data, seqno):
                return
        except timeout:
            trial += 1
    raise NoServerResponseException


def split_data_into_packets(buffer_size, file_binary, seqno):
    packets = []
    i = 0
    while i < len(file_binary):
        rest_space = buffer_size - len(str(f"d|{seqno}|").encode())
        if rest_space <= 0:
            raise SmallServerBufferException
        end_index = i + rest_space
        end_index = end_index if end_index <= len(file_binary) else len(file_binary)
        packets.append(file_binary[i:end_index])
        seqno += 1
        i = end_index
    return packets


if __name__ == "__main__":
        with open(sys.argv[1], 'rb') as file:
            file_binary = file.read()
            with socket(AF_INET, SOCK_DGRAM) as s:
                s.bind(("localhost", PORT))
                try:
                    seqno = SEQNO0
                    buffsize = send_start_message(s, seqno, file.name.split(".")[-1], len(file_binary))
                    seqno += 1
                    data_frames = split_data_into_packets(buffsize, file_binary, seqno)
                    for data_frame in data_frames:
                        send_data_packet(s, seqno, data_frame)
                        seqno += 1
                    print("The file was sent.")
                except Exception as e:
                    print("Something going wrong...")