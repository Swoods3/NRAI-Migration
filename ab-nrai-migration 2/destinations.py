import requests

class Destinations():
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


    def getDestination(self, id):
        q = f'''
        {{
          actor {{
            account(id: {self.sourceAccount}) {{
              aiNotifications {{
                destinations(filters: {{id: "{id}"}}) {{
                  entities {{
                    properties {{
                      displayValue
                      key
                      label
                      value
                    }}
                    active
                    name
                    type
                    id
                    status
                    auth {{
                      ... on AiNotificationsBasicAuth {{
                        authType
                        user
                      }}
                    }}
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
                destination = parsed['data']['actor']['account']['aiNotifications']['destinations']['entities']
            else:
                print('Unable to fetch destination: ' + str(resp.status_code))
        except Exception as e:
            print('Fetch Destination - Exception occurred')
            raise

        if (len(destination) > 0):
            return(destination[0])
        else:
            return(None)


    def getDestinations(self):
        q = f'''
        {{
          actor {{
            account(id: {self.sourceAccount}) {{
              aiNotifications {{
                destinations {{
                  entities {{
                    properties {{
                      displayValue
                      key
                      label
                      value
                    }}
                    active
                    name
                    type
                    id
                    status
                    auth {{
                      ... on AiNotificationsBasicAuth {{
                        authType
                        user
                      }}
                    }}
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
                destinations = parsed['data']['actor']['account']['aiNotifications']['destinations']['entities']
            else:
                print('Unable to fetch destinations: ' + str(resp.status_code))
        except Exception as e:
            print('Fetch Destinations - Exception occurred')
            raise

        return(destinations)


    def createDestination(self, destination): #no basic auth implemented, except for SNOW (required)
        if ('Service Now' in destination['name']):
            return(None)
            # vars = {
            #   "props": destination['properties'],
            #   "type": destination['type'],
            #   "name": destination['name'],
            #   "user": "snow_ws",
            #   "pass": "<abc>"
            # }
            #
            # q = """
            #     mutation create($props: [AiNotificationsPropertyInput!]!, $type: AiNotificationsDestinationType!, $name: String!, $user: String!, $pass: SecureValue!) {
            #       aiNotificationsCreateDestination(accountId: %d, destination: {name: $name, properties: $props, type: $type, auth: {type: BASIC, basic: {password: $pass, user: $user}}}) {
            #         destination {
            #           name
            #           id
            #         }
            #         error {
            #           ... on AiNotificationsResponseError {
            #             description
            #             details
            #           }
            #           ... on AiNotificationsDataValidationError {
            #             details
            #           }
            #           ... on AiNotificationsConstraintsError {
            #             constraints {
            #               dependencies
            #               name
            #             }
            #           }
            #         }
            #       }
            #     }
            # """ % (self.destAccount)
        else:
            vars = {
              "props": destination['properties'],
              "type": destination['type'],
              "name": destination['name']
            }

            q = """
                mutation create($props: [AiNotificationsPropertyInput!]!, $type: AiNotificationsDestinationType!, $name: String!) {
                  aiNotificationsCreateDestination(accountId: %d, destination: {name: $name, properties: $props, type: $type}) {
                    destination {
                      name
                      id
                    }
                    error {
                      ... on AiNotificationsResponseError {
                        description
                        details
                      }
                      ... on AiNotificationsDataValidationError {
                        details
                      }
                      ... on AiNotificationsConstraintsError {
                        constraints {
                          dependencies
                          name
                        }
                      }
                    }
                  }
                }
            """ % (self.destAccount)

            try:
                resp = self.sendRequest(q, 'dest', vars)
                if (resp.status_code == 200):
                    parsed = resp.json()
                    destResult = parsed['data']['aiNotificationsCreateDestination']
                else:
                    print('Unable to create destination: ' + str(resp.status_code))
            except Exception as e:
                print('Create Destination - Exception occurred')
                raise

            return(destResult)


#Get Destinations
# {
#   actor {
#     account(id: 1) {
#       aiNotifications {
#         destinations {
#           entities {
#             properties {
#               displayValue
#               key
#               label
#               value
#             }
#             active
#             name
#             type
#             id
#             status
#             auth {
#               ... on AiNotificationsBasicAuth {
#                 authType
#                 user
#               }
#             }
#           }
#         }
#       }
#     }
#   }
# }


#Create Destinations:

## Email Example -
# mutation {
#   aiNotificationsCreateDestination(accountId: 1, destination: {name: "test@gmail.com", properties: {key: "email", value: "test@gmail.com"}, type: EMAIL}) {
#     destination {
#       name
#       id
#     }
#     error {
#       ... on AiNotificationsResponseError {
#         description
#         details
#       }
#       ... on AiNotificationsDataValidationError {
#         details
#       }
#       ... on AiNotificationsConstraintsError {
#         constraints {
#           dependencies
#           name
#         }
#       }
#     }
#   }
# }


## SNOW Example -
# mutation {
#   aiNotificationsCreateDestination(destination: {name: "keagan-test-snow", properties: {key: "domain", value: "https://dev113099.service-now.com"}, type: SERVICE_NOW, auth: {basic: {password: "test", user: "admin"}, type: BASIC}}, accountId: 1) {
#     destination {
#       name
#       id
#     }
#     error {
#       ... on AiNotificationsResponseError {
#         description
#         details
#       }
#       ... on AiNotificationsDataValidationError {
#         details
#       }
#       ... on AiNotificationsConstraintsError {
#         constraints {
#           dependencies
#           name
#         }
#       }
#     }
#   }
# }

##Webhook Example -
# mutation {
#   aiNotificationsCreateDestination(destination: {name: "test", properties: {key: "url", value: "https://www.google2.com"}, type: WEBHOOK}, accountId: 1) {
#     destination {
#       name
#       id
#     }
#     error {
#       ... on AiNotificationsResponseError {
#         description
#         details
#       }
#       ... on AiNotificationsDataValidationError {
#         details
#       }
#       ... on AiNotificationsConstraintsError {
#         constraints {
#           dependencies
#           name
#         }
#       }
#     }
#   }
# }
