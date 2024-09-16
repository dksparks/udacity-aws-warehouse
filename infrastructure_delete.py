import boto3
import configparser


# get config info

config = configparser.ConfigParser()

# get access keys from (untracked) config file
config.read("access_keys.cfg")
key = config.get("AWS", "KEY")
secret = config.get("AWS", "SECRET")

config.read("infrastructure.cfg")
role_name = config.get("IAM", "ROLE_NAME")
cluster_identifier = config.get("CLUSTER", "CLUSTER_IDENTIFIER")


# delete redshift cluster

redshift = boto3.client(
    "redshift",
    region_name="us-east-1",
    aws_access_key_id=key,
    aws_secret_access_key=secret,
)

try:
    redshift.delete_cluster(
        ClusterIdentifier=cluster_identifier,
        SkipFinalClusterSnapshot=True,
    )
except Exception as e:
    print(e)


# delete iam role

iam = boto3.client(
    "iam",
    region_name="us-east-1",
    aws_access_key_id=key,
    aws_secret_access_key=secret,
)

try:
    iam.detach_role_policy(
        RoleName=role_name,
        PolicyArn="arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess",
    )
    iam.delete_role(RoleName=role_name)
except Exception as e:
    print(e)
