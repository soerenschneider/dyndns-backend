variable "lambda_name" {
  description = "The name of the lambda function"
  type        = string
}

variable "lambda_invoke" {
  description = "ARN of the lambda invoke"
  type        = string
}

variable "region" {
  type = string
}
