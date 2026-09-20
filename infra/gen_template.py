"""Generates infra/backend.json (CloudFormation) for the API, auth, tables and media bucket."""
import json, sys, re
ORIGINS = ["https://srivenkaiahswamy.com", "https://www.srivenkaiahswamy.com", "https://bhagavansrivenkaiahswamy.com", "https://www.bhagavansrivenkaiahswamy.com", "https://bhagavansrivenkaiahswamy.org", "https://www.bhagavansrivenkaiahswamy.org", "https://venkayaswamy.com", "https://www.venkayaswamy.com",
           "http://localhost:3000", "https://localhost"]
PUBLIC = [("GET", "/events"), ("GET", "/media"), ("GET", "/sponsors/dates"), ("POST", "/sponsors")]
AUTH = [("POST", "/events"), ("PUT", "/events/{id}"), ("DELETE", "/events/{id}"), ("POST", "/media/upload-url"), ("POST", "/media"),
        ("DELETE", "/media/{id}"), ("GET", "/sponsors"), ("PUT", "/sponsors/{id}"), ("GET", "/users"), ("POST", "/users"), ("DELETE", "/users/{username}")]

def table(name):
    return {"Type": "AWS::DynamoDB::Table", "Properties": {"TableName": {"Fn::Sub": "${AWS::StackName}-" + name}, "BillingMode": "PAY_PER_REQUEST",
            "AttributeDefinitions": [{"AttributeName": "id", "AttributeType": "S"}], "KeySchema": [{"AttributeName": "id", "KeyType": "HASH"}],
            "PointInTimeRecoverySpecification": {"PointInTimeRecoveryEnabled": True}}}

R = {
 "UserPool": {"Type": "AWS::Cognito::UserPool", "Properties": {"UserPoolName": {"Fn::Sub": "${AWS::StackName}-users"}, "UsernameAttributes": ["email"],
   "AutoVerifiedAttributes": ["email"], "MfaConfiguration": "OFF", "AdminCreateUserConfig": {"AllowAdminCreateUserOnly": True,
   "InviteMessageTemplate": {"EmailSubject": "Your login for Sri Venkaiah Swamy Temple website",
     "EmailMessage": "Namaskaram,<br><br>You have been given access to the Sri Venkaiah Swamy Temple website.<br>Sign in at https://srivenkaiahswamy.com/admin/<br><br>Username: {username}<br>Temporary password: {####}<br><br>You will be asked to choose a new password on first login."}},
   "Policies": {"PasswordPolicy": {"MinimumLength": 8, "RequireUppercase": False, "RequireNumbers": True, "RequireSymbols": False, "RequireLowercase": True}},
   "Schema": [{"Name": "email", "Required": True, "Mutable": True}]}},
 "UserPoolClient": {"Type": "AWS::Cognito::UserPoolClient", "Properties": {"ClientName": "web", "UserPoolId": {"Ref": "UserPool"}, "GenerateSecret": False,
   "ExplicitAuthFlows": ["ALLOW_USER_PASSWORD_AUTH", "ALLOW_USER_SRP_AUTH", "ALLOW_REFRESH_TOKEN_AUTH"], "PreventUserExistenceErrors": "ENABLED",
   "AccessTokenValidity": 12, "IdTokenValidity": 12, "RefreshTokenValidity": 30, "TokenValidityUnits": {"AccessToken": "hours", "IdToken": "hours", "RefreshToken": "days"}}},
 "AdminGroup": {"Type": "AWS::Cognito::UserPoolGroup", "Properties": {"GroupName": "admin", "UserPoolId": {"Ref": "UserPool"}, "Description": "Full access"}},
 "MemberGroup": {"Type": "AWS::Cognito::UserPoolGroup", "Properties": {"GroupName": "member", "UserPoolId": {"Ref": "UserPool"}, "Description": "Can upload photos and videos"}},
 "EventsTable": table("events"), "SponsorsTable": table("sponsors"), "MediaTable": table("media"), "MessagesTable": table("messages"),
 "MediaBucket": {"Type": "AWS::S3::Bucket", "Properties": {"BucketName": {"Fn::Sub": "${AWS::StackName}-media-${AWS::AccountId}"},
   "PublicAccessBlockConfiguration": {"BlockPublicAcls": True, "BlockPublicPolicy": True, "IgnorePublicAcls": True, "RestrictPublicBuckets": True},
   "BucketEncryption": {"ServerSideEncryptionConfiguration": [{"ServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]},
   "CorsConfiguration": {"CorsRules": [{"AllowedOrigins": ORIGINS, "AllowedMethods": ["PUT", "GET", "HEAD"], "AllowedHeaders": ["*"], "MaxAge": 3600}]}}},
 "MediaBucketPolicy": {"Type": "AWS::S3::BucketPolicy", "Properties": {"Bucket": {"Ref": "MediaBucket"}, "PolicyDocument": {"Version": "2012-10-17", "Statement": [
   {"Sid": "CloudFrontRead", "Effect": "Allow", "Principal": {"Service": "cloudfront.amazonaws.com"}, "Action": "s3:GetObject", "Resource": {"Fn::Sub": "${MediaBucket.Arn}/*"},
    "Condition": {"StringEquals": {"AWS:SourceArn": {"Fn::Sub": "arn:aws:cloudfront::${AWS::AccountId}:distribution/${DistributionId}"}}}}]}}},
 "FnRole": {"Type": "AWS::IAM::Role", "Properties": {"AssumeRolePolicyDocument": {"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"}]},
   "ManagedPolicyArns": ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"],
   "Policies": [{"PolicyName": "app", "PolicyDocument": {"Version": "2012-10-17", "Statement": [
     {"Effect": "Allow", "Action": ["dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:UpdateItem", "dynamodb:DeleteItem", "dynamodb:Scan", "dynamodb:Query"],
      "Resource": [{"Fn::GetAtt": ["EventsTable", "Arn"]}, {"Fn::GetAtt": ["SponsorsTable", "Arn"]}, {"Fn::GetAtt": ["MediaTable", "Arn"]}, {"Fn::GetAtt": ["MessagesTable", "Arn"]}]},
     {"Effect": "Allow", "Action": ["translate:TranslateText"], "Resource": "*"},
     {"Effect": "Allow", "Action": ["s3:PutObject", "s3:GetObject", "s3:DeleteObject"], "Resource": {"Fn::Sub": "${MediaBucket.Arn}/*"}},
     {"Effect": "Allow", "Action": ["ses:SendEmail", "ses:SendRawEmail"], "Resource": "*"},
     {"Effect": "Allow", "Action": ["sns:Publish"], "NotResource": "arn:aws:sns:*:*:*"},
     {"Effect": "Allow", "Action": ["cognito-idp:ListUsers", "cognito-idp:AdminCreateUser", "cognito-idp:AdminDeleteUser", "cognito-idp:AdminAddUserToGroup", "cognito-idp:AdminListGroupsForUser"],
      "Resource": {"Fn::GetAtt": ["UserPool", "Arn"]}}]}}]}},
 "Fn": {"Type": "AWS::Lambda::Function", "Properties": {"FunctionName": {"Fn::Sub": "${AWS::StackName}-api"}, "Runtime": "python3.12", "Handler": "app.handler",
   "Role": {"Fn::GetAtt": ["FnRole", "Arn"]}, "Timeout": 20, "MemorySize": 256,
   "Code": {"S3Bucket": {"Ref": "CodeBucket"}, "S3Key": {"Ref": "CodeKey"}},
   "Environment": {"Variables": {"EVENTS_TABLE": {"Ref": "EventsTable"}, "SPONSORS_TABLE": {"Ref": "SponsorsTable"}, "MEDIA_TABLE": {"Ref": "MediaTable"}, "MESSAGES_TABLE": {"Ref": "MessagesTable"},
     "MEDIA_BUCKET": {"Ref": "MediaBucket"}, "USER_POOL_ID": {"Ref": "UserPool"}, "SENDER_EMAIL": {"Ref": "SenderEmail"}, "ADMIN_EMAIL": {"Ref": "AdminEmail"}, "SITE_URL": {"Ref": "SiteUrl"}}}}},
 "Api": {"Type": "AWS::ApiGatewayV2::Api", "Properties": {"Name": {"Fn::Sub": "${AWS::StackName}-api"}, "ProtocolType": "HTTP",
   "CorsConfiguration": {"AllowOrigins": ORIGINS, "AllowMethods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], "AllowHeaders": ["authorization", "content-type"], "MaxAge": 3600}}},
 "Stage": {"Type": "AWS::ApiGatewayV2::Stage", "Properties": {"ApiId": {"Ref": "Api"}, "StageName": "$default", "AutoDeploy": True}},
 "Integration": {"Type": "AWS::ApiGatewayV2::Integration", "Properties": {"ApiId": {"Ref": "Api"}, "IntegrationType": "AWS_PROXY", "PayloadFormatVersion": "2.0",
   "IntegrationUri": {"Fn::GetAtt": ["Fn", "Arn"]}}},
 "Authorizer": {"Type": "AWS::ApiGatewayV2::Authorizer", "Properties": {"ApiId": {"Ref": "Api"}, "AuthorizerType": "JWT", "Name": "cognito", "IdentitySource": ["$request.header.Authorization"],
   "JwtConfiguration": {"Audience": [{"Ref": "UserPoolClient"}], "Issuer": {"Fn::Sub": "https://cognito-idp.${AWS::Region}.amazonaws.com/${UserPool}"}}}},
 "FnPermission": {"Type": "AWS::Lambda::Permission", "Properties": {"Action": "lambda:InvokeFunction", "FunctionName": {"Ref": "Fn"}, "Principal": "apigateway.amazonaws.com",
   "SourceArn": {"Fn::Sub": "arn:aws:execute-api:${AWS::Region}:${AWS::AccountId}:${Api}/*"}}},
}
def route(name, method, path, auth):
    p = {"ApiId": {"Ref": "Api"}, "RouteKey": f"{method} {path}", "Target": {"Fn::Sub": "integrations/${Integration}"}}
    if auth:
        p["AuthorizationType"] = "JWT"; p["AuthorizerId"] = {"Ref": "Authorizer"}
    R[name] = {"Type": "AWS::ApiGatewayV2::Route", "Properties": p}
# Route logical names are positional; never reorder PUBLIC/AUTH. Add new routes to EXTRA only.
EXTRA = [("GET", "/youtube", False), ("GET", "/messages", False), ("POST", "/messages", True), ("DELETE", "/messages/{id}", True)]
i = 0
for m, p in PUBLIC: i += 1; route(f"RoutePub{i}", m, p, False)
for m, p in AUTH: i += 1; route(f"RouteAuth{i}", m, p, True)
for n, (m, p, a) in enumerate(EXTRA, 1): route(f"RouteExtra{n}", m, p, a)

T = {"AWSTemplateFormatVersion": "2010-09-09", "Description": "Sri Venkaiah Swamy Temple site backend: auth, API, tables, media",
 "Parameters": {"CodeBucket": {"Type": "String"}, "CodeKey": {"Type": "String"}, "DistributionId": {"Type": "String"},
   "SenderEmail": {"Type": "String"}, "AdminEmail": {"Type": "String"}, "SiteUrl": {"Type": "String", "Default": "https://srivenkaiahswamy.com"}},
 "Resources": R,
 "Outputs": {"ApiUrl": {"Value": {"Fn::GetAtt": ["Api", "ApiEndpoint"]}}, "UserPoolId": {"Value": {"Ref": "UserPool"}}, "ClientId": {"Value": {"Ref": "UserPoolClient"}},
   "MediaBucket": {"Value": {"Ref": "MediaBucket"}}, "MediaBucketDomain": {"Value": {"Fn::GetAtt": ["MediaBucket", "RegionalDomainName"]}}}}
json.dump(T, open(sys.argv[1] if len(sys.argv) > 1 else "backend.json", "w"), indent=1)
print("template written,", len(R), "resources")
