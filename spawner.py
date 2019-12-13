import os
import subprocess
import argparse
import socket

cwd = os.getcwd()

parser = argparse.ArgumentParser(
    description='Run redis dockers in cluster mode')
parser.add_argument('-c', '--create', action='store_true',
                    help='create the initial cluster')

parser.add_argument('-e', '--extend', action='store_true',
                    help='extends the initial cluster by adding one node to it')

parser.add_argument('-s', '--stop', action='store_true',
                    help='stops the initial cluster')

parser.add_argument('-n', '--number', type=int,
                    help='number of cluster nodes', default=4)
parser.add_argument('-p', '--port', type=int,
                    help='starting port number', default=7000)

parser.add_argument('--host', type=str,
                    help='address of a node in the cluster')
parser.add_argument('--host-port', type=int,
                    help='port of host node')


args = parser.parse_args()

conf_dir = 'redis-confs'


def get_lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


def clear_conf_dir():
    if not os.path.exists(conf_dir):
        os.makedirs(conf_dir)

    for filename in os.listdir(conf_dir):
        file_path = os.path.join(conf_dir, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
        except Exception as e:
            print('failed to delete {}. reason: {}'.format(file_path, e))


def create_redis_conf(port):
    file = open('redis.conf', 'r')
    conf_data = file.read()
    file.close()
    new_conf = conf_data.replace('port-number', port)
    file = open('{}/redis-{}.conf'.format(conf_dir, port), 'w')
    file.write(new_conf)
    file.close()


def create_container(container_id, port):
    create_redis_conf(str(port))
    subprocess.run(['docker', 'create', '--name', 'redis-{}'.format(
        container_id), '--rm', '--net=host', 'redis', 'redis-server', '/redis.conf'], stdout=subprocess.DEVNULL)
    subprocess.run(['docker', 'cp', '{}/redis-{}.conf'.format(conf_dir,
                                                              port), 'redis-{}:/redis.conf'.format(container_id)], stdout=subprocess.DEVNULL)


def start_container(n):
    return subprocess.run(
        ['docker', 'start', 'redis-{}'.format(n)], stdout=subprocess.DEVNULL)


def create_cluster(n):
    nodes = []
    ip = get_lan_ip()
    for i in range(1, n + 1):
        nodes.append('{}:{}'.format(ip, args.port + i))
    subprocess.run(['docker', 'run', '--rm', '--net=host', 'redis', 'redis-cli',
                    '--cluster', 'create'] + nodes + ['--cluster-replicas', '0', '--cluster-yes'], stdout=subprocess.DEVNULL)


def extend_cluster(host, host_port, ip, port):
    subprocess.run(['docker', 'run', '--rm', '--net=host', 'redis', 'redis-cli',
                    '--cluster', 'add-node', '{}:{}'.format(ip, port), '{}:{}'.format(host, host_port), '--cluster-slave'], stdout=subprocess.DEVNULL)


def create(n):
    clear_conf_dir()
    ip = get_lan_ip()
    processes = []
    for i in range(1, n + 1):
        port = args.port + i
        print('creating configuration file for redis-{} on {}:{}'.format(i, ip, port))
        create_container(i, port)
        print('starting container redis-{}'.format(i))
        processes.append(start_container(i))
    print('creating a cluster with {} nodes'.format(n))
    create_cluster(n)


def extend():
    if args.host is None or args.host_port is None:
        print('you need to specify host and host-port using --host and --host-port')
        exit(1)

    files = os.listdir(conf_dir)
    port = args.port + 1
    if (len(files) > 0):
        latest_file = sorted(files)[-1]
        if latest_file[:6] != 'redis-' or latest_file[-5:] != '.conf':
            print(
                'please don\'t touch redis-confs folder, remove the folder and try again')
            exit(1)
        port = int(latest_file[6:-5]) + 1
    container_id = port - args.port
    ip = get_lan_ip()
    print('creating redis-{} container on {}:{}'.format(container_id, ip, port))
    create_container(container_id, port)
    start_container(container_id)
    extend_cluster(args.host, args.host_port, ip, port)


def stop():
    count = len(os.listdir(conf_dir))
    print('going to stop {} nodes'.format(count))
    for i in range(1, count + 1):
        print('stopping container redis-{}'.format(i))
        subprocess.run(['docker', 'stop', 'redis-{}'.format(i)],
                       stdout=subprocess.DEVNULL)
    clear_conf_dir()


if __name__ == '__main__':
    if args.create:
        create(args.number)
    elif args.stop:
        stop()
    elif args.extend:
        extend()
