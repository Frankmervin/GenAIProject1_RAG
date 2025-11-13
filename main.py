from flask import Flask, request, jsonify, render_template
from app.models.vector_store import VectorStore
from app.services.storage_service import S3Storage
from app.services.llm_service import LLMService
from config import Config
import os
import tempfile
import logging

from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_classic.text_splitter import RecursiveCharacterTextSplitter
# If this import fails, use:
# from langchain.text_splitter import RecursiveCharacterTextSplitter



app = Flask(__name__)


vector_store = VectorStore(Config.VECTOR_DB_PATH)
storage_service = S3Storage()
llm_service = LLMService(vector_store)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Default route
@app.route('/')
def index():
    return render_template('index.html')


def process_document(file):
    """Process document based on file type and return text chunks."""
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, file.filename)

    try:
        # Save file temporarily
        file.save(temp_path)

        # Normalize extension
        ext = os.path.splitext(file.filename)[1].lower()

        # Process based on file type
        if ext == '.pdf':
            loader = PyPDFLoader(temp_path)
            documents = loader.load()
        elif ext == '.txt':
            loader = TextLoader(temp_path)
            documents = loader.load()
        else:
            raise ValueError("Unsupported file type. Only .txt and .pdf are supported.")

        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        text_chunks = text_splitter.split_documents(documents)

        return text_chunks

    finally:
        # Clean up temp file / folder
        if os.path.exists(temp_path):
            os.remove(temp_path)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)


@app.route('/upload', methods=['POST'])
def upload_document():
    try:
        logger.debug("Upload endpoint called")

        if 'file' not in request.files:
            logger.warning("No file in request")
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']

        if file.filename == '':
            logger.warning("Empty filename")
            return jsonify({'error': 'No file selected'}), 400

        # Validate extension
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ('.txt', '.pdf'):
            logger.warning(f"Unsupported file type: {file.filename}")
            return jsonify({'error': 'Only .txt or .pdf files are supported'}), 400

        logger.debug(f"Processing file: {file.filename}")

        # Process the document into chunks
        try:
            text_chunks = process_document(file)
            logger.debug(f"Document processed into {len(text_chunks)} chunks")
        except Exception as e:
            logger.error(f"Error processing document into chunks: {str(e)}")
            return jsonify({'error': f'Error processing document: {str(e)}'}), 500

        # Upload file into S3
        try:
            file.seek(0)  # Reset file pointer
            storage_service.upload_file(file, file.filename)
            logger.debug("File uploaded to S3")
        except Exception as e:
            logger.error(f"Error uploading into S3: {str(e)}")
            return jsonify({'error': f'Error uploading into S3: {str(e)}'}), 500

        # Add to vector store
        try:
            vector_store.add_documents(text_chunks)
            logger.debug("Documents added to vector store")
        except Exception as e:
            logger.error(f"Error adding to vector store: {str(e)}")
            return jsonify({'error': f'Error adding to vector store: {str(e)}'}), 500

        return jsonify({
            'message': 'File uploaded and processed successfully till vector embeddings',
            'chunks_processed': len(text_chunks)
        })

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500


@app.route('/query', methods=['POST'])
def query():
    data = request.json or {}
    if 'question' not in data:
        return jsonify({'error': 'No question provided'}), 400

    try:
        response = llm_service.get_response(data['question'])
        return jsonify({'response': response})
    except Exception as e:
        logger.error(f"Response error: {str(e)}")
        return jsonify({'error': f'Response error: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
