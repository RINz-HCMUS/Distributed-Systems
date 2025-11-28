import socket
import threading
import time
import random
from message import Message


class NetworkModule:
    def __init__(self, process_id, ip, port, ses_process_callback):
        self.process_id = process_id
        self.ip = ip
        self.port = port
        self.callback = ses_process_callback
        self.running = True
        
        self.outgoing_connections = {}
        self.lock = threading.Lock()

    # Khởi động server lắng nghe kết nối đến
    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server.bind((self.ip, self.port))
            server.listen(20)
            
            # Bắt đầu thread lắng nghe kết nối
            thread = threading.Thread(target=self._listen_loop, args=(server,))
            thread.daemon = True
            thread.start()
        except Exception as e:
            print(f"Server Start Error: {e}")

    # Vòng lặp lắng nghe kết nối đến
    def _listen_loop(self, server):
        while self.running:
            try:
                client, addr = server.accept()
                handler = threading.Thread(target=self._handle_keep_alive_client, args=(client,))
                handler.daemon = True
                handler.start()
            except:
                break
    
    def _handle_keep_alive_client(self, client_sock):
        """
        Đọc tin nhắn và GIẢ LẬP MẠNG LAG BẤT ĐỒNG BỘ.
        """
        try:
            stream = client_sock.makefile('r', encoding='utf-8')
            for line in stream:
                if not line.strip(): continue
                
                try:
                    msg = Message.from_json(line.strip())
                    
                    # --- Tạo độ trễ (mạng lag) để gây buffer---
                    # Thay vì gọi callback ngay, ta ném nó vào một thread riêng và delay ngẫu nhiên.
                    # Điều này cho phép msg đến sau có thể vượt mặt msg đến trước.
                    def delayed_delivery(message_obj):
                        # Delay ngẫu nhiên từ 0.5s đến 3.0s
                        time.sleep(random.uniform(0.5, 3.0))
                        self.callback(message_obj)

                    t = threading.Thread(target=delayed_delivery, args=(msg,))
                    t.start()
                    
                except Exception:
                    pass
        except Exception:
            pass
        finally:
            pass

    # Tạo kết nối peer-to-peer
    def connect_to_peer(self, target_id, target_ip, target_port):
        if target_id in self.outgoing_connections: return True
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((target_ip, target_port))
            with self.lock:
                self.outgoing_connections[target_id] = sock
            return True
        except Exception:
            return False

    def send_packet_persistent(self, target_id, message_obj):
        try:
            sock = self.outgoing_connections.get(target_id)
            if sock:
                data = message_obj.to_json() + "\n"
                sock.sendall(data.encode('utf-8'))
                return True
            else:
                return False
        except Exception:
            with self.lock:
                if target_id in self.outgoing_connections:
                    del self.outgoing_connections[target_id]
            return False