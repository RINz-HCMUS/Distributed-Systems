import threading
import queue
import time
import random
import logging
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# ======================================
# CONFIG
# ======================================

NUM_PROCESSES = 15
MESSAGES_PER_DEST = 150     # mỗi process gửi 150 msg cho mỗi process khác


def get_send_interval(pid: int):
    """
    Điều chỉnh tốc độ gửi để runtime ~5 phút.
    """
    if pid == 0:
        return random.uniform(1.0, 1.5)
    elif 1 <= pid <= 7:
        return random.uniform(2.0, 3.0)
    else:
        return random.uniform(4.0, 7.0)


# ======================================
# GLOBAL LOGGER
# ======================================

def setup_global_logger() -> logging.Logger:
    logger = logging.getLogger("GLOBAL")
    logger.setLevel(logging.DEBUG)

    os.makedirs("logs", exist_ok=True)

    fh = logging.FileHandler(os.path.join("logs", "global.log"), mode="w", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fmt = logging.Formatter("%(asctime)s %(message)s", datefmt="%H:%M:%S")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    logger.addHandler(ch)

    logger.propagate = False
    return logger


# ======================================
# PER-PROCESS LOGGER
# ======================================

def setup_process_logger(pid: int) -> logging.Logger:
    logger = logging.getLogger(f"PROC_{pid}")
    logger.setLevel(logging.DEBUG)

    os.makedirs("logs", exist_ok=True)
    fh = logging.FileHandler(os.path.join("logs", f"process_{pid}.log"), mode="w", encoding="utf-8")
    fh.setLevel(logging.DEBUG)

    fmt = logging.Formatter(
        "%(asctime)s [P%(process_id)d] [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S"
    )
    fh.setFormatter(fmt)

    class ProcessFilter(logging.Filter):
        def filter(self, record):
            record.process_id = pid
            return True

    logger.addFilter(ProcessFilter())
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    logger.addHandler(ch)

    logger.propagate = False
    return logger


# ======================================
# MESSAGE STRUCTURE
# ======================================

@dataclass
class SESMessage:
    src: int
    dst: int
    seq: int
    tm: List[int]
    v_m: Dict[int, List[int]] = field(default_factory=dict)


# ======================================
# NETWORK SIMULATION
# ======================================

class Network:
    def __init__(self, num_processes: int, global_logger: logging.Logger):
        self.num_processes = num_processes
        self.queues = {pid: queue.Queue() for pid in range(num_processes)}
        self.global_logger = global_logger

    def send(self, msg: SESMessage):
        net_delay = random.uniform(0.02, 0.10)
        time.sleep(net_delay)
        self.queues[msg.dst].put(msg)

        # Network không log gì thêm (hoặc bật lại nếu cần)
        # self.global_logger.info(f"[P{msg.src}] delivered_to_P{msg.dst} msg#{msg.seq}")

    def get_inbox(self, pid: int):
        return self.queues[pid]


# ======================================
# VECTOR CLOCK SUPPORT
# ======================================

def vc_copy(vc: List[int]):
    return list(vc)

def vc_componentwise_max(a: List[int], b: List[int]):
    return [max(x, y) for x, y in zip(a, b)]

def vc_greater_strict(a: List[int], b: List[int]):
    return all(a_i > b_i for a_i, b_i in zip(a, b))


# ======================================
# SES PROCESS IMPLEMENTATION
# ======================================

class SESProcess:
    def __init__(self, pid: int, num_processes: int, network: Network):
        self.pid = pid
        self.num_processes = num_processes
        self.network = network

        self.tP = [0] * num_processes
        self.V_P = {}
        self.buffer = []

        self.inbox = self.network.get_inbox(pid)
        self.logger = setup_process_logger(pid)

        self.sent_count = 0
        self.delivered_count = 0
        self.buffered_count = 0

        self.lock = threading.Lock()
        self.stop_event = threading.Event()

        self.sender_threads = []
        self.receiver_thread = None

    # Helper
    def _log_state_prefix(self):
        vp = ", ".join(f"{k}:{v}" for k, v in self.V_P.items())
        return f"[P{self.pid}] tP={self.tP} V_P={{ {vp} }}"

    def _increment_clock(self):
        self.tP[self.pid] += 1

    # --------------------------------
    # SENDER
    # --------------------------------
    def _sender_worker(self, dst: int):
        for seq in range(1, MESSAGES_PER_DEST + 1):

            with self.lock:
                self._increment_clock()
                tm = vc_copy(self.tP)
                v_m = {k: vc_copy(v) for k, v in self.V_P.items()}

                msg = SESMessage(self.pid, dst, seq, tm, v_m)
                self.sent_count += 1

                # console
                print(f"[P{self.pid}] SEND msg#{seq} → P{dst}")

                # per-process log
                self.logger.info(f"SEND seq={seq} → P{dst} tm={tm}")

                # global log (THEO FORMAT YÊU CẦU)
                self.network.global_logger.info(
                    f"[P{self.pid}] [SEND] to P{dst} | msg#{seq} | tm={tm}"
                )

            self.network.send(msg)

            with self.lock:
                self.V_P[dst] = vc_copy(tm)

            time.sleep(get_send_interval(self.pid))

    # --------------------------------
    # RECEIVER
    # --------------------------------
    def _can_deliver(self, msg: SESMessage):
        entry = msg.v_m.get(self.pid)
        if entry is None:
            return True
        if vc_greater_strict(msg.tm, self.tP):
            return False
        return True

    def _deliver_message(self, msg: SESMessage, reason: str):
        self.tP = vc_componentwise_max(self.tP, msg.tm)

        for p, t in msg.v_m.items():
            if p not in self.V_P:
                self.V_P[p] = vc_copy(t)
            else:
                self.V_P[p] = vc_componentwise_max(self.V_P[p], t)

        self.delivered_count += 1

        if reason == "DIRECT":
            print(f"[P{self.pid}] DELIVER_DIRECT msg#{msg.seq} from P{msg.src}")
        else:
            print(f"[P{self.pid}] DELIVER_FROM_BUFFER msg#{msg.seq} from P{msg.src}")

        self.logger.info(
            f"{reason} <- src={msg.src} seq={msg.seq} {self._log_state_prefix()}"
        )

    def _buffer_message(self, msg: SESMessage):
        self.buffer.append(msg)
        self.buffered_count += 1

        print(f"[P{self.pid}] BUFFER msg#{msg.seq} from P{msg.src}")
        self.logger.info(
            f"BUFFER <- src={msg.src} seq={msg.seq} {self._log_state_prefix()}"
        )

    def _try_deliver_buffer(self):
        changed = True
        while changed:
            changed = False
            for msg in list(self.buffer):
                if self._can_deliver(msg):
                    self.buffer.remove(msg)
                    self._deliver_message(msg, "DELIVER_FROM_BUFFER")
                    changed = True

    def _receiver_worker(self):
        while not self.stop_event.is_set() or not self.inbox.empty():
            try:
                msg = self.inbox.get(timeout=0.2)
            except queue.Empty:
                continue

            with self.lock:
                if self._can_deliver(msg):
                    self._deliver_message(msg, "DELIVER_DIRECT")
                    self._try_deliver_buffer()
                else:
                    self._buffer_message(msg)

    # --------------------------------
    # PUBLIC API
    # --------------------------------

    def start(self):
        for dst in range(self.num_processes):
            if dst == self.pid:
                continue
            t = threading.Thread(target=self._sender_worker, args=(dst,), daemon=True)
            self.sender_threads.append(t)

        self.receiver_thread = threading.Thread(target=self._receiver_worker, daemon=True)
        self.receiver_thread.start()

        for t in self.sender_threads:
            t.start()

    def wait_until_done(self):
        for t in self.sender_threads:
            t.join()

        time.sleep(5)
        self.stop_event.set()

        if self.receiver_thread:
            self.receiver_thread.join()

        self.logger.info(
            f"SUMMARY sent={self.sent_count}, delivered={self.delivered_count}, buffered={self.buffered_count} "
            f"{self._log_state_prefix()}"
        )


# ======================================
# MAIN
# ======================================

def main():
    global_logger = setup_global_logger()
    global_logger.info("=== SES 15-PROCESS SIMULATION START ===")

    network = Network(NUM_PROCESSES, global_logger)
    processes = [SESProcess(pid, NUM_PROCESSES, network) for pid in range(NUM_PROCESSES)]

    for p in processes:
        p.start()

    for p in processes:
        p.wait_until_done()

    global_logger.info("=== SES 15-PROCESS SIMULATION END ===")


if __name__ == "__main__":
    main()
