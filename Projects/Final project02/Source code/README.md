# ĐỒ ÁN HỆ THỐNG PHÂN TÁN: MÔ PHỎNG THUẬT TOÁN SES

**Tên đề tài:** Cài đặt thuật toán Schiper-Eggli-Sandoz (SES) 

---

## 1. GIỚI THIỆU (Introduction)

Dự án này xây dựng một hệ thống mô phỏng gồm **15 Tiến trình (Processes)** hoạt động song song, giao tiếp theo mô hình mạng lưới đầy đủ (Full-Mesh). Hệ thống được thiết kế để minh họa cơ chế **Vector Clock** và **Buffer** của thuật toán SES nhằm xử lý các thông điệp đến sai thứ tự do độ trễ mạng.

### Điểm nổi bật về Kỹ thuật (Technical Highlights):
* **Kiến trúc Bền vững (Persistent Connection):** Sử dụng kết nối TCP Keep-Alive thay vì đóng mở socket liên tục, giúp hệ thống chịu tải cao, tốc độ gửi cực nhanh và tránh lỗi cạn kiệt cổng (Port Exhaustion).
* **Cơ chế Smart Jitter/Chaos:** Tầng mạng (`network.py`) tự động tạo độ trễ ngẫu nhiên và xáo trộn thứ tự gói tin để ép buộc thuật toán SES phải thực hiện hành động **BUFFER** (kiểm chứng tính đúng đắn).
* **Cơ chế Báo hiệu (Flag Signaling):** Hệ thống tự động giám sát và kết thúc thông qua việc kiểm tra các file cờ (`.done`), đảm bảo tính đồng bộ hoàn hảo mà không cần can thiệp thủ công.
* **Logging An toàn (Atomic Write):** Cơ chế ghi log đảm bảo không bị xung đột, không bị ghi đè hay mất dữ liệu khi đa tiến trình cùng hoạt động trên Windows.

---

## 2. CẤU TRÚC DỰ ÁN (Project Structure)

```text
Project_SES/
│
├── main.py             # Chương trình chính
├── ses_process.py      # Module thuật toán SES 
├── network.py          # Module mạng 
├── message.py          # Định nghĩa cấu trúc gói tin 
├── logger.py           # Module ghi log và tạo tín hiệu cờ (.done)
├── run_system.py       # Script Quản lý hệ thống
├── generate_config.py  # Script sinh cấu hình mạng
├── requirements.txt    
├── config.json         # Cấu hình thông số hệ thống và các process
├── logs/               # Chứa file log chi tiết của từng Process
│   ├── process_1.log
│   └── ...
└── flags/              # Chứa các file tín hiệu hoàn thành (.done)
```

---

## 3. YÊU CẦU HỆ THỐNG (Prerequisites)

* **Ngôn ngữ:** Python 3.8 trở lên.
* **Hệ điều hành:** Windows 11
* **Thư viện:** Chỉ sử dụng Thư viện chuẩn của Python như `socket`, `threading`, `json`, `logging`, `os`...

---

## 4. HƯỚNG DẪN CÀI ĐẶT & CHẠY (Installation & Usage)

### Bước 1: Tạo cấu hình mạng
Mở terminal tại thư mục dự án và chạy lệnh:
```bash
python generate_config.py
```
*Lệnh này sẽ tạo ra file `config.json` với cấu hình chuẩn cho các process.*

### Bước 2: Khởi chạy hệ thống
Chạy script quản lý trung tâm để kích hoạt toàn bộ hệ thống:
```bash
python run_system.py
```

### Bước 3: Quan sát quá trình chạy
1.  Chương trình sẽ tự động bật **15 cửa sổ Terminal con**.
2.  Tại mỗi cửa sổ, tiêu đề sẽ hiển thị **ID** và **PID** (Process ID thực trong Task Manager) để tiện theo dõi tài nguyên.
3.  **Giai đoạn 1 (Standby):** Các process chờ 5s để tất cả cùng khởi động server.
4.  **Giai đoạn 2 (Connecting):** Các process thiết lập kết nối bền vững với nhau.
5.  **Giai đoạn 3 (Sending):** Bắt đầu gửi tin nhắn xoay vòng (Round-Robin).
6.  **Giai đoạn 4 (Receiving & Buffering):** Đây là lúc thuật toán SES hoạt động. Bạn sẽ thấy các dòng log `BUFFERED` xuất hiện trên các cửa sổ con khi tin nhắn đến sai thứ tự.

### Bước 4: Kết thúc tự động
Tại cửa sổ `run_system.py` (cửa sổ chính), bạn sẽ thấy dòng trạng thái như sau:
`>> Status: X/X Processes Finished.`

* Khi một Process hoàn thành (Gửi đủ + Nhận đủ + Buffer rỗng), nó sẽ tạo một file cờ trong thư mục `flags/`.
* Khi đủ **15/15**, hệ thống sẽ thông báo `ALL PROCESSES COMPLETED!` và tự động đóng toàn bộ các cửa sổ sau 3 giây.

---

## 5. CÁCH KIỂM TRA KẾT QUẢ (Verification)


**1. Kiểm tra thư mục `flags/`:**
Phải có đủ 15 file (từ `P1.done` đến `P15.done`).
> *Ý nghĩa:* Sự tồn tại của file này chứng tỏ Process đó đã **gửi đủ 100% số tin nhắn đặt ra** cùng với đó là  **nhận đủ 100% số tin nhắn kỳ vọng** và **không còn tin nhắn nào bị kẹt trong Buffer**.

**2. Kiểm tra file log (`logs/process_X.log`):**
Mở bất kỳ file log nào để kiểm tra chi tiết hoạt động của thuật toán.
* Tìm từ khóa `BUFFERED`: Để thấy thuật toán đã chặn tin nhắn sai thứ tự như thế nào.
    * *Ví dụ:* `BUFFERED Msg from P1 | Reason: Constraint [...] > Local [...]`
* Tìm từ khóa `RE-SCANNING`: Để thấy tin nhắn được giải phóng khỏi Buffer khi điều kiện nhân quả được thỏa mãn.
* Dòng cuối cùng của log sẽ luôn là thông báo hoàn thành nhiệm vụ.

---

## 6. CẤU HÌNH TÙY CHỈNH (Configuration)

Bạn có thể thay đổi kịch bản mô phỏng bằng cách sửa file `generate_config.py` và chạy lại nó:

* **`TOTAL_PROCESSES`**: Số lượng tiến trình (Mặc định: 15).
* **`TOTAL_MESSAGES_PER_PAIR`**: Số lượng tin nhắn mỗi cặp gửi cho nhau (Mặc định: 150).
* **`DELAY_FAST_RANGE` / `DELAY_SLOW_RANGE`**: Tinh chỉnh tốc độ gửi để kiểm thử khả năng chịu tải hoặc tạo độ lệch pha lớn hơn.

---
