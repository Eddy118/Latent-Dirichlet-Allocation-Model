# README for Latent Model Flask Project

## Overview

This project is a Flask-based web application that processes and clusters documents, utilizing natural language processing (NLP) and a topic modeling approach using Latent Dirichlet Allocation (LDA). The application fetches documents from a corpus, performs topic extraction, and stores the results in MongoDB. Additionally, it provides an API for querying the clustered documents based on specified criteria.

## Features

- **Document Processing:** Uses NLP techniques such as tokenization, lemmatization, and stopword removal to process the documents.
- **Clustering:** Documents are clustered using Gensim's LDA model to extract topics and determine suitable categories.
- **Storage:** Extracted topics and categorized documents are stored in MongoDB for future access.
- **APIs:**
  - Fetch all documents: `GET /documents`
  - Fetch matching documents based on selected categories: `POST /documents/match`
- **Cron Job:** A background scheduler runs every 12 hours to fetch documents, perform clustering, and update the MongoDB database.

## Technologies Used

- **Flask:** For building the web API.
- **MongoDB:** For storing the clustered document data.
- **Gensim:** For topic modeling using LDA.
- **NLTK:** For text preprocessing, including tokenization, stopword removal, and lemmatization.
- **APScheduler:** For setting up a background scheduler to run document clustering every 12 hours.
- **Flask-CORS:** To allow cross-origin requests.

## Prerequisites

Ensure you have Python 3 installed and have the necessary dependencies. Below are the major libraries required:

- Flask
- pymongo
- APScheduler
- gensim
- nltk
- Flask-CORS
- certifi

You can install the required dependencies using the following command:

```bash
pip install Flask pymongo apscheduler gensim nltk flask-cors certifi
```

## Project Structure

- `latenent-model.py`: Main file that contains the Flask application, background scheduler, and routes to handle document processing and clustering.
  
## How to Run the Project

1. **Clone the Repository** (if applicable)
   ```bash
   git clone https://github.com/Eddy118/Latent-Dirichlet-Allocation-Model.git
   cd Latent-Dirichlet-Allocation-Model
   ```

2. **Set Up MongoDB**

   Make sure you have MongoDB running on `localhost:27017`. This project connects to a MongoDB database named `readIt` and uses a collection named `documents`.

3. **Run the Flask Application**

   Execute the following command to start the Flask server:
   ```bash
   python3 latenent-model.py
   ```

   The server will start and listen at `http://127.0.0.1:5000/`.

## API Endpoints

### 1. `GET /documents`
- **Description:** Fetches all the documents currently stored in the MongoDB collection.
- **Response:** A JSON array containing all the documents.

### 2. `POST /documents/match`
- **Description:** Fetches all matching documents based on the selected categories.
- **Request Body:** JSON object containing categories to match.
- **Response:** A JSON array of documents that match the given categories.

## Scheduler Details

The background scheduler, implemented using APScheduler, runs every 12 hours and performs the following operations:

1. Fetches all documents from the corpus (`nltk.corpus.reuters`).
2. Preprocesses the documents (tokenization, removing stopwords, and lemmatization).
3. Uses Gensim's LDA model to determine document topics.
4. Updates the MongoDB collection with the clustered documents.

## Environment Configuration

To configure SSL certificate:
- The environment variable `SSL_CERT_FILE` is set to `certifi.where()` to ensure that SSL certificates are properly handled when accessing HTTPS URLs.

## NLTK Setup

This project uses NLTK's `punkt`, `stopwords`, `reuters`, and `wordnet` datasets. They will be downloaded the first time the application runs if not already available.

## Example Usage

To get all documents:
- Send a `GET` request to `http://127.0.0.1:5000/documents`.

To find matching documents based on categories:
- Send a `POST` request to `http://127.0.0.1:5000/documents/match` with a JSON body, for example:
  ```json
  {
    "categories": ["category1", "category2"]
  }
  ```

## Notes

- Ensure MongoDB is running and accessible on the default port (`27017`).
- Make sure that `nltk` datasets are downloaded successfully; otherwise, some of the NLP functionalities will not work.
