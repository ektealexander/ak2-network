1. Connect Cisco console cable

2. Run one of the scripts based on the device:

    python baselineSW.py

    or

    python baselineRU.py



Scripts

baselineSW.py

Sets hostname, domain name, enable secret
Creates a local admin user
Generates RSA keys and enables SSH v2
Configures management VLAN + SVI
Sets trunk ports
Configures default gateway
Saves the configuration


baselineRU.py

Sets hostname, domain name, enable secret
Creates a local admin user
Generates RSA keys and enables SSH v2
Configures console and VTY lines
Assigns IP on a management interface
Saves the configuration


Switch baseline via COM3:
python baselineSW.py

=== Baseline Cisco SWITCH ===
Serialport [COM3]:
Hostname: SW3
Enable secret:
Local admin-account [admin]: cisco
Password for local admin:
MGMT VLAN ID [99]:
MGMT IP: 10.0.99.2
MGMT network mask: 255.255.255.0
MGMT default-gateway: 10.0.99.1
Trunk-ports (coulmn, Gi1/0/24,Gi1/0/28): Gi0/1

Config transferred complete


ssh admin@10.0.99.2


Router baseline via COM3:
python baselineRU.py

=== Baseline Cisco ROUTER ===
Serial port [COM3]:
Hostname: R1
Enable secret:
Local admin username [admin]: cisco
Password for local admin:
Management interface (e.g. GigabitEthernet0/0/0): gi0/0/1
Management IP address: 10.0.99.1
Management subnet mask: 255.255.255.0
Default route next-hop IP: 10.0.99.1

Config transferred complete

ssh admin@10.0.99.1
