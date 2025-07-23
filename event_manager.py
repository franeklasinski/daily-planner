from datetime import datetime, date, timedelta
from database import DatabaseManager

class EventManager:
    """Klasa do zarządzania wydarzeniami w kalendarzu"""
    
    def __init__(self):
        self.db = DatabaseManager()
    
    def add_event(self, event_date, start_time, end_time, title, description=""):
        """Dodaje nowe wydarzenie"""
        # Walidacja danych
        if not title.strip():
            raise ValueError("Tytuł wydarzenia nie może być pusty")
        
        # Konwersja daty do formatu string jeśli potrzeba
        if isinstance(event_date, date):
            event_date = event_date.strftime("%Y-%m-%d")
        
        # Walidacja godzin
        if self._validate_time_format(start_time):
            if end_time and not self._validate_time_format(end_time):
                raise ValueError("Nieprawidłowy format godziny końcowej (HH:MM)")
            
            # Sprawdza czy godzina końcowa jest późniejsza niż początkowa
            if end_time and start_time >= end_time:
                raise ValueError("Godzina końcowa musi być późniejsza niż początkowa")
        else:
            raise ValueError("Nieprawidłowy format godziny początkowej (HH:MM)")
        
        return self.db.add_event(event_date, start_time, end_time, title, description)
    
    def get_events_for_date(self, event_date):
        """Pobiera wydarzenia dla konkretnej daty"""
        if isinstance(event_date, date):
            event_date = event_date.strftime("%Y-%m-%d")
        
        return self.db.get_events_for_date(event_date)
    
    def get_events_for_month(self, year, month):
        """Pobiera liczbę wydarzeń dla każdego dnia w miesiącu"""
        return self.db.get_events_for_month(year, month)
    
    def update_event(self, event_id, start_time, end_time, title, description=""):
        """Aktualizuje wydarzenie"""
        if not title.strip():
            raise ValueError("Tytuł wydarzenia nie może być pusty")
        
        if not self._validate_time_format(start_time):
            raise ValueError("Nieprawidłowy format godziny początkowej (HH:MM)")
        
        if end_time and not self._validate_time_format(end_time):
            raise ValueError("Nieprawidłowy format godziny końcowej (HH:MM)")
        
        if end_time and start_time >= end_time:
            raise ValueError("Godzina końcowa musi być późniejsza niż początkowa")
        
        return self.db.update_event(event_id, start_time, end_time, title, description)
    
    def delete_event(self, event_id):
        """Usuwa wydarzenie"""
        return self.db.delete_event(event_id)
    
    def get_event_by_id(self, event_id):
        """Pobiera szczegóły wydarzenia"""
        return self.db.get_event_by_id(event_id)
    
    def search_events(self, search_term):
        """Wyszukuje wydarzenia"""
        return self.db.search_events(search_term)
    
    def get_today_events(self):
        """Pobiera wydarzenia na dzisiaj"""
        today = date.today()
        return self.get_events_for_date(today)
    
    def get_upcoming_events(self, days=7):
        """Pobiera nadchodzące wydarzenia w określonym zakresie dni"""
        events = []
        today = date.today()
        
        for i in range(days):
            current_date = today + timedelta(days=i)
            daily_events = self.get_events_for_date(current_date)
            for event in daily_events:
                events.append((current_date.strftime("%Y-%m-%d"), *event))
        
        return events
    
    def _validate_time_format(self, time_str):
        """Waliduje format godziny (HH:MM)"""
        try:
            datetime.strptime(time_str, "%H:%M")
            return True
        except ValueError:
            return False
    
    def get_time_slots_for_date(self, event_date, slot_duration=60):
        """Pobiera dostępne sloty czasowe dla daty (w minutach)"""
        events = self.get_events_for_date(event_date)
        
        # lista zajętych godzin
        busy_slots = []
        for event in events:
            start_time = event[1]  # start_time
            end_time = event[2] if event[2] else start_time  # end_time lub start_time
            busy_slots.append((start_time, end_time))
        
        return busy_slots
    
    def has_conflicts(self, event_date, start_time, end_time, exclude_event_id=None):
        """Sprawdza czy nowe wydarzenie koliduje z istniejącymi"""
        events = self.get_events_for_date(event_date)
        
        for event in events:
            event_id = event[0]
            if exclude_event_id and event_id == exclude_event_id:
                continue
                
            event_start = event[1]
            event_end = event[2] if event[2] else event[1]
            
            # Sprawdza kolizję czasową
            if (start_time < event_end and end_time > event_start):
                return True, f"Konflikt z wydarzeniem: {event[3]}"
        
        return False, None
