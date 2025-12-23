import os
import time
from common.constants import LOG_DIR


class Logger:
    _file_path = None

    @staticmethod
    def setup(name):
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)
        Logger._file_path = os.path.join(
            LOG_DIR, f"{name}_{int(time.time())}.log"
        )

    @staticmethod
    def _write(level, msg):
        if not Logger._file_path:
            return
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] [{level}] {msg}\n"
        with open(Logger._file_path, "a", encoding="utf-8") as f:
            f.write(line)

    @staticmethod
    def info(msg):
        Logger._write("INFO", msg)

    @staticmethod
    def warning(msg):
        Logger._write("WARN", msg)

    @staticmethod
    def error(msg):
        Logger._write("ERROR", msg)
