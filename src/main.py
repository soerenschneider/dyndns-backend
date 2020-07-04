#!/usr/bin/env python3

import json
import re
import boto3
import hashlib
import os

# Tell the script where to find the configuration file.
config_s3_region = os.getenv("S3_REGION", "us-west-1")
config_s3_bucket = os.getenv("S3_BUCKET")
config_s3_key = os.getenv("S3_KEY", "dyndns/dyndns.json")

def is_valid_ipv4(ip):
    m = re.match(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$", ip)
    return bool(m) and all(map(lambda n: 0 <= int(n) <= 255, m.groups()))

def read_s3_config():
    # Define the S3 client.
    s3_client = boto3.client(
        's3',
        config_s3_region,
    )

    # Download the config to /tmp
    tmp_file = '/tmp/dyndns.json'
    s3_client.download_file(
        config_s3_bucket,
        config_s3_key,
        tmp_file
    )
    
    # Open the config and return the json as a dictionary.
    full_config = open(tmp_file).read()
    return(json.loads(full_config))

def is_request_allowed(request, config):
    secret = request['secret']
    entry = request['entry']
    public_ip = request['public_ip']
    
def check_request(validation_hash, dns_record, public_ip, config):
    print(dns_record)
    if not dns_record in config:
        raise Exception("Bad request")

    shared_secret = config[dns_record]['shared_secret']
    
    hashable = "{}{}{}".format(dns_record, public_ip, shared_secret)
    calculated_hash = hashlib.sha256(hashable.encode()).hexdigest()
    if not calculated_hash == validation_hash:
        print("Calculated hash mismatches requests hash")
        raise Exception("Bad request")
        
    print("Upserting {} -> {} using hash '{}'".format(dns_record, public_ip, calculated_hash))

def upsert_entry(dns_record, public_ip, route_53_zone_id, ttl=300, type="A"):
    route53_client = boto3.client('route53', region_name=config_s3_region)
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

    try:
        validation_hash = event['validation_hash']
        dns_record = event['dns_record']
        public_ip = event['public_ip']
    except KeyError:
        return {
            "statusCode": 400,
            "body": "Bad request: Provide 'validation_hash', 'dns_record' and 'public_ip'"
        }
    except:
        return {
            "statusCode": 500,
            "body": "Internal error"
        }

    
    config = read_s3_config()
    check_request(validation_hash, dns_record, public_ip, config)
    upsert_entry(dns_record, public_ip, config[dns_record]['route_53_zone_id'])
    
    return {
        "statusCode": 200,
        "body": "OK"
    }
