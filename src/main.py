#!/usr/bin/env python3

import json
import re
import boto3
import hashlib
import os
import logging

# tunables
config_s3_region = os.getenv("S3_REGION", "us-west-1")
config_s3_bucket = os.getenv("S3_BUCKET")
config_s3_key = os.getenv("S3_KEY", "dyndns/dyndns.json")

# re-use clients
S3_CLIENT = None
ROUTE53_CLIENT = None

# add logger
log = logging.getLogger()
log.setLevel(logging.INFO)


def is_valid_ipv4(ip):
    m = re.match(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$", ip)
    return bool(m) and all(map(lambda n: 0 <= int(n) <= 255, m.groups()))


def read_s3_config():
    global S3_CLIENT
    if not S3_CLIENT:
        log.info("Re-generating s3 client")
        S3_CLIENT = boto3.client('s3', config_s3_region,)

    log.info("Downloading config file")
    tmp_file = '/tmp/dyndns.json'
    S3_CLIENT.download_file(
        config_s3_bucket,
        config_s3_key,
        tmp_file
    )
    
    log.info("Decoding config file")
    conf = None
    with open(tmp_file) as json_config:
        conf = json.loads(json_config.read())

    return conf
    
def check_request(validation_hash, dns_record, public_ip, config):
    if not dns_record in config:
        log.warning("No such record in config: %s", dns_record)
        raise Exception("Bad request")

    shared_secret = config[dns_record]['shared_secret']

    hashable = "{}{}{}".format(dns_record, public_ip, shared_secret)
    calculated_hash = hashlib.sha256(hashable.encode()).hexdigest()
    if not calculated_hash == validation_hash:
        log.warn("Calculated hash '%s' mismatches requests hash '%s'", calculated_hash, validation_hash)
        raise Exception("Bad request")

def upsert_entry(dns_record, public_ip, route_53_zone_id, ttl=300, type="A"):
    global ROUTE53_CLIENT
    if not ROUTE53_CLIENT:
        log.info("Re-generating route53 client")
        route53_client = boto3.client('route53', region_name=config_s3_region)

    log.info("Upserting dns record %s to %s", dns_record, public_ip)
    change_route53_record_set = route53_client.change_resource_record_sets(
        HostedZoneId=route_53_zone_id,
        ChangeBatch={
            'Changes': [ 
                {
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': dns_record,
                        'Type': type,
                        'TTL': ttl,
                        'ResourceRecords': [
                            {
                                'Value': public_ip
                            }
                        ]
                    }
                }
            ]
        }
    )

def handler(event, context):
    if not config_s3_bucket:
        return {"statusCode": 500, "body": "Configuration error"}

    ip = "UNKNOWN"
    try:
        ip = event['requestContext']['identity']['sourceIp']
        body = message = json.loads(event['body'])
        validation_hash = body['validation_hash']
        dns_record = body['dns_record']
        public_ip = body['public_ip']
    except KeyError:
        log.warn("Client '%s' did not provide all information", ip)
        return {
            "statusCode": 400,
            "body": "Bad request: Provide 'validation_hash', 'dns_record' and 'public_ip'"
        }

    log.info("Client %s wants to update record '%s' to %s", ip, dns_record, public_ip)
    try:
        config = read_s3_config()
        check_request(validation_hash, dns_record, public_ip, config)
        upsert_entry(dns_record, public_ip, config[dns_record]['route_53_zone_id'])
    except Exception as e:
        log.error("Encountered error: %s", e)
        return {
            "statusCode": 500,
            "body": "Internal error"
        }

    log.info("Successfully executed request, bye")
    return {
        "statusCode": 200,
        "body": "OK"
    }
