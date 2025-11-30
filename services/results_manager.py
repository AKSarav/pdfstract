from pathlib import Path
from datetime import datetime
import json
import os
import shutil
from services.logger import logger


class ResultsManager:
    """Manages storage and retrieval of conversion results"""
    
    def __init__(self, results_dir="results"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
    
    def create_task_directory(self, task_id):
        """Create directory for task results"""
        task_dir = self.results_dir / task_id
        task_dir.mkdir(exist_ok=True)
        logger.info(f"Created results directory for task {task_id}")
        return task_dir
    
    def save_conversion(self, task_id, library_name, content, output_format='markdown'):
        """Save converted content to file"""
        task_dir = self.results_dir / task_id
        task_dir.mkdir(exist_ok=True)
        
        if output_format == 'markdown':
            filename = f"{library_name}.md"
        elif output_format == 'json':
            filename = f"{library_name}.json"
        else:
            filename = f"{library_name}.txt"
        
        file_path = task_dir / filename
        
        try:
            if isinstance(content, dict):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(content, f, indent=2)
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(str(content))
            
            file_size = os.path.getsize(file_path)
            logger.info(f"Saved conversion for {library_name}: {file_size} bytes")
            return str(file_path), file_size
        except Exception as e:
            logger.error(f"Error saving conversion for {library_name}: {str(e)}")
            raise
    
    def save_metadata(self, task_id, task_data):
        """Save task metadata"""
        task_dir = self.results_dir / task_id
        task_dir.mkdir(exist_ok=True)
        metadata_path = task_dir / "metadata.json"
        
        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(task_data, f, indent=2)
            logger.info(f"Saved metadata for task {task_id}")
            return str(metadata_path)
        except Exception as e:
            logger.error(f"Error saving metadata for {task_id}: {str(e)}")
            raise
    
    def get_conversion_content(self, task_id, library_name, output_format='markdown'):
        """Retrieve conversion result"""
        task_dir = self.results_dir / task_id
        
        if output_format == 'markdown':
            filename = f"{library_name}.md"
        elif output_format == 'json':
            filename = f"{library_name}.json"
        else:
            filename = f"{library_name}.txt"
        
        file_path = task_dir / filename
        
        if not file_path.exists():
            logger.warning(f"Conversion file not found: {file_path}")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if output_format == 'json':
                    return json.load(f)
                else:
                    return f.read()
        except Exception as e:
            logger.error(f"Error reading conversion file {file_path}: {str(e)}")
            return None
    
    def list_task_files(self, task_id):
        """List all files in a task directory"""
        task_dir = self.results_dir / task_id
        
        if not task_dir.exists():
            return []
        
        return [f.name for f in task_dir.iterdir() if f.is_file()]
    
    def delete_task_results(self, task_id):
        """Delete all results for a task"""
        task_dir = self.results_dir / task_id
        
        if task_dir.exists():
            try:
                shutil.rmtree(task_dir)
                logger.info(f"Deleted results for task {task_id}")
            except Exception as e:
                logger.error(f"Error deleting results for {task_id}: {str(e)}")
                raise

