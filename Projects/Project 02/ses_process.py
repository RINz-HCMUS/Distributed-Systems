import threading
import copy
from message import Message

class SESProcess:
    def __init__(self, config_node, all_nodes_config, logger, network):
        self.id = config_node['id']
        self.logger = logger
        self.network = network
        self.all_nodes = all_nodes_config
        self.total_nodes = len(all_nodes_config)

        # Logic SES
        self.local_clock = [0] * self.total_nodes
        self.dependency_vector = {}
        self.buffer = []
        self.lock = threading.Lock()

        # KPIs (Chỉ tiêu)
        self.msg_sent_count = 0
        self.msg_delivered_count = 0
        self.expected_total = 0 # Sẽ được set từ main.py
        self.finished = False

    def check_finish(self):
        """Kiểm tra điều kiện hoàn thành"""
        if self.finished: return

        # Điều kiện: Gửi đủ + Nhận đủ + Buffer sạch
        if (self.expected_total > 0 and 
            self.msg_sent_count >= self.expected_total and 
            self.msg_delivered_count >= self.expected_total and 
            len(self.buffer) == 0):
            
            self.finished = True
            self.logger.signal_completion()

    def get_clock_index(self, pid):
        return int(pid) - 1

    def send_message(self, target_id, content):
        target_info = next((n for n in self.all_nodes if n['id'] == target_id), None)
        if not target_info: return

        with self.lock:
            my_idx = self.get_clock_index(self.id)
            self.local_clock[my_idx] += 1
            tm = copy.deepcopy(self.local_clock)
            vm = copy.deepcopy(self.dependency_vector)
            self.dependency_vector[str(target_id)] = tm

        msg = Message(self.id, target_id, content, tm, vm)
        self.logger.log(f"SENDING Msg to P{target_id} | TS: {tm}")
        
        # Gửi đi
        if self.network.send_packet_persistent(target_id, msg):
            with self.lock:
                self.msg_sent_count += 1
            self.check_finish() # Kiểm tra ngay sau khi gửi

    def process_incoming_message(self, msg):
        with self.lock:
            can_deliver, reason = self.check_delivery_condition(msg)
            if can_deliver:
                self.deliver(msg, source="NETWORK")
            else:
                self.buffer.append(msg)
                self.logger.log_buffer(msg, reason)

    def check_delivery_condition(self, msg):
        msg_vector = msg.dependency_vector
        my_id_str = str(self.id)
        if my_id_str in msg_vector:
            t_constraint = msg_vector[my_id_str]
            if not self.is_vector_less_equal(t_constraint, self.local_clock):
                 return False, f"Constraint {t_constraint} > Local {self.local_clock}"
        return True, "OK"

    def deliver(self, msg, source):
        self.logger.log_deliver(msg, source)
        self.msg_delivered_count += 1
        
        for i in range(self.total_nodes):
            self.local_clock[i] = max(self.local_clock[i], msg.timestamp[i])
        my_idx = self.get_clock_index(self.id)
        self.local_clock[my_idx] += 1
        
        for pid, t_vec in msg.dependency_vector.items():
            if pid not in self.dependency_vector:
                self.dependency_vector[pid] = t_vec
            else:
                self.dependency_vector[pid] = self.max_vector(self.dependency_vector[pid], t_vec)
        
        self.check_finish() # Kiểm tra ngay sau khi nhận
        
        if source == "NETWORK":
            self.check_buffer()

    def check_buffer(self):
        if not self.buffer: return
        while True:
            deliverable = []
            for m in self.buffer:
                can_del, _ = self.check_delivery_condition(m)
                if can_del:
                    deliverable.append(m)
            if not deliverable: break 
            for m in deliverable:
                self.buffer.remove(m)
                self.logger.log(f"RE-SCANNING BUFFER: Found deliverable Msg from P{m.sender_id}")
                self.deliver(m, source="BUFFER")

    def is_vector_less_equal(self, v1, v2):
        if len(v1) != len(v2): return False
        for i in range(len(v1)):
            if v1[i] > v2[i]: return False
        return True

    def max_vector(self, v1, v2):
        res = []
        for i in range(len(v1)):
            res.append(max(v1[i], v2[i]))
        return res