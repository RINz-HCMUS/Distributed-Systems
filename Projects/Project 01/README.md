# 💬 ĐỒ ÁN 01: ỨNG DỤNG CHAT SỬ DỤNG gRPC

**Sinh viên thực hiện:**
- Võ Hữu Tuấn – MSSV: 22127439

**Giảng viên hướng dẫn"**
- Thầy Dũng Trần Trung 

**Ngôn ngữ:** Python 3.10  
**Thư viện:** gRPC, Protobuf  

---

## 🎯 1. Mục tiêu đồ án
Mục tiêu: 
- Tìm hiểu và Sử dụng grpc để giao tiếp giữa các tiến trình. 
- Xây dựng hệ thống chat nhóm và chat riêng giữa nhiều client thông qua gRPC.  

Ứng dụng đáp ứng các yêu cầu:
- Đăng ký, đăng nhập user  
- Chat riêng (1-1)  
- Tạo nhóm chat  
- Thêm/rời nhóm  
- Gửi tin nhắn nhóm  
- Tra cứu lịch sử tin nhắn  

---

## 🧱 2. Kiến trúc hệ thống

```text
+----------------+
|   ChatClient   |  (nhiều tiến trình)
|  CLI (Python)  |
|----------------|
| gRPC call →    |
|   RegisterUser |
|   SendMessage  |
|   GetHistory   |
+----------------+
         │
         ▼
+----------------+
|   ChatServer   |
|  Python gRPC   |
|----------------|
|  user_sessions |
|  group manager |
|  log system    |
+----------------+
         │
         ▼
+----------------+
|   Data Layer   |
| data_manager.py|
|----------------|
| users.json     |
| groups.json    |
| chatlog.jsonl  |
+----------------+


## 📦 3. Cấu trúc thư mục

Project01/
├── chat.proto
├── chat_pb2.py
├── chat_pb2_grpc.py
├── server.py
├── client.py
├── data_manager.py
├── requirements.txt
├── README.md
└── data/
    ├── users.json
    ├── groups.json
    └── chatlog.jsonl

## ⚙️ 4. Cài đặt và chạy chương trình