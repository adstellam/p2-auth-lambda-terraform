data "aws_ecr_image" "lambda_authorizer_image" {
    depends_on = [
        null_resource.lambda_authorizer_image
    ]
    repository_name = aws_ecr_repository.lambda_authorizer.repository_url
    image_tag = var.ecr_image_tag
}

data "aws_iam_policy_document" "lambda_function_default_execution_policy" {
    statement {
        effect = "Allow"
        actions = [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents"
        ]
        resources = [ "*" ]
        sid = "CreateCloudWatchLogs"
    }
    statement {
        effect = "Allow"
        actions = [
            "codecommit:GitPull",
            "codecommit:GitPush",
            "codecommit:GitBranch",
            "codecommit:ListBranches",
            "codecommit:CreateCommit",
            "codecommit:GetCommit",
            "codecommit:GetCommitHistory",
            "codecommit:GetDifferences",
            "codecommit:GetReferences",
            "codecommit:BatchGetCommits",
            "codecommit:GetTree",
            "codecommit:GetObjectIdentifier",
            "codecommit:GetMergeCommit"
        ]
        resources = [ "*" ]
        sid = "CodeCommit"
    }
}