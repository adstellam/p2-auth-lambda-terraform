import cognitojwt
import re

def lambda_handler(event, context):

    methodArn = event['methodArn']
    authorizationToken = event['authorizedToken']
    print("MethodArn: " + methodArn)
    print("authorizationToken: " + authorizationToken)
    
    if authorizationToken.startwith('Bearer') or authorizationToken.startwith('bearer'):
        authorizationToken = authorizationToken[7:]
    cognitoRegion = 'us-west-1'
    cognitoUserPoolId = 'us-west-1_ZGkthDlkr'
    cognitoClientId = '6egh8631ivbaku0pcpfgb760q5'
    verifiedPayload = cognitojwt.decode(authorizationToken, cognitoRegion, cognitoUserPoolId, cognitoClientId)
    if verifiedPayload == None:
        raise Exception('Unauthorized')
    principalId = verifiedPayload['cognito:username']
    
    policy = AuthPolicy(principalId, methodArn)
    policy.allowMethod(HttpVerb.ALL, '/')
    #policy.denyMethod()
    authResponse = policy.build()
    authResponse['context'] = context

    return authResponse


class HttpVerb:
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    PATCH = 'PATCH'
    HEAD = 'HEAD'
    DELETE = 'DELETE'
    OPTIONS = 'OPTIONS'
    ALL = '*'


class AuthPolicy(object):

    def __init__(self, principalId, methodArn):

        self.principalId = principalId
        self.methodArn = methodArn
        self.version = '2012-10-17'
        self.allowMethods = []
        self.denyMethods = []
        self.pathRegex = '^[/.a-zA-Z0-9-\*]+$'
        self.region = methodArn.split(':')[3]
        self.awsAccountId = methodArn.split(':')[4]
        self.restApiId = methodArn.split(':')[5].split('/')[0]
        self.stage = methodArn.split(':')[5].split('/')[1]

    def _addMethod(self, effect, verb, resource, conditions):

        if verb != '*' and not hasattr(HttpVerb, verb):
            raise NameError('Invalid HTTP verb ' + verb)
        resourcePattern = re.compile(self.pathRegex)
        if not resourcePattern.match(resource):
            raise NameError('Invalid resource path: ' + resource)
        if resource[:1] == '/':
            resource = resource[1:]
        resourceArn = 'arn:aws:execute-api:{}:{}:{}/{}/{}/{}'.format(self.region, self.awsAccountId, self.restApiId, self.stage, verb, resource)

        if effect.lower() == 'allow':
            self.allowMethods.append({
                'resourceArn': resourceArn,
                'conditions': conditions
            })
        elif effect.lower() == 'deny':
            self.denyMethods.append({
                'resourceArn': resourceArn,
                'conditions': conditions
            })

    def _getEmptyStatement(self, effect):

        statement = {
            'Action': 'execute-api:Invoke',
            'Effect': effect[:1].upper() + effect[1:].lower(),
            'Resource': []
        }

        return statement

    def _getStatementForEffect(self, effect, methods):

        statements = []
        if len(methods) > 0:
            statement = self._getEmptyStatement(effect)
            for method in methods:
                if method['conditions'] is None or len(method['conditions']) == 0:
                    statement['Resource'].append(method['resourceArn'])
                else:
                    conditionalStatement = self._getEmptyStatement(effect)
                    conditionalStatement['Resource'].append(method['resourceArn'])
                    conditionalStatement['Condition'] = method['conditions']
                    statements.append(conditionalStatement)
            if statement['Resource']:
                statements.append(statement)

        return statements

    def allowAllMethods(self):
        self._addMethod('Allow', HttpVerb.ALL, '*', [])

    def denyAllMethods(self):
        self._addMethod('Deny', HttpVerb.ALL, '*', [])

    def allowMethod(self, verb, resource):
        self._addMethod('Allow', verb, resource, [])

    def denyMethod(self, verb, resource):
        self._addMethod('Deny', verb, resource, [])

    def allowMethodWithConditions(self, verb, resource, conditions):
        self._addMethod('Allow', verb, resource, conditions)

    def denyMethodWithConditions(self, verb, resource, conditions):
        self._addMethod('Deny', verb, resource, conditions)

    def build(self):

        if ((self.allowMethods is None or len(self.allowMethods) == 0) and
            (self.denyMethods is None or len(self.denyMethods) == 0)):
            raise NameError('No statements defined for the policy')

        policy = {
            'principalId': self.principalId,
            'policyDocument': {
                'Version': self.version,
                'Statement': []
            }
        }

        policy['policyDocument']['Statement'].extend(self._getStatementForEffect('Allow', self.allowMethods))
        policy['policyDocument']['Statement'].extend(self._getStatementForEffect('Deny', self.denyMethods))

        return policy
