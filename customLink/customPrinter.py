from customLink.customPrusaLink import PrusaLink

def connect_to_printer(printer_ip, api_key, port=80):
    print("Connecting to printer...")

    printer = PrusaLink(printer_ip, api_key, port)

    try:
        print("Connected to printer!")
        print(f"Printer Version: {printer.printer_version()["api"]}")
        return printer
    except Exception as e:
        print(f"Failed to connect to printer: {e}")
        return None


def statistics(cPrinter):
    print(f"Bed Temperature: {cPrinter.printer_bed_temperature()}°C")
    print(f"Nozzle Temperature: {cPrinter.printer_nozzle_temperature()}°C")
    print(f"Printer Status: {cPrinter.printer_status()}")

def dir(cPrinter, storage, folder):
    directory_items = cPrinter.files_on_storage(storage, target_folder=folder)["children"]
    
    if len(directory_items) == 0:
        print("\n")
        print(f"No items at '{storage}/{folder}'")
        return

    print("\n")
    print(f"                ({storage}/{folder})                   ")
    print("\n")


    final_str = []
    latest_folder_index = 0

    for item in directory_items:
        item_type = item["type"]
        item_name = item["name"]

        if item_type == "FOLDER":
            final_str.insert(latest_folder_index, f"-> {item_name}")
            latest_folder_index += 1

        elif item_type == "PRINT_FILE":
            final_str.append(f"- {item_name}")
        else:
            final_str.append(f"(No item type found for '{item_name}')")


    for s in final_str:
        print(s)

def display_storage(cPrinter):
    storage = cPrinter.storages()

    for i in storage["storage_list"]:
        storage_type = i["type"]
        storage_path = i["path"]
        storage_is_read_only = i["read_only"]

        print(f"Storage type: {storage_type}")
        print(f"Storage path: {storage_path}")
        print(f"Storage is read only: {storage_is_read_only}")
        print("-------------\n")

def push_gcode_to_storage(cPrinter, gcode_file_name, storage, target_folder):
    status = cPrinter.push_gcode_to_storage(gcode_file_name, storage, target_folder)
    print(f"GCode push to '{storage}/{target_folder}': {status}")

    if status != None and status.status_code != 201:
        print(status.content.decode())
    
    if status != None and status.status_code == 201:
        print("Successfully pushed gcode to storage!")

def overwrite_gcode_in_storage(cPrinter, gcode_file_name, storage, target_folder):
    status = cPrinter.overwrite_gcode_in_storage(gcode_file_name, storage, target_folder)
    print(f"GCode overwrite to '{storage}/{target_folder}': {status}")

    if status != None and status.status_code != 201:
        print(status.content.decode())
    
    if status != None and status.status_code == 201:
        print("Successfully overwrote gcode in storage!")

def file_exists(cPrinter, gcode_file_name, storage, target_folder):
    print("\n")

    exists = cPrinter.file_exists(gcode_file_name, storage, target_folder)

    if exists == None:
        return
    
    if exists:
        print(f"File '{storage}/{target_folder + "/" if len(target_folder) > 0 else ""}{gcode_file_name}.gcode' already exists!")
    else:
        print(f"File '{storage}/{target_folder + "/" if len(target_folder) > 0 else ""}{gcode_file_name}.gcode' does not exists yet...")
    
def start_print_from_storage(cPrinter, gcode_file_name, storage, target_folder):
    print("\n")

    #204
    print_start_status = cPrinter.start_printing_from_storage(gcode_file_name, storage, target_folder)
    print(f"Start to print from storage: {print_start_status}")

    if print_start_status != None and print_start_status.status_code == 204:
        print("Print started sccessfully!")
    

def stop_print(cPrinter):
    status = cPrinter.stop_print()
    if status == None:
        print("There was no print to be stopped or it failed...")
    else:
        print("Print stopped successfully!")

def pause_print(cPrinter):
    status = cPrinter.pause_print()
    if status == None:
        print("There was no print to be paused or it failed...")
    else:
        print("Print paused successfully!")

def resume_print(cPrinter):
    status = cPrinter.resume_print()
    if status == None:
        print("There was no print to be resumed or it failed...")
    else:
        print("Print resumed successfully!")