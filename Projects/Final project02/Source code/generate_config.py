import json
import random

# --- CONFIG ---

# Số lượng Process
TOTAL_PROCESSES = 15

# Số tin nhắn mỗi Process gửi cho mỗi Process khác 
TOTAL_MESSAGES_PER_PAIR = 150 

# Địa chỉ IP và Port cơ sở
BASE_IP = "127.0.0.1"
BASE_PORT = 5000

# Cấu hình độ trễ gửi tin nhắn
DELAY_FAST_RANGE = [0.001, 0.01] # Nhanh (1ms - 10ms)   | 100 - 1000 msg/s 
DELAY_SLOW_RANGE = [0.01, 0.02]  # Chậm (10ms - 20ms)   | 50 - 100 msg/s


# Tạo cấu hình và lưu vào file JSON
def generate_config():
    config = {
        "system_settings": {
            "total_processes": TOTAL_PROCESSES,
            "total_messages_per_pair": TOTAL_MESSAGES_PER_PAIR
        },
        "nodes": []
    }

    # Tạo cấu hình cho từng Process
    for i in range(1, TOTAL_PROCESSES + 1):
        # Lẻ: nhanh | Chẵn: chậm
        current_delay = DELAY_FAST_RANGE if i % 2 != 0 else DELAY_SLOW_RANGE
        
        node = {
            "id": i,
            "ip": BASE_IP,
            "port": BASE_PORT + i,
            "send_delay_range": current_delay
        }
        config["nodes"].append(node)

    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)
    print(f"Generated FAST config for {TOTAL_PROCESSES} processes.")

if __name__ == "__main__":
    generate_config()