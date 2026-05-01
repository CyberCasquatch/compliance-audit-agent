#!/usr/bin/env bash
# collect_aws.sh — Collect AWS account configuration for compliance auditing.
#
# Prerequisites:
#   - AWS CLI installed and configured (aws configure)
#   - Sufficient IAM permissions: SecurityAudit managed policy or equivalent
#
# Usage:
#   bash scripts/collect_aws.sh > my_aws_config.txt
#   python src/agent.py --env aws --framework both --input my_aws_config.txt

set -euo pipefail

REGION="${AWS_DEFAULT_REGION:-us-east-1}"

echo "=== AWS Compliance Config Snapshot ==="
echo "Date: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "Region: $REGION"
echo ""

echo "--- Account Info ---"
aws sts get-caller-identity 2>/dev/null || echo "ERROR: Could not get caller identity"
echo ""

echo "--- IAM Password Policy ---"
aws iam get-account-password-policy 2>/dev/null || echo "No password policy configured"
echo ""

echo "--- IAM Users (summary) ---"
aws iam list-users --query 'Users[*].{User:UserName,Created:CreateDate,PasswordLastUsed:PasswordLastUsed}' --output table 2>/dev/null
echo ""

echo "--- Root Account MFA ---"
aws iam get-account-summary --query 'SummaryMap.AccountMFAEnabled' --output text 2>/dev/null
echo ""

echo "--- Access Keys (age check) ---"
for user in $(aws iam list-users --query 'Users[*].UserName' --output text 2>/dev/null); do
  aws iam list-access-keys --user-name "$user" \
    --query "AccessKeyMetadata[*].{User:'$user',KeyId:AccessKeyId,Status:Status,Created:CreateDate}" \
    --output json 2>/dev/null
done
echo ""

echo "--- CloudTrail Trails ---"
aws cloudtrail describe-trails --include-shadow-trails false 2>/dev/null
echo ""

echo "--- S3 Buckets ---"
aws s3api list-buckets --query 'Buckets[*].Name' --output text 2>/dev/null | tr '\t' '\n' | while read -r bucket; do
  echo "Bucket: $bucket"
  aws s3api get-bucket-acl --bucket "$bucket" --query 'Grants[?Grantee.URI==`http://acs.amazonaws.com/groups/global/AllUsers`]' --output text 2>/dev/null | grep -q . && echo "  PUBLIC ACL: YES" || echo "  Public ACL: no"
  aws s3api get-bucket-versioning --bucket "$bucket" 2>/dev/null
done
echo ""

echo "--- Security Groups (open ingress) ---"
aws ec2 describe-security-groups \
  --filters "Name=ip-permission.cidr,Values=0.0.0.0/0" \
  --query 'SecurityGroups[*].{ID:GroupId,Name:GroupName,Ingress:IpPermissions}' \
  --output table 2>/dev/null
echo ""

echo "--- VPC Flow Logs ---"
aws ec2 describe-flow-logs --output table 2>/dev/null
echo ""

echo "--- GuardDuty Detectors ---"
aws guardduty list-detectors --output text 2>/dev/null || echo "GuardDuty: not enabled or no detectors"
echo ""

echo "--- AWS Config Status ---"
aws configservice describe-configuration-recorders --output table 2>/dev/null || echo "AWS Config: not enabled"
echo ""

echo "--- RDS Instances ---"
aws rds describe-db-instances \
  --query 'DBInstances[*].{ID:DBInstanceIdentifier,Engine:Engine,Encrypted:StorageEncrypted,Public:PubliclyAccessible}' \
  --output table 2>/dev/null
echo ""

echo "--- KMS Keys ---"
aws kms list-keys --query 'Keys[*].KeyId' --output text 2>/dev/null | tr '\t' '\n' | while read -r key; do
  aws kms describe-key --key-id "$key" \
    --query 'KeyMetadata.{ID:KeyId,Enabled:Enabled,Rotation:KeyRotationEnabled,Manager:KeyManager}' \
    --output json 2>/dev/null
done
echo ""

echo "=== End of snapshot ==="
