# Asthma Guardian v3 Troubleshooting Guide

## Overview

This guide provides comprehensive troubleshooting information for common issues with Asthma Guardian v3, including technical problems, user issues, and system maintenance.

## Table of Contents

- [Common Issues](#common-issues)
- [Technical Troubleshooting](#technical-troubleshooting)
- [User Support Issues](#user-support-issues)
- [System Monitoring](#system-monitoring)
- [Performance Issues](#performance-issues)
- [Security Issues](#security-issues)
- [Emergency Procedures](#emergency-procedures)
- [Contact Information](#contact-information)

## Common Issues

### Application Not Loading

#### Symptoms
- Blank page or loading spinner that never completes
- "This site can't be reached" error
- 404 or 500 error pages

#### Troubleshooting Steps

1. **Check Internet Connection**
   ```bash
   # Test connectivity
   ping asthmaguardian.nsw.gov.au
   nslookup asthmaguardian.nsw.gov.au
   ```

2. **Clear Browser Cache**
   - Chrome: Ctrl+Shift+Delete → Clear browsing data
   - Firefox: Ctrl+Shift+Delete → Clear recent history
   - Safari: Cmd+Option+E → Empty caches

3. **Check Browser Console**
   ```javascript
   // Open Developer Tools (F12)
   // Check Console tab for errors
   console.log('Checking for JavaScript errors');
   ```

4. **Try Different Browser**
   - Test in Chrome, Firefox, Safari, or Edge
   - Check if issue is browser-specific

5. **Check System Status**
   - Visit: https://status.asthmaguardian.nsw.gov.au
   - Check for known issues or maintenance

#### Resolution
- If issue persists, contact support with browser details and error messages

### API Errors

#### Symptoms
- "Failed to load data" messages
- 401 Unauthorized errors
- 500 Internal Server Error
- Timeout errors

#### Troubleshooting Steps

1. **Check API Status**
   ```bash
   # Test API endpoint
   curl -I https://api.asthmaguardian.nsw.gov.au/api/health
   ```

2. **Verify Authentication**
   ```javascript
   // Check if token is present
   console.log('Token:', localStorage.getItem('jwt_token'));
   ```

3. **Check Network Tab**
   - Open Developer Tools → Network tab
   - Look for failed requests (red entries)
   - Check response status codes

4. **Test Different Endpoints**
   ```bash
   # Test basic endpoint
   curl https://api.asthmaguardian.nsw.gov.au/api/air-quality/current?postcode=2000
   ```

#### Resolution
- Check API documentation for correct usage
- Verify authentication token is valid
- Contact support if API is down

### Data Not Updating

#### Symptoms
- Air quality data appears stale
- User profile changes not saving
- Notifications not appearing

#### Troubleshooting Steps

1. **Check Data Freshness**
   ```javascript
   // Check timestamp of last update
   console.log('Last update:', airQualityData.timestamp);
   ```

2. **Force Refresh**
   - Hard refresh: Ctrl+F5 (Windows) or Cmd+Shift+R (Mac)
   - Clear cache and reload

3. **Check Data Sources**
   - Verify NSW Government API is accessible
   - Check external data source status

4. **Verify User Permissions**
   - Ensure user has correct access rights
   - Check if account is active

#### Resolution
- Refresh page or restart application
- Check if data source is experiencing issues
- Verify user account status

## Technical Troubleshooting

### CDK Deployment Issues

#### Common Errors

1. **Bootstrap Required**
   ```bash
   Error: This stack uses assets, so the toolkit stack must be deployed to the environment
   ```
   **Solution:**
   ```bash
   cdk bootstrap aws://ACCOUNT-NUMBER/REGION
   ```

2. **Permission Denied**
   ```bash
   Error: User is not authorized to perform: iam:CreateRole
   ```
   **Solution:**
   - Check IAM permissions
   - Ensure user has necessary roles
   - Contact AWS administrator

3. **Resource Already Exists**
   ```bash
   Error: Resource already exists
   ```
   **Solution:**
   ```bash
   cdk destroy StackName
   cdk deploy StackName
   ```

#### Debugging CDK Issues

1. **Enable Verbose Logging**
   ```bash
   cdk deploy --verbose
   ```

2. **Check CloudFormation Events**
   ```bash
   aws cloudformation describe-stack-events --stack-name StackName
   ```

3. **Validate Template**
   ```bash
   cdk synth
   aws cloudformation validate-template --template-body file://cdk.out/StackName.template.json
   ```

### Lambda Function Issues

#### Common Problems

1. **Function Timeout**
   ```python
   # Check function timeout
   aws lambda get-function-configuration --function-name function-name
   ```

2. **Memory Issues**
   ```python
   # Check memory usage
   aws lambda get-function-configuration --function-name function-name --query 'MemorySize'
   ```

3. **Permission Errors**
   ```python
   # Check IAM role
   aws lambda get-function --function-name function-name --query 'Configuration.Role'
   ```

#### Debugging Lambda

1. **Check Logs**
   ```bash
   aws logs tail /aws/lambda/function-name --follow
   ```

2. **Test Function Locally**
   ```python
   # Create test event
   test_event = {
       "httpMethod": "GET",
       "path": "/test",
       "queryStringParameters": {}
   }
   
   # Test handler
   from handler import handler
   result = handler(test_event, {})
   print(result)
   ```

3. **Check Environment Variables**
   ```bash
   aws lambda get-function-configuration --function-name function-name --query 'Environment'
   ```

### Database Issues

#### DynamoDB Problems

1. **Table Not Found**
   ```bash
   aws dynamodb describe-table --table-name table-name
   ```

2. **Permission Denied**
   ```bash
   aws dynamodb scan --table-name table-name --limit 1
   ```

3. **Throttling**
   ```bash
   # Check throttled requests
   aws cloudwatch get-metric-statistics \
     --namespace AWS/DynamoDB \
     --metric-name ThrottledRequests \
     --dimensions Name=TableName,Value=table-name \
     --start-time 2024-12-19T00:00:00Z \
     --end-time 2024-12-19T23:59:59Z \
     --period 3600 \
     --statistics Sum
   ```

#### Debugging Database

1. **Check Table Status**
   ```bash
   aws dynamodb describe-table --table-name table-name --query 'Table.TableStatus'
   ```

2. **Query Table Data**
   ```bash
   aws dynamodb scan --table-name table-name --limit 10
   ```

3. **Check Metrics**
   ```bash
   aws cloudwatch get-metric-statistics \
     --namespace AWS/DynamoDB \
     --metric-name ConsumedReadCapacityUnits \
     --dimensions Name=TableName,Value=table-name \
     --start-time 2024-12-19T00:00:00Z \
     --end-time 2024-12-19T23:59:59Z \
     --period 3600 \
     --statistics Sum
   ```

## User Support Issues

### Authentication Problems

#### Symptoms
- "Invalid credentials" error
- User can't log in
- Session expires immediately

#### Troubleshooting Steps

1. **Check Credentials**
   - Verify email address is correct
   - Check password (case-sensitive)
   - Try password reset

2. **Check Account Status**
   - Verify account is active
   - Check if account is locked
   - Contact support for account issues

3. **Clear Authentication Data**
   ```javascript
   // Clear stored tokens
   localStorage.removeItem('jwt_token');
   localStorage.removeItem('user_data');
   ```

4. **Check Browser Settings**
   - Ensure cookies are enabled
   - Check if JavaScript is enabled
   - Disable ad blockers temporarily

#### Resolution
- Reset password if needed
- Clear browser data and try again
- Contact support for account issues

### Profile Issues

#### Symptoms
- Profile data not saving
- Changes not reflected
- Validation errors

#### Troubleshooting Steps

1. **Check Required Fields**
   - Ensure all required fields are filled
   - Check for validation errors
   - Verify data format

2. **Check Network Connection**
   - Ensure stable internet connection
   - Try saving again
   - Check for timeout errors

3. **Clear Form Data**
   - Refresh the page
   - Re-enter information
   - Try saving again

#### Resolution
- Fill in all required fields
- Check internet connection
- Contact support if issue persists

### Notification Issues

#### Symptoms
- Not receiving notifications
- Notifications going to spam
- Wrong notification content

#### Troubleshooting Steps

1. **Check Notification Settings**
   - Verify notifications are enabled
   - Check notification preferences
   - Ensure correct email/phone number

2. **Check Email Settings**
   - Look in spam/junk folder
   - Check email filters
   - Add sender to safe list

3. **Check Quiet Hours**
   - Verify quiet hours settings
   - Check time zone settings
   - Adjust notification schedule

#### Resolution
- Update notification preferences
- Check email settings
- Contact support for notification issues

## System Monitoring

### Health Checks

#### API Health Check
```bash
# Check API status
curl -f https://api.asthmaguardian.nsw.gov.au/api/health
```

#### Database Health Check
```bash
# Check DynamoDB table
aws dynamodb describe-table --table-name asthma-guardian-users --query 'Table.TableStatus'
```

#### Frontend Health Check
```bash
# Check CloudFront distribution
aws cloudfront get-distribution --id DISTRIBUTION_ID --query 'Distribution.Status'
```

### Monitoring Tools

#### CloudWatch Metrics
```bash
# Get API Gateway metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApiGateway \
  --metric-name Count \
  --dimensions Name=ApiName,Value=asthma-guardian-v3-api \
  --start-time 2024-12-19T00:00:00Z \
  --end-time 2024-12-19T23:59:59Z \
  --period 3600 \
  --statistics Sum
```

#### Log Analysis
```bash
# Search logs for errors
aws logs filter-log-events \
  --log-group-name /aws/apigateway/asthma-guardian-v3-api \
  --filter-pattern "ERROR"
```

### Alerting

#### Set Up Alarms
```bash
# Create CloudWatch alarm
aws cloudwatch put-metric-alarm \
  --alarm-name "API-Error-Rate" \
  --alarm-description "API error rate too high" \
  --metric-name 5XXError \
  --namespace AWS/ApiGateway \
  --statistic Sum \
  --period 300 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold
```

## Performance Issues

### Slow Response Times

#### Symptoms
- Pages load slowly
- API calls timeout
- User complaints about performance

#### Troubleshooting Steps

1. **Check Response Times**
   ```bash
   # Test API response time
   curl -w "@curl-format.txt" -o /dev/null -s https://api.asthmaguardian.nsw.gov.au/api/health
   ```

2. **Check CloudWatch Metrics**
   ```bash
   # Get latency metrics
   aws cloudwatch get-metric-statistics \
     --namespace AWS/ApiGateway \
     --metric-name Latency \
     --start-time 2024-12-19T00:00:00Z \
     --end-time 2024-12-19T23:59:59Z \
     --period 300 \
     --statistics Average
   ```

3. **Check Database Performance**
   ```bash
   # Get DynamoDB metrics
   aws cloudwatch get-metric-statistics \
     --namespace AWS/DynamoDB \
     --metric-name SuccessfulRequestLatency \
     --dimensions Name=TableName,Value=asthma-guardian-users \
     --start-time 2024-12-19T00:00:00Z \
     --end-time 2024-12-19T23:59:59Z \
     --period 300 \
     --statistics Average
   ```

#### Resolution
- Scale up resources if needed
- Optimize database queries
- Implement caching strategies

### High Error Rates

#### Symptoms
- Many 4xx/5xx errors
- User complaints about errors
- System instability

#### Troubleshooting Steps

1. **Check Error Logs**
   ```bash
   # Search for errors
   aws logs filter-log-events \
     --log-group-name /aws/apigateway/asthma-guardian-v3-api \
     --filter-pattern "ERROR" \
     --start-time 1640000000000
   ```

2. **Check Error Metrics**
   ```bash
   # Get error rate
   aws cloudwatch get-metric-statistics \
     --namespace AWS/ApiGateway \
     --metric-name 4XXError \
     --start-time 2024-12-19T00:00:00Z \
     --end-time 2024-12-19T23:59:59Z \
     --period 300 \
     --statistics Sum
   ```

3. **Check Lambda Errors**
   ```bash
   # Get Lambda error metrics
   aws cloudwatch get-metric-statistics \
     --namespace AWS/Lambda \
     --metric-name Errors \
     --dimensions Name=FunctionName,Value=air-quality-lambda \
     --start-time 2024-12-19T00:00:00Z \
     --end-time 2024-12-19T23:59:59Z \
     --period 300 \
     --statistics Sum
   ```

#### Resolution
- Fix code issues causing errors
- Implement better error handling
- Add retry logic for transient errors

## Security Issues

### Authentication Bypass

#### Symptoms
- Users accessing data without authentication
- Unauthorized API access
- Security audit findings

#### Troubleshooting Steps

1. **Check API Gateway Configuration**
   ```bash
   # Check API Gateway authorizers
   aws apigateway get-authorizers --rest-api-id API_ID
   ```

2. **Check Lambda Function Permissions**
   ```bash
   # Check Lambda function policy
   aws lambda get-policy --function-name function-name
   ```

3. **Check IAM Roles**
   ```bash
   # Check IAM role policies
   aws iam get-role-policy --role-name role-name --policy-name policy-name
   ```

#### Resolution
- Fix authentication configuration
- Update IAM policies
- Implement proper authorization

### Data Breach

#### Symptoms
- Unauthorized data access
- Data exfiltration
- Security incident reports

#### Emergency Response

1. **Immediate Actions**
   - Isolate affected systems
   - Change all passwords and keys
   - Notify security team

2. **Investigation**
   - Check access logs
   - Identify compromised accounts
   - Assess data exposure

3. **Recovery**
   - Patch security vulnerabilities
   - Implement additional security measures
   - Notify affected users

## Emergency Procedures

### System Down

#### Immediate Response

1. **Check System Status**
   - Verify all services are running
   - Check CloudWatch alarms
   - Review recent deployments

2. **Activate Incident Response**
   - Notify on-call engineer
   - Create incident ticket
   - Start communication with users

3. **Begin Recovery**
   - Check logs for errors
   - Identify root cause
   - Implement fix

#### Recovery Steps

1. **Rollback if Needed**
   ```bash
   # Rollback to previous version
   cdk rollback StackName
   ```

2. **Scale Resources**
   ```bash
   # Increase Lambda concurrency
   aws lambda put-provisioned-concurrency-config \
     --function-name function-name \
     --provisioned-concurrency-config ProvisionedConcurrencyConfig='{ProvisionedConcurrencyConfig={AllocatedConcurrency=10}}'
   ```

3. **Monitor Recovery**
   - Watch CloudWatch metrics
   - Check user reports
   - Verify functionality

### Data Loss

#### Immediate Response

1. **Stop Data Processing**
   - Pause data ingestion
   - Stop user-facing services
   - Preserve current state

2. **Assess Damage**
   - Check backup status
   - Identify lost data
   - Estimate recovery time

3. **Begin Recovery**
   - Restore from backups
   - Replay transaction logs
   - Verify data integrity

#### Recovery Steps

1. **Restore from Backup**
   ```bash
   # Restore DynamoDB table
   aws dynamodb restore-table-from-backup \
     --target-table-name table-name \
     --backup-arn backup-arn
   ```

2. **Verify Data Integrity**
   ```bash
   # Check table item count
   aws dynamodb scan --table-name table-name --select COUNT
   ```

3. **Resume Services**
   - Gradually resume data processing
   - Monitor for issues
   - Notify users of recovery

## Contact Information

### Technical Support

- **Email**: tech-support@asthmaguardian.nsw.gov.au
- **Phone**: 1800 TECH (1800 832 424)
- **Hours**: 24/7 for critical issues

### User Support

- **Email**: support@asthmaguardian.nsw.gov.au
- **Phone**: 1800 ASTHMA (1800 278 462)
- **Hours**: 8 AM - 6 PM AEST

### Emergency Contacts

- **Security Issues**: security@asthmaguardian.nsw.gov.au
- **Data Breach**: incident-response@asthmaguardian.nsw.gov.au
- **System Down**: on-call@asthmaguardian.nsw.gov.au

### Escalation Procedures

1. **Level 1**: User Support
2. **Level 2**: Technical Support
3. **Level 3**: Engineering Team
4. **Level 4**: Architecture Team
5. **Level 5**: Management

### Documentation

- **API Documentation**: https://docs.asthmaguardian.nsw.gov.au/api
- **Developer Guide**: https://docs.asthmaguardian.nsw.gov.au/developer
- **User Guide**: https://docs.asthmaguardian.nsw.gov.au/user
- **Status Page**: https://status.asthmaguardian.nsw.gov.au

---

**Note**: This troubleshooting guide is regularly updated. For the latest version, visit our documentation site.
