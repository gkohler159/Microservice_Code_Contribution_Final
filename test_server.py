import zmq 
import logging
import threading
import time 
import json

#implemented debugging
logging.basicConfig(
    format='%(asctime)s | %(levelname)s | %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S'
)

date_one = "2025-08-03T15:55:00"
date_two = "2025-08-04T15:55:00"
date_three = "2025-08-05T15:55:00"
date_four = "2025-08-06T15:55:00"

def json_generator():
    """Generates JSON examples to be sent off to server"""
    card_id = input("Please input card ID: ")
    date = input("Please input date in ISO format (2025-08-06T15:55:00): ")
    action = input("Please press 1 for new_card and 2 for check_due_date: ")
    if action == '1':
        action = "new_card"
    else:
        action = "check_due_date"

    payload = {'card_id' : card_id,
               'due_date' : date,
               'action' : action,
               }
    return payload

def create_client_socket():
    """Creates a client socket for testing"""
    client_context = zmq.Context()
    socket = client_context.socket(zmq.DEALER)
    socket.connect("tcp://localhost:5458") 
    return socket

def create_server_socket():
    """Creates a server socket for testing"""
    server_context = zmq.Context()
    socket = server_context.socket(zmq.ROUTER)
    socket.bind("tcp://*:5456") 
    return socket

def client_message():
    """The client part of this"""
    client_socket = create_client_socket()
    while True:
        package = json_generator()
        if package is not None:
            logging.debug("Sending message...")
            reply = json.dumps(package).encode('utf-8')
            client_socket.send(reply)
            print(f"reply: {reply}")
            logging.debug("Sent Message")
        time.sleep(0.5)

def server_thread():
    """Server thread"""
    server_socket = create_server_socket()
    while True: 
        message = None
        message_contents = server_socket.recv_multipart()
        identity, content = message_contents[0], message_contents[-1]
        message = zmq.utils.jsonapi.loads(content.decode('utf-8'))
        logging.debug("Recieved data")
        response = {'card_id': message.get("card_id"), 'status' : 'recieved'}
        if message.get('urgency'):
            urgency = message.get('urgency')
            print(urgency)
        logging.debug("server thread sent response")
        server_socket.send_multipart([identity, b'',
            json.dumps(response).encode("utf-8")
        ])
        print(response)


def main():
    server_thread_instance = threading.Thread(target=server_thread, daemon=True)
    server_thread_instance.start()
    time.sleep(2)
    client_message()

if __name__ == "__main__":
    main()


