# sender.py
import lcm
import time

lc = lcm.LCM("udpm://239.255.76.67:7667?recv_addr=192.168.1.101&ttl=1")

print("LCM sender running...")
while True:
    msg = f"Hello from the other side!".encode()
    lc.publish("EXAMPLE", msg)
    print("Message sent.")
    time.sleep(1)
