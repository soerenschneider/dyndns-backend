variable api_id {
  type        = string
  description = "API Gateway REST API ID."
}

variable host_record {
  type        = string
  description = "Custom domain name."
}

variable certificate_arn {
  type        = string
  description = "ACM certificate ARN."
}

variable route53_zone_id {
  type        = string
  description = "Route53 hosted zone ID."
}
