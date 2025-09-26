# Azure Container Apps Deployment

## Option 1: Azure Container Apps (Recommended)

### 1. Prerequisites
```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login to Azure
az login

# Install Container Apps extension
az extension add --name containerapp --upgrade
```

### 2. Create Resource Group and Environment
```bash
# Set variables
RESOURCE_GROUP="smart-code-review-rg"
LOCATION="eastus"
CONTAINERAPPS_ENVIRONMENT="smart-code-review-env"

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Container Apps environment
az containerapp env create \
  --name $CONTAINERAPPS_ENVIRONMENT \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION
```

### 3. Deploy Container App
```bash
# Create container app
az containerapp create \
  --name smart-code-review \
  --resource-group $RESOURCE_GROUP \
  --environment $CONTAINERAPPS_ENVIRONMENT \
  --image udaybhatia/smart-code-review:latest \
  --target-port 8080 \
  --ingress external \
  --env-vars \
    APP_HOST=0.0.0.0 \
    APP_PORT=8080 \
    LOG_LEVEL=INFO \
    MISTRAL_MODEL=mistral-small \
  --secrets \
    github-token=$GITHUB_TOKEN \
    webhook-secret=$GITHUB_WEBHOOK_SECRET \
    mistral-api-key=$MISTRAL_API_KEY \
  --env-vars \
    GITHUB_TOKEN=secretref:github-token \
    GITHUB_WEBHOOK_SECRET=secretref:webhook-secret \
    MISTRAL_API_KEY=secretref:mistral-api-key \
  --cpu 0.25 --memory 0.5Gi \
  --min-replicas 0 --max-replicas 3
```

---

## Option 2: Azure App Service (Alternative)

### 1. Create App Service Plan
```bash
# Create App Service plan
az appservice plan create \
  --name smart-code-review-plan \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku B1 \
  --is-linux
```

### 2. Create Web App
```bash
# Create web app
az webapp create \
  --name smart-code-review-app \
  --resource-group $RESOURCE_GROUP \
  --plan smart-code-review-plan \
  --deployment-container-image-name udaybhatia/smart-code-review:latest
```

### 3. Configure App Settings
```bash
# Set application settings
az webapp config appsettings set \
  --name smart-code-review-app \
  --resource-group $RESOURCE_GROUP \
  --settings \
    GITHUB_TOKEN=$GITHUB_TOKEN \
    GITHUB_WEBHOOK_SECRET=$GITHUB_WEBHOOK_SECRET \
    MISTRAL_API_KEY=$MISTRAL_API_KEY \
    MISTRAL_MODEL=mistral-small \
    APP_HOST=0.0.0.0 \
    APP_PORT=8080 \
    LOG_LEVEL=INFO \
    WEBSITES_PORT=8080
```

---

## Option 3: Azure Kubernetes Service (AKS)

### 1. Create AKS Cluster
```bash
# Create AKS cluster
az aks create \
  --resource-group $RESOURCE_GROUP \
  --name smart-code-review-aks \
  --node-count 1 \
  --node-vm-size Standard_B2s \
  --enable-managed-identity \
  --generate-ssh-keys
```

### 2. Deploy with Kubernetes manifests
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: smart-code-review
spec:
  replicas: 2
  selector:
    matchLabels:
      app: smart-code-review
  template:
    metadata:
      labels:
        app: smart-code-review
    spec:
      containers:
      - name: smart-code-review
        image: udaybhatia/smart-code-review:latest
        ports:
        - containerPort: 8080
        env:
        - name: GITHUB_TOKEN
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: github-token
        - name: GITHUB_WEBHOOK_SECRET
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: webhook-secret
        - name: MISTRAL_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: mistral-api-key
        - name: MISTRAL_MODEL
          value: "mistral-small"
        - name: APP_HOST
          value: "0.0.0.0"
        - name: APP_PORT
          value: "8080"
        - name: LOG_LEVEL
          value: "INFO"
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: smart-code-review-service
spec:
  selector:
    app: smart-code-review
  ports:
  - port: 80
    targetPort: 8080
  type: LoadBalancer
```

---

## Cost Comparison

### Container Apps (Recommended):
- $0.000024/vCPU second + $0.000004/GiB second
- Scale to zero when not in use
- ~$15-30/month depending on usage

### App Service B1:
- ~$13.14/month
- Always running
- 1.75GB RAM, 1 vCPU

### AKS:
- Node costs: ~$30/month (Standard_B2s)
- Plus ingress controller costs
- More complex but highly scalable

---

## Security Best Practices

### 1. Use Azure Key Vault
```bash
# Create Key Vault
az keyvault create \
  --name smart-code-review-kv \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# Store secrets
az keyvault secret set --vault-name smart-code-review-kv --name github-token --value $GITHUB_TOKEN
az keyvault secret set --vault-name smart-code-review-kv --name webhook-secret --value $GITHUB_WEBHOOK_SECRET
az keyvault secret set --vault-name smart-code-review-kv --name mistral-api-key --value $MISTRAL_API_KEY
```

### 2. Enable Managed Identity
```bash
# Enable system-assigned managed identity
az containerapp identity assign \
  --name smart-code-review \
  --resource-group $RESOURCE_GROUP \
  --system-assigned
```

### 3. Network Security
- Use Virtual Network integration
- Configure Network Security Groups
- Enable HTTPS only
- Use Azure Front Door for global distribution