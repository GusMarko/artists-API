# prikupljanje podataka vec ostojecih resursa


data "aws_s3_bucket" "artists" {
  bucket = "project1-artists-${var.env}"
}

data "aws_ssm_parameter" "priv_sub_id" {
  name = "/vpc/dev/private_subnet/id"
}

data "aws_ssm_parameter" "vpc_id" {
  name = "/vpc/dev/id"
}

data "aws_s3_bucket" "songs" {
  bucket = "project1-songs-${var.env}"
}

# podesavanje saobracaja ka internetu, mozda kasnije propustiti saobracaj od spotifaja

resource "aws_security_group" "main" {

  name        = "project1-artists-api-${var.env}"
  description = "Security groupd for artists lambda"
  vpc_id      = data.aws_ssm_parameter.vpc_id.value

  egress = [
    {
      from_port        = 0
      to_port          = 0
      protocol         = "-1"
      cidr_blocks      = ["0.0.0.0/0"]
      ipv6_cidr_blocks = ["::/0"]
      prefix_list_ids  = []
      security_groups  = []
      description      = "Allow all egress"
      self             = false
    }
  ]
}

# podesavanja lambda role

data "aws_iam_policy_document" "assume_policy" {
  statement {
    effect = "Allow"

    principals {
      identifiers = ["lambda.amazonaws.com"]
      type        = "Service"
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "main" {

  name               = "project1-artists-${var.env}"
  assume_role_policy = data.aws_iam_policy_document.assume_policy.json

}


data "aws_iam_policy_document" "dynamodb_access" {
  statement {
    actions = [
      "dynamodb:*"
    ]
    resources = [data.aws_dynamodb_table.artists.arn]
    effect    = "Allow"
  }
}


resource "aws_iam_policy" "dynamodb_access" {
  name   = "project1-artists-dynamodb-access-${var.env}"
  policy = data.aws_iam_policy_document.dynamodb_access.json
}

resource "aws_iam_role_policy_attachment" "dynamodb_access" {
  role       = aws_iam_role.main.name
  policy_arn = aws_iam_policy.dynamodb_access.arn
}


resource "aws_iam_role_policy_attachment" "vpc_policy_for_lambda" {
  role       = aws_iam_role.main.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole" #AWS predefined policy
}


resource "aws_iam_policy" "s3_access" {
  name        = "project1-artists-s3-access-${var.env}"
  description = "A test policy"


  policy = <<EOF
   {
"Version": "2012-10-17",
"Statement": [
   
    {
        "Effect": "Allow",
        "Action": [
            "s3:*"
        ],
        "Resource": "${data.aws_s3_bucket.songs.arn}", "${data.aws_s3_bucket.artists.arn}"
    }
]

} 
    EOF
}


resource "aws_iam_role_policy_attachment" "s3_access" {
  role       = aws_iam_role.main.name
  policy_arn = aws_iam_policy.s3_access.arn
}

# podesavanja lambde
resource "aws_lambda_function" "main" {
  function_name = "project1-artists-api-${var.env}"
  role          = aws_iam_role.main.arn
  memory_size   = 128
  timeout       = 10
  package_type  = "Image"
  image_uri     = var.image_uri


  environment {
    variables = {
      ARTISTS_TABLE = data.aws_dynamodb_table.artists.id
      CLIENT_ID     = var.client_id
      CLIENT_SECRET = var.client_secret
    }
  }

  vpc_config {
    subnet_ids         = [data.aws_ssm_parameter.priv_sub_id.value]
    security_group_ids = [aws_security_group.main.id]
  }

}


# podesavanje trigera

resource "aws_lambda_permission" "allow_bucket" {
  statement_id  = "AllowExecutionFromS3Bucket-${var.env}"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.main.arn
  principal     = "s3.amazonaws.com"
  source_arn    = data.aws_s3_bucket.songs.arn
}

resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = data.aws_s3_bucket.songs.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.main.arn
    events              = ["s3:ObjectCreated:*"]
    filter_suffix       = ".csv"
  }

  depends_on = [aws_lambda_permission.allow_bucket]
}
