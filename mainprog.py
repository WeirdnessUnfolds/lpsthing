import requests
import json
import os

def make_http_request(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("An error occurred while making the HTTP request:", e)
        return {}

def save_data_to_file(data, filename):
    with open(filename, "w", encoding="utf-8-sig") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def check_file_existence(filename):
    if os.path.exists(filename):
        print("File exists")
    else:
        print("File does not exist")

def get_route_list(data):
    route_list = []
    for item in data:
        for route in item['routes']:
            cells = route['name'].split('|')
            if len(cells) == 1:
                route_list.append(cells[0].strip())
            elif not any(char.isalpha() and ord(char) < 128 for char in cells[0]):
                route_list.append(cells[1].strip())
            else:
                route_list.append(cells[0].strip())
    return route_list

def get_station_list(data):
    station_list = []
    station_data = data[0]['stations'].items()
    for key, value in station_data:
            station_list.append(value['name'])
    return station_list



def get_station_id_name_map(data):
    station_id_name_map = {}
    for x, z in get_station_pos_map(data).items():
        for station_id, station_info in data[0]['stations'].items():
            if station_info['x'] == x and station_info['z'] == z:
                station_id_name_map[station_id] = station_info['name']
    return station_id_name_map

def get_station_pos_map(data):
    station_pos_map = {}
    station_x_z_map = {}
    for station_id, station_info in data[0]['stations'].items():
        station_x_z_map[station_info['x']] = station_info['z']


    return station_x_z_map


def get_route_stations(data):
    station_id_name_map = get_station_id_name_map(data)
    route_stations = {}
    for item in data:
        for route in item['routes']:
            cells = route['name'].split('|')
            if len(cells) == 1:
                route_name = cells[0].strip()
            elif not any(char.isalpha() and ord(char) < 128 for char in cells[0]):
                route_name = cells[1].strip()
            else:
                route_name = cells[0].strip()

            if route_name not in route_stations:
                route_stations[route_name] = []

            for station_id in route['stations']:
                if station_id.split('_', 1)[0] in station_id_name_map:
                    route_stations[route_name].append(station_id_name_map[station_id.split('_', 1)[0]])



    # Remove duplicate entries from route_stations
    for route, stations in route_stations.items():
        route_stations[route] = list(set(stations))

    # Remove routes with no stations
    route_stations = {route: stations for route, stations in route_stations.items() if stations}

    return route_stations

def get_total_stations(data):
    return len(get_station_pos_map(data))

def get_station_map(station_data):
    station_map = {}
    for i in range(len(station_data) - 1):
        for key in station_data[i]:
            station_map[key] = station_data[i][key]['name']
    return station_map

def get_visited_stations():
    visited_stations = set()
    if os.path.exists("save_data.json"):
        with open("save_data.json", "r") as save_file:
            visited_stations = set(json.load(save_file))
    return visited_stations

def save_visited_stations(visited_stations):
    with open("save_data.json", "w") as save_file:
        json.dump(list(visited_stations), save_file)

def main():
    url = "https://letsplay.minecrafttransitrailway.com/system-map/data"
    data = make_http_request(url)
    save_data_to_file(data, "mapdata.json")
    check_file_existence("save_data.json")
    route_list = get_route_list(data)
    station_list = get_station_list(data)
    print("Total amount of stations:", get_total_stations(data))
    visited_stations = get_visited_stations()
    route_stations = get_route_stations(data)
    while True:

        station_name = input("Enter the name of a station you have visited (or 'q' to quit. To see the progress of all lines, press 'l'.): ").lower()
        if station_name == 'q':
            break
        elif station_name == 'l':
            # for station_list, idx in route_stations.values():
            print(route_stations.items())
            for route, stations in route_stations.items():
                visited_stations_in_route = visited_stations.intersection(stations)
                visited_percentage = len(visited_stations_in_route) / len(stations) * 100
                if visited_percentage == 100:
                    print(f"{route}:  COMPLETE")
                print(f"{route}: {len(visited_stations_in_route)} out of {len(stations)} stations visited ({visited_percentage:.2f}%)")
            print(f"Completed lines:" + ", ".join(route for route, stations in route_stations.items() if len(visited_stations.intersection(stations)) == len(stations)))
        else:
            matching_stations = []
            for name in station_list:
                if station_name in name.lower():
                    matching_stations.append(name)
            if len(matching_stations) == 0:
                print("No station with that name exists.")
            else:
                print("Stations found:")
            for i, station in enumerate(matching_stations):
                print(f"{i+1}. {station}")
            print("Enter 'b' to go back to the main menu.")
            choice = input("Enter the number of the station you have visited: ")
            if choice == 'b':
                continue
            elif choice.isdigit() and 1 <= int(choice) <= len(matching_stations):
                visited_stations.add(matching_stations[int(choice)-1])
                visited_percentage = len(visited_stations) / get_total_stations(data) * 100
                print(f"{len(visited_stations)} out of {get_total_stations(data)} stations visited ({visited_percentage:.2f}%)")

            else:
                print("Invalid choice. Please enter a valid number.")
                
    save_visited_stations(visited_stations)
    print("Exiting the program.")

if __name__ == "__main__":
    main()
