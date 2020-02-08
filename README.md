[![CircleCI](https://circleci.com/gh/GovWizely/lambda-au-trade-leads/tree/master.svg?style=svg)](https://circleci.com/gh/GovWizely/lambda-au-trade-leads/tree/master)
[![Maintainability](https://api.codeclimate.com/v1/badges/d783738b80f2c6fc6703/maintainability)](https://codeclimate.com/github/GovWizely/lambda-au-trade-leads/maintainability)

# Australia Trade Leads Lambda

This project provides an AWS Lambda that creates a single JSON document from the RSS endpoint 
at [https://www.tenders.gov.au/public_data/rss/rss.xml](https://www.tenders.gov.au/public_data/rss/rss.xml) and the data in each HTML page.
It uploads that JSON file to a S3 bucket.

## Prerequisites

- This project is tested against Python 3.7+ in [CircleCI](https://app.circleci.com/github/GovWizely/lambda-au-trade-leads/pipelines).

## Getting Started

	git clone git@github.com:GovWizely/lambda-au-trade-leads.git
	cd lambda-au-trade-leads
	mkvirtualenv -p /usr/local/bin/python3.8 -r requirements-test.txt au-trade-leads

If you are using PyCharm, make sure you enable code compatibility inspections for Python 3.7/3.8.

### Tests

```bash
python -m pytest
```

## Configuration

* Define AWS credentials in either `config.yaml` or in the [default] section of `~/.aws/credentials`. To use another profile, you can do something like `export AWS_DEFAULT_PROFILE=govwizely`.
* Edit `config.yaml` if you want to specify a different AWS region, role, and so on.
* Make sure you do not commit the AWS credentials to version control.

## Invocation

	lambda invoke -v
 
## Deploy
    
To deploy:

	lambda deploy --requirements requirements.txt
