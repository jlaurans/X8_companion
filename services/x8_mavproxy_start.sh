#!/bin/bash
sleep 2
cd /home/pi/X8_Companion/
/home/pi/X8_Companion/venv/bin/python3 /home/pi/X8_Companion/venv/bin/mavproxy.py --master=/dev/ttyAMA0 --baud=921600 --out=udp:127.0.0.1:14551 --out=udp:192.168.1.115:14550 --out=udp:10.148.178.3:14550 --out=udp:10.148.178.64:14552 --aircraft="logs" --daemon --non-interactive
