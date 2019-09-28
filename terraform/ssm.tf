# Store secrets in Parameter Store

resource "aws_ssm_parameter" "consumer_key" {
  name        = "/twitter/credentials/consumer_key"
  description = "The parameter description"
  type        = "SecureString"
  value       = var.consumer_key
  tags        = local.tags
}

resource "aws_ssm_parameter" "consumer_secret" {
  name        = "/twitter/credentials/consumer_secret"
  description = "The parameter description"
  type        = "SecureString"
  value       = var.consumer_secret
  tags        = local.tags
}

resource "aws_ssm_parameter" "access_token" {
  name        = "/twitter/credentials/access_token"
  description = "The parameter description"
  type        = "SecureString"
  value       = var.access_token
  tags        = local.tags
}

resource "aws_ssm_parameter" "access_token_secret" {
  name        = "/twitter/credentials/access_token_secret"
  description = "The parameter description"
  type        = "SecureString"
  value       = var.access_token_secret
  tags        = local.tags
}
