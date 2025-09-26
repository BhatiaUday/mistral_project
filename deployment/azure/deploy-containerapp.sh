#!/bin/bash
set -e

echo "🚀 Deploying Smart Code Review Assistant to Azure Container Apps..."

# Configuration
APP_NAME="smart-code-review"
RESOURCE_GROUP="smart-code-review-rg"
LOCATION="eastus"
CONTAINERAPPS_ENVIRONMENT="smart-code-review-env"
CONTAINER_REGISTRY="smartcodereviewacr"

# Check if Azure CLI is installed and logged in
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI not found. Please install it first:"
    echo "   curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash"
    exit 1
fi

if ! az account show > /dev/null 2>&1; then
    echo "❌ Not logged in to Azure. Please run 'az login' first."
    exit 1
fi

# Install Container Apps extension if not already installed
echo "🔧 Installing Azure Container Apps extension..."
az extension add --name containerapp --upgrade --yes 2>/dev/null || true

# Read environment variables from .env file
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
    echo "✅ Loaded environment variables from .env"
else
    echo "❌ .env file not found. Please create it with your API keys."
    exit 1
fi

# Validate required environment variables
if [ -z "$GITHUB_TOKEN" ] || [ "$GITHUB_TOKEN" = "your_github_token_here" ]; then
    echo "❌ GITHUB_TOKEN not set in .env file"
    exit 1
fi

if [ -z "$MISTRAL_API_KEY" ] || [ "$MISTRAL_API_KEY" = "your_mistral_api_key_here" ]; then
    echo "❌ MISTRAL_API_KEY not set in .env file"
    exit 1
fi

if [ -z "$GITHUB_WEBHOOK_SECRET" ]; then
    echo "❌ GITHUB_WEBHOOK_SECRET not set in .env file"
    exit 1
fi

echo "✅ All required environment variables are set"

# Create resource group
echo "📦 Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION --output none
echo "✅ Resource group created: $RESOURCE_GROUP"

# Create Container Registry
echo "🏗️  Creating Azure Container Registry..."
az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $CONTAINER_REGISTRY \
    --sku Basic \
    --admin-enabled true \
    --output none 2>/dev/null || echo "✅ Container Registry already exists"

# Get ACR credentials
ACR_SERVER=$(az acr show --name $CONTAINER_REGISTRY --resource-group $RESOURCE_GROUP --query loginServer --output tsv)
ACR_USERNAME=$(az acr credential show --name $CONTAINER_REGISTRY --resource-group $RESOURCE_GROUP --query username --output tsv)
ACR_PASSWORD=$(az acr credential show --name $CONTAINER_REGISTRY --resource-group $RESOURCE_GROUP --query passwords[0].value --output tsv)

echo "✅ Container Registry: $ACR_SERVER"

# Build and push Docker image
echo "🐳 Building and pushing Docker image..."
az acr build --registry $CONTAINER_REGISTRY --image $APP_NAME:latest . --output none
echo "✅ Docker image built and pushed to ACR"

# Create Container Apps environment
echo "🌍 Creating Container Apps environment..."
az containerapp env create \
    --name $CONTAINERAPPS_ENVIRONMENT \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --output none 2>/dev/null || echo "✅ Container Apps environment already exists"

# Create the container app
echo "🚀 Creating Container App..."
az containerapp create \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $CONTAINERAPPS_ENVIRONMENT \
    --image "$ACR_SERVER/$APP_NAME:latest" \
    --registry-server $ACR_SERVER \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --target-port 8080 \
    --ingress external \
    --secrets \
        github-token="$GITHUB_TOKEN" \
        webhook-secret="$GITHUB_WEBHOOK_SECRET" \
        mistral-api-key="$MISTRAL_API_KEY" \
    --env-vars \
        GITHUB_TOKEN=secretref:github-token \
        GITHUB_WEBHOOK_SECRET=secretref:webhook-secret \
        MISTRAL_API_KEY=secretref:mistral-api-key \
        MISTRAL_MODEL=mistral-small \
        APP_HOST=0.0.0.0 \
        APP_PORT=8080 \
        LOG_LEVEL=INFO \
    --cpu 0.25 --memory 0.5Gi \
    --min-replicas 0 --max-replicas 3 \
    --output none

# Get the application URL
APP_URL=$(az containerapp show \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn \
    --output tsv)

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📋 Application Details:"
echo "   Name: $APP_NAME"
echo "   Resource Group: $RESOURCE_GROUP"
echo "   URL: https://$APP_URL"
echo "   Health Check: https://$APP_URL/health"
echo "   Status: https://$APP_URL/status"
echo ""
echo "🔗 GitHub Webhook URL: https://$APP_URL/webhook/github"
echo "🔑 Webhook Secret: $GITHUB_WEBHOOK_SECRET"
echo ""
echo "🧪 Test the deployment:"
echo "   curl https://$APP_URL/health"
echo ""
echo "📊 Monitor your app:"
echo "   az containerapp logs show --name $APP_NAME --resource-group $RESOURCE_GROUP --follow"
echo ""
echo "💰 Cost optimization:"
echo "   - The app will scale to zero when not in use"
echo "   - Estimated cost: $15-30/month depending on usage"
echo ""
echo "🎯 Next steps:"
echo "   1. Test your endpoints"
echo "   2. Configure GitHub webhooks"
echo "   3. Create a test PR to verify functionality"