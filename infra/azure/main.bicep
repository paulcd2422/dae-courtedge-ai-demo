// Azure hosting for the ProGear Sales Agent frontend (Next.js, containerised).
//
// Creates:
//   - Azure Container Registry (holds the frontend image)
//   - Linux App Service Plan
//   - Web App for Containers with a system-assigned identity that pulls from ACR
//
// Deploy (resource-group scope):
//   az group create -n rg-progear-demo -l uksouth
//   az deployment group create -g rg-progear-demo -f infra/azure/main.bicep \
//     -p appName=progear-frontend-<unique> acrName=progearacr<unique> \
//        nextAuthSecret=<secret> oktaClientSecret=<secret>
//
// The GitHub Actions workflow (.github/workflows/deploy-frontend-azure.yml)
// then builds the image, pushes it to ACR and points the Web App at it.

targetScope = 'resourceGroup'

@description('Globally unique Web App name. Public URL becomes https://<appName>.azurewebsites.net')
param appName string

@description('Globally unique ACR name (5-50 alphanumeric characters).')
param acrName string

@description('Azure region.')
param location string = resourceGroup().location

@description('App Service Plan SKU. B1 is the cheapest always-on Linux tier.')
param planSku string = 'B1'

@description('Image repository name inside ACR.')
param imageRepository string = 'progear-frontend'

@description('Image tag to run. The deploy workflow overwrites this on each release.')
param imageTag string = 'latest'

@secure()
@description('NextAuth session encryption secret (openssl rand -base64 32).')
param nextAuthSecret string

@secure()
@description('Okta OIDC application client secret.')
param oktaClientSecret string

var acrLoginServer = '${acr.name}.azurecr.io'
var acrPullRoleId = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')

resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: acrName
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: false
  }
}

resource plan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: '${appName}-plan'
  location: location
  kind: 'linux'
  sku: {
    name: planSku
  }
  properties: {
    reserved: true // required for Linux
  }
}

resource webApp 'Microsoft.Web/sites@2023-01-01' = {
  name: appName
  location: location
  kind: 'app,linux,container'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: plan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'DOCKER|${acrLoginServer}/${imageRepository}:${imageTag}'
      acrUseManagedIdentityCreds: true
      alwaysOn: true
      http20Enabled: true
      minTlsVersion: '1.2'
      ftpsState: 'Disabled'
      healthCheckPath: '/api/debug'
      appSettings: [
        // Next.js standalone server listens on PORT; tell App Service which port the container exposes.
        { name: 'WEBSITES_PORT', value: '3000' }
        { name: 'PORT', value: '3000' }
        { name: 'HOSTNAME', value: '0.0.0.0' }
        { name: 'NODE_ENV', value: 'production' }
        { name: 'DOCKER_REGISTRY_SERVER_URL', value: 'https://${acrLoginServer}' }
        // Runtime (server-only) configuration. NEXT_PUBLIC_* values are baked
        // into the image at build time by the workflow, not set here.
        { name: 'NEXTAUTH_URL', value: 'https://${appName}.azurewebsites.net' }
        { name: 'NEXTAUTH_SECRET', value: nextAuthSecret }
        { name: 'OKTA_CLIENT_SECRET', value: oktaClientSecret }
      ]
    }
  }
}

// Allow the Web App's managed identity to pull images from ACR.
resource acrPull 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(acr.id, webApp.id, acrPullRoleId)
  scope: acr
  properties: {
    roleDefinitionId: acrPullRoleId
    principalId: webApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

output webAppUrl string = 'https://${webApp.properties.defaultHostName}'
output acrLoginServer string = acrLoginServer
output oktaSignInRedirectUri string = 'https://${webApp.properties.defaultHostName}/api/auth/callback/okta'
output oktaSignOutRedirectUri string = 'https://${webApp.properties.defaultHostName}/auth/signin'
