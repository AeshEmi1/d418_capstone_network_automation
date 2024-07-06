import yaml
import os

# Create a dictionary of the Switch group
switches = {
    "HQSwitch1":[
        "10.100.0.33",
        "HQSwitch1_BACKUP"
    ],
    "HQSwitch2":[
        "10.100.0.34",
        "HQSwitch2_BACKUP"

    ],
    "RemoteOfficeSwitch1":[
        "10.1.0.2",
        "RemoteOfficeSwitch1_BACKUP"
    ]
}

switch_variables = {
    "ansible_connection":"ansible.netcommon.network_cli",
    "ansible_network_os":"community.network.exos",
    "ansible_user":"admin",
    "ansible_ssh_pass":""
}

# Create a dictionary of the firewalls
firewall = {
    "HQFW":[
        "10.0.0.1",
        "HQFW_BACKUP"
    ],
    "RemoteOfficeFW":[
        "10.1.0.1",
        "RemoteOfficeFW_BACKUP"
    ]
}

firewall_variables = {
    "ansible_connection":"httpapi",
    "username":"admin",
    "password":"P@ssw0rd"
}

# Create an array of each of the groups to pass into the ansible_format function
switch_groups = [{"switches":switches}, {"firewalls":firewall}]
group_variables = {
    "switches": switch_variables,
    "firewalls": firewall_variables
    }

# Turn the array of device groups into an ansible friendly format, returns an object that's easily parsable into YAML
def ansible_format(device_groups):
    # Create the ansible_inventory
    ansible_inventory = {}

    # Loop through each device group
    for device_group in device_groups:
        # The device variables
        device_variables = [
            "ansible_host",
            "backup_name"
        ]

        # Grab the device group name from the dictionary 
        device_group_name = next(iter(device_group))

        # Create a dictionary in the ansible_dictionary with the appropriate group name
        ansible_inventory[device_group_name] = {}

        # Add hosts: to the ansible inventory
        ansible_inventory[device_group_name]["hosts"] = {}

        # Add vars: to the ansible inventory
        ansible_inventory[device_group_name]["vars"] = {}

        # Loop through each device in that group to grab it's array of elements 
        for device, element in device_group[device_group_name].items():
            # Add the device into the ansible_inventory under hosts:
            ansible_inventory[device_group_name]["hosts"][device] = {device_variables[i]: element[i] for i in range(len(device_variables))}
        
        # Add the group variables 
        ansible_inventory[device_group_name]["vars"] = group_variables[device_group_name]
    
    # Return the ansible inventory
    return ansible_inventory

# Write the ansible inventory to the ansible hosts file
os.makedirs("/etc/ansible/inventory", exist_ok=True)

with open("/etc/ansible/inventory/devices", "w") as f:
    yaml.safe_dump(ansible_format(switch_groups), f, sort_keys=False)
    print("Successfully wrote switch inventory file to /etc/ansible/inventory/devices!")
