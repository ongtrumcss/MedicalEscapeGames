import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
import sys
import os

class MedicalState:
    def __init__(self):
        self.docs_left = 3
        self.pats_left = 3
        self.docs_right = 0
        self.pats_right = 0
        self.cart_pos = 'left' # 'left' (Vùng Đỏ) or 'right' (Vùng Xanh)
        self.game_over = False
        self.win = False
        self.msg = ""

    def move(self, docs, pats):
        if self.game_over or self.win:
            return False, "Thiết bị bị khóa! Chiến dịch đã kết thúc."

        total = docs + pats
        if total < 1 or total > 2:
            return False, "Cảnh báo tải trọng: Xe điện y tế chỉ chở được từ 1 đến 2 người!"

        # Xác minh vị trí
        if self.cart_pos == 'left':
            if docs > self.docs_left or pats > self.pats_left:
                return False, "Hệ thống lỗi: Sai lệch số liệu y tế ở Vùng Đỏ!"
            self.docs_left -= docs
            self.pats_left -= pats
            self.docs_right += docs
            self.pats_right += pats
            self.cart_pos = 'right'
        else:
            if docs > self.docs_right or pats > self.pats_right:
                return False, "Hệ thống lỗi: Sai lệch số liệu y tế ở Vùng Xanh!"
            self.docs_right -= docs
            self.pats_right -= pats
            self.docs_left += docs
            self.pats_left += pats
            self.cart_pos = 'left'

        self.check_rules()
        return True, "Di chuyển xe diện thành công."

    def check_rules(self):
        # 1. Kiểm tra lây nhiễm / Bạo loạn (Quy tắc sinh tồn: Bệnh nhân > Bác sĩ)
        if self.docs_left > 0 and self.pats_left > self.docs_left:
            self.game_over = True
            self.msg = "VÙNG ĐỎ MẤT KIỂM SOÁT: Bệnh nhân hoảng loạn áp đảo lực lượng y tế!"
        elif self.docs_right > 0 and self.pats_right > self.docs_right:
            self.game_over = True
            self.msg = "VÙNG XANH NHIỄM SÂM: Bệnh nhân bạo động, an ninh bị chọc thủng!"
            
        # 2. Kiểm tra Thắng cuộc
        elif self.docs_right == 3 and self.pats_right == 3:
            self.win = True
            self.msg = "Tất cả đã an toàn tới Vùng Xanh. Vô hiệu hóa vùng lây nhiễm..."

state = MedicalState()

class GameHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
            
        elif self.path == '/api/state':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(state.__dict__).encode('utf-8'))
            return
            
        return super().do_GET()

    def do_POST(self):
        global state
        if self.path == '/api/move':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            
            docs = data.get('docs', 0)
            pats = data.get('pats', 0)
            
            success, msg = state.move(docs, pats)
            
            res = {
                "success": success, 
                "msg": msg, 
                "state": state.__dict__
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(res).encode('utf-8'))
            
        elif self.path == '/api/reset':
            state = MedicalState()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": True}).encode('utf-8'))

if __name__ == '__main__':
    # Chuyển thư mục về thư mục chứa script để đọc html chuẩn xác
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    port = int(os.environ.get('PORT', 8888)) # Render sẽ cấp PORT
    
    server = HTTPServer(('0.0.0.0', port), GameHandler)
    print(f"===========================================================")
    print(f" ☣️ HỆ THỐNG AN NINH Y TẾ DÃ CHIẾN (PYTHON) ĐANG CHẠY ☣️ ")
    print(f"===========================================================")
    print(f" ► API Logic Mode: Isometric Medical Escape")
    print(f" ► Truy cập trình duyệt: http://localhost:{port} hoặc IP/Domain của host")
    print(f" Nhấn Ctrl+C để tắt hệ thống.")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nĐã hạ cầu dao toàn hệ thống.")
        sys.exit(0)
