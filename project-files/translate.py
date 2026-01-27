import json
import boto3
import os
import datatier
import urllib.parse
from configparser import ConfigParser
from pypdf import PdfReader
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

def split_text(text, max_size):
    """
    Splits a text into chunks, each with a maximum size.
    """
    return [text[i:i+max_size] for i in range(0, len(text), max_size)]

def lambda_handler(event, context):
    local_results_file = "/tmp/results.txt"
    bucketkey_results_file = ""
    try:
        # Configurations
        config_file = 'config.ini'
        os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file

        configur = ConfigParser()
        configur.read(config_file)

        # S3 Setup
        s3_profile = 's3readwrite'
        boto3.setup_default_session(profile_name=s3_profile)

        bucketname = configur.get('s3', 'bucket_name')
        
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(bucketname)

        # RDS Setup
        rds_endpoint = configur.get('rds', 'endpoint')
        rds_portnum = int(configur.get('rds', 'port_number'))
        rds_username = configur.get('rds', 'user_name')
        rds_pwd = configur.get('rds', 'user_pwd')
        rds_dbname = configur.get('rds', 'db_name')

        # AWS Translate Setup
        translate = boto3.client(service_name='translate', region_name='us-east-2', use_ssl=True)

        # Event Handling
        bucketkey = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
        local_pdf = "/tmp/data.pdf"
        bucket.download_file(bucketkey, local_pdf)

        # PDF Text Extraction
        reader = PdfReader(local_pdf)
        extracted_text = ''
        for page in reader.pages:
            extracted_text += page.extract_text() + '\n'

        # Determine target language (hardcoded for example, should be dynamic)
        target_language = event.get('target_language', 'de')  # Default to English if not provided
        
        # Translation with Text Splitting
        max_chunk_size = 5000  # 5000 bytes
        text_chunks = split_text(extracted_text.encode('utf-8'), max_chunk_size)
        translated_text = ''

        for chunk in text_chunks:
            try:
                result = translate.translate_text(Text=chunk.decode('utf-8'), 
                                                  SourceLanguageCode="auto", 
                                                  TargetLanguageCode=target_language)
                translated_text += result.get('TranslatedText')
            except Exception as e:
                print(f"Error translating chunk: {e}")
                # Optionally, handle this error more gracefully

        # Save Translated Text to S3
        print("Before uploading to bucket")
        bucketkey_results_file = bucketkey[0:-4] + ".txt"

        outfile = open(local_results_file, "w")
        outfile.write(translated_text)
        outfile.close()
        
        bucket.upload_file(local_results_file,
                       bucketkey_results_file,
                       ExtraArgs={
                         'ACL': 'public-read',
                         'ContentType': 'text/plain'
                       })
        print("Right after uploading to bucket")
        
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Translation successful', 'translatedText': translated_text})
        }

    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps('Error occurred in lambda function')
        }