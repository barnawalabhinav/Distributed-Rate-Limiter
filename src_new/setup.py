import os
import subprocess as sp
import time
from constants import IPS, MASTER_NODE_IP, IN, PORT
# from mrds import MyRedis


def get_redis():
    return MyRedis(IPS)


def setup_redis(rds):
    for red in rds.conns.values():
        print(red)
        red.flushall()
        red.xgroup_create(IN, "worker", id="0", mkstream=True)
        red.set("FileCnt", 0)
        red.set("Finish", 0)


def get_top_words(rds, network_heal=False):
    if network_heal:
        return rds.top(3, True)
    else:
        return rds.top(3, False)


def get_full_name(ip: str) -> str:
    return f'baadalvm@{ip}'


def copy_code(ip: str) -> None:
    print(f"=== Copying code to {ip}")
    full_name = get_full_name(ip)

    # Create the folders and copy all the files
    print("Creating lab folder")
    sp.run(['sshpass', '-p', "987654321", 'ssh', full_name,
           'mkdir -p /home/baadalvm/lab5_sol']).check_returncode()
    sp.run(['sshpass', '-p', "987654321", 'ssh', full_name,
           'rm -rf /home/baadalvm/lab5_sol/*']).check_returncode()

    print("Copying code")
    mydir = os.path.dirname(os.path.realpath(__file__))
    sp.run(['sshpass', '-p', "987654321", 'scp', '-r', mydir,
           f'{full_name}:/home/baadalvm/']).check_returncode()


def start_client(ip: str) -> None:
    print(f"=== Starting client on {ip}")
    full_name = get_full_name(ip)
    sp.Popen(['sshpass', '-p', "987654321", 'ssh', full_name,
             f"cd /home/baadalvm/lab5_sol; cat mylib.lua | redis-cli -h {ip} -a pass -x FUNCTION LOAD REPLACE; python3 client.py &"])

    print(f"SSH DONE! on {ip}")


if __name__ == "__main__":
    # Network Partition Setup
    current_ip = {MASTER_NODE_IP}
    faulty_node_ips = list(set(IPS).difference(current_ip))

    for ip in faulty_node_ips:
        copy_code(ip)

    isolate_command = \
        f'''sudo iptables -I INPUT 1 -s {faulty_node_ips[0]} -p tcp --dport {PORT} -j DROP; 
    sudo iptables -I OUTPUT 1 -d {faulty_node_ips[0]} -p tcp --dport {PORT} -j DROP;'''

    heal_command = \
        f'''sudo iptables -D INPUT -s {faulty_node_ips[0]} -p tcp --dport {PORT} -j DROP; 
    sudo iptables -D OUTPUT -d {faulty_node_ips[0]} -p tcp --dport {PORT} -j DROP;'''

    sp.run([heal_command], shell=True, text=True, input='DUMMY\n')

    # System Cleanup
    rds = get_redis()
    setup_redis(rds)

    sp.run([isolate_command], shell=True, text=True, input='DUMMY\n')

    for ip in IPS:
        start_client(ip)

    print(get_top_words(rds, network_heal=False))
    # time.sleep(160)

    sp.run([heal_command], shell=True, text=True, input='DUMMY\n')

    print(get_top_words(rds, network_heal=True))
