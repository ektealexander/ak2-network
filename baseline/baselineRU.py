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
    """
    Send a command and wait briefly.
    Provides longer delays for known "slow" contexts like key generation,
    interface configuration, and writing to memory.
    """
    base_wait, long_wait = 0.25, 0.9
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
    if not cmd.endswith("\n"): cmd += "\n"
    ser.write(cmd.encode("utf-8"))
    time.sleep(wait)

def skip_initial_dialog(ser):
    """Bypass the initial setup and autoinstall prompts on a fresh device."""
    for _ in range(3):
        send_cmd(ser, "\r", 0.5)
    send_cmd(ser, "no", 1.0)   # Skip initial configuration dialog
    send_cmd(ser, "yes", 1.0)  # Terminate autoinstall

def parse_if_list(expr: str):
    """Turn a comma-separated string of interfaces into a Python list."""
    return [p.strip() for p in expr.split(",") if p.strip()]

def main():
    print("=== Baseline Cisco ROUTER ===")
    port     = input("Serial port [COM3]: ").strip() or "COM3"
    hostname = input("Hostname: ").strip()
    enable_s = getpass.getpass("Enable secret: ").strip()
    user     = input("Local admin username [admin]: ").strip() or "admin"
    pw       = getpass.getpass("Password for local admin: ").strip()
    mgmt_if  = input("Management interface (e.g. GigabitEthernet0/0/0): ").strip()
    mgmt_ip  = input("Management IP address: ").strip()
    mgmt_msk = input("Management subnet mask: ").strip()

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

        # SSH setup (order matters: domain -> keys -> ssh v2)
        "crypto key generate rsa modulus 2048",
        "ip ssh version 2",

        # Console and VTY settings
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

        # Management interface
        f"interface {mgmt_if}",
        f" ip address {mgmt_ip} {mgmt_msk}",
        " no shutdown",
        "exit",
    ]

    # Save configuration
    cmds += ["do write memory", "end"]

    for c in cmds:
        send_cmd(ser, c)
        if c.startswith("crypto key generate rsa"):
            time.sleep(2.0)  # extra time for RSA key generation

    print("Router configuration sent. SSH should be available once the management link is up.")
    ser.close()

if __name__ == "__main__":
    main()