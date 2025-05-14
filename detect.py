import serial.tools.list_ports

def get_active_ports():
    ports = serial.tools.list_ports.comports()
    resolved = {}
    for port, desc, hwid in sorted(ports):
        resolved[port] = desc, hwid
    return resolved