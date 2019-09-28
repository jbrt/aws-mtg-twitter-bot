# CloudWatch LogGroup

resource "aws_cloudwatch_log_group" "fetching_card_loggroup" {
  name              = "/aws/lambda/${var.lambda_fetching_card_name}"
  retention_in_days = var.log_retention
}

resource "aws_cloudwatch_log_group" "publishing_tweet_loggroup" {
  name              = "/aws/lambda/${var.lambda_publishing_tweet_name}"
  retention_in_days = var.log_retention
}

# CloudWatch Event

resource "aws_cloudwatch_event_rule" "fetch_MTG_card_every_4_hours" {
    name = "fetch_MTG_card_every_4_hours"
    description = "Fires every 4 hours"
    schedule_expression = "rate(4 hours)"
}

resource "aws_cloudwatch_event_target" "check_foo_every_five_minutes" {
    rule = aws_cloudwatch_event_rule.fetch_MTG_card_every_4_hours.name
    target_id = "lambda_fetching_card_mtg"
    arn = aws_lambda_function.fetching_card.arn
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_fetching_card" {
    statement_id = "AllowExecutionFromCloudWatch"
    action = "lambda:InvokeFunction"
    function_name = aws_lambda_function.fetching_card.function_name
    principal = "events.amazonaws.com"
    source_arn = aws_cloudwatch_event_rule.fetch_MTG_card_every_4_hours.arn
}