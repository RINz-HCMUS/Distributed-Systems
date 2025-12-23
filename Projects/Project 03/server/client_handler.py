import threading
from common.protocol import recv_msg, send_msg

class ClientHandler(threading.Thread):
    def __init__(self, sock, addr, server):
        super().__init__(daemon=True)
        self.sock = sock
        self.addr = addr
        self.server = server
        self.player_id = None
        self.username = None

    def run(self):
        while True:
            msg = recv_msg(self.sock)
            if not msg:
                break

            action = msg.get("action")

            if action == "LOGIN":
                self._handle_login(msg)

            elif action == "REGISTER":
                self._handle_register(msg)

            elif action == "GET_RANKING":
                self._handle_ranking()

            elif action == "MOVE":
                self.server.handle_move(
                    self.player_id, msg.get("direction")
                )

            elif action == "SHOOT":
                self.server.handle_shoot(self.player_id)

        self._cleanup()

    # -------------------------------------------------

    def _handle_login(self, msg):
        u = msg.get("username")
        p = msg.get("password")

        ok, reason = self.server.user_mgr.validate(u, p)
        if not ok:
            send_msg(self.sock, {
                "type": "LOGIN_RESULT",
                "payload": {
                    "status": "fail",
                    "reason": reason
                }
            })
            return

        self.player_id = self.server.add_player(u, self.sock)
        self.username = u

        send_msg(self.sock, {
            "type": "LOGIN_RESULT",
            "payload": {
                "status": "success",
                "player_id": self.player_id
            }
        })

    # -------------------------------------------------

    def _handle_register(self, msg):
        u = msg.get("username")
        p = msg.get("password")

        ok, reason = self.server.user_mgr.create_user(u, p)

        send_msg(self.sock, {
            "type": "REGISTER_RESULT",
            "payload": {
                "status": "success" if ok else "fail",
                "reason": reason
            }
        })

    # -------------------------------------------------

    def _handle_ranking(self):
        top, sorted_users = self.server.user_mgr.get_ranking()

        my_rank = None
        my_score = None

        if self.username:
            for i, (u, info) in enumerate(sorted_users, start=1):
                if u == self.username:
                    my_rank = i
                    my_score = info["score"]
                    break

        send_msg(self.sock, {
            "type": "RANKING_RESULT",
            "payload": {
                "top": top,
                "my_rank": my_rank,
                "my_score": my_score
            }
        })

    # -------------------------------------------------

    def _cleanup(self):
        if self.player_id:
            self.server.remove_player(self.player_id)
        try:
            self.sock.close()
        except:
            pass
