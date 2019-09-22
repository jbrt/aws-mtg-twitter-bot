# SQS Queue

module "sqs" {
  source  = "terraform-aws-modules/sqs/aws"
  version = "2.0.0"
  name    = var.queue_name
  tags    = local.tags
}