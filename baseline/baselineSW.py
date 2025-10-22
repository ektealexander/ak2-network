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

def skip_initial_dialog(ser):
    print("Skipping initial config dialog sequence...")
    send_cmd(ser, "\r", 1.0)      # 1. Wake console
    send_cmd(ser, "no", 1.0)      # 2. Answer 'no'
    send_cmd(ser, "yes", 1.0)     # 3. Confirm skip
    print("Waiting 20 seconds for device to fully load...")
    time.sleep(20)                # 4. Wait for system boot
    send_cmd(ser, "\r", 1.0)      # 5. Final Enter to reach prompt
    print("Device ready for configuration.")

def parse_if_list(expr: str):
    return [p.strip() for p in expr.split(",") if p.strip()]

def main():
    print("=== Baseline Cisco SW ===")
    port       = input("Serialport [COM3]: ").strip() or "COM3"
    hostname   = input("Hostname: ").strip()
    enable_s   = getpass.getpass("Enable secret [cisco]: ").strip() or "cisco"
    user       = input("Local admin-account [cisco]: ").strip() or "cisco"
    pw         = getpass.getpass("Password for local admin [cisco]: ").strip() or "cisco"
    mgmt_vlan  = input("MGMT VLAN ID [99]: ").strip() or "99"
    mgmt_ip    = input("MGMT IP: ").strip()
    mgmt_msk   = input("MGMT network mask: ").strip()
    mgmt_gw    = input("MGMT default-gateway: ").strip()

    trunks_expr   = input("Trunk-ports (e.g. gi1/0/24,gi1/0/28,fa0/1,fa0/3): ").strip()
    trunks        = parse_if_list(trunks_expr)
    if not trunks:
        print("Select at least 1 trunk-port"); sys.exit(1)

    acc_expr = input("Access-ports in MGMT VLAN? (default=no, e.g. gi1/0/1,gi1/0/2): ").strip()
    access_ports = parse_if_list(acc_expr) if acc_expr else []

    ser = open_serial(port, baudrate=9600)
    skip_initial_dialog(ser)

    cmds = [
        "enable",
        "configure terminal",
        f"hostname {hostname}",
        "ip domain-name fsi-alespi.com",
        "no ip domain-lookup",
        f"enable secret {enable_s}",
        f"username {user} privilege 15 secret {pw}",

        "crypto key generate rsa modulus 2048",
        "ip ssh version 2",

        f"vlan {mgmt_vlan}",
        "name MGMT",
        "exit",
        f"interface vlan {mgmt_vlan}",
        f"ip address {mgmt_ip} {mgmt_msk}",
        "no shutdown",
        "exit",

        f"ip default-gateway {mgmt_gw}",

        "line vty 0 15",
        "login local",
        "transport input ssh",
        "exec-timeout 10 0",
        "exit",
    ]

    trunk_block = [
        "switchport",
        "switchport mode trunk",
        f"switchport trunk allowed vlan add {mgmt_vlan}",
        "no shutdown",
        "exit",
    ]
    if len(trunks) > 1:
        cmds += ["interface range " + ",".join(trunks)] + trunk_block
    else:
        cmds += [f"interface {trunks[0]}"] + trunk_block

    if access_ports:
        acc_block = [
            "switchport",
            f"switchport mode access",
            f"switchport access vlan {mgmt_vlan}",
            "spanning-tree portfast",
            "no shutdown",
            "exit",
        ]
        if len(access_ports) > 1:
            cmds += ["interface range " + ",".join(access_ports)] + acc_block
        else:
            cmds += [f"interface {access_ports[0]}"] + acc_block

    cmds += ["do write memory", "end"]

    for c in cmds:
        send_cmd(ser, c)
        if c.startswith("crypto key generate rsa"):
            time.sleep(2.0)

    print("Config transferred complete")
    ser.close()

if __name__ == "__main__":
    main()