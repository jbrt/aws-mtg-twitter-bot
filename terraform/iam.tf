# IAM Role

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

# Attaching managed policy for CloudWatch Logging
data "aws_iam_policy" "AWSLambdaBasicExecutionRole" {
  arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Rights for S3
resource "aws_iam_policy" "S3PutObjectPolicy" {
  name = "${var.lambda_fetching_card_name}-S3PutObject"
  description = "Authorize Lambda function for put S3 objects"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Stmt1569162938455",
      "Action": [
        "s3:PutObject"
      ],
      "Effect": "Allow",
      "Resource": "arn:aws:s3:::${var.bucket_name}/*"
    }
  ]
}
EOF
}

# Rights for SQS
resource "aws_iam_policy" "SQSSendMessagePolicy" {
  name = "${var.lambda_fetching_card_name}-SQSSendMessage"
  description = "Authorize Lambda function for put S3 objects"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Stmt1569163258326",
      "Action": [
        "sqs:SendMessage"
      ],
      "Effect": "Allow",
      "Resource": "${module.sqs.this_sqs_queue_arn}"
    }
  ]
}
EOF
}

# Attach policies
resource "aws_iam_role_policy_attachment" "sqs-sendmessage--role-policy-attach" {
  role       = aws_iam_role.fetching_card_role.name
  policy_arn = aws_iam_policy.SQSSendMessagePolicy.arn
}

resource "aws_iam_role_policy_attachment" "s3bucket-role-policy-attach" {
  role       = aws_iam_role.fetching_card_role.name
  policy_arn = aws_iam_policy.S3PutObjectPolicy.arn
}

resource "aws_iam_role_policy_attachment" "lambda-basic-exec-role-policy-attach" {
  role       = aws_iam_role.fetching_card_role.name
  policy_arn = data.aws_iam_policy.AWSLambdaBasicExecutionRole.arn
}