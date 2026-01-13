import sqlite3
import json
import os
from datetime import datetime

class DBManager:
    def __init__(self):
        # Determine path to database file
        # Assuming we are in gatec/core/db_manager.py, db is in data/history.db
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.db_path = os.path.join(base_dir, 'data', 'history.db')
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        """Initialize the database schema if it doesn't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calculations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                plant_location TEXT,
                fuel_type TEXT,
                plant_efficiency REAL,
                total_output REAL,
                total_efficiency REAL,
                efficiency_drop REAL,
                total_emissions REAL,
                inputs_json TEXT,
                results_json TEXT
            )
        ''')
        
        conn.commit()
        conn.close()

    def save_calculation(self, input_data, results):
        """Save calculation inputs and results to database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Prepare data
            timestamp = datetime.now()
            
            # Extract basic fields
            plant_location = input_data.get('plant_location', '')
            fuel_type = input_data.get('fuel_type', '')
            plant_efficiency = float(input_data.get('plant_efficiency', 0))
            total_output = float(input_data.get('total_output', 0))
            
            total_efficiency = results.get('total_efficiency', 0)
            efficiency_drop = results.get('efficiency_drop', 0)
            total_emissions = results.get('total_emissions', 0)
            
            # Serialize JSON columns
            inputs_json = json.dumps(input_data)
            results_json = json.dumps(results)
            
            cursor.execute('''
                INSERT INTO calculations (
                    timestamp, plant_location, fuel_type, plant_efficiency, total_output,
                    total_efficiency, efficiency_drop, total_emissions, inputs_json, results_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp, plant_location, fuel_type, plant_efficiency, total_output,
                total_efficiency, efficiency_drop, total_emissions, inputs_json, results_json
            ))
            
            conn.commit()
            print(f"Calculation saved to DB at {self.db_path}")
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        except Exception as e:
            print(f"Error saving to database: {e}")
        finally:
            if conn:
                conn.close()

    def get_history(self):
        """Retrieve all calculation history ordered by newest first"""
        try:
            conn = self.get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, timestamp, plant_location, fuel_type, total_efficiency, efficiency_drop, inputs_json 
                FROM calculations 
                ORDER BY timestamp DESC
            ''')
            
            rows = cursor.fetchall()
            # Convert to list of dicts for easier handling
            return [dict(row) for row in rows]
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def delete_calculation(self, id):
        """Delete a calculation by ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM calculations WHERE id = ?', (id,))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
        finally:
            if conn:
                conn.close()

# Singleton instance for easy access
db = DBManager()
