# SQS Queue

module "sqs" {
  source                     = "terraform-aws-modules/sqs/aws"
  version                    = "2.0.0"
  name                       = var.queue_name
  visibility_timeout_seconds = var.lambda_timeout
  tags                       = local.tags
}