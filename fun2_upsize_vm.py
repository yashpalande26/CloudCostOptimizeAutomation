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

def get_machine_type_from_db(instance_name):
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        select_query = "SELECT machine_type FROM machine_types WHERE instance_name = %s"
        cursor.execute(select_query, (instance_name,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return None
    except Exception as e:
        raise e
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def truncate_table():
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        truncate_query = "TRUNCATE TABLE machine_types"
        cursor.execute(truncate_query)
        connection.commit()
        return {"message": "Table 'machine_types' truncated successfully"}
    except Exception as e:
        return {"error": str(e)}
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


