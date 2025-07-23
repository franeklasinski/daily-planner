let currentYear = new Date().getFullYear();
let currentMonth = new Date().getMonth() + 1;
let selectedDate = null;
let todayString = new Date().toISOString().split('T')[0];
let calendarData = {};

const monthNames = [
    'Styczeń', 'Luty', 'Marzec', 'Kwiecień', 'Maj', 'Czerwiec',
    'Lipiec', 'Sierpień', 'Wrzesień', 'Październik', 'Listopad', 'Grudzień'
];

const dayNames = ['Poniedziałek', 'Wtorek', 'Środa', 'Czwartek', 'Piątek', 'Sobota', 'Niedziela'];

async function apiCall(url, options = {}) {
    showLoading();
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API call failed:', error);
        showToast('Wystąpił błąd podczas łączenia z serwerem', 'error');
        throw error;
    } finally {
        hideLoading();
    }
}

async function loadCalendar(year, month) {
    try {
        calendarData = await apiCall(`/api/calendar/${year}/${month}`);
        renderCalendar();
        updateMonthDisplay();
    } catch (error) {
        console.error('Failed to load calendar:', error);
    }
}

function renderCalendar() {
    const calendarBody = document.getElementById('calendar-body');
    calendarBody.innerHTML = '';
    
    const { calendar, events } = calendarData;
    
    calendar.forEach(week => {
        week.forEach(day => {
            const dayElement = createDayElement(day, events);
            calendarBody.appendChild(dayElement);
        });
    });
}

function createDayElement(day, events) {
    const dayElement = document.createElement('div');
    dayElement.className = 'calendar-day';
    
    if (day === 0) {
        dayElement.className += ' other-month';
        return dayElement;
    }
    
    const dayDate = `${currentYear}-${String(currentMonth).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    const dayEvents = events[dayDate] || [];
    
    if (dayDate === todayString) {
        dayElement.className += ' today';
    }
    if (dayDate === selectedDate) {
        dayElement.className += ' selected';
    }
    if (dayEvents.length > 0) {
        dayElement.className += ' has-events';
    }
    
    const dayNumber = document.createElement('div');
    dayNumber.className = 'day-number';
    dayNumber.textContent = day;
    dayElement.appendChild(dayNumber);
    
    const dayEventsContainer = document.createElement('div');
    dayEventsContainer.className = 'day-events';
    
    dayEvents.slice(0, 3).forEach((event, index) => {
        const eventDot = document.createElement('div');
        eventDot.className = `event-dot event-${(index % 5) + 1}`;
        eventDot.textContent = event.title;
        eventDot.title = `${event.start_time} - ${event.title}`;
        dayEventsContainer.appendChild(eventDot);
    });
    
    if (dayEvents.length > 3) {
        const moreDot = document.createElement('div');
        moreDot.className = 'event-dot';
        moreDot.textContent = `+${dayEvents.length - 3}`;
        moreDot.style.background = '#6c757d';
        dayEventsContainer.appendChild(moreDot);
    }
    
    dayElement.appendChild(dayEventsContainer);
    
    dayElement.addEventListener('click', () => selectDate(dayDate));
    
    return dayElement;
}

async function selectDate(dateString) {
    selectedDate = dateString;
    renderCalendar(); 
    
    const date = new Date(dateString);
    const dayName = dayNames[date.getDay() === 0 ? 6 : date.getDay() - 1]; 
    const formattedDate = `${dayName}, ${date.getDate()} ${monthNames[date.getMonth()]} ${date.getFullYear()}`;
    document.getElementById('selected-date').textContent = formattedDate;
    
    await loadEventsForDate(dateString);
}

async function loadEventsForDate(dateString) {
    try {
        const events = await apiCall(`/api/events/${dateString}`);
        renderDailyEvents(events);
    } catch (error) {
        console.error('Failed to load events:', error);
    }
}

function renderDailyEvents(events) {
    const eventsList = document.getElementById('events-list');
    
    if (events.length === 0) {
        eventsList.innerHTML = `
            <div class="no-events">
                <i class="fas fa-calendar-plus"></i>
                <p>Brak wydarzeń na ten dzień</p>
                <button class="btn btn-primary" onclick="showAddEventModal('${selectedDate}')">
                    <i class="fas fa-plus"></i> Dodaj wydarzenie
                </button>
            </div>
        `;
        return;
    }
    
    eventsList.innerHTML = '';
    
    events.forEach(event => {
        const eventElement = createEventElement(event);
        eventsList.appendChild(eventElement);
    });
}

function createEventElement(event) {
    const eventDiv = document.createElement('div');
    eventDiv.className = 'event-item';
    
    let timeDisplay = event.start_time;
    if (event.end_time && event.end_time !== event.start_time) {
        timeDisplay += ` - ${event.end_time}`;
    }
    
    eventDiv.innerHTML = `
        <div class="event-time">${timeDisplay}</div>
        <div class="event-title">${event.title}</div>
        ${event.description ? `<div class="event-description">${event.description}</div>` : ''}
        <div class="event-actions">
            <button class="event-btn edit" onclick="editEvent(${event.id})">
                <i class="fas fa-edit"></i> Edytuj
            </button>
            <button class="event-btn delete" onclick="deleteEvent(${event.id}, '${event.title}')">
                <i class="fas fa-trash"></i> Usuń
            </button>
        </div>
    `;
    
    return eventDiv;
}

function changeMonth(delta) {
    currentMonth += delta;
    
    if (currentMonth > 12) {
        currentMonth = 1;
        currentYear++;
    } else if (currentMonth < 1) {
        currentMonth = 12;
        currentYear--;
    }
    
    loadCalendar(currentYear, currentMonth);
}

function goToToday() {
    const today = new Date();
    currentYear = today.getFullYear();
    currentMonth = today.getMonth() + 1;
    loadCalendar(currentYear, currentMonth);
    selectDate(todayString);
}

function updateMonthDisplay() {
    document.getElementById('month-year').textContent = `${monthNames[currentMonth - 1]} ${currentYear}`;
}

function showAddEventModal(date = null) {
    const modal = document.getElementById('event-modal');
    const form = document.getElementById('event-form');
    
    form.reset();
    document.getElementById('event-id').value = '';
    const targetDate = date || selectedDate || todayString;
    document.getElementById('event-date').value = targetDate;
    document.getElementById('modal-title').textContent = 'Dodaj wydarzenie';
    
    modal.style.display = 'block';
    document.getElementById('event-title').focus();
}

function closeEventModal() {
    document.getElementById('event-modal').style.display = 'none';
}

async function editEvent(eventId) {
    try {
        const events = await apiCall(`/api/events/${selectedDate}`);
        const event = events.find(e => e.id === eventId);
        
        if (!event) {
            showToast('Nie znaleziono wydarzenia', 'error');
            return;
        }
        
        document.getElementById('event-id').value = event.id;
        document.getElementById('event-date').value = event.date;
        document.getElementById('start-time').value = event.start_time;
        document.getElementById('end-time').value = event.end_time || '';
        document.getElementById('event-title').value = event.title;
        document.getElementById('event-description').value = event.description || '';
        document.getElementById('modal-title').textContent = 'Edytuj wydarzenie';
        
        document.getElementById('event-modal').style.display = 'block';
    } catch (error) {
        console.error('Failed to load event for editing:', error);
    }
}

async function deleteEvent(eventId, eventTitle) {
    if (!confirm(`Czy na pewno chcesz usunąć wydarzenie "${eventTitle}"?`)) {
        return;
    }
    
    try {
        await apiCall(`/api/events/${eventId}`, { method: 'DELETE' });
        showToast('Wydarzenie zostało usunięte', 'success');
        
        await loadCalendar(currentYear, currentMonth);
        if (selectedDate) {
            await loadEventsForDate(selectedDate);
        }
    } catch (error) {
        console.error('Failed to delete event:', error);
    }
}

function showSearchModal() {
    document.getElementById('search-modal').style.display = 'block';
    document.getElementById('search-input').focus();
}

function closeSearchModal() {
    document.getElementById('search-modal').style.display = 'none';
    document.getElementById('search-input').value = '';
    document.getElementById('search-results').innerHTML = '<p class="search-placeholder">Wpisz frazę, aby wyszukać wydarzenia</p>';
}

let searchTimeout;
async function performSearch() {
    const query = document.getElementById('search-input').value.trim();
    
    if (searchTimeout) {
        clearTimeout(searchTimeout);
    }
    
    if (query.length < 2) {
        document.getElementById('search-results').innerHTML = '<p class="search-placeholder">Wpisz co najmniej 2 znaki</p>';
        return;
    }
    
    searchTimeout = setTimeout(async () => {
        try {
            const results = await apiCall(`/api/search?q=${encodeURIComponent(query)}`);
            renderSearchResults(results);
        } catch (error) {
            console.error('Search failed:', error);
        }
    }, 300);
}

function renderSearchResults(results) {
    const container = document.getElementById('search-results');
    
    if (results.length === 0) {
        container.innerHTML = '<p class="search-placeholder">Nie znaleziono żadnych wydarzeń</p>';
        return;
    }
    
    container.innerHTML = '';
    
    results.forEach(event => {
        const resultDiv = document.createElement('div');
        resultDiv.className = 'search-result';
        resultDiv.innerHTML = `
            <div class="search-result-date">${formatDate(event.date)} o ${event.start_time}</div>
            <div class="search-result-title">${event.title}</div>
            ${event.description ? `<div class="search-result-description">${event.description}</div>` : ''}
        `;
        
        resultDiv.addEventListener('click', () => {
            closeSearchModal();
            goToEvent(event);
        });
        
        container.appendChild(resultDiv);
    });
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const dayName = dayNames[date.getDay() === 0 ? 6 : date.getDay() - 1];
    return `${dayName}, ${date.getDate()} ${monthNames[date.getMonth()]}`;
}

async function goToEvent(event) {
    const eventDate = new Date(event.date);
    currentYear = eventDate.getFullYear();
    currentMonth = eventDate.getMonth() + 1;
    
    await loadCalendar(currentYear, currentMonth);
    await selectDate(event.date);
}

document.getElementById('event-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const eventId = document.getElementById('event-id').value;
    const eventData = {
        date: document.getElementById('event-date').value,
        start_time: document.getElementById('start-time').value,
        end_time: document.getElementById('end-time').value || null,
        title: document.getElementById('event-title').value.trim(),
        description: document.getElementById('event-description').value.trim()
    };
    
    if (!eventData.title) {
        showToast('Tytuł wydarzenia jest wymagany', 'error');
        return;
    }
    
    try {
        if (eventId) {
            await apiCall(`/api/events/${eventId}`, {
                method: 'PUT',
                body: JSON.stringify(eventData)
            });
            showToast('Wydarzenie zostało zaktualizowane', 'success');
        } else {
            await apiCall('/api/events', {
                method: 'POST',
                body: JSON.stringify(eventData)
            });
            showToast('Wydarzenie zostało dodane', 'success');
        }
        
        closeEventModal();
        
        await loadCalendar(currentYear, currentMonth);
        if (selectedDate) {
            await loadEventsForDate(selectedDate);
        }
        
    } catch (error) {
        console.error('Failed to save event:', error);
    }
});

function showLoading() {
    document.getElementById('loading').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

document.addEventListener('DOMContentLoaded', function() {
    window.addEventListener('click', function(e) {
        const eventModal = document.getElementById('event-modal');
        const searchModal = document.getElementById('search-modal');
        
        if (e.target === eventModal) {
            closeEventModal();
        }
        if (e.target === searchModal) {
            closeSearchModal();
        }
    });
    
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeEventModal();
            closeSearchModal();
        }
        
        if (e.key === 'n' && e.ctrlKey) {
            e.preventDefault();
            showAddEventModal();
        }
        
        if (e.key === 'f' && e.ctrlKey) {
            e.preventDefault();
            showSearchModal();
        }
    });
});


function initializeFromHTML() {
    if (typeof window.currentYear !== 'undefined') {
        currentYear = window.currentYear;
    }
    if (typeof window.currentMonth !== 'undefined') {
        currentMonth = window.currentMonth;
    }
    if (typeof window.todayString !== 'undefined') {
        todayString = window.todayString;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    initializeFromHTML();
    loadCalendar(currentYear, currentMonth);
});