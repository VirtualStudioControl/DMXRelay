import serial.tools.list_ports as list_ports

ports = list_ports.comports(True)

devices = []

for info in ports:
    devices.append("{} ({} {})".format(info.device, info.manufacturer, info.product))

print(devices)