# main.py

import time
from shared_utils import stop_vm, update_machine_type, start_vm, get_machine_type_from_db, truncate_table

def entry_point2(request):
    try:
        # Replace these values with your actual project, zone, and instance name
        project = ''
        zone = ''
        instance_name = ''

        # Step 1: Stop the VM
        stop_vm_result = stop_vm(project, zone, instance_name)

        # Sleep for a few seconds to allow the VM to stop
        time.sleep(40)

        # Step 2: Update the VM instance with the machine type from the SQL database
        machine_type = get_machine_type_from_db(instance_name)
        update_machine_type_result = update_machine_type(project, zone, instance_name, machine_type)

        # Sleep for a few seconds to allow the machine type update to take effect
        time.sleep(40)

        # Step 3: Start the VM
        start_vm_result = start_vm(project, zone, instance_name)

        # Sleep for a few seconds to ensure the VM has started
        time.sleep(40)

        # Step 4: Run the truncate command on the 'machine_types' table
        truncate_result = truncate_table()

        return {
            "stop_vm_result": stop_vm_result,
            "update_machine_type_result": update_machine_type_result,
            "start_vm_result": start_vm_result,
            "truncate_result": truncate_result,
            "message": "VM stopped, machine type updated, VM started, and table truncated successfully"
        }
    except Exception as e:
        return {"error": str(e)}

