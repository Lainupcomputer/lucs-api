from urllib import request


def check_version(server):
    req = request.urlopen(server)
    server_data = req.read().decode('UTF-8')
    return server_data


local_version = "0.1.1"
app_name = "Tilerunner"


if __name__ == "__main__":
    server_address = "http://127.0.0.1:5000/api/v1/"
    organisation = "LainupComputer"
    data = f"?version={local_version}&app={app_name}"
    print(check_version(server_address + organisation + data))
