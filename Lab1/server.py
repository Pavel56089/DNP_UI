import time, socket

def handle_start_message(data):
    indices = []
    for index, el in enumerate(data):
        if el == 124:
            indices.append(index)
    seqno0 = data[indices[0] + 1:indices[1]].decode()
    extension = data[indices[1] + 1:indices[2]].decode()
    size = data[indices[2] + 1:].decode()
    seqno0 = int(seqno0)
    file_info = {'next_seqno': seqno0 + 1,
                 'extension': str(extension),
                 'expected_size': int(size),
                 'file_binary': b'',
                 'time': recv_time,
                 'finished_session': False}
    clients[addr[0]] = file_info
    s.sendto(f"a|{seqno0 + 1}|{100}".encode(), addr)


def handle_data_message(data, recfiles):
    indices = []
    for index, el in enumerate(data):
        if el == 124:
            indices.append(index)
    seqno = data[indices[0] + 1:indices[1]].decode()
    data_bytes = data[indices[1] + 1:]
    next_seqno = clients[addr[0]]['next_seqno']
    if int(seqno) == next_seqno:
        next_seqno += 1
        s.sendto(f"a|{next_seqno}".encode(), addr)
        clients[addr[0]]['time'] = recv_time
        clients[addr[0]]['next_seqno'] = next_seqno
        clients[addr[0]]['file_binary'] += data_bytes
        if len(clients[addr[0]]['file_binary']) == clients[addr[0]]['expected_size']:
            clients[addr[0]]['finished_session'] = True
            recfiles += 1
            file_name = f'file {recfiles}.' + clients[addr[0]]['extension']
            with open(file_name, 'wb') as f:
                f.write(clients[addr[0]]['file_binary'])
                print(f'Received file from {addr[0]}')

    return recfiles

def is_start_message(data):
    try:
        if data[0:1].decode() == "s":
            return True
    except (ValueError, UnicodeDecodeError):
        pass
    return False


def is_data_message(data):
    try:
        if data[0:1].decode() == "d":
            return True
    except (ValueError, UnicodeDecodeError):
        pass
    return False

IP_ADDRESS = "127.0.0.1"
PORT = 65432
RECEIVED_FILES = 0
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind((IP_ADDRESS, PORT))
    try:
        clients = {}
        while True:
            print(f'Active clients: {len(clients.keys())}')
            s.settimeout(1)
            try:
                data, addr = s.recvfrom(100)
                recv_time = time.time()
                if is_start_message(data):
                    handle_start_message(data)
                elif is_data_message(data):
                    RECEIVED_FILES = handle_data_message(data, RECEIVED_FILES)
            except socket.timeout:
                t = time.time()
                clients_to_delete = []
                for client in clients:
                    file_info = clients[client]
                    last_tstamp = t - file_info['time']
                    if file_info['finished_session'] and last_tstamp >= 1:
                        clients_to_delete.append(client)
                    elif not file_info['finished_session'] and last_tstamp >= 3:
                        clients_to_delete.append(client)
                for client in clients_to_delete:
                    clients.pop(client, None)
    except KeyboardInterrupt:
        print("Keyboard interrupt, server is shutting down.")

        //print smth