variable "aws_account_id" {
    type = string
    default = ""
}

variable "aws_region" {
    type = string
    default = "us-west-1"
}

variable "aws_access_key_id" {
    type = string
    default = ""
}

variable "aws_secret_access_key" {
    type = string
    default = ""
}

variable "ecr_image_tag" {
    type = string
    default = "latest"
}