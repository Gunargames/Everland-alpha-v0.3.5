from ursinanetworking import *

Server = UrsinaNetworkingServer("localhost", 25565)
players = {}  # {client_id: position}

def on_message_received(client, message_type, data):
    sender_id = str(id(client))
    if message_type == 'position_update':
        print(f"Received position_update from {sender_id}: {data['position']}")
        players[sender_id] = data['position']
        # Relay position update to all other clients
        for c in Server.clients:
            if c != client:
                Server.send_message(c, 'player_position', {'client': sender_id, 'position': data['position']})

def on_client_connected(client):
    new_id = str(id(client))
    print(f"Client connected: {new_id}")
    # Send all existing player positions to the new client
    for pid, pos in players.items():
        Server.send_message(client, 'player_position', {'client': pid, 'position': pos})

def on_client_disconnected(client):
    disc_id = str(id(client))
    print(f"Client disconnected: {disc_id}")
    if disc_id in players:
        del players[disc_id]
    # Notify all clients to remove this player
    for c in Server.clients:
        Server.send_message(c, 'player_disconnect', {'client': disc_id})

Server.on_message_received = on_message_received
Server.on_client_connected = on_client_connected
Server.on_client_disconnected = on_client_disconnected

print("Server started. Waiting for players...")
while True:
    Server.process_net_events()
