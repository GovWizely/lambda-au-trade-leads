# Australia Trade Leads Lambda

This project provides an AWS Lambda that creates a single JSON document from the RSS endpoint 
at [https://www.tenders.gov.au/public_data/rss/rss.xml](https://www.tenders.gov.au/public_data/rss/rss.xml) and the data in each HTML page.
It uploads that JSON file to a S3 bucket.

## Prerequisites

Follow instructions from [python-lambda](https://github.com/nficano/python-lambda) to ensure your basic development environment is ready,
including:

* Python
* Pip
* Virtualenv
* Virtualenvwrapper
* AWS credentials

## Getting Started

	git clone git@github.com:GovWizely/lambda-au-trade-leads.git
	cd lambda-au-trade-leads
	mkvirtualenv -r requirements.txt lambda-au-trade-leads

## Configuration

* Define AWS credentials in either `config.yaml` or in the [default] section of ~/.aws/credentials.
* Edit `config.yaml` if you want to specify a different AWS region, role, and so on.
* Make sure you do not commit the AWS credentials to version control

## Invocation

	lambda invoke -v
 
## Deploy

	lambda deploy
