# 🎮 Tank Battle 

Game bắn xe tăng multiplayer theo mô hình **client–server**, được phát triển bằng **Python + Pygame**.

---

## 📌 TÍNH NĂNG CHÍNH

- Multiplayer real-time (TCP, server authoritative)
- Player di chuyển, bắn và tiêu diệt nhau
- Hệ thống hồi sinh an toàn (danger-zone aware)
- Giao diện đầy đủ:
  - Login / Register
  - Main Menu
  - Game Screen
  - Ranking TOP 25
  - Settings 
- Event log trong trận đấu
- Điểm trong trận và điểm tích lũy (lưu lâu dài)

---

## 📁 CẤU TRÚC DỰ ÁN

```
project_root/
├── common/            # Hằng số, protocol, logger dùng chung
├── server/            # Game server (authoritative)
├── client/            # Game client (UI + render)
│   └── assets/        # Hình ảnh (tank, barrel, bullet, map)
├── data/
│   └── users.json     # Dữ liệu người chơi (username, password, score)
├── logs/              # Log runtime (tự tạo)
└── README.md
```

---

## ⚙️ YÊU CẦU HỆ THỐNG

- Python **3.8 trở lên**
- Hệ điều hành: Windows / Linux / macOS
- Thư viện cần thiết:
  - `pygame`

---

## 📦 CÀI ĐẶT

### 1️⃣ Cài Python

Tải Python tại:  
https://www.python.org/downloads/

Trong quá trình cài đặt, nhớ chọn:
```
Add Python to PATH
```

---

### 2️⃣ Cài Pygame

Mở Terminal / CMD / PowerShell:

```bash
pip install pygame
```

Kiểm tra cài đặt:

```bash
python -c "import pygame; print(pygame.__version__)"
```

---

## ▶️ CÁCH CHẠY GAME

### Bước 1: Chạy Server

Tại thư mục gốc của project:

```bash
python server/server.py
```

Server sẽ chạy nền và chờ client kết nối.

---

### Bước 2: Chạy Client (có thể chạy nhiều client)

Mỗi cửa sổ terminal mới:

```bash
python client/client.py
```

Có thể mở **2–3 client** để kiểm thử multiplayer.

---

## 🧭 HƯỚNG DẪN SỬ DỤNG

### 🔐 LOGIN SCREEN
- Nhập **Username**
- Nhập **Password**
- `TAB` : chuyển ô input
- `ENTER` : đăng nhập
- `SPACE` : đăng ký tài khoản mới

---

### 🏠 MAIN MENU
- **PLAY** : vào game
- **SETTINGS** : cấu hình phím điều khiển
- **RANKING** : xem bảng xếp hạng TOP 25
- **INFO** : thông tin game
- **QUIT** : thoát game

---

### 🎮 IN-GAME CONTROLS (Mặc định)

| Hành động | Phím |
|---------|-----|
| Move Up | ↑ |
| Move Down | ↓ |
| Move Left | ← |
| Move Right | → |
| Shoot | SPACE |

(Có thể thay đổi trong mục **SETTINGS**)

---

### 🏆 RANKING
- Hiển thị **TOP 25 người chơi** theo điểm tích lũy
- Hiển thị:
  - Thứ hạng hiện tại của người chơi
  - Điểm tích lũy cá nhân
- Nếu người chơi ngoài TOP 25 → hiển thị `TOP25+`

---

## 🔄 CƠ CHẾ GAME

### 🔫 Bắn
- Mỗi player tối đa **4 viên đạn đang tồn tại**
- Mỗi lần bắn: **−1 điểm**
- Bắn trúng đối thủ: **+11 điểm**

### ☠️ Bị bắn trúng
- Player bị tiêu diệt ngay
- **−5 điểm**
- Xe tăng biến mất khỏi map

### ♻️ Hồi sinh
- Sau tối thiểu **3 giây**
- Chỉ hồi sinh tại vị trí **an toàn**:
  - Không trùng player khác
  - Không nằm trong tầm bắn trực diện của player còn sống
  - Có xét vật cản (wall) chặn đạn

---

## 🧠 KIẾN TRÚC KỸ THUẬT

- Mô hình **Server Authoritative**
- Client chỉ gửi intent (`MOVE`, `SHOOT`)
- Server xử lý:
  - Va chạm
  - Trúng đạn
  - Chết / hồi sinh
  - Điểm số
- Không sử dụng thread riêng cho gameplay logic

---

## 🧪 GỢI Ý KIỂM THỬ

- Chạy server
- Mở 2–3 client
- Kiểm tra:
  - Di chuyển & xoay barrel
  - Bắn và màu đạn đúng
  - Kill & respawn
  - Event log
  - Ranking cập nhật
  - Rebind phím trong SETTINGS

---

## 👤 TÁC GIẢ

- Sinh viên: *Võ Hữu Tuấn*
- Mã số sinh viên: *22127439*
- Học phần: *Chuyên đề Hệ thống phân tán*
- Lớp: *22MMT*
