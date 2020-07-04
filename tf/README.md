# Vars

# Configuration file

```json
{
    "host1.yourdomain.tld.": {
        "route_53_zone_id" : "zoneid",
	    "route_53_record_ttl": 900,
	    "route_53_record_type": "A",
        "shared_secret": "very.secret",
	    "aws_region": "us-west-1"
    },
    "host2.yourdomain.tld.": {
        "route_53_zone_id" : "zoneid",
    	"route_53_record_ttl": 300,
	    "route_53_record_type": "A",
        "shared_secret": "another.secret",
    	"aws_region": "us-west-1"
    }
}

```
