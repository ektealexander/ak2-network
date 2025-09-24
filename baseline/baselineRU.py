import serial, time, sys, getpass

def open_serial(port, baudrate=9600, timeout=8):
    try:
        return serial.Serial(
            port=port,
            baudrate=baudrate,
            parity="N",
            stopbits=1,
            bytesize=8,
            timeout=timeout
        )
    except serial.serialutil.SerialException as e:
        print("Serial-fault:", e); sys.exit(1)

def send_cmd(ser, cmd, wait=None):
    base_wait = 0.25
    long_wait = 0.9

    if wait is None:
        if cmd.startswith(("configure terminal",
                           "interface ",
                           "crypto key generate rsa",
                           "do write memory",
                           "end",
                           "exit")):
            wait = long_wait
        else:
            wait = base_wait
    if not cmd.endswith("\n"):
        cmd += "\n"
    ser.write(cmd.encode("utf-8"))
    time.sleep(wait)

def skip_initial_dialog(ser):
    for _ in range(3):
        send_cmd(ser, "\r", 0.5)
    send_cmd(ser, "no", 1.0)
    send_cmd(ser, "yes", 1.0)

def parse_if_list(expr: str):
    return [p.strip() for p in expr.split(",") if p.strip()]

def main():
    print("=== Baseline Cisco ROUTER ===")
    port     = input("Serial port [COM3]: ").strip() or "COM3"
    hostname = input("Hostname: ").strip()
    enable_s = getpass.getpass("Enable secret [cisco]: ").strip() or "cisco"
    user     = input("Local admin-account [cisco]: ").strip() or "cisco"
    pw       = getpass.getpass("Password for local admin [cisco]: ").strip() or "cisco"
    mgmt_ip  = input("MGMT IP: ").strip()
    mgmt_msk = input("MGMT network mask: ").strip()
    mgmt_if  = input("MGMT interface (e.g. gi0/0/0): ").strip()

    ser = open_serial(port, baudrate=9600)
    skip_initial_dialog(ser)

    cmds = [
        "enable",
        "configure terminal",
        f"hostname {hostname}",
        f"ip domain name fsi-alespi.com",
        "no ip domain lookup",
        f"enable secret {enable_s}",
        f"username {user} privilege 15 secret {pw}",

        "crypto key generate rsa modulus 2048",
        "ip ssh version 2",

        "line con 0",
        " logging synchronous",
        " exec-timeout 10 0",
        " login local",
        "exit",
        "line vty 0 15",
        " login local",
        " transport input ssh",
        " exec-timeout 10 0",
        "exit",

        f"interface {mgmt_if}",
        " no shutdown",
        f"interface {mgmt_if}.99",
        "encapsulation dot1Q 99",
        f"ip address {mgmt_ip} {mgmt_msk}",
        "exit",
    ]

    cmds += ["do write memory", "end"]

    for c in cmds:
        send_cmd(ser, c)
        if c.startswith("crypto key generate rsa"):
            time.sleep(2.0)

    print("Config transferred complete")
    ser.close()

if __name__ == "__main__":
    main()