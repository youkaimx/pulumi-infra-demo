# An Introduction to Infrastructure as Code

## Infrastructure
- Compute power, storage, networks are usually conceived as infrastructure, elements that support the use of software
- More recently with the rise of the "as code" practices and the cloud, elements like permissions, network configuration and others are also considered infrastructure

## Infrastructure as Code
- The practice of managing elements of infrastructure via programming "languages"
  - Managing here refers to creating, updating and deleting those elements
- Language used for IaC can be
  - Domain Specific Languages like Terraform's HCL
  - General Purpose Languages like Javascript or Python for CDK or Pulumi

## Workflow for IaC
- Code for the Infrastructure is bundled usually as a folder alongside the code
- Code is versioned on a Version Control system like git
- On code updates, a series of steps or pipeline is run to
  - update the required infrastructure
  - build the software
  - deploy the software on the infrastruture

## Example code
- This example involves the usage of
  - AWS
    - Cloudfront
    - S3 Bucket as an Origin for Cloudfront
  - Python flavored Pulumi
