
    def get_enabled_libraries(self):
        """Get list of enabled library names"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()
        
        cursor.execute('SELECT library_name FROM user_libraries WHERE is_enabled = 1')
        libraries = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return libraries

    def set_library_status(self, library_name, is_enabled):
        """Enable or disable a library"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_libraries (library_name, is_enabled) 
            VALUES (?, ?)
            ON CONFLICT(library_name) DO UPDATE SET is_enabled = ?
        ''', (library_name, 1 if is_enabled else 0, 1 if is_enabled else 0))
        
        conn.commit()
        conn.close()
