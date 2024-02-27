# main.py

from shared_utils import capture_and_store_machine_type

def entry_point(request):
    result = capture_and_store_machine_type(request)

    if "error" not in result:
        # If capturing and storing the machine type is successful, stop the VM
        stop_vm_result = stop_vm(request)

        # Add the stop result to the response
        result["stop_vm_result"] = stop_vm_result

        # Sleep for a few seconds to allow the VM to stop
        time.sleep(10)

        # Update the VM machine type to e2-micro
        update_machine_type_result = update_machine_type(request, 'e2-micro')

        # Add the update result to the response
        result["update_machine_type_result"] = update_machine_type_result

        # Sleep for a few seconds to allow the machine type update to take effect
        time.sleep(10)

        # Start the VM
        start_vm_result = start_vm(request)

        # Add the start result to the response
        result["start_vm_result"] = start_vm_result

    return result

