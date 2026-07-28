import requests
import json

from config import CONFIG

class PrusaLink:
    def __init__(self, printer_ip, api_key, port):
        self.__printer_ip = printer_ip
        self.__api_key = api_key
        self.__port = port
        self.__base_url = f"http://{self.__printer_ip}:{self.__port}/api"
        self.__headers = {
            "X-Api-Key": self.__api_key
        }
        self.__DEFINITE_STATUS = {
            "IDLE": "Idle",
            "PRINTING": "Printing",
            "PAUSED": "Paused",
            "STOPPED": "Stopped",
            "ATTENTION": "Filament change",
            "FINISHED": "Finished" 
        }

    def printer_version(self):
        try:
            return requests.get(
                    f"{self.__base_url}/version",
                    headers=self.__headers
                ).json()
        
        except Exception as e:
            print(f"Error occurred while fetching printer version: {e}")
            return None

    def printer_bed_temperature(self):
        try:
            return requests.get(
                f"{self.__base_url}/printer",
                headers=self.__headers
            ).json()["telemetry"]["temp-bed"]
        
        except Exception as e:
            print(f"Error occurred while fetching printer bed temperature: {e}")
            return None
        
    def printer_nozzle_temperature(self):
        try:
            return requests.get(
                f"{self.__base_url}/printer",
                headers=self.__headers
            ).json()["telemetry"]["temp-nozzle"]
        
        except Exception as e:
            print(f"Error occurred while fetching printer nozzle temperature: {e}")
            return None
        
    def printer_status(self):
        try:
            r = requests.get(
                f"{self.__base_url}/v1/status",
                headers=self.__headers
            ).json()["printer"]["state"]

            return self.__DEFINITE_STATUS[r]
        
        except Exception as e:
            print(f"Error occurred while fetching printer status: {e}")
            return None
        
    def files_on_storage(self, storage, target_folder):
        try:
            return requests.get(
                f"{self.__base_url}/v1/files/{storage}/{target_folder}",
                headers=self.__headers
            ).json()
        
        except Exception as e:
            print(f"Error occurred while fetching files on SD card: {e}")
            return None
        
    def storages(self):
        try:
            return requests.get(
                f"{self.__base_url}/v1/storage",
                headers=self.__headers
            ).json()
        
        except Exception as e:
            print(f"Error occurred while fetching storage information: {e}")
            return None
        
    def push_gcode_to_storage(self, gcode_file_name, storage, target_folder):
        print("\n")

        if self.file_exists(gcode_file_name, storage, target_folder):
            do_overwrite = input("Overwrite? (y/n): ")
            if do_overwrite != "y":
                print("Chose not to overwrite. If you want to overwrite manually, there is a command for that. Stopping procedure.")
                return None
            else:
                return self.overwrite_gcode_in_storage(gcode_file_name, storage, target_folder)

        try:
            file_path = f"{CONFIG["GCODES-FOLDER"]}/{gcode_file_name}.gcode"
            gcode_data = open(file_path, "r").read()
            gcode_file_path_on_printer = f"{self.__base_url}/v1/files/{storage}/{target_folder + "/" if len(target_folder) > 0 else ""}{gcode_file_name}.gcode"
            print(f"Trying to write '{file_path}' ({len(gcode_data)} B) to '{gcode_file_path_on_printer}'...")
            return requests.put(
                gcode_file_path_on_printer,
                headers={
                    "Accept": "application/json",
                    "X-Api-Key": self.__api_key,
                    "Content-Type": "text/x.gcode"
                },
                data=gcode_data
            )            
    
        except Exception as e:
            print(f"Failed to push gcode to storage: {e}")
            return None
    
    def overwrite_gcode_in_storage(self, gcode_file_name, storage, target_folder):
        try:
            file_path = f"{CONFIG["GCODES-FOLDER"]}/{gcode_file_name}.gcode"
            gcode_data = open(file_path, "r").read()
            gcode_file_path_on_printer = f"{self.__base_url}/v1/files/{storage}/{target_folder + "/" if len(target_folder) > 0 else ""}{gcode_file_name}.gcode"
            print(f"Trying to replace '{file_path}' ({len(gcode_data)} B) to '{gcode_file_path_on_printer}'...")
            return requests.put(
                gcode_file_path_on_printer,
                headers={
                    "Accept": "application/json",
                    "X-Api-Key": self.__api_key,
                    "Content-Type": "text/x.gcode",
                    "Overwrite": "?1"
                },
                data=gcode_data
            )
        except Exception as e:
            print(f"Failed to overwrite file: {e}")
            return None

    def file_exists(self, gcode_file_name, storage, target_folder):
        gcode_file_path_on_printer = f"{self.__base_url}/v1/files/{storage}/{target_folder + "/" if len(target_folder) > 0 else ""}{gcode_file_name}.gcode"
        try:
            r = requests.head(
                gcode_file_path_on_printer,
                headers=self.__headers
            )

            return r.status_code == 200
        
        except Exception as e:
            print(f"Failed to check wether file '{gcode_file_path_on_printer}' exists: {e}")
            return None

    def start_printing_from_storage(self, gcode_file_name, storage, target_folder):
        gcode_file_path_on_printer = f"{self.__base_url}/v1/files/{storage}/{target_folder + "/" if len(target_folder) > 0 else ""}{gcode_file_name}.gcode"
        file_exists_check = self.file_exists(gcode_file_name, storage, target_folder)

        if not file_exists_check or file_exists_check == None:
            print(f"File '{gcode_file_path_on_printer}' does not exist! There is a command for pushing gcode files to storage.")
            return
        
        try:
            return requests.post(
                gcode_file_path_on_printer,
                headers=self.__headers,
                data=json.dumps(
                    {
                        "command": "start"
                    }
                )
            )
        except Exception as e:
            print(f"Failed to start printing from storage: {e}")
            return None
        
    def get_job(self):
        try:
            return requests.get(
                f"{self.__base_url}/v1/job",
                headers=self.__headers
            ).json()
        
        except Exception as e:
            print(f"Failed to get job: {e}")
            return None

    def stop_print(self):
        if self.printer_status() not in ["Printing", "Paused"]:
            print("Can not stop printing; the printer is not printing.")
            return
        
        job = self.get_job()
        if job == None:
            return None
        
        try:
            id = str(job["id"])
            return requests.delete(
                f"{self.__base_url}/v1/job/{id}",
                headers=self.__headers
            )
        
        except Exception as e:
            print(f"Failed to stop print: {e}")
            return None
        
    def pause_print(self):
        if self.printer_status() != "Printing":
            print("Can not pause printing; the printer is not printing.")
            return
        
        job = self.get_job()
        if job == None:
            return None
        
        try:
            id = str(job["id"])
            return requests.put(
                f"{self.__base_url}/v1/job/{id}/pause",
                headers=self.__headers
            )
        
        except Exception as e:
            print(f"Failed to pause print: {e}")
            return None
        
    def resume_print(self):
        if self.printer_status() != "Paused":
            print("Can not resume printing; the printer is not paused.")
            return
        
        job = self.get_job()
        if job == None:
            return None
        
        try:
            id = str(job["id"])
            return requests.put(
                f"{self.__base_url}/v1/job/{id}/resume",
                headers=self.__headers
            )
        
        except Exception as e:
            print(f"Failed to resume print: {e}")
            return None


        
