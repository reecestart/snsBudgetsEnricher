# snsBudgetsEnricher

This is an example Lambda function that enriches SMS messages.

In this example the Lambda Function is triggered by the SNS Topic when an AWS Budget event occurs. The Lambda Function then checks to see if the event is actually over Budget or forecast to be over Budget. The function then calls Cost Explorer to determine which AWS Service cost the most in the last day with an amount spent on that service, then which API Call for that service, then which AZ for that API call. Then the function will post this information to an enriched SNS topic.

## Architecture

<insert image>

## To Do

Update the ARN on line 13 to your target, enriched SNS Topic.

arn = "arn:aws:sns:region:123456789012:enriched-sns-topic"

Create an SNS Topic for your Budget, ensure the Topic Policy is updated so Budgets can post to it. Once you have deployed the lambda function ensure that it has access to Cost Explorer and is triggered from the Budgets SNS Topic.
