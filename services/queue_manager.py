import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from services.logger import logger


class QueueManager:
    """Manages parallel conversion execution with max 3 workers"""
    
    MAX_WORKERS = 3
    TIMEOUT_SECONDS = 300  # 5 minutes
    
    def __init__(self, db_service):
        self.db = db_service
    
    async def run_comparisons(self, file_path, task_id, libraries, 
                            output_format, convert_single_func):
        """
        Run converters with max 3 in parallel
        
        Args:
            file_path: Path to PDF file
            task_id: Task ID for tracking
            libraries: List of library names to compare
            output_format: Output format (markdown, json, text)
            convert_single_func: Async function that converts with one library
                                 signature: async def convert_single_func(task_id, library_name, file_path, output_format)
        """
        library_queue = list(libraries)
        active_conversions = {}
        results = {}
        
        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            while library_queue or active_conversions:
                # Start new conversions if slots available
                while len(active_conversions) < self.MAX_WORKERS and library_queue:
                    lib = library_queue.pop(0)
                    
                    # Record in DB
                    self.db.add_comparison(task_id, lib)
                    
                    logger.info(f"Starting conversion for {lib} in task {task_id}")
                    
                    # Submit to thread pool
                    future = executor.submit(
                        asyncio.run,
                        convert_single_func(task_id, lib, file_path, output_format)
                    )
                    active_conversions[lib] = {
                        'future': future,
                        'start_time': time.time()
                    }
                
                # Check for completed/timed out
                for lib in list(active_conversions.keys()):
                    conv_data = active_conversions[lib]
                    elapsed = time.time() - conv_data['start_time']
                    
                    # Check timeout
                    if elapsed > self.TIMEOUT_SECONDS:
                        logger.warning(f"Conversion timeout for {lib} in task {task_id}")
                        conv_data['future'].cancel()
                        self.db.timeout_comparison(task_id, lib)
                        del active_conversions[lib]
                        continue
                    
                    # Check if done
                    if conv_data['future'].done():
                        try:
                            result = conv_data['future'].result()
                            results[lib] = result
                            logger.info(f"Conversion completed for {lib} in task {task_id}")
                        except Exception as e:
                            logger.error(f"Conversion error for {lib}: {str(e)}")
                            # Error already logged in DB by convert_single_func
                            pass
                        del active_conversions[lib]
                
                # Brief sleep to avoid busy waiting
                await asyncio.sleep(0.5)
        
        return results

