# kafka-rebalance-partitions
A quick script to make rebalancing partitions in kafka easier

# Example

    python3 rebalancer-helper.py
    
    Saving topics in ./all-topics-1578092133.json
    generating topic assignment with /opt/kafka/bin/kafka-reassign-partitions.sh --generate --topics-to-move-json-file ./all-topics-1578092133.json --broker-list 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16 --zookeeper prod-zookeeper01.example.com:2181,prod-zookeeper02.example.com:2181,prod-zookeeper03.example.com:2181/kafka_chroot/tango_default
    created ./new-assignments-1578092133.json
    
    == When ready to perform rebalance, run the following ==
    /opt/kafka/bin/kafka-reassign-partitions.sh --execute --reassignment-json-file  ./new-assignments-1578092133.json --zookeeper prod-zookeeper01.example.com:2181,prod-zookeeper02.example.com:2181,prod-zookeeper03.example.com:2181/kafka_chroot/tango_default
    
    
    == Watch the rebalance process with ==
    /opt/kafka/bin/kafka-reassign-partitions.sh --verify --reassignment-json-file  ./new-assignments-1578092133.json --zookeeper prod-zookeeper01.example.com:2181,prod-zookeeper02.example.com:2181,prod-zookeeper03.example.com:2181/kafka_chroot/tango_default


