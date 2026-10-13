import os
import sys
import json
import time
import random
import socket
import ssl
import base64
import shutil
import threading
import subprocess
import ctypes
from urllib.parse import urlsplit

import colorama
from colorama import Fore, Style
from selenium import webdriver

colorama.init(autoreset=True)

BAZA_PROFILEY = "profiliki.json"

COLOR_PASTEL = (152, 238, 152)
COLOR_LIME = (200, 255, 100)
COLOR_MINT = (140, 220, 180)
COLOR_DIM = (110, 160, 120)

def rgb_fg(r, g, b):
    return f"\033[38;2;{int(r)};{int(g)};{int(b)}m"

def gradient_text(text, c_start=COLOR_PASTEL, c_end=COLOR_LIME):
    n = len(text)
    if n <= 1:
        return f"{rgb_fg(*c_start)}{text}{Style.RESET_ALL}"
    res = []
    for i, ch in enumerate(text):
        ratio = i / (n - 1)
        r = c_start[0] + (c_end[0] - c_start[0]) * ratio
        g = c_start[1] + (c_end[1] - c_start[1]) * ratio
        b = c_start[2] + (c_end[2] - c_start[2]) * ratio
        res.append(f"{rgb_fg(r, g, b)}{ch}")
    return "".join(res) + Style.RESET_ALL

def gradient_banner(banner_lines, c_start=COLOR_PASTEL, c_end=COLOR_LIME):
    total = len(banner_lines)
    colored_lines = []
    for i, line in enumerate(banner_lines):
        ratio = i / max(total - 1, 1)
        r = c_start[0] + (c_end[0] - c_start[0]) * ratio
        g = c_start[1] + (c_end[1] - c_start[1]) * ratio
        b = c_start[2] + (c_end[2] - c_start[2]) * ratio
        colored_lines.append(f"{rgb_fg(r, g, b)}{line}{Style.RESET_ALL}")
    return "\n".join(colored_lines)

def c_lime(text):
    return f"{rgb_fg(*COLOR_LIME)}{text}{Style.RESET_ALL}"

def c_pastel(text):
    return f"{rgb_fg(*COLOR_PASTEL)}{text}{Style.RESET_ALL}"

def c_mint(text):
    return f"{rgb_fg(*COLOR_MINT)}{text}{Style.RESET_ALL}"

def c_dim(text):
    return f"{rgb_fg(*COLOR_DIM)}{text}{Style.RESET_ALL}"

BANNER_TEXT = r"""  ___  _    ___     _   _  _ _____ ___ ___  ___ _____ ___ ___ ___ 
   ▄████████ ▀█████████▄   ▄█          ▄████████ ███▄▄▄▄       ███      ▄█  
  ███    ███   ███    ███ ███         ███    ███ ███▀▀▀██▄ ▀█████████▄ ███  
  ███    █▀    ███    ███ ███▌        ███    ███ ███   ███    ▀███▀▀██ ███▌ 
 ▄███▄▄▄      ▄███▄▄▄██▀  ███▌        ███    ███ ███   ███     ███   ▀ ███▌ 
▀▀███▀▀▀     ▀▀███▀▀▀██▄  ███▌      ▀███████████ ███   ███     ███     ███▌ 
  ███          ███    ██▄ ███         ███    ███ ███   ███     ███     ███  
  ███          ███    ███ ███         ███    ███ ███   ███     ███     ███  
  ███        ▄█████████▀  █▀          ███    █▀   ▀█   █▀     ▄████▀   █▀   
                                                                            """

RAW_BANNER = BANNER_TEXT.splitlines()

SIGNATURE = "by lolz.team/vagina\n"

CPU_POOL = [
    {"name": "Intel Core i3-10100", "threads": 8, "ram": 8},
    {"name": "Intel Core i3-12100", "threads": 8, "ram": 16},
    {"name": "Intel Core i5-10400F", "threads": 12, "ram": 16},
    {"name": "Intel Core i5-11400", "threads": 12, "ram": 16},
    {"name": "Intel Core i5-1135G7", "threads": 8, "ram": 8},
    {"name": "Intel Core i7-1165G7", "threads": 8, "ram": 16},
    {"name": "Intel Core i5-8250U", "threads": 8, "ram": 8},
    {"name": "Intel Core i7-8550U", "threads": 8, "ram": 8},
    {"name": "Intel Core i3-1115G4", "threads": 4, "ram": 8},
    {"name": "AMD Ryzen 3 3200G", "threads": 4, "ram": 8},
    {"name": "AMD Ryzen 3 4300G", "threads": 8, "ram": 8},
    {"name": "AMD Ryzen 5 3500X", "threads": 6, "ram": 16},
    {"name": "AMD Ryzen 5 2600", "threads": 12, "ram": 16},
    {"name": "AMD Ryzen 5 1600", "threads": 12, "ram": 16},
    {"name": "AMD Ryzen 5 3600", "threads": 12, "ram": 16},
    {"name": "AMD Ryzen 5 5600X", "threads": 12, "ram": 16},
    {"name": "AMD Ryzen 5 5600G", "threads": 12, "ram": 16},
    {"name": "AMD Ryzen 7 3700X", "threads": 16, "ram": 16},
    {"name": "AMD Ryzen 7 5700X", "threads": 16, "ram": 32},
    {"name": "AMD Ryzen 7 5800X", "threads": 16, "ram": 32},
    {"name": "Intel Core i5-12400F", "threads": 12, "ram": 16},
    {"name": "Intel Core i5-12600K", "threads": 16, "ram": 32},
    {"name": "Intel Core i5-13400F", "threads": 16, "ram": 16},
    {"name": "Intel Core i5-13600K", "threads": 20, "ram": 32},
    {"name": "Intel Core i5-14400F", "threads": 16, "ram": 32},
    {"name": "Intel Core i5-14600K", "threads": 20, "ram": 32},
    {"name": "Intel Core i7-10700K", "threads": 16, "ram": 16},
    {"name": "Intel Core i7-11700K", "threads": 16, "ram": 32},
    {"name": "AMD Ryzen 7 7700X", "threads": 16, "ram": 32},
    {"name": "AMD Ryzen 7 7800X3D", "threads": 16, "ram": 32},
    {"name": "AMD Ryzen 9 5900X", "threads": 24, "ram": 32},
    {"name": "AMD Ryzen 9 5950X", "threads": 32, "ram": 64},
    {"name": "AMD Ryzen 9 7900X", "threads": 24, "ram": 32},
    {"name": "AMD Ryzen 9 7950X", "threads": 32, "ram": 64},
    {"name": "Intel Core i7-12700K", "threads": 20, "ram": 32},
    {"name": "Intel Core i7-13700K", "threads": 24, "ram": 32},
    {"name": "Intel Core i7-14700K", "threads": 28, "ram": 32},
    {"name": "Intel Core i9-12900K", "threads": 24, "ram": 32},
    {"name": "Intel Core i9-13900K", "threads": 32, "ram": 64},
    {"name": "Intel Core i9-14900K", "threads": 32, "ram": 64}
]

GPU_POOL = [
    {"name": "Intel HD Graphics 630", "vendor": "Google Inc. (Intel)", "renderer": "ANGLE (Intel, Intel(R) HD Graphics 630 Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"name": "Intel UHD Graphics 620", "vendor": "Google Inc. (Intel)", "renderer": "ANGLE (Intel, Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"name": "Intel UHD Graphics 730", "vendor": "Google Inc. (Intel)", "renderer": "ANGLE (Intel, Intel(R) UHD Graphics 730 Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"name": "Intel UHD Graphics 770", "vendor": "Google Inc. (Intel)", "renderer": "ANGLE (Intel, Intel(R) UHD Graphics 770 Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"name": "Intel Iris Xe Graphics", "vendor": "Google Inc. (Intel)", "renderer": "ANGLE (Intel, Intel(R) Iris(R) Xe Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"name": "AMD Radeon Vega 8", "vendor": "Google Inc. (AMD)", "renderer": "ANGLE (AMD, AMD Radeon(TM) Vega 8 Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"name": "AMD Radeon RX Vega 11", "vendor": "Google Inc. (AMD)", "renderer": "ANGLE (AMD, AMD Radeon(TM) RX Vega 11 Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"name": "AMD Radeon 680M", "vendor": "Google Inc. (AMD)", "renderer": "ANGLE (AMD, AMD Radeon 680M Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"name": "AMD Radeon 780M", "vendor": "Google Inc. (AMD)", "renderer": "ANGLE (AMD, AMD Radeon 780M Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"name": "NVIDIA GeForce GTX 1050 Ti", "vendor": "Google Inc. (NVIDIA)", "renderer": "ANGLE (NVIDIA, NVIDIA GeForce GTX 1050 Ti Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"name": "NVIDIA GeForce GTX 1060 6GB", "vendor": "Google Inc. (NVIDIA)", "renderer": "ANGLE (NVIDIA, NVIDIA GeForce GTX 1060 6GB Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"name": "NVIDIA GeForce GTX 1650", "vendor": "Google Inc. (NVIDIA)", "renderer": "ANGLE (NVIDIA, NVIDIA GeForce GTX 1650 Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"name": "NVIDIA GeForce GTX 1660 Super", "vendor": "Google Inc. (NVIDIA)", "renderer": "ANGLE (NVIDIA, NVIDIA GeForce GTX 1660 SUPER Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"name": "NVIDIA GeForce GTX 1660 Ti", "vendor": "Google Inc. (NVIDIA)", "renderer": "ANGLE (NVIDIA, NVIDIA GeForce GTX 1660 Ti Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"name": "AMD Radeon RX 570", "vendor": "Google Inc. (AMD)", "renderer": "ANGLE (AMD, Radeon RX 570 Series Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"name": "AMD Radeon RX 580", "vendor": "Google Inc. (AMD)", "renderer": "ANGLE (AMD, Radeon RX 580 Series Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"name": "AMD Radeon RX 6500 XT", "vendor": "Google Inc. (AMD)", "renderer": "ANGLE (AMD, AMD Radeon RX 6500 XT Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"name": "NVIDIA GeForce RTX 2060", "vendor": "Google Inc. (NVIDIA)", "renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 2060 Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"name": "NVIDIA GeForce RTX 2060 Super", "vendor": "Google Inc. (NVIDIA)", "renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 2060 SUPER Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"name": "NVIDIA GeForce RTX 2070", "vendor": "Google Inc. (NVIDIA)", "renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 2070 Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"name": "NVIDIA GeForce RTX 2070 Super", "vendor": "Google Inc. (NVIDIA)", "renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 2070 SUPER Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"name": "NVIDIA GeForce RTX 2080 Super", "vendor": "Google Inc. (NVIDIA)", "renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 2080 SUPER Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"name": "NVIDIA GeForce RTX 3050", "vendor": "Google Inc. (NVIDIA)", "renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 3050 Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"name": "NVIDIA GeForce RTX 3060", "vendor": "Google Inc. (NVIDIA)", "renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"name": "NVIDIA GeForce RTX 3060 Ti", "vendor": "Google Inc. (NVIDIA)", "renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 Ti Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"name": "NVIDIA GeForce RTX 3070", "vendor": "Google Inc. (NVIDIA)", "renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 3070 Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"name": "NVIDIA GeForce RTX 3070 Ti", "vendor": "Google Inc. (NVIDIA)", "renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 3070 Ti Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"name": "NVIDIA GeForce RTX 4060", "vendor": "Google Inc. (NVIDIA)", "renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 4060 Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"name": "NVIDIA GeForce RTX 4060 Ti", "vendor": "Google Inc. (NVIDIA)", "renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 4060 Ti Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"name": "AMD Radeon RX 6600", "vendor": "Google Inc. (AMD)", "renderer": "ANGLE (AMD, AMD Radeon RX 6600 Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"name": "AMD Radeon RX 6600 XT", "vendor": "Google Inc. (AMD)", "renderer": "ANGLE (AMD, AMD Radeon RX 6600 XT Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"name": "AMD Radeon RX 6700 XT", "vendor": "Google Inc. (AMD)", "renderer": "ANGLE (AMD, AMD Radeon RX 6700 XT Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"name": "AMD Radeon RX 7600", "vendor": "Google Inc. (AMD)", "renderer": "ANGLE (AMD, AMD Radeon RX 7600 Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"name": "NVIDIA GeForce RTX 3080", "vendor": "Google Inc. (NVIDIA)", "renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 3080 Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"name": "NVIDIA GeForce RTX 3080 Ti", "vendor": "Google Inc. (NVIDIA)", "renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 3080 Ti Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"name": "NVIDIA GeForce RTX 3090", "vendor": "Google Inc. (NVIDIA)", "renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 3090 Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"name": "NVIDIA GeForce RTX 4070", "vendor": "Google Inc. (NVIDIA)", "renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 4070 Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"name": "NVIDIA GeForce RTX 4070 Ti", "vendor": "Google Inc. (NVIDIA)", "renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 4070 Ti Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"name": "NVIDIA GeForce RTX 4080", "vendor": "Google Inc. (NVIDIA)", "renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 4080 Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"name": "NVIDIA GeForce RTX 4090", "vendor": "Google Inc. (NVIDIA)", "renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 4090 Direct3D11 vs_5_0 ps_5_0, D3D11)"}
]

FONT_CATALOG = [
    "Arial", "Calibri", "Cambria", "Comic Sans MS", "Consolas", "Courier New",
    "Georgia", "Impact", "Lucida Console", "Lucida Sans Unicode", "Segoe UI",
    "Tahoma", "Times New Roman", "Trebuchet MS", "Verdana", "Franklin Gothic Medium",
    "Palatino Linotype", "Candara", "Constantia", "Corbel", "Century Gothic",
    "Gill Sans MT", "Garamond", "MS Gothic", "MS PGothic", "SimSun", "Malgun Gothic",
    "Yu Gothic", "Sitka Text", "Ebrima", "Gadugi", "Leelawadee UI", "Nirmala UI"
]

def get_short_path(path):
    if os.name != 'nt':
        return path
    os.makedirs(path, exist_ok=True)
    buf = ctypes.create_unicode_buffer(1024)
    res = ctypes.windll.kernel32.GetShortPathNameW(path, buf, 1024)
    if res > 0 and buf.value:
        return buf.value
    return path

def osvobodit_profil(papka_sessii, profile_name):
    for zameck in ["SingletonLock", "SingletonSocket", "SingletonCookie", "LOCK"]:
        p = os.path.join(papka_sessii, zameck)
        if os.path.exists(p) or os.path.islink(p):
            try:
                os.remove(p)
            except Exception:
                pass

    if os.name == 'nt':
        try:
            ps_script = (
                f"Get-CimInstance Win32_Process -Filter \"name = 'chrome.exe'\" | "
                f"Where-Object {{ $_.CommandLine -like '*{profile_name}*' }} | "
                f"ForEach-Object {{ Stop-Process -Id $_.ProcessId -Force }}"
            )
            subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=4
            )
        except Exception:
            pass

class LocalProxyBridge:
    def __init__(self, upstream_info):
        self.upstream = upstream_info
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(("127.0.0.1", 0))
        self.port = self.server.getsockname()[1]
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self):
        self.server.listen(100)
        while self.running:
            try:
                client, _ = self.server.accept()
                threading.Thread(target=self._handle_client, args=(client,), daemon=True).start()
            except Exception:
                break

    def _recv_exact(self, sock, num_bytes):
        buf = b""
        while len(buf) < num_bytes:
            chunk = sock.recv(num_bytes - len(buf))
            if not chunk:
                break
            buf += chunk
        return buf

    def _handle_client(self, client):
        client.settimeout(30)
        upstream_sock = None
        try:
            req_data = client.recv(8192)
            if not req_data:
                client.close()
                return

            req_line = req_data.split(b"\r\n")[0].decode('utf-8', errors='ignore')
            parts = req_line.split(" ")
            if len(parts) < 2:
                client.close()
                return

            method, target = parts[0], parts[1]
            u_scheme = self.upstream.get("scheme", "http").lower()
            u_host = self.upstream["host"]
            u_port = self.upstream["port"]
            u_user = self.upstream.get("user")
            u_pass = self.upstream.get("pass")

            raw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            raw_sock.settimeout(20)
            raw_sock.connect((u_host, u_port))

            if u_scheme == "https":
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                upstream_sock = ctx.wrap_socket(raw_sock, server_hostname=u_host)
            else:
                upstream_sock = raw_sock

            if u_scheme in ["http", "https"]:
                if method.upper() == "CONNECT":
                    conn_hdr = f"CONNECT {target} HTTP/1.1\r\nHost: {target}\r\nProxy-Connection: Keep-Alive\r\n"
                    if u_user and u_pass:
                        auth_str = base64.b64encode(f"{u_user}:{u_pass}".encode()).decode()
                        conn_hdr += f"Proxy-Authorization: Basic {auth_str}\r\n"
                    conn_hdr += "\r\n"
                    upstream_sock.sendall(conn_hdr.encode())

                    resp = b""
                    while b"\r\n\r\n" not in resp:
                        chunk = upstream_sock.recv(1024)
                        if not chunk:
                            break
                        resp += chunk

                    if b"200" in resp.split(b"\r\n")[0]:
                        client.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
                        pos = resp.find(b"\r\n\r\n")
                        extra = resp[pos+4:]
                        if extra:
                            client.sendall(extra)
                    else:
                        client.sendall(resp)
                        client.close()
                        upstream_sock.close()
                        return
                else:
                    if u_user and u_pass:
                        auth_str = base64.b64encode(f"{u_user}:{u_pass}".encode()).decode()
                        header_to_inject = f"Proxy-Authorization: Basic {auth_str}\r\n".encode()
                        pos = req_data.find(b"\r\n") + 2
                        req_data = req_data[:pos] + header_to_inject + req_data[pos:]
                    upstream_sock.sendall(req_data)

            elif u_scheme == "socks5":
                if u_user and u_pass:
                    upstream_sock.sendall(b"\x05\x02\x00\x02")
                    greet = self._recv_exact(upstream_sock, 2)
                    if len(greet) == 2 and greet[1] == 2:
                        u_b, p_b = u_user.encode(), u_pass.encode()
                        upstream_sock.sendall(b"\x01" + bytes([len(u_b)]) + u_b + bytes([len(p_b)]) + p_b)
                        auth_res = self._recv_exact(upstream_sock, 2)
                        if len(auth_res) < 2 or auth_res[1] != 0:
                            client.close()
                            upstream_sock.close()
                            return
                else:
                    upstream_sock.sendall(b"\x05\x01\x00")
                    self._recv_exact(upstream_sock, 2)

                if ":" in target:
                    thost, tport = target.split(":")
                    tport = int(tport)
                else:
                    thost, tport = target, 80

                thost_b = thost.encode()
                upstream_sock.sendall(b"\x05\x01\x00\x03" + bytes([len(thost_b)]) + thost_b + tport.to_bytes(2, 'big'))
                
                resp_head = self._recv_exact(upstream_sock, 4)
                if len(resp_head) < 4 or resp_head[1] != 0:
                    client.close()
                    upstream_sock.close()
                    return

                atyp = resp_head[3]
                if atyp == 1:
                    self._recv_exact(upstream_sock, 6)
                elif atyp == 3:
                    nlen = self._recv_exact(upstream_sock, 1)[0]
                    self._recv_exact(upstream_sock, nlen + 2)
                elif atyp == 4:
                    self._recv_exact(upstream_sock, 18)

                if method.upper() == "CONNECT":
                    client.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
                else:
                    if target.startswith("http://") or target.startswith("https://"):
                        parsed_url = urlsplit(target)
                        rel_path = parsed_url.path or "/"
                        if parsed_url.query:
                            rel_path += "?" + parsed_url.query
                        req_data = req_data.replace(target.encode(), rel_path.encode(), 1)
                    upstream_sock.sendall(req_data)

            elif u_scheme == "socks4":
                if ":" in target:
                    thost, tport = target.split(":")
                    tport = int(tport)
                else:
                    thost, tport = target, 80
                try:
                    tip = socket.gethostbyname(thost)
                except Exception:
                    client.close()
                    upstream_sock.close()
                    return
                ip_b = socket.inet_aton(tip)
                port_b = tport.to_bytes(2, 'big')
                user_b = (u_user or "").encode() + b"\x00"
                upstream_sock.sendall(b"\x04\x01" + port_b + ip_b + user_b)
                s4_resp = self._recv_exact(upstream_sock, 8)
                if len(s4_resp) < 2 or s4_resp[1] != 90:
                    client.close()
                    upstream_sock.close()
                    return
                if method.upper() == "CONNECT":
                    client.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
                else:
                    if target.startswith("http://") or target.startswith("https://"):
                        parsed_url = urlsplit(target)
                        rel_path = parsed_url.path or "/"
                        if parsed_url.query:
                            rel_path += "?" + parsed_url.query
                        req_data = req_data.replace(target.encode(), rel_path.encode(), 1)
                    upstream_sock.sendall(req_data)

            def forward(source, destination):
                try:
                    while True:
                        chunk = source.recv(32768)
                        if not chunk:
                            break
                        destination.sendall(chunk)
                except Exception:
                    pass
                finally:
                    try:
                        source.close()
                    except Exception:
                        pass
                    try:
                        destination.close()
                    except Exception:
                        pass

            t1 = threading.Thread(target=forward, args=(client, upstream_sock), daemon=True)
            t2 = threading.Thread(target=forward, args=(upstream_sock, client), daemon=True)
            t1.start()
            t2.start()

        except Exception:
            try:
                client.close()
            except Exception:
                pass
            if upstream_sock:
                try:
                    upstream_sock.close()
                except Exception:
                    pass

    def stop(self):
        self.running = False
        try:
            self.server.close()
        except Exception:
            pass

def sozdat_bazu_esli_net():
    if not os.path.exists(BAZA_PROFILEY):
        with open(BAZA_PROFILEY, "w", encoding="utf-8") as f:
            json.dump({}, f)

def chitat_bazu():
    sozdat_bazu_esli_net()
    with open(BAZA_PROFILEY, "r", encoding="utf-8") as f:
        return json.load(f)

def sohranit_bazu(baza_kormit):
    with open(BAZA_PROFILEY, "w", encoding="utf-8") as f:
        json.dump(baza_kormit, f, indent=4, ensure_ascii=False)

def razobrat_proksi(raw_proxy, default_scheme="http"):
    if not raw_proxy or not isinstance(raw_proxy, str):
        return None
    clean = raw_proxy.strip()
    scheme = default_scheme
    if "://" in clean:
        scheme, clean = clean.split("://", 1)
        scheme = scheme.lower()

    user = None
    password = None
    host = None
    port = None

    if "@" in clean:
        chasti = clean.split("@", 1)
        first_segment = chasti[0].split(":")[0]
        if any(c.isalpha() for c in first_segment) and "." not in first_segment:
            user_pass, host_port = chasti[0], chasti[1]
        else:
            host_port, user_pass = chasti[0], chasti[1]
        
        if ":" in user_pass:
            user, password = user_pass.split(":", 1)
        if ":" in host_port:
            host, port = host_port.split(":", 1)
    elif clean.count(":") == 3:
        chasti = clean.split(":")
        if "." in chasti[0] and chasti[1].isdigit():
            host, port, user, password = chasti[0], chasti[1], chasti[2], chasti[3]
        else:
            user, password, host, port = chasti[0], chasti[1], chasti[2], chasti[3]
    elif clean.count(":") == 1:
        host, port = clean.split(":")
    else:
        return None

    if not host or not port or not str(port).isdigit():
        return None

    return {
        "scheme": scheme.lower(),
        "host": host,
        "port": int(port),
        "user": user,
        "pass": password
    }

def poluchit_info_proksi(p_info, timeout=7):
    if not p_info or not isinstance(p_info, dict):
        return False, "Неправильный конфиг прокси"
    
    scheme = p_info.get("scheme", "http").lower()
    host = p_info.get("host")
    port = p_info.get("port")
    user = p_info.get("user")
    passwd = p_info.get("pass")

    try:
        raw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw_sock.settimeout(timeout)
        raw_sock.connect((host, port))

        if scheme == "https":
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            s = ctx.wrap_socket(raw_sock, server_hostname=host)
        else:
            s = raw_sock

        raw_resp = b""

        if scheme in ["http", "https"]:
            target_url = "http://ip-api.com/json/?fields=status,message,country,city,timezone,isp,org,as,mobile,proxy,hosting,query"
            req = f"GET {target_url} HTTP/1.1\r\nHost: ip-api.com\r\nUser-Agent: Mozilla/5.0\r\n"
            if user and passwd:
                auth = base64.b64encode(f"{user}:{passwd}".encode()).decode()
                req += f"Proxy-Authorization: Basic {auth}\r\n"
            req += "Connection: close\r\n\r\n"
            s.sendall(req.encode())

            while True:
                try:
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    raw_resp += chunk
                except socket.timeout:
                    break
            s.close()

        elif scheme == "socks5":
            if user and passwd:
                s.sendall(b"\x05\x02\x00\x02")
                res = s.recv(2)
                if len(res) == 2 and res[1] == 2:
                    u_b, p_b = user.encode(), passwd.encode()
                    s.sendall(b"\x01" + bytes([len(u_b)]) + u_b + bytes([len(p_b)]) + p_b)
                    auth_res = s.recv(2)
                    if len(auth_res) < 2 or auth_res[1] != 0:
                        s.close()
                        return False, "Неправильный логин или пароль SOCKS5"
            else:
                s.sendall(b"\x05\x01\x00")
                s.recv(2)

            target_domain = b"ip-api.com"
            s.sendall(b"\x05\x01\x00\x03" + bytes([len(target_domain)]) + target_domain + (80).to_bytes(2, 'big'))
            res2 = s.recv(1024)
            if len(res2) < 2 or res2[1] != 0:
                s.close()
                return False, "SOCKS5 не смог подключиться к серверу"

            s.sendall(b"GET /json/?fields=status,message,country,city,timezone,isp,org,as,mobile,proxy,hosting,query HTTP/1.1\r\nHost: ip-api.com\r\nUser-Agent: Mozilla/5.0\r\nConnection: close\r\n\r\n")
            while True:
                try:
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    raw_resp += chunk
                except socket.timeout:
                    break
            s.close()

        elif scheme == "socks4":
            try:
                ip_resolved = socket.gethostbyname("ip-api.com")
            except Exception:
                ip_resolved = "208.95.112.1"
            ip_b = socket.inet_aton(ip_resolved)
            port_b = (80).to_bytes(2, byteorder='big')
            user_b = (user or "").encode() + b"\x00"
            s.sendall(b"\x04\x01" + port_b + ip_b + user_b)
            res = s.recv(8)
            if len(res) < 2 or res[1] != 90:
                s.close()
                return False, "SOCKS4 отклонил запрос"

            s.sendall(b"GET /json/?fields=status,message,country,city,timezone,isp,org,as,mobile,proxy,hosting,query HTTP/1.1\r\nHost: ip-api.com\r\nUser-Agent: Mozilla/5.0\r\nConnection: close\r\n\r\n")
            while True:
                try:
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    raw_resp += chunk
                except socket.timeout:
                    break
            s.close()

        resp_text = raw_resp.decode('utf-8', errors='ignore')
        if not resp_text:
            return False, "Нету ответа"
        if "407 Proxy Authentication Required" in resp_text:
            return False, "Неправильный логин или пароль (407 Proxy Auth Required)"

        start = resp_text.find('{')
        end = resp_text.rfind('}')
        if start != -1 and end != -1:
            data = json.loads(resp_text[start:end+1])
            if data.get("status") == "fail":
                return False, f"Ошибка сервиса IP: {data.get('message', 'Неизвестно')}"
            
            mobile = data.get("mobile", False)
            hosting = data.get("hosting", False)
            if mobile:
                p_type = "Мобильный"
            elif hosting:
                p_type = "Датацентр"
            else:
                p_type = "Резидентский"
            
            data["proxy_type"] = p_type
            return True, data
        else:
            return False, f"Не получилось извлечь данные: {resp_text[:80].strip()}"

    except socket.timeout:
        return False, "Ответ от прокси не был получен, вероятнее всего мёртв"
    except ConnectionRefusedError:
        return False, "Соединение отказано хостом"
    except Exception as e:
        return False, f"Ошибка сети: {e}"

def zamazat_sleydi(cpu, ram, gpu_vendor, gpu_renderer, allowed_fonts):
    fonts_json = json.dumps(allowed_fonts)
    barhatnie_tyagi = f"""
    (() => {{
        const origToString = Function.prototype.toString;
        const patchedFns = new WeakSet();

        const myToString = function toString() {{
            if (patchedFns.has(this)) {{
                const fnName = this.name || '';
                return 'function ' + fnName + '() {{ [native code] }}';
            }}
            return origToString.apply(this, arguments);
        }};
        patchedFns.add(myToString);
        Function.prototype.toString = myToString;

        const iframeProto = HTMLIFrameElement.prototype;
        const origContentWinGet = Object.getOwnPropertyDescriptor(iframeProto, 'contentWindow').get;
        Object.defineProperty(iframeProto, 'contentWindow', {{
            get: function() {{
                const win = origContentWinGet.apply(this, arguments);
                if (win && win.Function && win.Function.prototype) {{
                    if (win.Function.prototype.toString !== myToString) {{
                        try {{ win.Function.prototype.toString = myToString; }} catch(e) {{}}
                    }}
                }}
                return win;
            }},
            configurable: true,
            enumerable: true
        }});

        function defineNativeGetter(proto, prop, getterFn) {{
            patchedFns.add(getterFn);
            Object.defineProperty(proto, prop, {{
                get: getterFn,
                set: undefined,
                enumerable: true,
                configurable: true
            }});
        }}

        const cpuHolder = {{ get [ 'hardwareConcurrency' ]() {{ return {cpu}; }} }};
        defineNativeGetter(Navigator.prototype, 'hardwareConcurrency', Object.getOwnPropertyDescriptor(cpuHolder, 'hardwareConcurrency').get);

        const ramHolder = {{ get [ 'deviceMemory' ]() {{ return {ram}; }} }};
        defineNativeGetter(Navigator.prototype, 'deviceMemory', Object.getOwnPropertyDescriptor(ramHolder, 'deviceMemory').get);

        const platHolder = {{ get [ 'platform' ]() {{ return 'Win32'; }} }};
        defineNativeGetter(Navigator.prototype, 'platform', Object.getOwnPropertyDescriptor(platHolder, 'platform').get);

        const langHolder = {{ get [ 'languages' ]() {{ return ['ru-RU', 'ru', 'en-US', 'en']; }} }};
        defineNativeGetter(Navigator.prototype, 'languages', Object.getOwnPropertyDescriptor(langHolder, 'languages').get);

        if (navigator.userAgentData && navigator.userAgentData.getHighEntropyValues) {{
            const origHints = navigator.userAgentData.getHighEntropyValues.bind(navigator.userAgentData);
            const hintsHook = function getHighEntropyValues(hints) {{
                return origHints(hints).then(res => {{
                    const out = Object.assign({{}}, res);
                    if (hints.includes('architecture')) out.architecture = 'x86';
                    if (hints.includes('bitness')) out.bitness = '64';
                    return out;
                }});
            }};
            patchedFns.add(hintsHook);
            navigator.userAgentData.getHighEntropyValues = hintsHook;
        }}

        const baseContext = window.WebGLRenderingContextBase || window.WebGLRenderingContext;
        if (baseContext && baseContext.prototype) {{
            const origGetParam = baseContext.prototype.getParameter;
            const paramProxy = function getParameter(param) {{
                if (param === 37445) return '{gpu_vendor}';
                if (param === 37446) return '{gpu_renderer}';
                return origGetParam.apply(this, arguments);
            }};
            patchedFns.add(paramProxy);
            baseContext.prototype.getParameter = paramProxy;
        }}

        const allowedFontSet = new Set({fonts_json}.map(f => f.toLowerCase()));
        const genericFonts = ['monospace', 'sans-serif', 'serif', 'cursive', 'fantasy', 'system-ui'];

        const fontDesc = Object.getOwnPropertyDescriptor(CanvasRenderingContext2D.prototype, 'font');
        if (fontDesc && fontDesc.set) {{
            const origFontSet = fontDesc.set;
            const fontObj = {{
                set [ 'font' ](val) {{
                    let cleanVal = val;
                    const match = String(val).match(/(?:[\\d\\.]+(?:px|pt|em|rem|%)\\s+)(.+)$/i);
                    if (match) {{
                        const families = match[1].split(',').map(s => s.trim().replace(/['"]/g, ''));
                        const primary = families[0].toLowerCase();
                        if (!genericFonts.includes(primary) && !allowedFontSet.has(primary)) {{
                            const fallback = families.find(f => genericFonts.includes(f.toLowerCase())) || 'monospace';
                            cleanVal = val.replace(match[1], fallback);
                        }}
                    }}
                    return origFontSet.call(this, cleanVal);
                }}
            }};
            const fontSetter = Object.getOwnPropertyDescriptor(fontObj, 'font').set;
            patchedFns.add(fontSetter);
            Object.defineProperty(CanvasRenderingContext2D.prototype, 'font', {{
                set: fontSetter,
                get: fontDesc.get,
                configurable: true,
                enumerable: true
            }});
        }}

        const famDesc = Object.getOwnPropertyDescriptor(CSSStyleDeclaration.prototype, 'fontFamily');
        if (famDesc && famDesc.set) {{
            const origFamSet = famDesc.set;
            const famObj = {{
                set [ 'fontFamily' ](val) {{
                    let cleanVal = val;
                    const parts = String(val).split(',').map(s => s.trim().replace(/['"]/g, ''));
                    const primary = parts[0].toLowerCase();
                    if (!genericFonts.includes(primary) && !allowedFontSet.has(primary)) {{
                        cleanVal = parts.find(f => genericFonts.includes(f.toLowerCase())) || 'monospace';
                    }}
                    return origFamSet.call(this, cleanVal);
                }}
            }};
            const famSetter = Object.getOwnPropertyDescriptor(famObj, 'fontFamily').set;
            patchedFns.add(famSetter);
            Object.defineProperty(CSSStyleDeclaration.prototype, 'fontFamily', {{
                set: famSetter,
                get: famDesc.get,
                configurable: true,
                enumerable: true
            }});
        }}

        if (document.fonts && document.fonts.check) {{
            const origCheck = document.fonts.check.bind(document.fonts);
            const checkHook = function check(font, text) {{
                const cleanFont = font.replace(/['"]/g, '').toLowerCase();
                for (let f of allowedFontSet) {{
                    if (cleanFont.includes(f)) return true;
                }}
                return false;
            }};
            patchedFns.add(checkHook);
            document.fonts.check = checkHook;
        }}

        for (const key in window) {{
            if (key.match(/^cdc_[a-zA-Z0-9]+_/)) {{
                delete window[key];
            }}
        }}
    }})();
    """
    return barhatnie_tyagi

def sobrat_kolesnicu(skuf, config, p_info):
    raw_papka = os.path.abspath(os.path.join("sessions", skuf))
    safe_papka = get_short_path(raw_papka)
    osvobodit_profil(raw_papka, skuf)
    
    sueta = webdriver.ChromeOptions()
    sueta.add_argument(f"--user-data-dir={safe_papka}")
    sueta.page_load_strategy = 'eager'
    
    sueta.add_argument("--no-sandbox")
    sueta.add_argument("--disable-dev-shm-usage")
    sueta.add_argument("--remote-allow-origins=*")
    sueta.add_argument("--disable-blink-features=AutomationControlled")
    sueta.add_argument("--disable-infobars")
    sueta.add_argument("--disable-features=AutofillServerCommunication,OptimizationHints,Translate,SafeBrowsingExtendedReporting")
    sueta.add_argument("--disable-background-timer-throttling")
    sueta.add_argument("--disable-backgrounding-occluded-windows")
    sueta.add_argument("--disable-breakpad")
    sueta.add_argument("--disable-component-update")
    sueta.add_argument("--disable-default-apps")
    sueta.add_argument("--disable-domain-reliability")
    sueta.add_argument("--disable-hang-monitor")
    sueta.add_argument("--disable-ipc-flooding-protection")
    sueta.add_argument("--disable-renderer-backgrounding")
    sueta.add_argument("--disable-sync")
    sueta.add_argument("--no-first-run")
    sueta.add_argument("--no-default-browser-check")
    sueta.add_argument("--disable-quic")
    sueta.add_argument("about:blank")
    sueta.add_argument(f"--window-size={config['width']},{config['height']}")
    
    zaschita = {
        "safebrowsing.enabled": False,
        "safebrowsing.enhanced": False
    }

    bridge = None
    if p_info and isinstance(p_info, dict):
        bridge = LocalProxyBridge(p_info)
        sueta.add_argument(f"--proxy-server=http://127.0.0.1:{bridge.port}")
        sueta.add_argument("--force-webrtc-ip-handling-policy=disable_non_proxied_udp")
        zaschita["webrtc.ip_handling_policy"] = "disable_non_proxied_udp"
        zaschita["webrtc.multiple_routes_enabled"] = False
        zaschita["webrtc.nonproxied_udp_enabled"] = False
    else:
        sueta.add_argument("--no-proxy-server")

    sueta.add_experimental_option("prefs", zaschita)
    sueta.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])

    try:
        chushpan = webdriver.Chrome(options=sueta)
    except Exception as e:
        if "session not created" in str(e).lower():
            print(f"{c_lime('[*]')} Обнаружен конфликт. Очищение сессии...")
            osvobodit_profil(raw_papka, skuf)
            time.sleep(1.5)
            chushpan = webdriver.Chrome(options=sueta)
        else:
            raise e
    
    chushpan.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {
        'width': config['width'],
        'height': config['height'],
        'deviceScaleFactor': 1,
        'mobile': False
    })
    
    timezone_id = config.get("timezone", "Europe/Kyiv")
    if timezone_id == "Europe/Kiev":
        timezone_id = "Europe/Kyiv"
    try:
        chushpan.execute_cdp_cmd('Emulation.setTimezoneOverride', {'timezoneId': timezone_id})
    except Exception:
        pass
    
    chushpan.execute_cdp_cmd(
        'Page.addScriptToEvaluateOnNewDocument', 
        {'source': zamazat_sleydi(
            config['cpu'], 
            config['ram'], 
            config['gpu_vendor'], 
            config['gpu_renderer'],
            config.get('fonts', FONT_CATALOG[:15])
        )}
    )
    
    return chushpan, bridge

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def render_divider(length=58):
    return gradient_text("—" * length, COLOR_PASTEL, COLOR_LIME)

def paginated_selector(pool, item_type="железо", page_size=10):
    total_pages = (len(pool) + page_size - 1) // page_size
    current_page = 0
    while True:
        clear_console()
        print(gradient_text(f"=== ВЫБОР: {item_type.upper()} (Страница {current_page + 1}/{total_pages}) ==="))
        start_idx = current_page * page_size
        end_idx = min(start_idx + page_size, len(pool))
        
        for i in range(start_idx, end_idx):
            item = pool[i]
            details = f"({item['threads']} потоков)" if 'threads' in item else f"({item['vendor']})"
            print(f" {c_lime(f'[{i + 1}]')} {c_pastel(item['name'])} {c_dim(details)}")
            
        print(render_divider())
        print(f" {c_mint('[N]')} След. стр. | {c_mint('[P]')} Пред. стр. | {c_mint('[R]')} Рандом")
        choice = input(f"\n {c_lime('>>')} Введите номер или команду: ").strip().lower()
        
        if choice == 'n':
            if current_page < total_pages - 1:
                current_page += 1
        elif choice == 'p':
            if current_page > 0:
                current_page -= 1
        elif choice == 'r':
            return random.choice(pool)
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(pool):
                return pool[idx]

def nastroika_proksi_flow():
    print(gradient_text("=== НАСТРОЙКА ПРОКСИ ==="))
    print(f" {c_lime('[1]')} HTTP / HTTPS")
    print(f" {c_lime('[2]')} SOCKS5")
    print(f" {c_lime('[3]')} SOCKS4")
    print(f" {c_lime('[4]')} HTTPS {c_dim('(Альтернативный вариант)')}")
    print(f" {c_lime('[5]')} Без прокси")
    proto_choice = input(f"\n {c_lime('>>')} Выберите тип соединения [1-5]: ").strip()
    
    p_info = None
    detected_tz = "Europe/Kyiv"

    if proto_choice in ["1", "2", "3", "4"]:
        proto_map = {"1": "http", "2": "socks5", "3": "socks4", "4": "https"}
        sel_proto = proto_map[proto_choice]
        
        while True:
            print(f"\n {c_mint(f'--- Ввод прокси ({sel_proto.upper()}) ---')}")
            print(f" {c_dim('Форматы: IP:PORT или IP:PORT:USER:PASS или IP:PORT@USER:PASS')}")
            print(f" {c_dim('(Введите \"0\" для отмены)')}")
            raw_proxy = input(f" {c_lime('>>')} Прокси: ").strip()
            
            if raw_proxy == "0":
                print(f" {c_dim('[-]')} Настройка отменена.")
                p_info = None
                break

            parsed = razobrat_proksi(raw_proxy, sel_proto)
            if not parsed:
                print(f" {Fore.LIGHTYELLOW_EX}[-] Неверный формат прокси! Попробуйте снова.{Style.RESET_ALL}")
                continue

            print(f" {c_lime('[*]')} Проверяем прокси {parsed['host']}:{parsed['port']}...")
            is_ok, res = poluchit_info_proksi(parsed, timeout=6)
            
            if is_ok:
                p_info = parsed
                detected_tz = res.get("timezone") or "Europe/Kyiv"
                if detected_tz == "Europe/Kiev":
                    detected_tz = "Europe/Kyiv"

                geo_str = f"{res.get('country')}, {res.get('city')}"
                isp_str = f"{res.get('isp')} ({res.get('as')})"

                print("\n" + render_divider(52))
                print(gradient_text("  [+] УСПЕШНОЕ ПОДКЛЮЧЕНИЕ"))
                print(render_divider(52))
                print(f"  Внешний IP:    {c_lime(res.get('query'))}")
                print(f"  Геолокация:    {c_pastel(geo_str)}")
                print(f"  Провайдер:     {c_mint(isp_str)}")
                print(f"  Тип прокси:    {c_pastel(res.get('proxy_type'))}")
                print(f"  Часовой пояс:  {c_lime(detected_tz)}")
                print(render_divider(52))
                print(f" {c_lime('[+]')} Часовой пояс подобран автоматически!")
                break
            else:
                print(f"\n {Fore.LIGHTRED_EX}[!] ОШИБКА: Прокси не работает или заблокирован!{Style.RESET_ALL}")
                print(f" {c_dim('Причина:')} {res}")
                print(f"\n {c_mint('Выберите дальнейшее действие:')}")
                print(f" {c_lime('[1]')} Ввести другой прокси")
                print(f" {c_lime('[2]')} Повторить проверку")
                print(f" {c_lime('[3]')} Отмена")
                act = input(f"\n {c_lime('>>')} Ваш выбор [1/2/3]: ").strip()
                
                if act == "2":
                    print(f" {c_lime('[*]')} Повторная проверка...")
                    is_ok_retry, res_retry = poluchit_info_proksi(parsed, timeout=8)
                    if is_ok_retry:
                        p_info = parsed
                        detected_tz = res_retry.get("timezone") or "Europe/Kyiv"
                        if detected_tz == "Europe/Kiev":
                            detected_tz = "Europe/Kyiv"
                        print(f" {c_lime('[+]')} Прокси ответил! Гео: {res_retry.get('country')}, {res_retry.get('city')}")
                        break
                    else:
                        print(f" {Fore.LIGHTRED_EX}[!] Повторная проверка не удалась: {res_retry}{Style.RESET_ALL}")
                        continue
                elif act == "3":
                    p_info = None
                    break
                else:
                    continue

    return p_info, detected_tz

def redaktirovat_profil(baza_kormit, imya):
    while True:
        clear_console()
        prof = baza_kormit[imya]
        prx = prof.get("proxy")
        if isinstance(prx, dict):
            prx_str = f"{prx.get('scheme', 'http')}://{prx.get('host', '')}:{prx.get('port', '')}"
        elif isinstance(prx, str) and prx.strip():
            prx_str = prx
        else:
            prx_str = "Без прокси"

        hw_desc = f"({prof.get('cpu')} ядер) / {prof.get('ram')}GB RAM"
        res_desc = f"{prof.get('width')}x{prof.get('height')}"

        print(gradient_text(f"=== РЕДАКТИРОВАНИЕ ПРОФИЛЯ: [{imya}] ==="))
        print(f" Процессор:      {c_pastel(prof.get('cpu_name', 'CPU'))} {c_dim(hw_desc)}")
        print(f" Видеокарта:  {c_pastel(prof.get('gpu_name', 'GPU'))}")
        print(f" Экран:       {c_lime(res_desc)}")
        print(f" Таймзона:    {c_mint(prof.get('timezone', 'Europe/Kyiv'))}")
        print(f" Шрифтов:     {c_pastel(str(len(prof.get('fonts', []))))} {c_dim('шт.')}")
        print(f" Прокси:      {c_lime(prx_str)}")
        print(render_divider())
        print(f" {c_lime('[1]')} - Изменить название профиля")
        print(f" {c_lime('[2]')} - Изменить процессор и видеокарту")
        print(f" {c_lime('[3]')} - Изменить разрешение экрана")
        print(f" {c_lime('[4]')} - Изменить / перепроверить прокси")
        print(f" {c_lime('[5]')} - Изменить часовой пояс")
        print(f" {c_lime('[6]')} - Перегенерировать шрифты")
        print(f" {c_lime('[7]')} - {Fore.LIGHTRED_EX}Удалить профиль навсегда{Style.RESET_ALL}")
        print(f" {c_mint('[0]')} - Вернуться в главное меню")
        print(render_divider())
        
        vib = input(f"\n {c_lime('>>')} Ваш выбор: ").strip()
        
        if vib == "1":
            novoe_imya = input(f"\n {c_lime('>>')} Новое название профиля: ").strip()
            if not novoe_imya:
                continue
            if novoe_imya == imya:
                print(f" {c_dim('Имя совпадает с текущим.')}")
                time.sleep(1)
                continue
            if novoe_imya in baza_kormit:
                print(f" {Fore.LIGHTRED_EX}[-] Профиль с таким именем уже существует!{Style.RESET_ALL}")
                time.sleep(1)
                continue
            
            baza_kormit[novoe_imya] = baza_kormit.pop(imya)
            old_dir = os.path.join(os.getcwd(), "sessions", imya)
            new_dir = os.path.join(os.getcwd(), "sessions", novoe_imya)
            if os.path.exists(old_dir):
                try:
                    os.rename(old_dir, new_dir)
                except Exception as e:
                    print(f" {Fore.LIGHTYELLOW_EX}[!] Не удалось переименовать папку сессии: {e}{Style.RESET_ALL}")
            imya = novoe_imya
            sohranit_bazu(baza_kormit)
            print(f" {c_lime('[+]')} Название успешно изменено!")
            time.sleep(1)

        elif vib == "2":
            print(f"\n {c_mint('Выберите как подбирать комплектующие:')}")
            print(f" {c_lime('[1]')} Выбрать вручную")
            print(f" {c_lime('[2]')} Рандом")
            t_choice = input(f"\n {c_lime('>>')} Выбор [1/2]: ").strip()
            if t_choice == "2":
                c = random.choice(CPU_POOL)
                g = random.choice(GPU_POOL)
            else:
                c = paginated_selector(CPU_POOL, "процессор")
                g = paginated_selector(GPU_POOL, "видеокарта")
            
            prof["cpu_name"] = c["name"]
            prof["cpu"] = c["threads"]
            prof["ram"] = c["ram"]
            prof["gpu_name"] = g["name"]
            prof["gpu_vendor"] = g["vendor"]
            prof["gpu_renderer"] = g["renderer"]
            sohranit_bazu(baza_kormit)
            print(f" {c_lime('[+]')} Комплектухи обновлены: {c['name']} / {g['name']}")
            time.sleep(1.5)

        elif vib == "3":
            print(f"\n {c_mint('Выберите разрешение:')}")
            print(f" {c_lime('[1]')} 1920x1080 (FullHD)")
            print(f" {c_lime('[2]')} 1366x768 (Ноутбук)")
            print(f" {c_lime('[3]')} 1600x900 (HD+)")
            print(f" {c_lime('[4]')} 2560x1440 (2K QHD)")
            print(f" {c_lime('[5]')} Ввести вручную")
            r_c = input(f"\n {c_lime('>>')} Выбор [1-5]: ").strip()
            if r_c == "1":
                prof["width"], prof["height"] = 1920, 1080
            elif r_c == "2":
                prof["width"], prof["height"] = 1366, 768
            elif r_c == "3":
                prof["width"], prof["height"] = 1600, 900
            elif r_c == "4":
                prof["width"], prof["height"] = 2560, 1440
            elif r_c == "5":
                try:
                    w = int(input(f" {c_lime('>>')} Ширина: ").strip())
                    h = int(input(f" {c_lime('>>')} Высота: ").strip())
                    prof["width"], prof["height"] = w, h
                except ValueError:
                    print(f" {Fore.LIGHTRED_EX}[-] Неверное число.{Style.RESET_ALL}")
                    time.sleep(1)
                    continue
            sohranit_bazu(baza_kormit)
            print(f" {c_lime('[+]')} Разрешение экрана обновлено: {prof['width']}x{prof['height']}")
            time.sleep(1)

        elif vib == "4":
            clear_console()
            new_p_info, auto_tz = nastroika_proksi_flow()
            prof["proxy"] = new_p_info
            if new_p_info:
                prof["timezone"] = auto_tz
            sohranit_bazu(baza_kormit)
            print(f" {c_lime('[+]')} Прокси профиля обновлен!")
            time.sleep(1.5)

        elif vib == "5":
            new_tz = input(f"\n {c_lime('>>')} Введите часовой пояс [{prof.get('timezone', 'Europe/Kyiv')}]: ").strip()
            if new_tz:
                if new_tz == "Europe/Kiev":
                    new_tz = "Europe/Kyiv"
                prof["timezone"] = new_tz
                sohranit_bazu(baza_kormit)
                print(f" {c_lime('[+]')} Часовой пояс обновлен!")
                time.sleep(1)

        elif vib == "6":
            f_count = random.randint(12, min(24, len(FONT_CATALOG)))
            prof["fonts"] = random.sample(FONT_CATALOG, f_count)
            sohranit_bazu(baza_kormit)
            print(f" {c_lime('[+]')} Сгенерирован набор из {f_count} шрифтов!")
            time.sleep(1)

        elif vib == "7":
            conf = input(f"\n {Fore.LIGHTRED_EX}[!] Удалить профиль [{imya}] и все его файлы сессии? (y/n): {Style.RESET_ALL}").strip().lower()
            if conf == 'y':
                del baza_kormit[imya]
                sohranit_bazu(baza_kormit)
                s_dir = os.path.join(os.getcwd(), "sessions", imya)
                if os.path.exists(s_dir):
                    try:
                        shutil.rmtree(s_dir)
                    except Exception:
                        pass
                print(f" {c_lime('[+]')} Профиль [{imya}] полностью удален.")
                time.sleep(1)
                return None
            else:
                print(f" {c_dim('[-] Удаление отменено.')}")
                time.sleep(1)

        elif vib == "0":
            break

    return imya

def main():
    tekushiy_profil = None
    active_bridge = None
    
    while True:
        clear_console()
        print(gradient_banner(RAW_BANNER))
        print(gradient_text(SIGNATURE, COLOR_MINT, COLOR_LIME))
        print(render_divider())
        prof_label = c_lime(tekushiy_profil) if tekushiy_profil else c_dim("[-] Не выбран")
        print(f" {c_pastel('Выбранный профиль:')} {prof_label}")
        print(render_divider())
        print(f" {c_lime('[1]')} - Добавить профиль")
        print(f" {c_lime('[2]')} - Список профилей и их выбор")
        print(f" {c_lime('[3]')} - Запуск профиля")
        print(f" {c_lime('[4]')} - Редактировать профиль")
        print(f" {c_mint('[5]')} - Выход")
        print(render_divider())
        
        vib = input(f"\n {c_lime('>>')} Ваш выбор: ").strip()
        baza_kormit = chitat_bazu()
        
        if vib == "1":
            print(f"\n {c_mint('--- СОЗДАНИЕ ПРОФИЛЯ ---')}")
            skuf = input(f" {c_lime('>>')} Название профиля: ").strip()
            if not skuf:
                continue
            if skuf in baza_kormit:
                input(f" {Fore.LIGHTRED_EX}[-] Профиль с таким именем уже существует! Enter...{Style.RESET_ALL}")
                continue
                
            print(f"\n {c_mint('Как собрать комплектующие профиля?')}")
            print(f" {c_lime('[1]')} Выбрать вручную")
            print(f" {c_lime('[2]')} Рандом")
            build_type = input(f"\n {c_lime('>>')} Ваш выбор [1/2]: ").strip()
            
            if build_type == "2":
                chosen_cpu = random.choice(CPU_POOL)
                chosen_gpu = random.choice(GPU_POOL)
            else:
                chosen_cpu = paginated_selector(CPU_POOL, "процессор")
                chosen_gpu = paginated_selector(GPU_POOL, "видеокарта")

            resolutions = [(1920, 1080), (1920, 1080), (1366, 768), (1600, 900), (2560, 1440)]
            width, height = random.choice(resolutions)
            
            font_count = random.randint(12, min(24, len(FONT_CATALOG)))
            profile_fonts = random.sample(FONT_CATALOG, font_count)

            clear_console()
            p_info, detected_tz = nastroika_proksi_flow()

            if not p_info:
                timezone = input(f"\n {c_lime('>>')} Часовой пояс [Europe/Kyiv]: ").strip() or "Europe/Kyiv"
            else:
                timezone = detected_tz

            baza_kormit[skuf] = {
                "cpu_name": chosen_cpu["name"],
                "cpu": chosen_cpu["threads"],
                "ram": chosen_cpu["ram"],
                "gpu_name": chosen_gpu["name"],
                "gpu_vendor": chosen_gpu["vendor"],
                "gpu_renderer": chosen_gpu["renderer"],
                "width": width,
                "height": height,
                "timezone": timezone,
                "fonts": profile_fonts,
                "proxy": p_info
            }
            sohranit_bazu(baza_kormit)
            tekushiy_profil = skuf
            input(f"\n {c_lime('[+]')} Профиль '{skuf}' сохранен! Enter для возврата...")
            
        elif vib == "2":
            print(f"\n {c_mint('--- СПИСОК ПРОФИЛЕЙ ---')}")
            if not baza_kormit:
                input(f" {c_dim('База пуста. Нажмите Enter...')}")
                continue
            spisok = list(baza_kormit.keys())
            for i, p in enumerate(spisok):
                prof = baza_kormit[p]
                prx = prof.get("proxy")
                if isinstance(prx, dict):
                    prx_str = f"{prx.get('scheme', 'http')}://{prx.get('host', '')}:{prx.get('port', '')}"
                elif isinstance(prx, str) and prx.strip():
                    prx_str = prx
                else:
                    prx_str = "Без прокси"
                print(f" {c_lime(f'[{i}]')} {c_pastel(p)} -> {c_mint(prof.get('cpu_name', 'CPU'))} / {c_mint(prof.get('gpu_name', 'GPU'))} / {c_dim(prx_str)}")
            
            vibor_p = input(f"\n {c_lime('>>')} Номер профиля для выбора (Enter - назад): ").strip()
            if vibor_p.isdigit() and 0 <= int(vibor_p) < len(spisok):
                tekushiy_profil = spisok[int(vibor_p)]
                
        elif vib == "3":
            if not tekushiy_profil:
                input(f"\n {Fore.LIGHTYELLOW_EX}[-] Профиль не выбран! Перейдите в меню [2]. Enter...{Style.RESET_ALL}")
                continue
            
            prof_data = baza_kormit[tekushiy_profil]
            p_info = prof_data.get("proxy")
            if isinstance(p_info, str) and p_info.strip():
                p_info = razobrat_proksi(p_info)
            elif not isinstance(p_info, dict):
                p_info = None

            if p_info:
                print(f"\n {c_lime('[*]')} Проверка прокси ({p_info['scheme']}://{p_info['host']}:{p_info['port']})...")
                is_valid, res = poluchit_info_proksi(p_info, timeout=5)
                if not is_valid:
                    print(f"\n {Fore.LIGHTRED_EX}[!] ОШИБКА: Прокси недоступен!{Style.RESET_ALL}")
                    print(f" {c_dim('Причина:')} {res}")
                    print(f" {Fore.LIGHTRED_EX}[!] Запуск отменен.{Style.RESET_ALL}")
                    input(f"\n {c_dim('Нажмите Enter для возврата в главное меню...')}")
                    continue
                
                live_tz = res.get("timezone")
                if live_tz:
                    if live_tz == "Europe/Kiev":
                        live_tz = "Europe/Kyiv"
                    prof_data["timezone"] = live_tz

                print(f" {c_lime('[+]')} Прокси рабочий: {c_mint(res.get('query'))} ({res.get('country')}, {res.get('proxy_type')})")
                print(f" {c_lime('[+]')} Часовой пояс синхронизирован: {c_mint(prof_data['timezone'])}")

            print(f" {c_lime('[*]')} Запуск профиля [{tekushiy_profil}]...")
            start_ts = time.time()
            try:
                chushpan, active_bridge = sobrat_kolesnicu(tekushiy_profil, prof_data, p_info)
                print(f" {c_lime('[+]')} Браузер запущен за {round(time.time() - start_ts, 2)} сек!")
                print(f" {c_pastel('[+] Сессия открыта. Закройте окно браузера или нажмите Ctrl+C для выхода.')}")

                while True:
                    try:
                        _ = chushpan.window_handles
                    except Exception:
                        print(f"\n {c_dim('[+] Окно браузера закрыто.')}")
                        break
                    time.sleep(1)

                try:
                    chushpan.quit()
                except Exception:
                    pass
                if active_bridge:
                    active_bridge.stop()

            except KeyboardInterrupt:
                print(f"\n {c_dim('Сессия завершена.')}")
                try:
                    chushpan.quit()
                except Exception:
                    pass
                if active_bridge:
                    active_bridge.stop()
            except Exception as e:
                print(f"\n {Fore.LIGHTRED_EX}[!] ОШИБКА ЗАПУСКА: {e}{Style.RESET_ALL}")
                if active_bridge:
                    active_bridge.stop()
                input(f"\n {c_dim('Нажмите Enter для возврата...')}")

        elif vib == "4":
            if not baza_kormit:
                input(f"\n {c_dim('[-] База пуста, нечего редактировать. Enter...')}")
                continue

            target_to_edit = tekushiy_profil
            if not target_to_edit:
                print(f"\n {c_mint('--- Выберите профиль для редактирования ---')}")
                spisok = list(baza_kormit.keys())
                for i, p in enumerate(spisok):
                    print(f" {c_lime(f'[{i}]')} {c_pastel(p)}")
                vibor_p = input(f"\n {c_lime('>>')} Номер профиля (Enter - отмена): ").strip()
                if vibor_p.isdigit() and 0 <= int(vibor_p) < len(spisok):
                    target_to_edit = spisok[int(vibor_p)]
                else:
                    continue

            new_name = redaktirovat_profil(baza_kormit, target_to_edit)
            if new_name is None:
                tekushiy_profil = None
            else:
                tekushiy_profil = new_name
                
        elif vib == "5":
            print(f" {c_mint('Выход.')}")
            sys.exit(0)

if __name__ == "__main__":
    main()
