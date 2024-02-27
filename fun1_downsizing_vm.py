# shared_utils.py

import googleapiclient.discovery
import mysql.connector
import re 
import time

# Cloud SQL connection configuration
db_config = {
    'user': '',
    'password': '',
    'host': '',
    'database': '',
}

def capture_and_store_machine_type(request):
    try:
        # Replace these values with your actual project, zone, and instance name
        project = ''
        zone = ''
        instance_name = ''

        # Get the current machine type of the instance
        machine_type = get_instance_machine_type(project, zone, instance_name)

        # Store the machine type in Cloud SQL database
        store_machine_type(instance_name, machine_type)

        # Stop the VM
        stop_vm(project, zone, instance_name)

        # Sleep for a few seconds to allow the VM to stop
        time.sleep(40)

        # Update the VM machine type to e2-micro
        update_machine_type(project, zone, instance_name, 'e2-micro')

        # Sleep for a few seconds to allow the machine type update to take effect
        time.sleep(40)

        # Start the VM
        start_vm(project, zone, instance_name)

        return {"message": f"Machine type captured, stored, VM stopped, and machine type updated and VM started: {machine_type}"}
    except Exception as e:
        return {"error": str(e)}

def get_instance_machine_type(project, zone, instance_name):
    compute = googleapiclient.discovery.build('compute', 'v1')
    instance_info = compute.instances().get(project=project, zone=zone, instance=instance_name).execute()
    return instance_info['machineType']

def store_machine_type(instance_name, full_machine_type_url):
    # Extract the machine type from the full URL
    machine_type_match = re.search(r'/machineTypes/([^/]+)$', full_machine_type_url)
    if machine_type_match:
        machine_type = machine_type_match.group(1)

        connection = None
        cursor = None
        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            insert_query = "INSERT INTO machine_types (instance_name, machine_type) VALUES (%s, %s)"
            cursor.execute(insert_query, (instance_name, machine_type))
            connection.commit()
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

def stop_vm(project, zone, instance_name):
    compute = googleapiclient.discovery.build('compute', 'v1')
    result = compute.instances().stop(project=project, zone=zone, instance=instance_name).execute()
    return result

def update_machine_type(project, zone, instance_name, new_machine_type):
    compute = googleapiclient.discovery.build('compute', 'v1')

    # Get the current machine type of the instance
    instance_info = compute.instances().get(project=project, zone=zone, instance=instance_name).execute()
    current_machine_type = instance_info['machineType']

    # If the current machine type is not the same as the new one, update it
    if current_machine_type != new_machine_type:
        body = {
            'machineType': f'zones/{zone}/machineTypes/{new_machine_type}'
        }
        result = compute.instances().setMachineType(project=project, zone=zone, instance=instance_name, body=body).execute()

        # Wait for some time to ensure the machine type update has taken effect
        time.sleep(10)

        return result
    else:
        return {"message": f"Machine type is already set to {new_machine_type}"}

def start_vm(project, zone, instance_name):
    compute = googleapiclient.discovery.build('compute', 'v1')
    result = compute.instances().start(project=project, zone=zone, instance=instance_name).execute()

    # Wait for some time to ensure the VM has started
    time.sleep(10)

    return result
