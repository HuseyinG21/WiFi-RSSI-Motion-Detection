import subprocess
import socket
import time
import re

BOARD = "UNO1"

LAPTOP_IP = "192.168.1.107"
PORT = 6000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:

    out = subprocess.check_output(
        ["/usr/sbin/iw", "dev", "wlan0", "station", "dump"],
        text=True
    )

    signal = re.search(r"signal:\s+(-?\d+)", out)
    avg = re.search(r"signal avg:\s+(-?\d+)", out)
    rate = re.search(r"rx bitrate:\s+([0-9.]+)", out)

    if signal and avg and rate:

        msg = f"{BOARD},{signal.group(1)},{avg.group(1)},{rate.group(1)}"

        sock.sendto(msg.encode(), (LAPTOP_IP, PORT))

        print(msg)

    time.sleep(0.1)
