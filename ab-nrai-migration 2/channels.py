import requests

class Channels():
    def __init__(self, sourceKey, sourceAccount, destKey, destAccount):
        SOURCE=sourceKey
        DEST=destKey
        self.sourceAccount = sourceAccount
        self.destAccount = destAccount
        self.url = 'https://api.newrelic.com/graphql'
        self.sourceHeaders = {
            'Content-Type': 'application/json',
            'API-Key': SOURCE
        }
        self.destHeaders = {
            'Content-Type': 'application/json',
            'API-Key': DEST
        }

    def sendRequest(self, q, s, vars):
        if (s == 'source'):
            res = requests.request("POST", self.url, headers=self.sourceHeaders, json={'query': q, 'variables': vars})
            return res

        if (s == 'dest'):
            res = requests.request("POST", self.url, headers=self.destHeaders, json={'query': q, 'variables': vars})
            return res


    def getChannel(self, id):
        q = f'''
            {{
              actor {{
                account(id: {self.sourceAccount}) {{
                  aiNotifications {{
                    channels(filters: {{id: "{id}"}}) {{
                      entities {{
                        id
                        destinationId
                        name
                        properties {{
                          displayValue
                          key
                          value
                          label
                        }}
                        status
                        type
                      }}
                    }}
                  }}
                }}
              }}
            }}
        '''

        try:
            resp = self.sendRequest(q, 'source', {})
            if (resp.status_code == 200):
                parsed = resp.json()
                channel = parsed['data']['actor']['account']['aiNotifications']['channels']['entities'][0]
            else:
                print('Unable to fetch channel: ' + str(resp.status_code))
        except Exception as e:
            print('Fetch Channel - Exception occurred')
            raise

        return(channel)


    def createChannel(self, destid, destName, channel):
        vars = {
          "destId": destid,
          "destName": destName,
          "props": channel['properties'],
          "type": channel['type']
        }

        q = """
            mutation create($destId: ID!, $destName: String!, $props: [AiNotificationsPropertyInput!]!, $type: AiNotificationsChannelType!) {
              aiNotificationsCreateChannel(channel: {destinationId: $destId, name: $destName, product: IINT, properties: $props, type: $type}, accountId: %d) {
                channel {
                  id
                  name
                  destinationId
                  type
                }
                error {
                  ... on AiNotificationsConstraintsError {
                    constraints {
                      dependencies
                      name
                    }
                  }
                  ... on AiNotificationsDataValidationError {
                    details
                    fields {
                      field
                      message
                    }
                  }
                  ... on AiNotificationsResponseError {
                    description
                    details
                    type
                  }
                }
              }
            }
        """ % self.destAccount

        try:
            resp = self.sendRequest(q, 'dest', vars)
            if (resp.status_code == 200):
                parsed = resp.json()
                channelResult = parsed['data']['aiNotificationsCreateChannel']
            else:
                print('Unable to create channel: ' + str(resp.status_code))
        except Exception as e:
            print('Create Channel - Exception occurred')
            raise

        return(channelResult)







#Get channel payload for a destination id
# {
#   actor {
#     account(id: 1) {
#       aiNotifications {
#         channels(filters: {destinationId: "2b4ff4de-8cc3-42c3-b527-a3ea0b2d7a6e"}) {
#           entities {
#             id
#             name
#             properties {
#               displayValue
#               key
#               value
#               label
#             }
#             status
#             type
#           }
#         }
#       }
#     }
#   }
# }

#Create channel:
# mutation {
#   aiNotificationsCreateChannel(accountId: 1, channel: {destinationId: "", name: "", product: IINT, properties: {key: "", value: ""}, type: WEBHOOK}) {
#     channel {
#       id
#       name
#       destinationId
#       type
#     }
#   }
# }
