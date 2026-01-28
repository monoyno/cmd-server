import socket
import sys

TARGET_IP = "ここにサーバー側のipを入力"

def start_client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((TARGET_IP, 5000))
            s.settimeout(None)
            while True:
                # 受信ループ
                while True:
                    s.settimeout(0.1)
                    try:
                        chunk = s.recv(8192)
                        if not chunk: break
                        
                        # 受信した塊に \x00 があれば UTF-16 とみなす
                        if b'\x00' in chunk:
                            try:
                                text = chunk.decode('utf-16', errors='replace')
                            except:
                                text = chunk.decode('cp932', errors='replace')
                        else:
                            text = chunk.decode('cp932', errors='replace')
                        
                        sys.stdout.write(text)
                        sys.stdout.flush()
                        
                        if text.strip().endswith(">"):
                            break
                    except socket.timeout:
                        continue

                cmd = input().strip()
                if not cmd:
                    s.sendall(b"\n")
                    continue
                s.sendall(cmd.encode('cp932'))
                if cmd.lower() == "exit": break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    start_client()
