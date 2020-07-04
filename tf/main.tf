provider aws {
  region  = var.aws_region
  version = "~> 2.68"
}

provider archive {
  version = "~> 1.3"
}


data "aws_caller_identity" "current" {}

module bucket {
  source      = "./s3"
  region      = var.aws_region
  bucket_name = var.bucket_name
  file_key    = var.file_key
  config_file = var.config_file
}

module lambda {
  source        = "./lambda"
  name          = "updateHostRecord"
  runtime       = "python3.8"
  handler       = "main.handler"
  hostedzone_id = var.hostedzone_id
  api_arn       = module.apigateway.api_arn
  region        = var.aws_region
  file_key      = var.file_key
  bucket_name   = var.bucket_name
}

module apigateway {
  source        = "./apigateway"
  lambda_name   = module.lambda.name
  lambda_invoke = module.lambda.invoke_arn
  region        = var.aws_region
}

module route53 {
  source          = "./route53"
  api_id          = module.apigateway.api_id
  host_record     = var.host_record
  certificate_arn = var.certificate_arn
  route53_zone_id = var.hostedzone_id
}
