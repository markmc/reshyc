# Setting up TransFTP

## Set up the AWS CLI

$ python3 -m venv aws-venv
$ . ./aws-venv/bin/activate
$ pip install -U pip
$ pip install awscli

$ aws sts get-caller-identity
Unable to locate credentials. You can configure credentials by running "aws configure".

Login at https://eu-west-1.console.aws.amazon.com/

Generate an access key at https://us-east-1.console.aws.amazon.com/iam/home?region=us-east-1#/security_credentials

$ aws configure
AWS Access Key ID [None]: ...
...
Default region name [None]: eu-west-1
...
$ aws sts get-caller-identity
{
    "UserId": "...",
    "Account": "...",
    "Arn": "arn:aws:iam::..."
}

## Create the S3 bucket

Create a bucket:

```shell
$ aws s3api create-bucket --bucket reshyc --create-bucket-configuration LocationConstraint=eu-west-1
$ BUCKET_ARN="arn:aws:s3:::reshyc"
```

## Set up an IAM role for Lambda

Create a role to allow Lambda send log events:

```shell
$ aws iam create-role --role-name transftpLambdaLoggingAccess --assume-role-policy-document '{"Version": "2012-10-17","Statement": [{ "Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"}]}'
$ aws iam attach-role-policy --role-name transftpLambdaLoggingAccess --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
$ LAMBDA_LOGGING_ROLE=$(aws iam get-role --role-name transftpLambdaLoggingAccess --query 'Role.[Arn]' --output text)
```

## Set up FTP server IAM role

First create an IAM role to allow the FTP server to send log events:

```shell
$ aws iam create-role --role-name transftpTransferAccess --assume-role-policy-document '{"Version": "2012-10-17","Statement": [{ "Effect": "Allow", "Principal": {"Service": "transfer.amazonaws.com"}, "Action": "sts:AssumeRole"}]}'
$ aws iam attach-role-policy --role-name transftpTransferAccess --policy-arn "arn:aws:iam::aws:policy/service-role/AWSTransferLoggingAccess"
$ TRANSFER_ROLE=$(aws iam get-role --role-name transftpTransferAccess --query 'Role.[Arn]' --output text)
```

Add a policy which gives read/write access to this bucket, and attach it to the role:

```shell
$ aws iam create-policy --policy-name transftpBucketReadWrite --policy-document '{"Version": "2012-10-17", "Statement": [{"Sid": "AllowListingOfUserFolder", "Effect": "Allow", "Action": ["s3:ListBucket", "s3:GetBucketLocation"], "Resource": "'"${BUCKET_ARN}"'"},{"Sid": "HomeDirObjectAccess", "Effect": "Allow", "Action": ["s3:PutObject", "s3:GetObject", "s3:DeleteObject", "s3:DeleteObjectVersion", "s3:GetObjectVersion", "s3:GetObjectACL", "s3:PutObjectACL"], "Resource": "'"${BUCKET_ARN}"'"}]}'
$ BUCKET_READ_WRITE_POLICY_ARN=$(aws iam list-policies --scope Local --query 'Policies[*].Arn' --output text | grep transftpBucketReadWrite)
$ aws iam attach-role-policy --role-name transftpTransferAccess --policy-arn "${BUCKET_READ_WRITE_POLICY_ARN}"
```

## Create the authentication Lambda function

To create the function:

```shell
$ . ../.ftp_credentials
$ make -C auth-function/ FTP_SERVER_ROLE="${TRANSFER_ROLE}"
$ aws lambda create-function --function-name transftpAuthFunction --zip-file fileb://auth-function/function.zip --handler function.handler --runtime python3.9 --role "${LAMBDA_LOGGING_ROLE}"
$ aws lambda add-permission --function-name transftpAuthFunction --action "lambda:InvokeFunction" --statement-id transftpAllowTransferInvocation --principal "transfer.amazonaws.com"
$ LAMBDA_AUTH_FUNCTION=$(aws lambda get-function --function-name transftpAuthFunction --query 'Configuration.[FunctionArn]' --output text)
```

To make changes:

```shell
$ make -C auth-function/
$ aws lambda update-function-code --function-name transftpAuthFunction --zip-file fileb://auth-function/function.zip
```

To test:

```shell
$ aws lambda invoke --function-name transftpAuthFunction out --log-type Tail --query 'LogResult' --output text |  base64 -d
START RequestId: c1600002-9ed2-4a7b-890a-d58c04066b98 Version: $LATEST
username required
END RequestId: c1600002-9ed2-4a7b-890a-d58c04066b98
REPORT RequestId: c1600002-9ed2-4a7b-890a-d58c04066b98	Duration: 1.45 ms	Billed Duration: 2 ms	Memory Size: 128 MB	Max Memory Used: 36 MB	Init Duration: 113.85 ms
```

To check the log events for the latest log stream in CloudWatch:

```shell
$ aws logs get-log-events --log-group-name "/aws/lambda/transftpAuthFunction" --log-stream-name $(aws logs describe-log-streams --log-group-name "/aws/lambda/transftpAuthFunction" --query 'logStreams[*].[lastEventTimestamp, logStreamName]' --output text | sort -n | tail -1 | awk '{print $2}') --output text
```

## Create the workflow Lambda function

To create the function and allow it to be invoked by S3:

```shell
$ . ../.ftp_credentials
$ make -C auth-function/
$ aws lambda create-function --function-name transftpWorkflowFunction --zip-file fileb://workflow-function/function.zip --handler function.handler --runtime python3.9 --role "${LAMBDA_LOGGING_ROLE}"
$ aws lambda add-permission --function-name transftpWorkflowFunction --action "lambda:InvokeFunction" --statement-id transftpAllowS3Invocation --principal "s3.amazonaws.com"
$ LAMBDA_WORKFLOW_FUNCTION=$(aws lambda get-function --function-name transftpWorkflowFunction --query 'Configuration.[FunctionArn]' --output text)
```

Configure the S3 bucket event notifications to trigger the workflow function when a .htm file is uploaded:

```shell
aws s3api put-bucket-notification-configuration --bucket reshyc --notification-configuration '{"LambdaFunctionConfigurations": [{"Id": "transftpWorkflowFunctionS3Trigger", "LambdaFunctionArn": "'"${LAMBDA_WORKFLOW_FUNCTION}"'", "Events": ["s3:ObjectCreated:Put"], "Filter": {"Key": {"FilterRules": [{"Name": "suffix", "Value": ".htm"}]}}}]}'
```

# Create the FTP server

Create the AWS Transfer Server using SFTP, S3, a public endpoint, and a lambda based identity provider:

```shell
$ aws transfer create-server --protocols SFTP --domain S3 --endpoint-type PUBLIC --identity-provider-type AWS_LAMBDA --identity-provider-details "Function=${LAMBDA_AUTH_FUNCTION}" --logging-role "${TRANSFER_ROLE}"
$ TRANSFER_SERVER_ID=$(aws transfer list-servers --query 'Servers[*].ServerId' --output text)
$ aws transfer wait server-online --server-id "${TRANSFER_SERVER_ID}"
```

Now try logging in!

```shell
$ sftp ${FTP_USER}@${TRANSFER_SERVER_ID}.server.transfer.eu-west-1.amazonaws.com
...
myuser@s-....server.transfer.eu-west-1.amazonaws.com's password: XXXX
```

# Delete server when not in use

```shell
$ TRANSFER_SERVER_ID=$(aws transfer list-servers --query 'Servers[*].ServerId' --output text)
$ aws transfer delete-server --server-id "${TRANSFER_SERVER_ID}"

# Recreate the server when needed

```shell
$ LAMBDA_AUTH_FUNCTION=$(aws lambda get-function --function-name transftpAuthFunction --query 'Configuration.[FunctionArn]' --output text)
$ TRANSFER_ROLE=$(aws iam get-role --role-name transftpTransferAccess --query 'Role.[Arn]' --output text)
$ aws transfer create-server --protocols SFTP --domain S3 --endpoint-type PUBLIC --identity-provider-type AWS_LAMBDA --identity-provider-details "Function=${LAMBDA_AUTH_FUNCTION}" --logging-role "${TRANSFER_ROLE}"
$ TRANSFER_SERVER_ID=$(aws transfer list-servers --query 'Servers[*].ServerId' --output text)
$ aws transfer wait server-online --server-id "${TRANSFER_SERVER_ID}"
```
