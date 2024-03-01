import requests

class Workflows():
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


    def getWorkflows(self):
        q = f'''
            {{
              actor {{
                account(id: {self.sourceAccount}) {{
                  aiWorkflows {{
                    workflows {{
                      entities {{
                        destinationConfigurations {{
                          channelId
                          name
                          type
                        }}
                        destinationsEnabled
                        enrichments {{
                          configurations {{
                            ... on AiWorkflowsNrqlConfiguration {{
                              query
                            }}
                          }}
                          name
                          id
                          type
                        }}
                        enrichmentsEnabled
                        id
                        issuesFilter {{
                          predicates {{
                            attribute
                            operator
                            values
                          }}
                          id
                          name
                          type
                        }}
                        mutingRulesHandling
                        workflowEnabled
                        name
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
                workflows = parsed['data']['actor']['account']['aiWorkflows']['workflows']['entities']
            else:
                print('Unable to fetch workflows: ' + str(resp.status_code))
        except Exception as e:
            print('Fetch Workflows - Exception occurred')
            raise

        return(workflows)

    def createWorkflow(self, channelId, workflow):
        if (workflow['enrichments']): #pass enrichments only if they exist
            vars = {
              "chanId": channelId,
              "enrichmentQuery": workflow['enrichments'][0]['configurations'][0]['query'],
              "enrichmentName": workflow['enrichments'][0]['name'],
              "enrichEnabled": workflow['enrichmentsEnabled'],
              "issuePredicates": workflow['issuesFilter']['predicates'],
              "filterType": workflow['issuesFilter']['type'],
              "mutingHandling": workflow['mutingRulesHandling'],
              "workflowName": workflow['name']
            }

            q = """
                mutation create($chanId: ID!, $enrichmentQuery: String!, $enrichmentName: String!, $enrichEnabled: Boolean!, $issuePredicates: [AiWorkflowsPredicateInput!]!, $filterType: AiWorkflowsFilterType!, $mutingHandling: AiWorkflowsMutingRulesHandling!, $workflowName: String!) {
                  aiWorkflowsCreateWorkflow(accountId: %d , createWorkflowData: {destinationConfigurations: {channelId: $chanId}, destinationsEnabled: true, enrichments: {nrql: {configuration: {query: $enrichmentQuery}, name: $enrichmentName}}, enrichmentsEnabled: $enrichEnabled, issuesFilter: {predicates: $issuePredicates, type: $filterType}, mutingRulesHandling: $mutingHandling, name: $workflowName, workflowEnabled: false}) {
                    errors {
                      type
                      description
                    }
                    workflow {
                      id
                      name
                    }
                  }
                }
            """ % self.destAccount
        else:
            vars = {
              "chanId": channelId,
              "issuePredicates": workflow['issuesFilter']['predicates'],
              "filterType": workflow['issuesFilter']['type'],
              "mutingHandling": workflow['mutingRulesHandling'],
              "workflowName": workflow['name']
            }

            q = """
                mutation create($chanId: ID!, $issuePredicates: [AiWorkflowsPredicateInput!]!, $filterType: AiWorkflowsFilterType!, $mutingHandling: AiWorkflowsMutingRulesHandling!, $workflowName: String!) {
                  aiWorkflowsCreateWorkflow(accountId: %d , createWorkflowData: {destinationConfigurations: {channelId: $chanId}, destinationsEnabled: true, issuesFilter: {predicates: $issuePredicates, type: $filterType}, mutingRulesHandling: $mutingHandling, name: $workflowName, workflowEnabled: false}) {
                    errors {
                      type
                      description
                    }
                    workflow {
                      id
                      name
                    }
                  }
                }
            """ % self.destAccount

        try:
            resp = self.sendRequest(q, 'dest', vars)
            if (resp.status_code == 200):
                parsed = resp.json()
                workflowResult = parsed['data']['aiWorkflowsCreateWorkflow']
            else:
                print('Unable to create workflow: ' + str(resp.status_code))
        except Exception as e:
            print('Create Workflow - Exception occurred')
            raise

        return(workflowResult)



#Get Workflows
# {
#   actor {
#     account(id: 1) {
#       aiWorkflows {
#         workflows {
#           entities {
#             destinationConfigurations {
#               channelId
#               name
#               type
#             }
#             destinationsEnabled
#             enrichments {
#               configurations {
#                 ... on AiWorkflowsNrqlConfiguration {
#                   query
#                 }
#               }
#               name
#               id
#               type
#             }
#             enrichmentsEnabled
#             id
#             issuesFilter {
#               predicates {
#                 attribute
#                 operator
#                 values
#               }
#               id
#               name
#               type
#             }
#             mutingRulesHandling
#             workflowEnabled
#             name
#           }
#         }
#       }
#     }
#   }
# }


#Create Workflows
# mutation {
#   aiWorkflowsCreateWorkflow(accountId: 1, createWorkflowData: {destinationConfigurations: {channelId: ""}, destinationsEnabled: false, enrichments: {nrql: {configuration: {query: ""}, name: ""}}, enrichmentsEnabled: true, issuesFilter: {name: "", predicates: {attribute: "", operator: CONTAINS, values: ""}, type: FILTER}, mutingRulesHandling: DONT_NOTIFY_FULLY_MUTED_ISSUES, name: "", workflowEnabled: false}) {
#     errors {
#       type
#       description
#     }
#     workflow {
#       id
#       name
#     }
#   }
# }
