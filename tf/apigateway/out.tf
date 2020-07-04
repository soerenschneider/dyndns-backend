output "api_arn" {
  value = "${aws_api_gateway_rest_api.dyndns.execution_arn}"
}

output "api_id" {
  value = "${aws_api_gateway_rest_api.dyndns.id}"
}
