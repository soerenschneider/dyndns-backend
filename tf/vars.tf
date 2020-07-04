variable aws_region {
  default = "us-east-1"
}

variable hostedzone_id {
  description = "ID of the hosted zone to attach the host record to"
  type        = string
}

variable certificate_arn {
  description = "Certificate ARN of the hosted zone"
  type        = string
}

variable host_record {
  description = "The host record FQDN to expose the api gateway on"
  type        = string
}

variable bucket_name {
  description = "The name of the S3 bucket to store the dyndns configuration to"
  default     = "dyndnsbucket"
}

variable file_key {
  description = "The key to the configuration file on the bucket"
  default     = "dyndns/dyndns.json"
}

variable config_file {
  description = "Path on your local fs to the config file to deploy"
  type        = string
}
