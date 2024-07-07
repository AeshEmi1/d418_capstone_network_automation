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
        """Sets banner for switches"""
        try:
            if self.switch_connection:
                banner = "WARNING: This system is monitored. Unauthorized acceess to this system is\nforbidden and will be prosecuted by law."
                self.switch_connection.send_command("enable cli prompting")
                show_vlan = self.switch_connection.send_config_set(f"conf banner bef\n{banner}\n\nsave")
        except:
            self.switch_connection.save_config()
            print(f"Banner configured on {self.host}")
            pass

    def remove_banner(self):
        """Sets banner for switches"""
        try:
            if self.switch_connection:
                self.switch_connection.send_config_set(f"unconfigure banner")
                self.switch_connection.send_config_set(f"save")
                print(f"Banner removed from {self.host}!")
        except:
            print("ERROR: Unexpected Error!")          

class FortiGateConfiguration:
    def __init__(self, fortigate_ip, username, password):
        fortigate_dict = {
            "device_type": "fortinet",
            "host": fortigate_ip,
            "username": username,
            "password": password
        }
        
        self.host = fortigate_ip
        self.fortigate_connection = None

        # Connect to the switches
        try:
            self.fortigate_connection = ConnectHandler(**fortigate_dict)
            print(f"Connection successful to {fortigate_dict['host']}!")
        except Exception as e:
            print(f"Connection failed! Maybe the switch is offline? - {e}")
        

    def set_banner(self):
        """Sets banner for fortigates"""
        try:
            if self.fortigate_connection:
                banner = "WARNING: This system is monitored. Unauthorized acceess to this system is forbidden and will be prosecuted by law."
                self.fortigate_connection.send_config_set("config system replacemsg admin pre_admin-disclaimer-text")
                self.fortigate_connection.send_config_set(f'set buffer "{banner}"')
                self.fortigate_connection.send_config_set("end")
                self.fortigate_connection.send_config_set("config system replacemsg admin post_admin-disclaimer-text")
                self.fortigate_connection.send_config_set(f'set buffer "{banner}"')
                self.fortigate_connection.send_config_set("end")
                self.fortigate_connection.send_config_set("config system global")
                self.fortigate_connection.send_config_set("set pre-login-banner enable")
                self.fortigate_connection.send_config_set("set post-login-banner enable")
                self.fortigate_connection.send_config_set("end")
                print(f"Banner configured on {self.host}!")
        except:
            print("ERROR: Unexpected Error!")          
    
    def remove_banner(self):
        """Sets banner for fortigates"""
        try:
            if self.fortigate_connection:
                self.fortigate_connection.send_config_set("config system replacemsg admin pre_admin-disclaimer-text")
                self.fortigate_connection.send_config_set("unset buffer")
                self.fortigate_connection.send_config_set("end")
                self.fortigate_connection.send_config_set("config system replacemsg admin post_admin-disclaimer-text")
                self.fortigate_connection.send_config_set("unset buffer")
                self.fortigate_connection.send_config_set("end")
                self.fortigate_connection.send_config_set("config system global")
                self.fortigate_connection.send_config_set("set pre-login-banner disable")
                self.fortigate_connection.send_config_set("set post-login-banner disable")
                self.fortigate_connection.send_config_set("end")
                print(f"Banner removed from {self.host}!")
        except:
            print("ERROR: Unexpected Error!")          

def main():
    parser = argparse.ArgumentParser(description="Script to configure and remove banners on switches and firewalls.")
    parser.add_argument('--configure', action='store_true', help='Configure banners')
    parser.add_argument('--remove', action='store_true', help='Remove banners')
    args = parser.parse_args()

    if args.remove and args.configure:
        print("ERROR: Please only select one option. --configure or --remove.")
        exit(1)
    elif not args.remove and not args.configure:
        print("ERROR: Please select one option. --configure or --remove.")
        exit(1)

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
        
        # Get fortigate ips and save them to an array
        fortigate_ips = [host['ansible_host'] for host in ansible_inventory['firewalls']['hosts'].values()]

        # Get the Switch's Credentials
        username = ansible_inventory['firewalls']['vars']['ansible_user']
        password = ansible_inventory['firewalls']['vars']['ansible_password']
        
        # Create an array of FortiGateConfiguration Objects
        firewalls = [FortiGateConfiguration(fortigate_ip, username, password) for fortigate_ip in fortigate_ips]
        
        if args.configure:
            for switch in switches:
                switch.set_banner()
            for firewall in firewalls:
                firewall.set_banner()
        elif args.remove:
            for switch in switches:
                switch.remove_banner()
            for firewall in firewalls:
                firewall.remove_banner()
        else:
            print("ERROR: Unexpected Error!")          

main()
