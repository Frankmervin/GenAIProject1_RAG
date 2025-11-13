# GenAIProject1_RAG

# How to run? 

### STEPS: 

### Step - 1: Create and activate virtual environment after opening the repository
    # Creating Command  :   python -m venv venv[Enter]
    # Activating Command:   venv\Scripts\activate[Enter]

### Step - 2: Install requirements.txt
    # pip install -r requirements.txt

### Step - 3: Get access to below applications 
    #1. AWS Account - Storage S3 (clould storage - RAG bucket )

### Step - 3: Run python file 
    # python app/main.py

### Step - 4: View Application 
Open up your local host and port 

### Step - 5: Implement CI/CD 
A. From local push to github from local (dev environment)
B. CI/CD - Github action, Jenkins , Circle CI - I'm going with Github Actions
C. for deployment we will use services - docker
D. ECR - Elastic Container Release from AWS - private 
E. EC2 - Virtual Machine Service 

    #i. Create a IAM User for deploymet with Specific access
    #ii. EC2 Access 
    #iii.ECR: Elastic Container registry to save your docker image in AWS

### Step - 6: Deployment 
1. Build docker image of the source code
2. Push your docker image of the source code
3. Launch your EC2
4. Pull your Image from ECR in EC2 
5. Launch your docker image in EC2

#Policy
1. AmazonEC2ContainerRegistryFullaccess
2. AmazonEC2FullAccess

### Create ECR repo to store//save docker image 
- Save the URI: 710735876999.dkr.ecr.ap-south-2.amazonaws.com/ai_screening_chatbot

### Set up EC2 Machine

### Open EC2 and Install docker in EC2 Machine

    #optional 

    sudo apt-get update -y

    sudo apt-get upgrade

    #required

    curl -fsSL https://get.docker.com -o get-docker.sh

    sudo sh get-docker.sh

    sudo usermod -aG docker ubuntu

    newgrp docker

### Configure EC2 as self - hosted runner:
    Settings > Actions > runner > New self hosted runner > choose os > Then run command one by one 

### Set up github secrets:
# OpenAI API Key
OPENAI_API_KEY
OPENAI_TIMEOUT
# AWS Credentials
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_BUCKET_NAME
AWS_EC2_REGION 
VECTOR_DB_PATH