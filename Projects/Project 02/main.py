import sys
import json
import time
import random
import threading
import os
from logger import SESLogger
from network import NetworkModule
from ses_process import SESProcess

def load_config():
    with open('config.json', 'r') as f: return json.load(f)

def run_simulation(process_id):
    config = load_config()
    nodes_config = config['nodes']
    my_config = next((n for n in nodes_config if n['id'] == process_id), None)
    
    logger = SESLogger(process_id)
    if os.name == 'nt':
        os.system(f'title P{process_id} (PID: {os.getpid()}) - Port {my_config["port"]}')

    logger.log(f"STARTED. PID: {os.getpid()}")

    ses = SESProcess(my_config, nodes_config, logger, None)
    
    # --- THIẾT LẬP CHỈ TIÊU (KPI) ---
    msg_per_pair = config['system_settings']['total_messages_per_pair']
    # Tổng nhận = (Tổng số node - 1) * số tin mỗi cặp
    ses.expected_total = msg_per_pair * (len(nodes_config) - 1)
    
    logger.log(f"TARGET: Send {ses.expected_total} | Receive {ses.expected_total}")

    network = NetworkModule(process_id, my_config['ip'], my_config['port'], ses.process_incoming_message)
    ses.network = network
    network.start_server()

    logger.log("STANDBY: Waiting 5s...")
    time.sleep(5) 

    peers = [n for n in nodes_config if n['id'] != process_id]
    logger.log("CONNECTING...")
    for peer in peers:
        for retry in range(3):
            if network.connect_to_peer(peer['id'], peer['ip'], peer['port']): break
            time.sleep(0.5)
    
    logger.log(f"CONNECTED to {len(network.outgoing_connections)} peers.")
    time.sleep(2)

    logger.log(f"STARTING SEND...")
    delay_range = my_config['send_delay_range']

    for i in range(msg_per_pair):
        msg_index = i + 1
        for peer in peers:
            if peer['id'] not in network.outgoing_connections: continue
            content = f"M{msg_index} from P{process_id}"
            ses.send_message(peer['id'], content)
            time.sleep(random.uniform(delay_range[0], delay_range[1]))

    logger.log("FINISHED SENDING LOOP. Waiting for completion...")

    # Giữ process sống để nhận tin cho đến khi bị run_system tắt
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    if len(sys.argv) < 2: print("Usage: python main.py <process_id>")
    else: run_simulation(int(sys.argv[1]))