# blueharvest_assessment
<!-- Design and deploy of a serverless ETL flow on AWS. -->


## Description
This project uses Cloudformation to deploy a script on AWS Lambda. 
It creates a script that consumes a 3rd party API (MARVEL) and extracts the list of all available marvel characters and the comics they appear in,and the uploads the data as a csv to an S3 bucket .

An AWS EventBridge rule is created to trigger the lambda function
The infrastructure design is displayed below:

![Architecture diagram]
![architecture_diagram](https://github.com/Loldozen/blueharvest_assessment/assets/56772631/0b5bb5a6-bd59-46a4-9625-51ca24dbe473)


## Retrieve code

-   `$ git clone https://github.com/Loldozen/blueharvest_assessment.git`


### Setup Infra
- Create an s3 bucket in the same region as the cloudformation stack and upload the Lambda zipped file `lambda_function.zip`
- Upload the Marvel API keys to AWS Secrets Manager 
- Edit the `lambda_parameters.json` file and fill it up with Bucket data and secrets name


**Note:** Ensure the exact name used to store the zipped lambda and the secrets are used in the parameters file 


### Running

~~~ 
# Ensure that the AWS CLI is configured before runniing the command below
# Check the region in the create.sh and update.sh file
# Edit the profile flag in the create.sh and update.sh to your local AWS CLI profile configured
# Create the infrastructure

cd ./infra

chmod +x create.sh

./create.sh <stack name> <cloudformation_template> <parameters_file.json>

 # And for updating the infrastructure
./update.sh <stack_name> <cloudformation_template.yml> <parameters_file.json>
~~~

### Testing

-   `$ python -m unittest`
-   Alternative command `$ python3 -m unittest`
