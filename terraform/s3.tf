# S3 Bucket

module "s3-bucket" {
  source        = "terraform-aws-modules/s3-bucket/aws"
  version       = "0.1.0"
  bucket        = var.bucket_name
  force_destroy = "true"
  acl           = "private"
}