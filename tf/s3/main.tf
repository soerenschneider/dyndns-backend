resource "aws_s3_bucket" "bucket" {
  bucket        = var.bucket_name
  region        = var.region
  acl           = "private"
  force_destroy = true
}

resource "aws_s3_bucket_object" "file_upload" {
  bucket = aws_s3_bucket.bucket.id
  key    = var.file_key
  source = var.config_file
}
