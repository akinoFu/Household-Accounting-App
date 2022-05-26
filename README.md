# Household-Accounting-App
## 1. About
- A school project associated with the Computer Information Technology Diploma program at British Columbia Institute of Technology (BC, Canada)
- Built as microservices architecture consisting of 8 services
- Each developed service has a Jenkins pipeline and Dockerfile
- Automatically deploy the service to Azure VM in every checkin using Jenkins Piplines
![Alt text](https://i.ibb.co/M2pRhB6/household-accounting-app1.jpg)
![Alt text](https://i.ibb.co/mByscm8/household-accounting-app2.jpg)
## 2. Repository Directries
| Dir Name | Description |
| --------| --------|
| ci_functions | Shared libraries for Jenkins pipelines of each service |
| deployment | Stores docker-compose.yml |
| src |  Contains source code for 6 services |
## 3. Requirements
- An Azure VM with Docker installed 
- Jenkins pipelines for 6 services: Audit, Health, Processing, Receiver, Storage and Dashboard UI
