# Region

variable "region" {
  description = "Region where all AWS objects will be created"
}

# CloudWatch variables

variable "log_retention" {
  description = "Number of days for log retention"
}

# Lambda functions

variable "lambda_fetching_card_name" {
  description = "Name of the fetching function"
}

variable "lambda_publishing_tweet_name" {
  description = "Name of the publishing function"
}

variable "lambda_timeout" {
  description = "Timeout for Lambda function execution"
  default     = 600
}

# S3 Buckets

variable "bucket_name" {
  description = "Name of the S3 Bucket"
}

# SQS Queue

variable "queue_name" {
  description = "Name of the S3 Bucket"
}

# Secrets for Tweeter
variable "consumer_key" {
  description = "Twitter API credential Consumer key"
}

variable "consumer_secret" {
  description = "Twitter API credential consumer secret"
}

variable "access_token" {
  description = "Twitter API credential access token"
}

variable "access_token_secret" {
  description = "Twitter API credential access token secret"
}

# Tags

locals {
  tags = {
    Terraform   = "true"
    Environment = "dev"
    Project     = "MTG-Twitter-Bot"
  }
}