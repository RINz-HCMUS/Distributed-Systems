# 🛰️ Project 01 – Distributed Chat System (gRPC-based)

> **Course:** Distributed Systems  
> **Student:** <span style="color:#00b4d8">Võ Hữu Tuấn — 22127439</span>  
> **Lecturers:** <span style="color:#ffafcc">Mr. Trần Trung Dũng</span>,  
> **Institution:** <span style="color:#48cae4">University of Science, VNU-HCM</span>  

---

## 📖 Overview

This project implements a **distributed real-time chat system** using **gRPC** in Python.  
It supports **multi-user, multi-group, and concurrent chat** with real-time updates and secure persistent logging.

Key Features:
- ✅ Secure login/logout with session management
- ✅ Private & group messaging
- ✅ Group creation, deletion, and membership management
- ✅ Persistent chat & system logs with timestamp normalization
- ✅ Multi-client concurrency using gRPC bidirectional streaming

---

## 🧩 System Architecture

```
+-------------+       +-------------+       +-------------+
|   Client 1  |       |   Client 2  |  ...  |   Client N  |
|-------------|       |-------------|       |-------------|
| gRPC Stub   |       | gRPC Stub   |       | gRPC Stub   |
| Command CLI |       | Command CLI |       | Command CLI |
+-------------+       +-------------+       +-------------+
          ⇅                  ⇅                   ⇅
          ⇄   gRPC SERVER (Python, asyncio)      ⇄
```

Clients connect to the **gRPC Server** through **bidirectional streaming**, ensuring real-time communication between users and groups.

---

## 📂 Directory Structure

```
Project01/
│
├── data/
│   ├── users.json        # User registry & group memberships
│   └── groups.json       # Group metadata and members
│
├── log/
│   ├── chatlog.jsonl     # Message logs (with anonymized users)
│   └── serverlog.jsonl   # System & error logs (timestamp-first format)
│
├── chat.proto            # gRPC protocol definition
├── chat_pb2.py           # Generated gRPC code
├── chat_pb2_grpc.py      # gRPC service bindings
│
├── data_manager.py       # File + log management utilities
├── server.py             # Chat server logic
├── client.py             # CLI chat client
│
├── requirements.txt      # Dependencies
└── READMEv2.md           # Documentation (this file)
```

---

## ⚙️ Installation & Setup

### 🪟 **For Windows**

Set up environment:
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. chat.proto
```

Start server in terminal:
```bash
python server.py
```

✅ Expected output:
```
Server started on port 50051
```

Start multiple clients in new terminals:
```bash
python client.py
```

### 🐧 **For Linux / macOS**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 server.py
```

Then open 3–5 terminals and run:
```bash
python3 client.py
```

---

## 💬 User Commands

Commands are entered directly in the client terminal. Type `help` to see available commands.

### 🔐 Login / Logout

| Command | Description |
|----------|--------------|
| `Enter your username:` | Log in with a username when starting client |
| `logout` | Disconnect from the server |

---

### 💬 Messaging

| Command | Description | Example |
|----------|--------------|----------|
| `msg user <username> <message> /end/` | Send private message | `msg user user02 hi /end/` |
| `msg group <group> <message> /end/` | Send group message | `msg group ABC hello team /end/` |

🧩 **Note:** Use `/end/` to mark message completion (supports multiline input).

---

### 👥 Group Management

| Command | Description | Example |
|----------|--------------|----------|
| `create group <name>` | Create a new group | `create group ABC` |
| `delete group <name>` | Delete a group *(admin only)* | `delete group ABC` |
| `add member <group> <user>` | Add user to group | `add member ABC user03` |
| `remove member <group> <user>` | Remove member *(admin only)* | `remove member ABC user03` |
| `leave group <name>` | Leave a group | `leave group ABC` |

📢 Notifications:
- **New member**: `[group ABC] user01 đã thêm bạn vào nhóm!`
- **Existing members**: `[group ABC] user01 đã thêm user03 vào nhóm!`

---

### 📋 Listing

| Command | Description |
|----------|--------------|
| `list users` | Show online users |
| `list groups` | Show joined groups |

Example:
```
Online users:
- user01
- user02

Your groups:
1. ABC <admin: user>
2. XYZ <admin: you>
```

---

### 🕘 Inbox & History

| Command | Description | Example |
|----------|--------------|----------|
| `inbox [n]` | Show last *n* incoming messages | `inbox 20` |
| `sent [n]` | View last *n* sent messages | `sent 20`|
| `history user <username> [n]` | View message history with a user | `history user user02 10` |
| `history group <group> [n]` | View recent group messages | `history group ABC 15` |

🧠 **Format:**
```
[2025-10-31 15:12:10] [from user] hi there!
[2025-10-31 15:12:12] [you] hello!
[2025-10-31 15:13:00] [from group ABC] [user02] welcome!
```

---


## 🧾 Logging System

### 🗂️ `log/chatlog.jsonl`
Stores anonymized message logs:
```
[2025-10-31 15:01:10] {"type": "private", "from": "user", "to": "user", "msg": "hello!"}
[2025-10-31 15:03:12] {"type": "group", "group": "ABC", "from": "user01", "msg": "welcome!"}
```

### 🧩 `log/serverlog.jsonl`
Stores system & error events (timestamp-first):
```
[2025-10-31 15:01:12] {"category": "system", "event": "login", "user": "user01"}
[2025-10-31 15:02:33] {"category": "group", "event": "add_member", "group": "ABC", "user": "user03", "by": "user01"}
[2025-10-31 15:04:01] {"category": "error", "function": "SendCommand", "message": "Invalid user"}
```

---

## 🧰 Troubleshooting

| Issue | Cause | Fix |
|--------|--------|------|
| “Server error. Please try again.” | Invalid command / gRPC issue | Check `serverlog.jsonl` |
| Logs missing | `log/` folder not found | Ensure `log/` directory exists |
| Client disconnects | Server inactive | Run `server.py` first |
| No colors visible | ANSI unsupported | Use VSCode / Windows Terminal |

---

## 📜 License

MIT License © <span style="color:#90e0ef">2025 Võ Hữu Tuấn</span>

---

## 🧠 Notes for Instructors

This project demonstrates:
- Distributed client-server synchronization  
- Real-time **gRPC bidirectional streaming**  
- Secure & structured logging  
- Multi-user concurrency management  

---

## 📸 Demo

🎥 **Video Demo:** [Watch on YouTube](https://youtu.be/demo_project01)

---

✨ *End of README*

