import requests

class Decisions():
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

    def getDecisions(self):
        q = """
            {
              actor {
                account(id: %d) {
                  aiDecisions {
                    decisions(decisionStates: ENABLED) {
                      decisions {
                        annotations {
                          key
                          value
                        }
                        correlationWindowLength
                        decisionExpression
                        decisionType
                        description
                        id
                        metadata {
                          mergeOpinionCount {
                            count
                            opinion
                          }
                        }
                        minCorrelationThreshold
                        name
                        overrideConfiguration {
                          description
                          priority
                          title
                        }
                        source
                        state
                      }
                    }
                  }
                }
              }
            }
        """ % self.sourceAccount

        try:
            resp = self.sendRequest(q, 'source', {})
            if (resp.status_code == 200):
                parsed = resp.json()
                decisions = parsed['data']['actor']['account']['aiDecisions']['decisions']['decisions']
            else:
                print('Unable to fetch decisions: ' + str(resp.status_code))
        except Exception as e:
            print('Fetch Decisions - Exception occurred')
            raise

        return(decisions)

    def createDecision(self, decision):
        vars = {
          "windowLength": decision['correlationWindowLength'],
          "description": decision['description'],
          "minThreshold": decision['minCorrelationThreshold'],
          "name": decision['name'],
          "ruleExpression": decision['decisionExpression'],
          "ruleType": decision['decisionType'],
          "source": decision['source']
        }

        q = """
        mutation create($windowLength: Milliseconds!, $description: String!, $minThreshold: Int!, $name: String!, $ruleExpression: AiDecisionsRuleExpressionInput!, $ruleType: AiDecisionsRuleType!, $source: AiDecisionsRuleSource!) {
          aiDecisionsCreateRule(accountId: %d, rule: {correlationWindowLength: $windowLength, description: $description, minCorrelationThreshold: $minThreshold, name: $name, ruleExpression: $ruleExpression, ruleType: $ruleType, source: $source}) {
            id
            name
          }
        }
        """ % self.destAccount

        try:
            resp = self.sendRequest(q, 'dest', vars)
            parsed = resp.json()
            if ('errors' in parsed):
                print('Unable to create decision')
                print(parsed['errors'])
                decisionResult = None
            else:
                decisionResult = parsed['data']['aiDecisionsCreateRule']
        except Exception as e:
            print('Create Decision - Exception occurred')
            raise

        return(decisionResult)



#Get Decisions
# {
#   actor {
#     account(id: 1) {
#       aiDecisions {
#         decisions {
#           decisions {
#             annotations {
#               key
#               value
#             }
#             correlationWindowLength
#             decisionExpression
#             decisionType
#             description
#             id
#             metadata {
#               mergeOpinionCount {
#                 count
#                 opinion
#               }
#             }
#             minCorrelationThreshold
#             name
#             overrideConfiguration {
#               description
#               priority
#               title
#             }
#             source
#             state
#           }
#         }
#       }
#     }
#   }
# }


#Create Decisions
# mutation {
#   aiDecisionsCreateRule(accountId: 2759999, rule: {correlationWindowLength: 0, description: "", minCorrelationThreshold: 0, name: "", ruleExpression: {}, ruleType: GLOBAL, source: USER})
# }
