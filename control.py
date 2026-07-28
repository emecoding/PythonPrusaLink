import customLink.customPrinter as cPrinter
from config import CONFIG, read_file_into_json

def display_commands(printer):
    global COMMANDS_FILE_DATA

    print("Available commands:")
    for command in COMMANDS_FILE_DATA.keys():
        shortcut = COMMANDS_FILE_DATA[command]["shortcut"]
        print(f"- {command}{f", {shortcut}" if shortcut != None else ""}")

def quit(printer):
    global CONTROLLING
    CONTROLLING = False

CONTROLLING = True

COMMANDS_FILE_DATA = read_file_into_json("commands.json")


def execute_command_json(printer, command):
    for command_name in COMMANDS_FILE_DATA.keys():
        if command_name != command and COMMANDS_FILE_DATA[command_name]["shortcut"] != command:
            continue

        command_data = COMMANDS_FILE_DATA[command_name]
        
        arg_values = []
        if command_data["args"] != None:
            print("\n")
            for arg in command_data["args"]:
                value = input(f"Enter value for '{arg}': ").strip()
                arg_values.append(value)
            print("\n")

        if command_data["function_loc"] == "globals":
            if command_data["function_name"] not in globals().keys():
                print(f"No such function with name '{command_data["function_name"]}' found from '{command_data["function_loc"]}'")
                return
            
            print("\n")
            globals()[command_data["function_name"]](printer, *arg_values)
            print("\n")

        elif command_data["function_loc"] == "cPrinter":
            print("\n")
            getattr(cPrinter, command_data["function_name"])(printer, *arg_values)
            print("\n")

        else:
            print(f"Undefined function_loc '{command_data["function_loc"]}' for '{command_name}'...")

        return

    print(f"Command '{command}' not found. Type 'help' to see available commands.")
    return None


def main():
    global CONTROLLING

    printer_instance = cPrinter.connect_to_printer(
        CONFIG["PRINTER-IP"],
        CONFIG["API-KEY"]
    )

    if not printer_instance:
        quit(printer_instance)

    while CONTROLLING:
        command = input("Enter command (type 'help' for available commands): ").strip()

        execute_command_json(printer_instance, command)

    print("Exiting the program.")  

if __name__ == "__main__":
    main()