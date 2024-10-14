import boto3
import configparser
import json


# get config info

config = configparser.ConfigParser()

# get access keys from (untracked) config file
config.read("access_keys/access_keys.cfg")
key = config.get("AWS", "KEY")
secret = config.get("AWS", "SECRET")

config.read("infrastructure.cfg")
role_name = config.get("IAM", "ROLE_NAME")
cluster_identifier = config.get("CLUSTER", "CLUSTER_IDENTIFIER")
cluster_type = config.get("CLUSTER", "CLUSTER_TYPE")
node_type = config.get("CLUSTER", "NODE_TYPE")

config.read("dwh.cfg")
db_name = config.get("CLUSTER", "DB_NAME")
db_user = config.get("CLUSTER", "DB_USER")
db_password = config.get("CLUSTER", "DB_PASSWORD")
db_port = int(config.get("CLUSTER", "DB_PORT"))


# create iam role

iam = boto3.client(
    "iam",
    region_name="us-east-1",
    aws_access_key_id=key,
    aws_secret_access_key=secret,
)

try:
    iam.create_role(
        Path="/",
        RoleName=role_name,
        AssumeRolePolicyDocument=json.dumps(
            {
                "Statement": [
                    {
                        "Action": "sts:AssumeRole",
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "redshift.amazonaws.com"
                        },
                    }
                ],
                "Version": "2012-10-17",
            }
        ),
    )
    iam.attach_role_policy(
        RoleName=role_name,
        PolicyArn="arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess",
    )
except Exception as e:
    print(e)

role_arn = iam.get_role(RoleName=role_name)["Role"]["Arn"]
print(role_arn)


# create redshift cluster

redshift = boto3.client(
    "redshift",
    region_name="us-east-1",
    aws_access_key_id=key,
    aws_secret_access_key=secret,
)

try:
    redshift.create_cluster(
        ClusterIdentifier=cluster_identifier,
        ClusterType=cluster_type,
        NodeType=node_type,
        DBName=db_name,
        MasterUsername=db_user,
        MasterUserPassword=db_password,
        Port=db_port,
        IamRoles=[role_arn],
    )
except Exception as e:
    print(e)
