# IAM Role

data "aws_iam_policy_document" "fetching_card_rights" {
  statement {
    actions   = ["s3:PutObject"]
    resources = ["arn:aws:s3:::${var.bucket_name}/*", ]
  }

  statement {
    actions   = ["sqs:SendMessage"]
    resources = [module.sqs.this_sqs_queue_arn, ]
  }
}

data "aws_iam_policy_document" "publishing_tweet_rights" {
  statement {
    actions   = ["s3:GetObject", "s3:DeleteObject"]
    resources = ["arn:aws:s3:::${var.bucket_name}/*", ]
  }

  statement {
    actions   = ["sqs:ChangeMessageVisibility", "sqs:DeleteMessage", "sqs:GetQueueAttributes", "sqs:ReceiveMessage"]
    resources = [module.sqs.this_sqs_queue_arn, ]
  }

  statement {
    actions   = ["ssm:GetParameter", "ssm:GetParameters", "ssm:GetParametersByPath"]
    resources = ["*", ]
  }
}

# Generated IAM policy object
resource "aws_iam_policy" "fetching-card-policy" {
  name   = "MTGBot-Fetching-card-righs"
  path   = "/"
  policy = data.aws_iam_policy_document.fetching_card_rights.json
}

resource "aws_iam_policy" "publishing-tweet-policy" {
  name   = "MTGBot-Publishing-tweet-righs"
  path   = "/"
  policy = data.aws_iam_policy_document.publishing_tweet_rights.json
}


#################################
# Role for fetching card function
#################################

resource "aws_iam_role" "fetching_card_role" {
  name = "${var.lambda_fetching_card_name}_role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF

  tags = local.tags
}

resource "aws_iam_role_policy_attachment" "fetching-card-policy-attach" {
  for_each = toset([
    "arn:aws:iam::aws:policy/AWSLambdaBasicExecutionRole",
    "arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess",
    aws_iam_policy.fetching-card-policy.arn
  ])

  role       = aws_iam_role.fetching_card_role.name
  policy_arn = each.value
}

#################################
# Role for fetching card function
#################################

resource "aws_iam_role" "publishing_tweet_role" {
  name = "${var.lambda_publishing_tweet_name}_role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF

  tags = local.tags
}

resource "aws_iam_role_policy_attachment" "publishing-card-policy-attach" {
  for_each = toset([
    "arn:aws:iam::aws:policy/AWSLambdaBasicExecutionRole",
    "arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess",
    aws_iam_policy.publishing-tweet-policy.arn
  ])

  role       = aws_iam_role.publishing_tweet_role.name
  policy_arn = each.value
}
