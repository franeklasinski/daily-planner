#!/usr/bin/env python3
"""
Kalendarz-App - Python Calendar Planner
Aplikacja kalendarza/planera do planowania dnia z bazą danych SQLite
Wersja webowa z Flask
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta
import calendar
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kalendarz-app-secret-key-2025'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///calendar.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Model bazy danych
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.String(5), nullable=False)  # HH:MM
    end_time = db.Column(db.String(5))  # HH:MM 
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.strftime('%Y-%m-%d'),
            'start_time': self.start_time,
            'end_time': self.end_time,
            'title': self.title,
            'description': self.description
        }

@app.route('/')
def index():
    """Strona główna kalendarza"""
    today = date.today()
    return render_template('calendar.html', 
                         current_year=today.year, 
                         current_month=today.month,
                         today=today.strftime('%Y-%m-%d'))

@app.route('/api/calendar/<int:year>/<int:month>')
def get_calendar_data(year, month):
    """API: Pobiera dane kalendarza dla danego miesiąca"""
    try:
        # Pobiera wydarzenia dla miesiąca
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        events = Event.query.filter(
            Event.date >= start_date,
            Event.date <= end_date
        ).all()
        
        # Grupuje wydarzenia po datach
        events_by_date = {}
        for event in events:
            date_str = event.date.strftime('%Y-%m-%d')
            if date_str not in events_by_date:
                events_by_date[date_str] = []
            events_by_date[date_str].append(event.to_dict())
        
        # Generuje kalendarz
        cal = calendar.monthcalendar(year, month)
        
        return jsonify({
            'calendar': cal,
            'events': events_by_date,
            'year': year,
            'month': month,
            'month_name': calendar.month_name[month]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/events/<date_str>')
def get_events_for_date(date_str):
    """API: Pobiera wydarzenia dla konkretnej daty"""
    try:
        event_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        events = Event.query.filter_by(date=event_date).order_by(Event.start_time).all()
        return jsonify([event.to_dict() for event in events])
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/events', methods=['POST'])
def add_event():
    """API: Dodaje nowe wydarzenie"""
    try:
        data = request.get_json()
        
        event = Event(
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            start_time=data['start_time'],
            end_time=data.get('end_time'),
            title=data['title'],
            description=data.get('description', '')
        )
        
        db.session.add(event)
        db.session.commit()
        
        return jsonify(event.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    """API: Aktualizuje wydarzenie"""
    try:
        event = Event.query.get_or_404(event_id)
        data = request.get_json()
        
        event.start_time = data['start_time']
        event.end_time = data.get('end_time')
        event.title = data['title']
        event.description = data.get('description', '')
        event.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify(event.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    """API: Usuwa wydarzenie"""
    try:
        event = Event.query.get_or_404(event_id)
        db.session.delete(event)
        db.session.commit()
        return jsonify({'message': 'Wydarzenie zostało usunięte'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/search')
def search_events():
    """API: Wyszukuje wydarzenia"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify([])
        
        events = Event.query.filter(
            db.or_(
                Event.title.contains(query),
                Event.description.contains(query)
            )
        ).order_by(Event.date, Event.start_time).all()
        
        return jsonify([event.to_dict() for event in events])
    except Exception as e:
        return jsonify({'error': str(e)}), 400

def init_db():
    """Inicjalizuje bazę danych"""
    with app.app_context():
        db.create_all()
        print("Baza danych została zainicjalizowana")

if __name__ == "__main__":
    print("Uruchamianie Kalendarza-App (wersja web)...")
    print("Aplikacja kalendarza/planera w Flask")
    print("Dane są przechowywane lokalnie w bazie SQLite")
    print("Dostępna na: http://localhost:5001")
    print("=" * 50)
    
    # Inicjalizuje bazę danych
    init_db()
    
    # Uruchamia aplikację zmieni poort jezeli zajety 
    app.run(debug=True, host='0.0.0.0', port=5001)
