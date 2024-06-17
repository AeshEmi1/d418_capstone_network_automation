import yaml
from netmiko import ConnectHandler
import re
import argparse

class SwitchConfiguration:
    def __init__(self, switch_ip, username, password):
        switch_dict = {
            "device_type": "extreme_exos",
            "host": switch_ip,
            "username": username,
            "password": password
        }
        self.host = switch_ip
        self.switch_connection = None

        # Connect to the switches
        try:
            self.switch_connection = ConnectHandler(**switch_dict)
            print(f"Connection successful to {switch_dict['host']}!")
        except Exception as e:
            print(f"Connection failed! Maybe the switch is offline? - {e}")

    def set_banner(self):
        """Method for part C1. Returns VLANs as an array."""
        try:
            if self.switch_connection:
                banner = "WARNING: This system is monitored. Unauthorized acceess to this system is\nforbidden and will be prosecuted by law."
                self.switch_connection.send_command("enable cli prompting")
                show_vlan = self.switch_connection.send_config_set(f"conf banner bef\n{banner}\n\nsave")
        except:
            print(f"Banner configured on {self.host}")
            pass
def main():
    # Read Ansible inventory file
    with open("/etc/ansible/inventory/devices", 'r') as f:
        ansible_inventory = yaml.safe_load(f)

        # Get switch ips and save them to an array
        switch_ips = [host['ansible_host'] for host in ansible_inventory['switches']['hosts'].values()]

        # Get the Switch's Credentials
        username = ansible_inventory['switches']['vars']['ansible_user']
        password = ansible_inventory['switches']['vars']['ansible_ssh_pass']
        
        # Create an array of SwitchConfiguration Objects
        switches = [SwitchConfiguration(switch_ip, username, password) for switch_ip in switch_ips]
        
        for switch in switches:
            switch.set_banner()
    
main()
