# Lambda Function & Layer

data "archive_file" "layer_zip" {
  type        = "zip"
  source_dir  = "../src/layer"
  output_path = "layer.zip"
}

data "archive_file" "fetching_card_zip" {
  type        = "zip"
  source_file = "../src/fetching_card.py"
  output_path = "fetching_card.zip"
}

resource "aws_lambda_layer_version" "lambda_layer" {
  filename            = "layer.zip"
  layer_name          = "MTGBot_BaseLibraryLayer"
  compatible_runtimes = ["python3.7"]
}

resource "aws_lambda_function" "fetching_card" {
  filename         = "fetching_card.zip"
  source_code_hash = data.archive_file.fetching_card_zip.output_base64sha256
  function_name    = var.lambda_fetching_card_name
  layers           = [aws_lambda_layer_version.lambda_layer.arn]
  role             = aws_iam_role.fetching_card_role.arn
  description      = "Extract one random card from MTG API and store it"
  handler          = "fetching_card.lambda_handler"
  runtime          = "python3.7"
  timeout          = var.lambda_timeout

  environment {
    variables = {
      BUCKET_NAME = var.bucket_name
      QUEUE_URL   = module.sqs.this_sqs_queue_id
    }
  }

  tags = local.tags
}