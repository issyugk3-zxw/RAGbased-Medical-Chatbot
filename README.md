# RAGbased-Medical-Chatbot

This project presents a comprehensive system for a Retrieval-Augmented Generation (RAG) based medical chatbot specifically designed for the Chinese language. It integrates advanced techniques to enhance the accuracy and efficiency of medical information retrieval and generation.

## Introduction

This system innovatively combines knowledge graph with the Chroma vector database to reduce the computational complexity of searching relevant documents. We leverage a knowledge graph to structure medical information and utilize Large Language Model-driven Cypher query generation to automatically identify the correct subject area for a given query. This approach allows us to then efficiently search for documents within a specific, pre-defined subject database, rather than performing a computationally intensive search across the entire corpus. This focused retrieval strategy greatly improves the speed and precision of information delivery.

### System Architecture

The system is composed of two distinct parts:

- **Frontend:** Built with Electron and Vue3, providing a responsive and intuitive user interface for interaction. I used pixiv-live2d for digital human. The system allows you to input by texting and speaking.
- **Backend:** Handles the core logic, including knowledge graph interactions, LLM integrations, voice data processing, and vector database management. I built Socket and Http services.

### Pre-requisites and Setup

To run this system, please follow these preliminary steps:

1. **Dataset Construction:** Transform the "面向家庭常见疾病知识图谱" (Knowledge Graph for Common Family Diseases) dataset from Open-KG into a sequence labeling dataset.
2. **Cloud Storage Setup:** Configure a cloud OSS (Object Storage Service) server for temporary storage of voice message data. Ensure your access key and other necessary credentials are updated in `Backend/Models/CustomLLM/VoiceDataTransfer.py`.
3. **QWen API Key:** Obtain an API key for Aliyun's QWen model and insert it into `Backend/Models/CustomLLM/QWen.py` for model invocation.
4. **Database Configuration:** Set up Redis, MongoDB, and Chroma databases using `docker-compose`. The necessary `.yml` file is located in `Backend/Docker`.
5. Frontend Initialization:
   - Navigate to the `Frontend/medchatbot-system` directory.
   - Run `npm install` to install all required packages.
   - Execute `npm run start` to launch the Electron and Vue3 project.

### Forbidden

This repository is intended solely for academic study and research purposes. **Commercial use of this project is strictly prohibited.**

##Acknowledgements
I extend my sincere gratitude to the developer of [RAGQnASystem](https://github.com/honeyandme/RAGQnASystem) for the valuable contributions and inspiration.
