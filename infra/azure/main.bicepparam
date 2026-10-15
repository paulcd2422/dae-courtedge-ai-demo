using './main.bicep'

// Copy and edit, then:
//   az deployment group create -g <rg> -f infra/azure/main.bicep -p infra/azure/main.bicepparam
param appName = 'progear-frontend-CHANGEME'
param acrName = 'progearacrCHANGEME'
param planSku = 'B1'

// Okta OIDC - Org Authorization Server URL (no /oauth2/<id> suffix) and client ID.
param oktaIssuer = 'https://your-org.okta.com'
param oktaClientId = '0oaCHANGEME'

// Supply secrets from the environment rather than committing them:
//   export NEXTAUTH_SECRET=$(openssl rand -base64 32)
//   export OKTA_CLIENT_SECRET=...
param nextAuthSecret = readEnvironmentVariable('NEXTAUTH_SECRET')
param oktaClientSecret = readEnvironmentVariable('OKTA_CLIENT_SECRET')
