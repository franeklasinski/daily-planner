import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import calendar
from datetime import date, datetime, timedelta
from event_manager import EventManager

class CalendarGUI:
    """Główny interfejs graficzny kalendarza"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Kalendarz - Planer Dnia")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        self.event_manager = EventManager()
        self.current_date = date.today()
        self.selected_date = date.today()
        
        self.setup_ui()
        self.update_calendar()
        self.update_daily_view()
    
    def setup_ui(self):
        """Tworzy interfejs użytkownika"""
        # Główny kontener
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Konfiguracja rozciągania
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Lewa strona - widok kalendarza
        self.setup_calendar_view(main_frame)
        
        # Prawa strona - widok dzienny
        self.setup_daily_view(main_frame)
        
        # Dolny panel - przyciski akcji
        self.setup_action_panel(main_frame)
    
    def setup_calendar_view(self, parent):
        """Tworzy widok kalendarza miesięcznego"""
        # Ramka kalendarza
        calendar_frame = ttk.LabelFrame(parent, text="Kalendarz", padding="10")
        calendar_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Nawigacja miesiąca
        nav_frame = ttk.Frame(calendar_frame)
        nav_frame.grid(row=0, column=0, columnspan=7, pady=(0, 10), sticky=(tk.W, tk.E))
        
        ttk.Button(nav_frame, text="◀", command=self.prev_month).grid(row=0, column=0)
        self.month_label = ttk.Label(nav_frame, text="", font=("Arial", 12, "bold"))
        self.month_label.grid(row=0, column=1, padx=20)
        ttk.Button(nav_frame, text="▶", command=self.next_month).grid(row=0, column=2)
        ttk.Button(nav_frame, text="Dzisiaj", command=self.go_to_today).grid(row=0, column=3, padx=(20, 0))
        
        # Nagłówki dni tygodnia
        days = ["Pon", "Wto", "Śro", "Czw", "Pią", "Sob", "Nie"]
        for i, day in enumerate(days):
            label = ttk.Label(calendar_frame, text=day, font=("Arial", 10, "bold"))
            label.grid(row=1, column=i, padx=2, pady=2)
        
        # Siatka dni
        self.day_buttons = {}
        for week in range(6):
            for day in range(7):
                btn = tk.Button(calendar_frame, text="", width=8, height=3,
                              font=("Arial", 9), relief="flat", bd=1)
                btn.grid(row=week+2, column=day, padx=1, pady=1)
                self.day_buttons[(week, day)] = btn
    
    def setup_daily_view(self, parent):
        """Tworzy widok dzienny z godzinami"""
        # Ramka widoku dziennego
        daily_frame = ttk.LabelFrame(parent, text="Plan dnia", padding="10")
        daily_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        daily_frame.columnconfigure(0, weight=1)
        daily_frame.rowconfigure(1, weight=1)
        
        # Data i przycisk dodawania
        date_frame = ttk.Frame(daily_frame)
        date_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        date_frame.columnconfigure(0, weight=1)
        
        self.selected_date_label = ttk.Label(date_frame, text="", font=("Arial", 14, "bold"))
        self.selected_date_label.grid(row=0, column=0, sticky=tk.W)
        
        ttk.Button(date_frame, text="+ Dodaj wydarzenie", 
                  command=self.add_event_dialog).grid(row=0, column=1)
        
        # Lista wydarzeń z przewijaniem
        list_frame = ttk.Frame(daily_frame)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Treeview dla wydarzeń
        columns = ("time", "title", "description")
        self.events_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        self.events_tree.heading("time", text="Godzina")
        self.events_tree.heading("title", text="Tytuł")
        self.events_tree.heading("description", text="Opis")
        
        self.events_tree.column("time", width=100, minwidth=80)
        self.events_tree.column("title", width=200, minwidth=150)
        self.events_tree.column("description", width=300, minwidth=200)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.events_tree.yview)
        self.events_tree.configure(yscrollcommand=scrollbar.set)
        
        self.events_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind double-click na edycję
        self.events_tree.bind("<Double-1>", self.edit_event_dialog)
        self.events_tree.bind("<Button-3>", self.show_context_menu)  # Prawy przycisk myszy
    
    def setup_action_panel(self, parent):
        """Tworzy panel z przyciskami akcji"""
        action_frame = ttk.Frame(parent)
        action_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0), sticky=(tk.W, tk.E))
        
        ttk.Button(action_frame, text="Edytuj wydarzenie", 
                  command=self.edit_selected_event).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(action_frame, text="Usuń wydarzenie", 
                  command=self.delete_selected_event).grid(row=0, column=1, padx=5)
        ttk.Button(action_frame, text="Wyszukaj", 
                  command=self.search_events_dialog).grid(row=0, column=2, padx=5)
    
    def update_calendar(self):
        """Aktualizuje widok kalendarza"""
        year = self.current_date.year
        month = self.current_date.month
        
        # Aktualizuj etykietę miesiąca
        months_pl = ["", "Styczeń", "Luty", "Marzec", "Kwiecień", "Maj", "Czerwiec",
                     "Lipiec", "Sierpień", "Wrzesień", "Październik", "Listopad", "Grudzień"]
        self.month_label.config(text=f"{months_pl[month]} {year}")
        
        # Pobierz dni miesiąca
        cal = calendar.monthcalendar(year, month)
        
        # Pobierz wydarzania dla tego miesiąca
        month_events = self.event_manager.get_events_for_month(year, month)
        
        # Wyczyść poprzednie przyciski
        for (week, day), btn in self.day_buttons.items():
            btn.config(text="", command=None, bg="SystemButtonFace", fg="black")
        
        # Wypełnij kalendarz
        for week_num, week in enumerate(cal):
            for day_num, day in enumerate(week):
                btn = self.day_buttons[(week_num, day_num)]
                
                if day == 0:
                    btn.config(text="", state="disabled")
                else:
                    day_date = date(year, month, day)
                    event_count = month_events.get(day_date.strftime("%Y-%m-%d"), 0)
                    
                    # Tekst przycisku
                    text = str(day)
                    if event_count > 0:
                        text += f" ({event_count})"
                    
                    # Kolory
                    bg_color = "SystemButtonFace"
                    fg_color = "black"
                    
                    if day_date == date.today():
                        bg_color = "#4CAF50"  # Zielony dla dzisiaj
                        fg_color = "white"
                    elif day_date == self.selected_date:
                        bg_color = "#2196F3"  # Niebieski dla wybranego dnia
                        fg_color = "white"
                    elif event_count > 0:
                        bg_color = "#FFC107"  # Żółty dla dni z wydarzeniami
                    
                    btn.config(text=text, state="normal", bg=bg_color, fg=fg_color,
                             command=lambda d=day_date: self.select_date(d))
    
    def update_daily_view(self):
        """Aktualizuje widok dzienny"""
        # Aktualizuj etykietę daty
        date_str = self.selected_date.strftime("%A, %d %B %Y")
        # Tłumaczenie dni tygodnia
        days_pl = {"Monday": "Poniedziałek", "Tuesday": "Wtorek", "Wednesday": "Środa",
                   "Thursday": "Czwartek", "Friday": "Piątek", "Saturday": "Sobota", "Sunday": "Niedziela"}
        for eng, pl in days_pl.items():
            date_str = date_str.replace(eng, pl)
        
        months_pl = {"January": "stycznia", "February": "lutego", "March": "marca",
                     "April": "kwietnia", "May": "maja", "June": "czerwca",
                     "July": "lipca", "August": "sierpnia", "September": "września",
                     "October": "października", "November": "listopada", "December": "grudnia"}
        for eng, pl in months_pl.items():
            date_str = date_str.replace(eng, pl)
        
        self.selected_date_label.config(text=date_str)
        
        # Wyczyść listę wydarzeń
        for item in self.events_tree.get_children():
            self.events_tree.delete(item)
        
        # Pobierz i wyświetl wydarzenia
        events = self.event_manager.get_events_for_date(self.selected_date)
        for event in events:
            event_id, start_time, end_time, title, description = event
            time_str = start_time
            if end_time and end_time != start_time:
                time_str += f" - {end_time}"
            
            self.events_tree.insert("", "end", values=(time_str, title, description or ""),
                                   tags=(event_id,))
    
    def select_date(self, selected_date):
        """Wybiera datę i aktualizuje widoki"""
        self.selected_date = selected_date
        self.update_calendar()
        self.update_daily_view()
    
    def prev_month(self):
        """Przechodzi do poprzedniego miesiąca"""
        if self.current_date.month == 1:
            self.current_date = self.current_date.replace(year=self.current_date.year-1, month=12)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month-1)
        self.update_calendar()
    
    def next_month(self):
        """Przechodzi do następnego miesiąca"""
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year+1, month=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month+1)
        self.update_calendar()
    
    def go_to_today(self):
        """Przechodzi do dzisiejszej daty"""
        today = date.today()
        self.current_date = today
        self.selected_date = today
        self.update_calendar()
        self.update_daily_view()
    
    def add_event_dialog(self):
        """Otwiera dialog dodawania wydarzenia"""
        dialog = EventDialog(self.root, "Dodaj wydarzenie")
        if dialog.result:
            try:
                self.event_manager.add_event(
                    self.selected_date,
                    dialog.result["start_time"],
                    dialog.result["end_time"],
                    dialog.result["title"],
                    dialog.result["description"]
                )
                self.update_calendar()
                self.update_daily_view()
                messagebox.showinfo("Sukces", "Wydarzenie zostało dodane!")
            except ValueError as e:
                messagebox.showerror("Błąd", str(e))
    
    def edit_event_dialog(self, event=None):
        """Otwiera dialog edycji wydarzenia"""
        self.edit_selected_event()
    
    def edit_selected_event(self):
        """Edytuje wybrane wydarzenie"""
        selection = self.events_tree.selection()
        if not selection:
            messagebox.showwarning("Uwaga", "Wybierz wydarzenie do edycji")
            return
        
        item = self.events_tree.item(selection[0])
        event_id = int(item["tags"][0])
        
        # Pobierz szczegóły wydarzenia
        event_data = self.event_manager.get_event_by_id(event_id)
        if not event_data:
            messagebox.showerror("Błąd", "Nie znaleziono wydarzenia")
            return
        
        # Otwórz dialog z wypełnionymi danymi
        dialog = EventDialog(self.root, "Edytuj wydarzenie", {
            "start_time": event_data[2],
            "end_time": event_data[3],
            "title": event_data[4],
            "description": event_data[5] or ""
        })
        
        if dialog.result:
            try:
                self.event_manager.update_event(
                    event_id,
                    dialog.result["start_time"],
                    dialog.result["end_time"],
                    dialog.result["title"],
                    dialog.result["description"]
                )
                self.update_calendar()
                self.update_daily_view()
                messagebox.showinfo("Sukces", "Wydarzenie zostało zaktualizowane!")
            except ValueError as e:
                messagebox.showerror("Błąd", str(e))
    
    def delete_selected_event(self):
        """Usuwa wybrane wydarzenie"""
        selection = self.events_tree.selection()
        if not selection:
            messagebox.showwarning("Uwaga", "Wybierz wydarzenie do usunięcia")
            return
        
        item = self.events_tree.item(selection[0])
        event_id = int(item["tags"][0])
        title = item["values"][1]
        
        if messagebox.askyesno("Potwierdzenie", f"Czy na pewno chcesz usunąć wydarzenie '{title}'?"):
            if self.event_manager.delete_event(event_id):
                self.update_calendar()
                self.update_daily_view()
                messagebox.showinfo("Sukces", "Wydarzenie zostało usunięte!")
            else:
                messagebox.showerror("Błąd", "Nie udało się usunąć wydarzenia")
    
    def search_events_dialog(self):
        """Otwiera dialog wyszukiwania wydarzeń"""
        search_term = simpledialog.askstring("Wyszukiwanie", "Wpisz szukaną frazę:")
        if search_term:
            results = self.event_manager.search_events(search_term)
            if results:
                result_text = f"Znaleziono {len(results)} wydarzeń:\n\n"
                for event in results:
                    result_text += f" {event[1]} o {event[2]} - {event[4]}\n"
                messagebox.showinfo("Wyniki wyszukiwania", result_text)
            else:
                messagebox.showinfo("Wyniki wyszukiwania", "Nie znaleziono żadnych wydarzeń")
    
    def show_context_menu(self, event):
        """Pokazuje menu kontekstowe"""
        selection = self.events_tree.selection()
        if selection:
            context_menu = tk.Menu(self.root, tearoff=0)
            context_menu.add_command(label="Edytuj", command=self.edit_selected_event)
            context_menu.add_command(label="Usuń", command=self.delete_selected_event)
            context_menu.tk_popup(event.x_root, event.y_root)


class EventDialog:
    """Dialog do dodawania/edycji wydarzeń"""
    
    def __init__(self, parent, title, initial_data=None):
        self.result = None
        
        # Tworzenie okna dialogowego
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrowanie okna
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.setup_dialog(initial_data)
        
        # Oczekiwanie na zamknięcie dialogu
        self.dialog.wait_window()
    
    def setup_dialog(self, initial_data):
        """Tworzy interfejs dialogu"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Godzina rozpoczęcia
        ttk.Label(main_frame, text="Godzina rozpoczęcia (HH:MM):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.start_time_var = tk.StringVar(value=initial_data.get("start_time", "") if initial_data else "")
        ttk.Entry(main_frame, textvariable=self.start_time_var, width=30).grid(row=0, column=1, pady=5, sticky=(tk.W, tk.E))
        
        # Godzina zakończenia
        ttk.Label(main_frame, text="Godzina zakończenia (opcjonalnie):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.end_time_var = tk.StringVar(value=initial_data.get("end_time", "") if initial_data else "")
        ttk.Entry(main_frame, textvariable=self.end_time_var, width=30).grid(row=1, column=1, pady=5, sticky=(tk.W, tk.E))
        
        # Tytuł
        ttk.Label(main_frame, text="Tytuł wydarzenia:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.title_var = tk.StringVar(value=initial_data.get("title", "") if initial_data else "")
        ttk.Entry(main_frame, textvariable=self.title_var, width=30).grid(row=2, column=1, pady=5, sticky=(tk.W, tk.E))
        
        # Opis
        ttk.Label(main_frame, text="Opis (opcjonalnie):").grid(row=3, column=0, sticky=(tk.W, tk.N), pady=5)
        self.description_text = tk.Text(main_frame, height=5, width=30)
        self.description_text.grid(row=3, column=1, pady=5, sticky=(tk.W, tk.E))
        if initial_data and initial_data.get("description"):
            self.description_text.insert("1.0", initial_data["description"])
        
        # Przyciski
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Zapisz", command=self.save_event).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Anuluj", command=self.dialog.destroy).grid(row=0, column=1, padx=5)
        
        # Konfiguracja rozciągania
        main_frame.columnconfigure(1, weight=1)
    
    def save_event(self):
        """Zapisuje dane wydarzenia"""
        start_time = self.start_time_var.get().strip()
        end_time = self.end_time_var.get().strip()
        title = self.title_var.get().strip()
        description = self.description_text.get("1.0", tk.END).strip()
        
        if not start_time:
            messagebox.showerror("Błąd", "Podaj godzinę rozpoczęcia")
            return
        
        if not title:
            messagebox.showerror("Błąd", "Podaj tytuł wydarzenia")
            return
        
        self.result = {
            "start_time": start_time,
            "end_time": end_time if end_time else None,
            "title": title,
            "description": description
        }
        
        self.dialog.destroy()
