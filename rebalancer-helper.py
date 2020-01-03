import subprocess
import json
import time

kafka_server_properties_path = "/opt/kafka/config/server.properties"

t = str(int(time.time()))

all_topics_out_path = './all-topics-' + t + '.json'
current_assignments_path = './current-assignments-' + t + '.json'
new_assignments_path = './new-assignments-' + t + '.json'

def get_zookeeper_connect():
    connect_prefix = 'zookeeper.connect='
    with open(kafka_server_properties_path, 'r') as fp:
        for l in fp:
            l = l.strip()
            if l.startswith(connect_prefix):
                return l[len(connect_prefix):].strip()

def get_zookeeper_host(zk_connect):
    return zk_connect.split(',')[0].split(':')[0]

def get_zookeeper_chroot(zk_connect):
    n = zk_connect.find('/')
    return zk_connect[n:]

def get_broker_ids(zookeeper_host, zookeeper_chroot):
    cmd = 'ssh ' + zookeeper_host + ' zookeepercli --servers localhost -c ls ' + zookeeper_chroot + '/brokers/ids'
    brokers = subprocess.check_output(cmd, shell=True).decode('ascii').split()
    return ','.join(str(x) for x in sorted(int(x) for x in brokers))

def get_all_under_replicated_topics(zk_connect):
    cmd = '/opt/kafka/bin/kafka-topics.sh --zookeeper ' + zk_connect + ' --describe --under-replicated-partitions'
    out = subprocess.check_output(cmd, shell=True).decode('ascii')
    topics = set()
    for l in out.splitlines():
        l = l.strip()
        if l.startswith('Topic: '):
            topic = l.split()[1]
            topics.add(topic)
    return list(topics)

def save_all_topics(topics, path):
    with open(path, 'w') as fp:
        fp.write(json.dumps({
            "version": 1,
            "topics": [{"topic": x} for x in topics]
            }))

zk = get_zookeeper_connect()
zk_host = get_zookeeper_host(zk)
zk_chroot = get_zookeeper_chroot(zk)
broker_ids = get_broker_ids(zk_host, zk_chroot)
topics = get_all_under_replicated_topics(zk)

print('Saving topics in ' + all_topics_out_path)
save_all_topics(topics, all_topics_out_path)

cmd = '/opt/kafka/bin/kafka-reassign-partitions.sh --generate --topics-to-move-json-file ' + all_topics_out_path + ' --broker-list ' + broker_ids + ' --zookeeper ' + zk
print('generating topic assignment with ' + cmd)
out = subprocess.check_output(cmd, shell=True).decode('ascii').splitlines()

assert out[0] == 'Current partition replica assignment'
assert out[3] == 'Proposed partition reassignment configuration'

with open(current_assignments_path, 'w') as fp:
    fp.write(out[1])

with open(new_assignments_path, 'w') as fp:
    fp.write(out[4])

print('created ' + new_assignments_path)
print('\n== When ready to perform rebalance, run the following ==')
print('/opt/kafka/bin/kafka-reassign-partitions.sh --execute --reassignment-json-file  ' + new_assignments_path + ' --zookeeper ' + zk)
print('')

print('\n== Watch the rebalance process with ==')
print('/opt/kafka/bin/kafka-reassign-partitions.sh --verify --reassignment-json-file  ' + new_assignments_path + ' --zookeeper ' + zk)
print('')

