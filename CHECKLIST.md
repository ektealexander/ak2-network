Network Lab Reproduction Checklist (one-line steps)

Prerequisites (run in PowerShell):
- python -m pip install --upgrade pip
- pip install pyserial ansible
- ansible-galaxy collection install cisco.ios

Serial baseline (do on each device; use COM port of console cable):
- Run router baseline for r1: python baseline\baselineRU.py -> COM3, Hostname: r1, Enable: cisco, Local user: cisco/cisco, Mgmt IF: GigabitEthernet0/0/1, Mgmt IP: 10.0.99.2, Mask: 255.255.255.0
- Run router baseline for r2: python baseline\baselineRU.py -> COM3, Hostname: r2, Enable: cisco, Local user: cisco/cisco, Mgmt IF: GigabitEthernet0/0/1, Mgmt IP: 10.0.99.3, Mask: 255.255.255.0
- Run switch baseline for sw1: python baseline\baselineSW.py -> COM3, Hostname: sw1, Enable: cisco, Local user: cisco/cisco, MGMT VLAN: 99, MGMT IP: 10.0.99.10, Mask: 255.255.255.0, GW: 10.0.99.1
- Run switch baseline for sw2: python baseline\baselineSW.py -> Hostname: sw2, MGMT IP: 10.1.99.10
- Run switch baseline for sw3: python baseline\baselineSW.py -> Hostname: sw3, MGMT IP: 10.1.99.11
- Run switch baseline for sw4: python baseline\baselineSW.py -> Hostname: sw4, MGMT IP: 10.1.99.12
- Run switch baseline for sw5: python baseline\baselineSW.py -> Hostname: sw5, MGMT IP: 10.1.99.13

Cabling (summary):
- sw1 Gi1/0/23 <-> r1 Gi0/0/0
- sw1 Gi1/0/24 <-> r2 Gi0/0/0
- r1 Gi0/0/1 <-> sw2 Gi0/0/23
- r2 Gi0/0/1 <-> sw2 Gi0/0/24
- sw2 Gi0/21 & Gi0/22 <-> sw3 Gi0/21 & Gi0/22 (EtherChannel / Port-channel10)
- sw3 Gi0/23 <-> sw4 Gi1/0/24
- sw3 Gi0/24 <-> sw5 Gi1/0/24

Ansible run order (PowerShell copy/paste):
- ansible-playbook -i ansible/hosts ansible/playbooks/sw1.yml
- ansible-playbook -i ansible/hosts ansible/playbooks/r1.yml
- ansible-playbook -i ansible/hosts ansible/playbooks/r2.yml
- ansible-playbook -i ansible/hosts ansible/playbooks/sw2.yml
- ansible-playbook -i ansible/hosts ansible/playbooks/sw3.yml
- ansible-playbook -i ansible/hosts ansible/playbooks/sw4-5.yml

Verification (examples):
- ssh cisco@10.0.99.2   # r1
- ssh cisco@10.0.99.3   # r2
- ssh cisco@10.0.99.10  # sw1
- show standby brief (on routers/switches) to confirm HSRP

Troubleshooting (quick):
- If SSH/auth fails: confirm ansible/hosts credentials or use the same local admin password created during baseline.
- If playbooks fail: ensure cisco.ios collection is installed: ansible-galaxy collection install cisco.ios
- If serial baseline hangs: close other console programs and increase delays in baseline/*.py send_cmd()

Notes:
- This checklist intentionally uses the exact IPs and default credentials (`cisco/cisco`) in the repo for reproducibility. Replace credentials before production use.

Image (optional): place the provided topology image at `docs/topology.png` to embed it in `REPLICATE.md` and make the visual diagram available.
