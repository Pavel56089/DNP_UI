import socket
import sys
from threading import Thread, Lock
from multiprocessing import Queue

#function to handle the client request
def worker(queue):
    while True:
        try:
            client_sock, addr = queue.get()
            # client_sock.settimeout(10)
            with client_sock:
                print(f'{addr} connected')
                data = client_sock.recv(1024)
                numbers = list(map(int, data.decode().split('\n')))
                ans = []
                #check if the number is prime or not from the list
                for number in numbers:
                    result = f'{number} is ' + 'not ' * (not is_prime(number)) + 'prime'
                    ans.append(result)
                client_sock.sendall(str.encode('\n'.join(ans)))
                print(f'{addr} disconnected')
        except Exception as e:
            pass

#function to compute whether a number is prime or not
def is_prime(n: int) -> bool:
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    for divisor in range(3, n, 2):
        if n % divisor == 0:
            return False
    return True

#main function
def work():
    PORT = int(sys.argv[1])
    #create a socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('', PORT))
        sock.listen(10)
        queue = Queue(10)
        for _ in range(5):
            t = Thread(target=worker, args=(queue,), daemon=True)
            t.start()
    #accept the client request
        while True:
            try:
                client_sock, addr = sock.accept()
                queue.put((client_sock, addr,), True, None)
            # client_sock.settimeout(10)
            #KeyboadInterrupt to exit the program
            except KeyboardInterrupt:
                print('^C')
                print('Shutting down')
                print('Done')
                exit()
            except Exception:
                pass


if __name__ == '__main__':
    work()