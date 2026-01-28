# PDF Processing and Analysis Using AWS Tools

This project is a **cloud-based PDF processing system** built with **AWS Lambda, S3, RDS, and a Python client**. It extends a previous project by adding automated analysis of PDFs, including **keyword extraction**, **language detection**, and **on-demand translation**.  

The system is **serverless and modular**, designed to be scalable and easy to extend.

---

## Project Overview

- **PDF Upload & Storage:** Users upload PDFs through the Python client or directly to S3.  
- **Serverless Processing:** Lambda functions automatically process PDFs for keyword extraction and language detection.  
- **Database Integration:** Keywords, PDFs, and metadata are stored in AWS RDS with relationships designed for efficient querying.  
- **On-Demand Translation:** Users can request translations of PDFs via the Python client, which triggers a Lambda function using AWS Translate.  
- **Python Client:** Interacts with Lambda functions, manages PDF uploads, and retrieves processed data from S3.  

> **Note:** For security, `config.ini` containing AWS credentials and database configuration is **not included**. The project cannot be run directly after download without providing your own configuration.

---

## Project Demo

A short demonstration of the system in action:

<p align="center">
  <a href=https://drive.google.com/file/d/1dMmCFeT0KSykX4wiJe0b0vVzeEDa0xtZ/view?usp=sharing target="_blank">Watch PDF Processing Short Demo</a>
</p>

<p align="center">
  <a href=https://drive.google.com/file/d/1sNh82mfQXIxTgEH-liOtJPSNnU4iuxGP/view?usp=sharing target="_blank">Watch PDF Processing Full Project Showcase</a>
</p>

- Uploading a PDF triggers keyword extraction and language detection  
- The Python client can request translations on-demand  
- Results are stored in S3 and the database for easy access  

---

## Functionalities & Components

### Keyword Extraction
- Triggered automatically when a PDF is uploaded  
- Extracts all words except stop words  
- Calculates word frequency and stores **top 5 keywords** in the database  
- Ensures keywords are **unique across PDFs**

### Language Detection
- Triggered automatically on PDF upload  
- Extracts text and detects the language using **LangDetect**  
- Uploads a `.txt` file containing the language code to S3

### Translation
- Triggered on-demand via the Python client  
- Inputs: PDF file + target language code (e.g., `'es'` for Spanish)  
- Uses **AWS Translate** to convert text  
- Returns translated text to the client and uploads a translated PDF copy to S3

### Database
- Built on **AWS RDS**  
- Stores PDFs, keywords, users, and jobs  
- Additional tables link PDFs and keywords, creating many-to-many relationships  
- Structured for future feature extensions like keyword search

---

## Notes for Running the Project

- The repository **does not include the `config.ini`** file for security reasons.  
- To run the project locally, you must create your own `config.ini` within the `project-files` directory with:  
  - AWS credentials (Access Key ID, Secret Access Key)  
  - RDS database connection info  
