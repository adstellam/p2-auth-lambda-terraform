terraform {
    required_version = ">= 0.13.0"
    required_providers {
        aws = {
            source  = "hashicorp/aws"
            version = ">= 2.0"
        }
        local = {
            source  = "hashicorp/local"
            version = ">= 1.3"
        }
    }
}

provider "aws" {
    region     = var.aws_region
    access_key = var.aws_access_key_id
    secret_key = var.aws_secret_access_key 
}

resource "aws_ecr_repository" "lambda_authorizer" {
    name = "lambda/lambda_authorizer"
}
 
resource "null_resource" "lambda_authorizer_image" {
    triggers = {
        python_file = md5(file("${path.module}/lambda-auth-image/index.py"))
        docker_file = md5(file("${path.module}/lambda-auth-image/Dockerfile"))
    }
    provisioner "local-exec" {
        command = <<-EOF
            aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${var.aws_account_id}.dkr.ecr.${var.aws_region}.amazonaws.com
            cd ${path.module}/lambda-auth-image
            docker build -t ${aws_ecr_repository.lambda_authorizer.repository_url}:${var.ecr_image_tag} .
            docker push ${aws_ecr_repository.lambda_authorizer.repository_url}:${var.ecr_image_tag}
        EOF
    }
}
 
resource "aws_iam_role" "lambda_authorizer_execution_role" {
    name = "lambda_authorizer_execution_role"
    assume_role_policy = <<-EOF
        {
          "Version": "2012-10-17",
          "Statement": [
              {
                  "Effect": "Allow",
                  "Action": "sts:AssumeRole",
                  "Principal": {
                      "Service": "lambda.amazonaws.com"
                  }
              }
          ]
        }
    EOF
}
 
resource "aws_iam_policy" "lambda_authorizer_execution_policy" {
    name = "lambda_authorizer_execution_policy"
    path = "/lambda/"
    policy = data.aws_iam_policy_document.lambda_function_default_execution_policy.json
}

resource "aws_iam_role_policy_attachment" "lambda_authorizer_role" {
    role = aws_iam_role.lambda_authorizer_execution_role.name
    policy_arn = aws_iam_policy.lambda_authorizer_execution_policy.arn
}
 
resource "aws_lambda_function" "lambda_authorizer" {
    depends_on = [
        null_resource.lambda_authorizer_image
    ]
    function_name = "lambda_authorizer"
    role = aws_iam_role.lambda_authorizer_execution_role.arn
    package_type = "Image"
    image_uri = data.aws_ecr_image.lambda_authorizer_image.repository_name
    timeout = 300
}
