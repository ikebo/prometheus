import time
import json
from datetime import datetime
import base64
import requests

def cur_ts():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def decrypt_port(encrypt_port):
    return 65535 - int(int(encrypt_port) / 13)

def swap_arr(arr, l, r):
    arr[l], arr[r] = arr[r], arr[l]

def decrypt_ip(encrypt_ip):
    arr = encrypt_ip.split('.')
    swap_arr(arr, 10, 7)
    swap_arr(arr, 8, 5)
    swap_arr(arr, 2, 4)
    return '.'.join(arr[4:8])

def decrypt_config(encrypt_config):
    estr = base64.b64decode(encrypt_config).decode()
    port, name, method, host, key = estr[len('ss://'):].split(':')
    return name, method, decrypt_ip(host), decrypt_port(port), key

def get_nodes():
    url = "http://smallwings.cc/api/server_list?skt=7mA9gI9D3DO3Pdf1NhtcFOJg0P1OnD"
    res = requests.get(url)
    return [decrypt_config(ns) for ns in res.json()['data']]

def gen_target(hosts, name):
    return {
        "targets": ["{}:9100".format(host) for host in hosts],
        "labels": {
            "job": name,
        }
    }

def refresh_targets():
    targets = []
    for node in get_nodes():
        targets.append(gen_target([node[2]], node[0]))
    targets_json = json.dumps(targets)
    with open("./targets.json", "w") as wf:
        wf.write(targets_json)
    return targets_json

if __name__ == "__main__":
    while True:
        rv = refresh_targets()
        print("{} {}".format(cur_ts(), rv))
        time.sleep(5 * 60)
