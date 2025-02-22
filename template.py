import os
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

project_name = 'waste_detection'

list_of_files = [
    '.github/workflows/.gitkeep',
    'data/.gitkeep',
    f'{project_name}/__init__.py',
    f'{project_name}/components/__init__.py',
    f'{project_name}/components/data_ingestion.py',
    f'{project_name}/components/data_validation.py',
    f'{project_name}/components/model_trainer.py',
    f'{project_name}/constants/__init__.py',
    f'{project_name}/constants/training_pipeline/__init__.py',
    f'{project_name}/constants/application.py',
    f'{project_name}/entity/config_entity.py',
    f'{project_name}/entity/artifacts_entity.py',
    f'{project_name}/exception/__init__.py',
    f'{project_name}/logger/__init__.py',
    f'{project_name}/pipeline/__init__.py',
    f'{project_name}/pipeline/training_pipeline.py',
    f'{project_name}/utils/__init__.py',
    f'{project_name}/utils/main_utils.py',
    'weights/model_epoch.pt',
    'notes/train_model_gc.ipynb',
    'app.py',
    'Dockerfile',
    'requirements.txt',
    'setup.py',
]

for file in list_of_files:
    filepath = Path(file)
    filedir, filename = os.path.split(filepath)

    # Create directory if it doesn't exist
    if filedir != '':
        os.makedirs(filedir, exist_ok=True)
        logging.info(f'Created directory: {filedir} for file: {filename}')

    # Check if the file exists and has content
    if not os.path.exists(filepath):
        # If the file does not exist, create it
        with open(filepath, 'w') as f:
            pass  # Just create the file without writing anything
        logging.info(f'Created new file: {filepath}')
    elif os.path.getsize(filepath) == 0:
        # If the file exists but is empty, leave it as is
        logging.info(f'File: {filepath} already exists but is empty.')
    else:
        # If the file exists and has content, log that it's untouched
        logging.info(f'File: {filepath} already exists with content. Skipping.')


logging.info('Project structure created successfully')