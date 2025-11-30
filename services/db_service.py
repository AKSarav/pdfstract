import sqlite3
from datetime import datetime
from pathlib import Path


class DatabaseService:
    """SQLite database service for task and comparison tracking"""
    
    def __init__(self, db_path="data/tasks.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.init_db()
    
    def init_db(self):
        """Create tables if they don't exist"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.execute('PRAGMA journal_mode=WAL')  # Enable WAL for better concurrency
        cursor = conn.cursor()
        
        # Tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                file_size_bytes INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                total_duration_seconds FLOAT,
                output_format TEXT,
                status TEXT,
                CONSTRAINT status_check CHECK (status IN ('running', 'completed', 'failed', 'cancelled'))
            )
        ''')
        
        # Comparisons table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comparisons (
                comparison_id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                library_name TEXT NOT NULL,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                duration_seconds FLOAT,
                output_file TEXT,
                output_size_bytes INTEGER,
                status TEXT,
                error_message TEXT,
                FOREIGN KEY(task_id) REFERENCES tasks(task_id),
                CONSTRAINT status_check CHECK (status IN ('pending', 'success', 'failed', 'timeout'))
            )
        ''')
        
        # Create indexes for faster queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_created ON tasks(created_at DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_comparisons_task ON comparisons(task_id)')
        
        conn.commit()
        conn.close()
    
    def create_task(self, task_id, filename, file_size_bytes, output_format):
        """Create new task record"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tasks (task_id, filename, file_size_bytes, output_format, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (task_id, filename, file_size_bytes, output_format, 'running'))
        
        conn.commit()
        conn.close()
    
    def add_comparison(self, task_id, library_name):
        """Start tracking a comparison"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO comparisons (task_id, library_name, start_time, status)
            VALUES (?, ?, ?, ?)
        ''', (task_id, library_name, datetime.now().isoformat(), 'pending'))
        
        conn.commit()
        conn.close()
    
    def complete_comparison(self, task_id, library_name, duration_seconds, 
                           output_file, output_size_bytes, error_message=None):
        """Mark comparison as completed/failed"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()
        
        status = 'success' if error_message is None else 'failed'
        
        cursor.execute('''
            UPDATE comparisons 
            SET end_time = ?, duration_seconds = ?, output_file = ?, 
                output_size_bytes = ?, status = ?, error_message = ?
            WHERE task_id = ? AND library_name = ?
        ''', (datetime.now().isoformat(), duration_seconds, output_file, 
              output_size_bytes, status, error_message, task_id, library_name))
        
        conn.commit()
        conn.close()
    
    def timeout_comparison(self, task_id, library_name):
        """Mark comparison as timed out after 5 minutes"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE comparisons 
            SET end_time = ?, duration_seconds = ?, status = ?, error_message = ?
            WHERE task_id = ? AND library_name = ?
        ''', (datetime.now().isoformat(), 300, 'timeout', 
              'Conversion timed out (>5 minutes)', task_id, library_name))
        
        conn.commit()
        conn.close()
    
    def complete_task(self, task_id, status='completed'):
        """Mark task as completed/cancelled/failed"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT SUM(duration_seconds) FROM comparisons WHERE task_id = ?
        ''', (task_id,))
        
        total_duration = cursor.fetchone()[0] or 0
        
        cursor.execute('''
            UPDATE tasks 
            SET status = ?, completed_at = ?, total_duration_seconds = ?
            WHERE task_id = ?
        ''', (status, datetime.now().isoformat(), total_duration, task_id))
        
        conn.commit()
        conn.close()
    
    def get_task_with_comparisons(self, task_id):
        """Get task and all its comparisons"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM tasks WHERE task_id = ?', (task_id,))
        task_row = cursor.fetchone()
        task = dict(task_row) if task_row else {}
        
        cursor.execute('''
            SELECT * FROM comparisons WHERE task_id = ? ORDER BY start_time
        ''', (task_id,))
        
        comparisons = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return {'task': task, 'comparisons': comparisons}
    
    def get_recent_tasks(self, limit=20):
        """Get recent tasks for history display"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT t.*, 
                   COUNT(c.comparison_id) as libraries_count,
                   GROUP_CONCAT(c.library_name, ', ') as library_names
            FROM tasks t
            LEFT JOIN comparisons c ON t.task_id = c.task_id
            GROUP BY t.task_id
            ORDER BY t.created_at DESC
            LIMIT ?
        ''', (limit,))
        
        tasks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return tasks
    
    def get_library_stats(self):
        """Get stats across all successful conversions"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                library_name,
                COUNT(*) as total_runs,
                AVG(duration_seconds) as avg_time,
                MIN(duration_seconds) as min_time,
                MAX(duration_seconds) as max_time,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_count
            FROM comparisons
            WHERE status IN ('success', 'failed', 'timeout')
            GROUP BY library_name
            ORDER BY avg_time ASC
        ''')
        
        stats = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return stats
    
    def delete_task(self, task_id):
        """Delete task and its comparisons"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()
        
        # Delete comparisons first (foreign key)
        cursor.execute('DELETE FROM comparisons WHERE task_id = ?', (task_id,))
        # Delete task
        cursor.execute('DELETE FROM tasks WHERE task_id = ?', (task_id,))
        
        conn.commit()
        conn.close()

