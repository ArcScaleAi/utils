import json
import os

folder_path = "D:\Image\JSON_SEPARATE\JSON_Files"

details_found = []
no_details_found = []
error_files = []

def read_json_files(folder_path):
    data = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, 'r') as file:
                    file_data = json.load(file)
                    data.extend(file_data)
            except json.JSONDecodeError as e:
                error_message = f"Error decoding JSON in file {filename}: {e}"
                print(error_message)
                error_files.append(error_message)
            except Exception as e:
                error_message = f"Unexpected error with file {filename}: {e}"
                print(error_message)
                error_files.append(error_message)
    return data

data = read_json_files(folder_path)

for item in data:
    for key, values in item.items():
        if values == ["No fashion details found"]:
            no_details_found.append({key: values})
        else:
            filtered_values = [v.split('=')[0] for v in values if int(v.split('=')[1][:-1]) >= 90]
            if filtered_values:
                details_found.append({key: filtered_values})

with open('details_found.json', 'w') as details_file:
    json.dump(details_found, details_file, indent=4)

with open('no_details_found.json', 'w') as no_details_file:
    json.dump(no_details_found, no_details_file, indent=4)

with open('error_log.txt', 'w') as error_file:
    for error in error_files:
        error_file.write(f"{error}\n")

print("Processing complete. Check 'details_found.json', 'no_details_found.json', and 'error_log.txt' for results.")
