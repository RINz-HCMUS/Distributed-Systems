import logging
import os
import sys
import threading
import time

# Tạo thư mục log và cờ hiệu
if not os.path.exists('logs'):
    os.makedirs('logs')
if not os.path.exists('flags'):
    os.makedirs('flags')

class SESLogger:
    _thread_lock = threading.Lock()

    def __init__(self, process_id):
        self.process_id = process_id
        self.log_file_path = f'logs/process_{process_id}.log'
        self.done_file_path = f'flags/P{process_id}.done'

        # Dọn dẹp file cũ 
        if os.path.exists(self.log_file_path): 
            try: os.remove(self.log_file_path)
            except: pass
        if os.path.exists(self.done_file_path): 
            try: os.remove(self.done_file_path)
            except: pass

        # Cấu hình Logger (Ghi file riêng biệt)
        self.logger = logging.getLogger(f'P{process_id}')
        self.logger.setLevel(logging.INFO)
        self.logger.handlers = [] 
        
        # File Handler: Atomic write style (delay=False, utf-8)
        f_handler = logging.FileHandler(self.log_file_path, mode='w', encoding='utf-8', delay=False)
        f_formatter = logging.Formatter(f'[%(asctime)s] [P{process_id}] %(message)s')
        f_handler.setFormatter(f_formatter)
        self.logger.addHandler(f_handler)

        # Console Handler: In ra màn hình
        c_handler = logging.StreamHandler(sys.stdout)
        c_handler.setFormatter(f_formatter)
        self.logger.addHandler(c_handler)

    def _force_flush(self):
        """Ép buộc ghi xuống đĩa ngay lập tức"""
        for h in self.logger.handlers:
            h.flush()
            if hasattr(h, 'stream') and hasattr(h.stream, 'fileno'):
                try: os.fsync(h.stream.fileno())
                except: pass

    def log(self, message):
        self.logger.info(message)
        self._force_flush()

    def log_buffer(self, msg, reason):
        self.logger.info(f"BUFFERED Msg from P{msg.sender_id} | TS: {msg.timestamp} | Reason: {reason}")
        self._force_flush()

    def log_deliver(self, msg, source="NETWORK"):
        self.logger.info(f"DELIVERED Msg from P{msg.sender_id} (Source: {source}) | TS: {msg.timestamp}")
        self._force_flush()

    def signal_completion(self):
        """TẠO FILE CỜ ĐỂ BÁO HIỆU HOÀN THÀNH"""
        try:
            with open(self.done_file_path, 'w') as f:
                f.write("DONE")
            self.logger.info(f"PROCESS COMPLETED! Flag created: {self.done_file_path}")
            self._force_flush()
        except Exception as e:
            self.logger.error(f"Failed to create flag file: {e}")