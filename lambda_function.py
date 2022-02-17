from __future__ import print_function

import json
from logging import Logger
import boto3
import datetime
from pprint import pprint
from datetime import date, timedelta

print('Loading function')

def logging_noncompliant():
    filename = input("Enter a file-name!: ")
    # Noncompliant: unsanitized input is logged.
    Logger.info("Processing %S", filename)


def lambda_handler(event, context):
    arn = "arn:aws:sns:region:123456789012:enriched-sns-topic"
    
    #print("Received event: " + json.dumps(event, indent=2))
    message = event['Records'][0]['Sns']['Message']
    print("From SNS: " + message)
    
    # Let's use Cost Explorer
    client = boto3.client('ce', region_name='us-east-1')
    
    # Set today and yesterday
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    yesterday = date.today() - timedelta(1)
    yesterday = yesterday.strftime('%Y-%m-%d')
    
    # Get the cost and usage by service
    response = client.get_cost_and_usage(
        TimePeriod={
            'Start': yesterday, # For example, 2017-01-01
            'End': today	
        },
        Granularity='DAILY',
        Metrics=[
            'BlendedCost',
        ],
        GroupBy=[
            {
                'Type': 'DIMENSION',
                'Key': 'SERVICE'
            }
        ]       
    )
    
    Groups = response['ResultsByTime'][0]['Groups']
    
    HighestCostService = []
    for i in Groups:
    	Service = (i['Keys'])
    	Service = ''.join(Service)
    	Cost = str(i['Metrics']['BlendedCost']['Amount'])
    	if float(Cost) > 0:
    		if not HighestCostService:
    			HighestCostService = Service
    			HighestValue = Cost
    		if Cost > HighestValue:
    			HighestCostService = Service
    			HighestValue = Cost
    
    HighestValue = float(HighestValue)
    HighestValue = '${:,.2f}'.format(HighestValue)
    highestCostService = (HighestCostService + ' is the highest cost at ' + HighestValue + ' USD')
    finalHighestCostService = HighestCostService
    finalHighestCostServiceValue = HighestValue
    print (highestCostService)
    
    # Get the cost and usage for the highest cost service by operation
    response = client.get_cost_and_usage(
        TimePeriod={
            'Start': yesterday, # For example, 2017-01-01
            'End': today	
        },
        Granularity='DAILY',
        Metrics=[
            'BlendedCost',
        ],
        Filter={
            'Dimensions': {
                'Key': 'SERVICE',
                'Values': [
                    HighestCostService,
                ]
            }
        },
        GroupBy=[
            {
                'Type': 'DIMENSION',
                'Key': 'OPERATION'
            }
        ]          
    )
    
    APICalls = response['ResultsByTime'][0]['Groups']
    
    HighestCostAPICall = []
    for i in APICalls:
    	API = (i['Keys'])
    	API = ''.join(API)
    	Cost = str(i['Metrics']['BlendedCost']['Amount'])
    	if float(Cost) > 0:
    		if not HighestCostAPICall:
    			HighestCostAPICall = API
    			HighestValue = Cost
    		if Cost > HighestValue:
    			HighestCostAPICall = API
    			HighestValue = Cost
    
    HighestValue = float(HighestValue)
    HighestValue = '${:,.2f}'.format(HighestValue)
    finalHighestCostAPICall = HighestCostAPICall
    highestCostAPICall = (HighestCostAPICall + ' is the highest cost API Call for ' + HighestCostService + ' for the day at ' + HighestValue + ' USD')
    
    print (highestCostAPICall)
    
    # Get the cost and usage for the highest cost service, and operation, for AZ
    response = client.get_cost_and_usage(
        TimePeriod={
            'Start': yesterday, # For example, 2017-01-01
            'End': today	
        },
        Granularity='DAILY',
        Metrics=[
            'BlendedCost',
        ],
        Filter={
            'Dimensions': {
                'Key': 'SERVICE',
                'Values': [
                    HighestCostService,
                ],
                'Key': 'OPERATION',
                'Values': [
                    HighestCostAPICall,
                ]
            }
        },
        GroupBy=[
            {
                'Type': 'DIMENSION',
                'Key': 'AZ'
            }
        ]          
    )
    
    AZs = response['ResultsByTime'][0]['Groups']
    
    HighestCostAZ = []
    for i in AZs:
    	AZ = (i['Keys'])
    	AZ = ''.join(AZ)
    	Cost = str(i['Metrics']['BlendedCost']['Amount'])
    	if float(Cost) > 0:
    		if not HighestCostAZ:
    			HighestCostAZ = AZ
    			HighestValue = Cost
    		if Cost > HighestValue:
    			HighestCostAZ = AZ
    			HighestValue = Cost
    
    HighestValue = float(HighestValue)
    HighestValue = '${:,.2f}'.format(HighestValue)
    finalHighestCostAZ = HighestCostAZ
    highestCostAZ = (HighestCostAZ + ' is the highest cost AZ for the API Call ' + HighestCostAPICall + ' for ' + HighestCostService + ' the day at ' + HighestValue + ' USD')
    print (highestCostAZ)
    
    if ('Forecasted' not in message):
        smsalert = "You are over your AWS Budget"
    else:
        smsalert = "You are forecast to be over your AWS Budget"
    
    smsmessage = (smsalert + ': ' + finalHighestCostService + ' ' + finalHighestCostServiceValue + 'USD ' + finalHighestCostAPICall + ' ' + finalHighestCostAZ)
    
    print (smsmessage)
    client = boto3.client('sns')
    response = client.publish(
        TargetArn=arn,
        Message=json.dumps({
            'default': json.dumps(smsmessage),
            'sms': smsalert
        }),
        MessageStructure='json',
        Subject='AWS Budget Notification'
    )

    return message
