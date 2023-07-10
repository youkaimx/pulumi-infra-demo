"""An AWS Python Pulumi program"""

import pulumi
import pulumi_aws as aws
from pulumi_aws import s3, cloudfront, iam


# Create an AWS resource (S3 Bucket)
env = pulumi.get_stack()
org = pulumi.get_organization()
project = pulumi.get_project()
project = "demo-class"
tags = {"Project": project, "Env": env, "ManagedByPulumi": "True"}
bucket_name = f"{project}-{env}-cloudfront-origin"

s3_origin = s3.Bucket(
    "s3_origin",
    bucket=bucket_name,
    tags={"Name": f"{project}-{env}-cforigin"}.update(tags),
)

ownership_controls = s3.BucketOwnershipControls(
    "s3_origin_ownership_controls",
    bucket=s3_origin.bucket,
    rule=s3.BucketOwnershipControlsRuleArgs(
        object_ownership="ObjectWriter",
    ),
)

s3_origin_oac = aws.cloudfront.OriginAccessControl(
    "s3_origin_oac",
    description=f"Origin Access Control for s3_origin",
    origin_access_control_origin_type="s3",
    signing_behavior="always",
    signing_protocol="sigv4",
)

cf_distribution = cloudfront.Distribution(
    "cloudfront-distribution",
    opts=pulumi.ResourceOptions(depends_on=[ownership_controls, s3_origin_oac]),
    enabled=True,
    restrictions=cloudfront.DistributionRestrictionsArgs(
        geo_restriction=cloudfront.DistributionRestrictionsGeoRestrictionArgs(
            restriction_type="none"
        )
    ),
    viewer_certificate=cloudfront.DistributionViewerCertificateArgs(
        cloudfront_default_certificate=True
    ),
    tags=tags,
    origins=[
        cloudfront.DistributionOriginArgs(
            domain_name=s3_origin.bucket_regional_domain_name,
            origin_id=s3_origin.bucket,
            origin_access_control_id=s3_origin_oac,
        )
    ],
    default_root_object="index.html",
    default_cache_behavior=aws.cloudfront.DistributionDefaultCacheBehaviorArgs(
        allowed_methods=[
            "OPTIONS",
            "GET",
            "HEAD",
        ],
        cached_methods=[
            "GET",
            "HEAD",
        ],
        target_origin_id=s3_origin.bucket,
        viewer_protocol_policy="allow-all",
        forwarded_values=cloudfront.DistributionDefaultCacheBehaviorForwardedValuesArgs(
            query_string=False,
            cookies=cloudfront.DistributionDefaultCacheBehaviorForwardedValuesCookiesArgs(
                forward="none",
            ),
        ),
        # cache_policy_id=cloudfront.CachePolicy(
        #    "cache_policy",
        #    opts=cloudfront.CachePolicyParametersInCacheKeyAndForwardedToOriginArgs(
        #        cookies_config=cloudfront.CachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfigArgs(
        #            cookie_behavior="none"
        #        ),
        #        headers_config=cloudfront.CachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfigArgs(
        #            header_behavior="none"
        #        ),
        #        query_strings_config=cloudfront.CachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfigArgs(
        #            query_string_behavior="none"
        #        ),
        #    ),
        # ),
    ),
)
#
# Export the name of the
# print(f"Visit your page at https://{cf_distribution.domain_name}")

s3_origin_acess_from_cloudfront_bucket_policy = s3.BucketPolicy(
    "s3_origin_access_from_cloudfront_bucket_policy",
    bucket=s3_origin.id,
    policy="""
    {
        "Version": "2008-10-17",
        "Id": "PolicyForCloudFrontPrivateContent",
        "Statement": [
            {
                "Sid": "AllowCloudFrontServicePrincipal",
                "Effect": "Allow",
                "Principal": {
                    "Service": "cloudfront.amazonaws.com"
                },
                "Action": "s3:GetObject",
                "Resource": "arn:aws:s3:::demo-class-dev-cloudfront-origin/*",
                "Condition": {
                    "StringEquals": {
                      "AWS:SourceArn": "arn:aws:cloudfront::014834224223:distribution/E4DVVK9X4W4MD"
                    }
                }
            }
        ]
    }
    """,
)

# Outputs
pulumi.export("bucket_name", s3_origin.id)
pulumi.export("cloudfront_url", cf_distribution.domain_name)
