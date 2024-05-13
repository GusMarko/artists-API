import os
import boto3
import json
import xml.etree.ElementTree as ET
import shutil


def main():
    env_name = get_environment()
    boto3_session = init_boto3_session()
    replace_tfvars(env_name, boto3_session)
    ecr_repo_name = f"project1/{env_name}/code-images"
    print(f"::set-output name=ecr_repo_name::{ecr_repo_name}")


def get_environment():
    env_name = os.environ.get("GITHUB_REF", "")
    env_name_parts = env_name.split("/")
    env_name = env_name_parts[-1]
    if env_name == "main":
        env_name = "prod"

    return env_name


def init_boto3_session():
    return boto3.Session(
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        region_name=os.environ.get("AWS_REGION"),
    )


def replace_tfvars(env, boto3_session):
    aws_region = os.environ.get("AWS_REGION")
    tf_role_credentials = get_aws_secret("/pipeline-user/credentials", boto3_session)
    access_key = tf_role_credentials["access_key"]
    secret_key = tf_role_credentials["secret_key"]
    tfvars_path = "../iac/terraform.tfvars"
    backend_config_path = "../iac/provider.tf"
    spotify_credentials = get_aws_secret("/spotify/credentials", boto3_session)
    client_id = spotify_credentials["client_id"]
    client_secret = spotify_credentials["client_secret"]

    with open(tfvars_path, "r") as f:
        tfvars = f.read()
    tfvars = tfvars.replace("aws_region_placeholder", aws_region)
    tfvars = tfvars.replace("access_key_placeholder", access_key)
    tfvars = tfvars.replace("secret_key_placeholder", secret_key)
    tfvars = tfvars.replace("env_placeholder", env)
    tfvars = tfvars.replace("client_id_placeholder", client_id)
    tfvars = tfvars.replace("client_secret_placeholder", client_secret)
    with open(tfvars_path, "w") as f:
        f.write(tfvars)

    with open(backend_config_path, "r") as f:
        backend_config = f.read()
    backend_config = backend_config.replace("aws_region_placeholder", aws_region)
    backend_config = backend_config.replace("access_key_placeholder", access_key)
    backend_config = backend_config.replace("secret_key_placeholder", secret_key)
    backend_config = backend_config.replace("env_placeholder", env)
    with open(backend_config_path, "w") as f:
        f.write(backend_config)


def get_aws_secret(secret_path, session):
    secrets_manager = session.client("secretsmanager")
    response = secrets_manager.get_secret_value(SecretId=secret_path)
    secret = json.loads(response["SecretString"])

    return secret


########## START ##########
if __name__ == "__main__":
    main()
