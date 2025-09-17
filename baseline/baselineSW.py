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
    Skriv kommando og vent litt. Gir automatisk lengre pauser for 'trege' kontekster.
    """
    base_wait = 0.25
    long_wait = 0.8

    if wait is None:
        if cmd.startswith(("configure terminal",
                           "vlan ",
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

def handle_initial_dialog(ser):
    for _ in range(3):
        send_cmd(ser, "\r", 0.5)
    send_cmd(ser, "no", 1.0)    # initial config dialog? -> no
    send_cmd(ser, "yes", 1.0)   # terminate autoinstall? -> yes

def parse_if_list(expr: str):
    return [p.strip() for p in expr.split(",") if p.strip()]

def main():
    print("=== Baseline Cisco SWITCH ===")
    port       = input("Serialport [COM3]: ").strip() or "COM3"
    hostname   = input("Hostname: ").strip()
    enable_s   = getpass.getpass("Enable secret: ").strip()
    user       = input("Local admin-account [admin]: ").strip() or "admin"
    pw         = getpass.getpass("Password for local admin: ").strip()
    mgmt_vlan  = input("MGMT VLAN ID [99]: ").strip() or "99"
    mgmt_ip    = input("MGMT IP: ").strip()
    mgmt_msk   = input("MGMT network mask: ").strip()
    mgmt_gw    = input("MGMT default-gateway: ").strip()

    trunks_expr   = input("Trunk-ports (coulmn, Gi1/0/24,Gi1/0/28): ").strip()
    trunks        = parse_if_list(trunks_expr)
    if not trunks:
        print("Select at least 1 trunk-port"); sys.exit(1)

    ser = open_serial(port, baudrate=9600)
    handle_initial_dialog(ser)

    cmds = [
        "enable",
        "configure terminal",
        f"hostname {hostname}",
        "ip domain-name fsi-alespi.com",
        "no ip domain-lookup",
        f"enable secret {enable_s}",
        f"username {user} privilege 15 secret {pw}",

        # SSH
        "crypto key generate rsa modulus 2048",
        "ip ssh version 2",

        # VLAN-tabell + SVI
        f"vlan {mgmt_vlan}",
        " name MGMT",
        "exit",
        f"interface vlan {mgmt_vlan}",
        f" ip address {mgmt_ip} {mgmt_msk}",
        " no shutdown",
        "exit",

        # default-gw (for L2 mgmt)
        f"ip default-gateway {mgmt_gw}",

        # VTY
        "line vty 0 15",
        " login local",
        " transport input ssh",
        " exec-timeout 10 0",
        "exit",
    ]

    # Trunk(er)
    trunk_block = [
        " switchport",
        " switchport mode trunk",
        f" switchport trunk allowed vlan add {mgmt_vlan}",
        " no shutdown",
        "exit",
    ]
    if len(trunks) > 1:
        cmds += ["interface range " + ",".join(trunks)] + trunk_block
    else:
        cmds += [f"interface {trunks[0]}"] + trunk_block

    # Lagre
    cmds += ["do write memory", "end"]

    for c in cmds:
        send_cmd(ser, c)
        if c.startswith("crypto key generate rsa"):
            time.sleep(2.0)  # ekstra tid for keygen

    print("Config transferred completed")
    ser.close()

if __name__ == "__main__":
    main()