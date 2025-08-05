import datetime
import zmq
import time
import threading
import logging
import json

logging.basicConfig(
    format='%(asctime)s | %(levelname)s | %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

class DataValue(): 
    """Class to represent the card date value"""
    def __init__(self, card_id, date):
        self.card_id = card_id
        self.date = date
        self.date_urgency = "Not urgent"

    def update_urgency(self):
        """updates the urgency of the date based on the current time"""
        curr_time_iso = datetime.datetime.now()
        datetime_iso = datetime.datetime.fromisoformat(self.date)
        if curr_time_iso > datetime_iso or (datetime_iso - curr_time_iso).total_seconds() <= (24 * 3600):
            self.date_urgency = "Due within 24 hours or overdue"
        elif curr_time_iso < datetime_iso and (datetime_iso - curr_time_iso).total_seconds() <= (48 * 3600):
            self.date_urgency = "Due within 48 hours"
        else:
            self.date_urgency = "Not urgent"
        return self.date_urgency
    
class DateCache():
    """Class to repreesent a cache of dates"""
    def __init__(self, cache=None):
        if cache is None:
            cache = {}
        self.cache = cache
    
    def add_card(self, card_id, date):
        """Adds a card to the cache"""
        card = DataValue(card_id, date)
        card.update_urgency()
        self.cache[card_id] = card
    
    def get_card(self, card_id):
        return self.cache.get(card_id)
    
    def remove_card(self, card_id):
        """Removes a card from the cache"""
        if card_id in self.cache:
            del self.cache[card_id]
    
    def all_cards(self):
        """Returns the values of the given cards"""
        return list(self.cache.values())


def create_client_socket():
    client_context = zmq.Context()
    socket = client_context.socket(zmq.DEALER)
    socket.connect("tcp://localhost:5456") 
    return socket

def create_server_socket(): 
    server_context = zmq.Context()
    socket = server_context.socket(zmq.ROUTER)
    socket.bind("tcp://*:5458") 
    return socket

def update_thread(card, client_socket):
    """Updates the thing"""
    curr_urgency = card.update_urgency()
    new_status = {
        'card_id' : card.card_id,
        'urgency' : curr_urgency
        }
    reply = json.dumps(new_status).encode('utf-8')
    print(f"Sending update: {reply}")
    client_socket.send(reply)

def main():
    data_cache = DateCache()
    logging.debug("Creates sockets for server and client")
    server_socket = create_server_socket()
    client_socket = create_client_socket()

    poller = zmq.Poller()
    poller.register(server_socket, zmq.POLLIN)

    while True:
        socket_dict = dict(poller.poll(timeout=1000))
        if server_socket in socket_dict:
            message = None
            message_contents = server_socket.recv_multipart()
            id, content = message_contents[0], message_contents[-1]
            message = zmq.utils.jsonapi.loads(content.decode('utf-8'))
            if message is not None and message != b"":
                print(message)
                logging.debug("Message Recieved")
                date = message.get("due_date")
                action = message.get("action")
                card_id = message.get("card_id")
            if action == "new_card":
                logging.debug("adding new card")
                data_cache.add_card(card_id, date)
                logging.debug("sends message")
                reply = json.dumps({'status': 'card_added'}).encode('utf-8')
                client_socket.send(reply)
            elif action == "check_due_date":
                logging.debug("check_due_date")
                if card_id in data_cache.cache:
                    update_thread(data_cache.get_card(card_id), client_socket)
                else:
                    logging.debug("sent response")
                    reply = json.dumps({'error' : 'Card number not found'}).encode('utf-8')
                    client_socket.send(reply)
            else:
                logging.debug("sent response")
                reply = json.dumps({'error': 'Unknown action'}).encode('utf-8')
                client_socket.send(reply)

if __name__ == "__main__":
    main()
        


        


            
