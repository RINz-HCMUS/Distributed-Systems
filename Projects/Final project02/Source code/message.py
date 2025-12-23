import json

class Message:
    def __init__(self, sender_id, receiver_id, content, timestamp, dependency_vector):
        self.sender_id = sender_id                  # ID người gửi
        self.receiver_id = receiver_id              # ID người nhận
        self.content = content                      # Nội dung tin nhắn
        self.timestamp = timestamp                  # Vector Clock tại thời điểm gửi (tm)
        self.dependency_vector = dependency_vector  # Vector phụ thuộc (VM)

    def to_json(self):
        """Chuyển đổi object thành chuỗi JSON để gửi qua mạng"""
        return json.dumps(self.__dict__)

    @staticmethod
    def from_json(json_str):
        """Tái tạo object từ chuỗi JSON nhận được"""
        data = json.loads(json_str)
        return Message(**data)

    def __repr__(self):
        return f"<Msg from P{self.sender_id} to P{self.receiver_id} | TS: {self.timestamp}>"