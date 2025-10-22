Network Lab Reproduction Checklist

Prerequisites (run in PowerShell):
- python -m pip install --upgrade pip
- pip install pyserial ansible
- ansible-galaxy collection install cisco.ios

Serial baseline (do on each device; use COM port of console cable):
- Run router baseline for R1: python baseline\baselineRU.py -> COM3, Hostname: R1, Enable: cisco, Local user: cisco/cisco, Mgmt IF: GigabitEthernet0/0/0, Mgmt IP: 10.0.99.2, Mask: 255.255.255.0
- Run router baseline for R2: python baseline\baselineRU.py -> COM3, Hostname: R2, Enable: cisco, Local user: cisco/cisco, Mgmt IF: GigabitEthernet0/0/0, Mgmt IP: 10.0.99.3, Mask: 255.255.255.0
- Run switch baseline for SW1: python baseline\baselineSW.py -> COM3, Hostname: SW1, Enable: cisco, Local user: cisco/cisco, MGMT VLAN: 99, MGMT IP: 10.0.99.10, Mask: 255.255.255.0, GW: 10.0.99.1
- Run switch baseline for SW2: python baseline\baselineSW.py -> Hostname: SW2, MGMT IP: 10.1.99.10
- Run switch baseline for SW3: python baseline\baselineSW.py -> Hostname: SW3, MGMT IP: 10.1.99.11
- Run switch baseline for SW4: python baseline\baselineSW.py -> Hostname: SW4, MGMT IP: 10.1.99.12
- Run switch baseline for SW5: python baseline\baselineSW.py -> Hostname: SW5, MGMT IP: 10.1.99.13

Cabling:
- SW1 Gi1/0/23 <-> R1 Gi0/0/0
- SW1 Gi1/0/24 <-> R2 Gi0/0/0
- R1 Gi0/0/1 <-> SW2 Fa0/23
- R2 Gi0/0/1 <-> SW2 Fa0/24
- SW2 Fa0/21 & Fa0/22 <-> SW3 Fa0/21 & Fa0/22 (EtherChannel / Port-channel6)
- SW3 Fa0/23 <-> SW4 Gi1/0/24
- SW3 Fa0/24 <-> SW5 Gi1/0/24

Ansible run order:
- ansible-playbook -i hosts playbooks/sw1.yml
- ansible-playbook -i hosts playbooks/r1.yml
- ansible-playbook -i hosts playbooks/r2.yml
- ansible-playbook -i hosts playbooks/sw2.yml
- ansible-playbook -i hosts playbooks/sw3.yml
- ansible-playbook -i hosts playbooks/sw4-5.yml


Verification:
- ssh cisco@10.0.99.2   # R1
- ssh cisco@10.0.99.3   # R2
- ssh cisco@10.0.99.10  # SW1
- show standby brief (on routers) to confirm HSRP

Troubleshooting (quick):
- If SSH/auth fails: confirm ansible/hosts credentials or use the same local admin password created during baseline.
- If playbooks fail: ensure cisco.ios collection is installed: ansible-galaxy collection install cisco.ios
- If serial baseline hangs: close other console programs and increase delays in baseline/*.py send_cmd()

Notes:
- This checklist intentionally uses the exact IPs and default credentials (`cisco/cisco`) in the repo for reproducibility. Replace credentials before production use.