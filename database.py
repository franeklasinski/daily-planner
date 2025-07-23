import sqlite3
import os
from datetime import datetime, date

class DatabaseManager:
    """Klasa do zarządzania bazą danych SQLite dla kalendarza"""
    
    def __init__(self, db_path="calendar.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicjalizuje bazę danych i tworzy tabele"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabela wydarzeń
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    title TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Indeks dla szybszego wyszukiwania po dacie
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_date ON events(date)
            ''')
            
            conn.commit()
    
    def add_event(self, event_date, start_time, end_time, title, description=""):
        """Dodaje nowe wydarzenie do bazy danych"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO events (date, start_time, end_time, title, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (event_date, start_time, end_time, title, description))
            conn.commit()
            return cursor.lastrowid
    
    def get_events_for_date(self, event_date):
        """Pobiera wszystkie wydarzenia dla konkretnej daty"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, start_time, end_time, title, description
                FROM events
                WHERE date = ?
                ORDER BY start_time
            ''', (event_date,))
            return cursor.fetchall()
    
    def get_events_for_month(self, year, month):
        """Pobiera wszystkie wydarzenia dla konkretnego miesiąca"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT date, COUNT(*) as event_count
                FROM events
                WHERE date LIKE ?
                GROUP BY date
            ''', (f"{year:04d}-{month:02d}-%",))
            return dict(cursor.fetchall())
    
    def update_event(self, event_id, start_time, end_time, title, description):
        """Aktualizuje istniejące wydarzenie"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE events
                SET start_time = ?, end_time = ?, title = ?, description = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (start_time, end_time, title, description, event_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_event(self, event_id):
        """Usuwa wydarzenie z bazy danych"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM events WHERE id = ?', (event_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_event_by_id(self, event_id):
        """Pobiera wydarzenie po ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, date, start_time, end_time, title, description
                FROM events
                WHERE id = ?
            ''', (event_id,))
            return cursor.fetchone()
    
    def search_events(self, search_term):
        """Wyszukuje wydarzenia po tytule lub opisie"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, date, start_time, end_time, title, description
                FROM events
                WHERE title LIKE ? OR description LIKE ?
                ORDER BY date, start_time
            ''', (f"%{search_term}%", f"%{search_term}%"))
            return cursor.fetchall()
