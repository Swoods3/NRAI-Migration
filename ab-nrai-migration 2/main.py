#Workflow Create Steps (order of operations)-
# 1. Create Destination
# 2. Create Channel - Logical binding of destination->workflow (relationship) -- this is where you can get/specify the payload of a destination tied to a workflow. Pre-req to Workflow creation
# 3. Create Workflow

import json
import sys
from decisions import Decisions
from destinations import Destinations
from workflows import Workflows
from channels import Channels

#Source account detail that you're moving the objects from
SOURCEKEY = '<source_key>'
SOURCE_ACCOUNTID = <source_accountId>

#Destination account detail you're moving the objects to
DESTKEY = '<dest_key>'
DEST_ACCOUNTID = <dest_accountId>

def main():
    decisions = Decisions(SOURCEKEY, SOURCE_ACCOUNTID, DESTKEY, DEST_ACCOUNTID)
    destinations = Destinations(SOURCEKEY, SOURCE_ACCOUNTID, DESTKEY, DEST_ACCOUNTID)
    workflows = Workflows(SOURCEKEY, SOURCE_ACCOUNTID, DESTKEY, DEST_ACCOUNTID)
    channels = Channels(SOURCEKEY, SOURCE_ACCOUNTID, DESTKEY, DEST_ACCOUNTID)

    sep = "**************************"

    try:
        allWorkflows = workflows.getWorkflows()
        allDecisions = decisions.getDecisions()

        print('Processing Workflows...')
        for w in allWorkflows: #for each workflow
            if ('Vetspace' not in w['name']): #only move non-Vetspace Workflows/Destinations/Channels
                print(sep)
                print('Processing Workflow: ' + w['name'])
                aChannel = channels.getChannel(w['destinationConfigurations'][0]['channelId'])
                print('Fetched Channel √')
                print('Getting Destination...')
                aDestination = destinations.getDestination(aChannel['destinationId'])
                if (aDestination is not None): #Represents unused channel (destination not attached to a given workflow) or deleted destination, so disregard
                    print('Fetched Destination √')
                    print("Creating destination in new account...")
                    destResult = destinations.createDestination(aDestination) #create destination
                    # print(destResult)
                    # if (destResult['error'] is not None): #destination create failure
                    #     print('Failed to create Destination')
                    #     print(destResult['error'])
                    if (destResult is None): #SNOW destination
                        print('Creating channel in new account...')
                        channelResult = channels.createChannel(newDestId, newDestName, aChannel) #create channel
                        if (channelResult['error'] is not None): #channel create failure
                            print('Failed to create Channel')
                            print(channelResult['error'])
                        else:
                            print('Successfully created channel in new account √')
                            newChannelId = channelResult['channel']['id']
                            newChannelName = channelResult['channel']['name']
                            print('Creating workflow in new account...')
                            workflowResult = workflows.createWorkflow(newChannelId, w) #create workflow
                            if (workflowResult['errors']):
                                print('Error creating workflow: ' + w['name'])
                            else:
                                print('Successfully created workflow in new account √')
                                print(sep)
                    else:
                        print('Successfully created destination √')
                        newDestId = destResult['destination']['id']
                        newDestName = destResult['destination']['name']
                        print('Creating channel in new account...')
                        channelResult = channels.createChannel(newDestId, newDestName, aChannel) #create channel
                        if (channelResult['error'] != None): #channel create failure
                            print('Failed to create Channel')
                            print(channelResult['error'])
                        else:
                            print('Successfully created channel in new account √')
                            newChannelId = channelResult['channel']['id']
                            newChannelName = channelResult['channel']['name']
                            print('Creating workflow in new account...')
                            workflowResult = workflows.createWorkflow(newChannelId, w) #create workflow
                            if (workflowResult['errors']):
                                print('Error creating workflow: ' + w['name'])
                            else:
                                print('Successfully created workflow in new account √')
                                print(sep)
    except Exception as e:
        raise
        sys.exit(1)



if __name__ == '__main__':
    main()
