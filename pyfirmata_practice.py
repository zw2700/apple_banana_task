import pyfirmata,time
import serial.tools.list_ports

ports = list(serial.tools.list_ports.comports())
for p in ports:
    if "usbmodem" in p.name:
        port = p.device
print(port)
board = pyfirmata.Arduino(port)
it = pyfirmata.util.Iterator(board)
it.start()

board.digital[2].mode = pyfirmata.INPUT

while True:
    touchbar = board.digital[2].read()
    if touchbar is True:
        print(touchbar)
        time.sleep(1)
