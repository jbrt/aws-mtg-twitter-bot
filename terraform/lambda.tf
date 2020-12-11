# Lambda Function & Layer

##########################################
# Creating ZIP files for functions & layer
##########################################

data "archive_file" "layer_zip" {
  type        = "zip"
  source_dir  = "../layer"
  output_path = "layer.zip"
}

data "archive_file" "fetching_card_zip" {
  type        = "zip"
  source_file = "../src/fetching_card.py"
  output_path = "fetching_card.zip"
}

data "archive_file" "publishing_tweet_zip" {
  type        = "zip"
  source_file = "../src/publishing_tweet.py"
  output_path = "publishing_tweet.zip"
}

resource "aws_lambda_layer_version" "lambda_layer" {
  filename            = "layer.zip"
  layer_name          = "MTGBot_BaseLibraryLayer"
  compatible_runtimes = ["python3.8"]
}

##########################################
# Function for fetching MTG card
##########################################

resource "aws_lambda_function" "fetching_card" {
  filename         = "fetching_card.zip"
  source_code_hash = data.archive_file.fetching_card_zip.output_base64sha256
  function_name    = var.lambda_fetching_card_name
  layers           = [aws_lambda_layer_version.lambda_layer.arn]
  role             = aws_iam_role.fetching_card_role.arn
  description      = "Extract one random card from MTG API and store it"
  handler          = "fetching_card.lambda_handler"
  runtime          = "python3.8"
  timeout          = var.lambda_timeout

  environment {
    variables = {
      BUCKET_NAME = var.bucket_name
      QUEUE_URL   = module.sqs.this_sqs_queue_id
    }
  }

  tags = local.tags
}

##########################################
# Function for publishing tweet & Trigger
##########################################

resource "aws_lambda_function" "publishing_tweet" {
  filename         = "publishing_tweet.zip"
  source_code_hash = data.archive_file.publishing_tweet_zip.output_base64sha256
  function_name    = var.lambda_publishing_tweet_name
  layers           = [aws_lambda_layer_version.lambda_layer.arn]
  role             = aws_iam_role.publishing_tweet_role.arn
  description      = "Send a tweet talking about a MTG card"
  handler          = "publishing_tweet.lambda_handler"
  runtime          = "python3.8"
  timeout          = var.lambda_timeout

  environment {
    variables = {
      BUCKET_NAME         = var.bucket_name
      QUEUE_URL           = module.sqs.this_sqs_queue_id
      CONSUMER_KEY        = aws_ssm_parameter.consumer_key.name
      CONSUMER_SECRET     = aws_ssm_parameter.consumer_secret.name
      ACCESS_TOKEN        = aws_ssm_parameter.access_token.name
      ACCESS_TOKEN_SECRET = aws_ssm_parameter.access_token_secret.name
    }
  }

  tags = local.tags
}

resource "aws_lambda_event_source_mapping" "event_source_mapping" {
  batch_size       = 1
  event_source_arn = module.sqs.this_sqs_queue_arn
  enabled          = true
  function_name    = aws_lambda_function.publishing_tweet.arn
}
