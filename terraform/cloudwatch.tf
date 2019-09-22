# CloudWatch LogGroup

resource "aws_cloudwatch_log_group" "fetching_card_loggroup" {
  name              = "/aws/lambda/${var.lambda_fetching_card_name}"
  retention_in_days = var.log_retention
}