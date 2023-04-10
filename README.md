HOW TO DEPLOY LAMBDA-AUTHORIZER FOR APIGATEWAY

1. Install terraform

    Follow the instructions at https://developer.hashicorp.com/terraform/cli/install/apt


2. To initialize the directory for terraform operations:

    terraform init


3. To deploy lambda-authorizer as a lambda function:

    terraform plan -out lambda-auth-plan
    terraform deploy lambda-auth-plan -var='aws_secret_access_ley= xxxx'