"""
Calendar UI - Event scheduling and calendar interface
Provides visual calendar for civic event management
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List

try:
    from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
        QLabel, QPushButton, QGroupBox, QFrame, QScrollArea,
        QListWidget, QListWidgetItem, QCalendarWidget, QDialog,
        QLineEdit, QTextEdit, QComboBox, QDateTimeEdit, QSpinBox,
        QMessageBox, QCheckBox, QTabWidget
    )
    from PyQt5.QtCore import Qt, QDateTime, pyqtSignal, QDate
    from PyQt5.QtGui import QFont, QTextCharFormat, QColor
    PYQT_AVAILABLE = True
except ImportError:
    print("Warning: PyQt5 not available. GUI functionality disabled.")
    PYQT_AVAILABLE = False

# Import event manager
sys.path.append(str(Path(__file__).parent.parent))
from events.event_manager import EventManager
from users.auth import SessionManager


class EventCreationDialog(QDialog if PYQT_AVAILABLE else object):
    """Dialog for creating new civic events"""
    
    def __init__(self, parent=None):
        if not PYQT_AVAILABLE:
            raise RuntimeError("PyQt5 not available")
        
        super().__init__(parent)
        self.event_manager = EventManager()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup event creation dialog UI"""
        self.setWindowTitle("Create Civic Event")
        self.setMinimumSize(600, 500)
        
        layout = QVBoxLayout()
        
        # Form for event details
        form_layout = QFormLayout()
        
        # Event title
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter event title...")
        form_layout.addRow("Title*:", self.title_input)
        
        # Event type
        self.type_combo = QComboBox()
        for event_type, details in EventManager.EVENT_TYPES.items():
            self.type_combo.addItem(f"{event_type.replace('_', ' ').title()} - {details['description']}", event_type)
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        form_layout.addRow("Event Type*:", self.type_combo)
        
        # Event datetime
        self.datetime_input = QDateTimeEdit()
        self.datetime_input.setDateTime(QDateTime.currentDateTime().addDays(7))
        self.datetime_input.setCalendarPopup(True)
        form_layout.addRow("Date & Time*:", self.datetime_input)
        
        # Event description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Enter event description...")
        self.description_input.setMaximumHeight(100)
        form_layout.addRow("Description*:", self.description_input)
        
        # Venue location
        self.venue_input = QLineEdit()
        self.venue_input.setPlaceholderText("Enter venue address or location...")
        form_layout.addRow("Venue:", self.venue_input)
        
        # Capacity
        self.capacity_input = QSpinBox()
        self.capacity_input.setRange(0, 10000)
        self.capacity_input.setValue(0)
        self.capacity_input.setSpecialValueText("No Limit")
        form_layout.addRow("Capacity:", self.capacity_input)
        
        # Registration required
        self.registration_checkbox = QCheckBox("Require registration")
        self.registration_checkbox.setChecked(True)
        form_layout.addRow("Registration:", self.registration_checkbox)
        
        layout.addLayout(form_layout)
        
        # Requirements notice
        self.requirements_label = QLabel()
        self.requirements_label.setWordWrap(True)
        self.requirements_label.setStyleSheet("color: blue; font-style: italic;")
        layout.addWidget(self.requirements_label)
        
        # Update requirements for default type
        self.on_type_changed(0)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        create_button = QPushButton("Create Event")
        create_button.clicked.connect(self.create_event)
        button_layout.addWidget(create_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def on_type_changed(self, index):
        """Update requirements display when event type changes"""
        event_type = self.type_combo.currentData()
        if event_type in EventManager.EVENT_TYPES:
            requirements = EventManager.EVENT_TYPES[event_type]
            
            req_text = f"Requirements: {requirements['public_notice_days']} days advance notice"
            if requirements['constitutional_review']:
                req_text += " • Constitutional review required"
            if requirements['recording_required']:
                req_text += " • Recording required"
            if requirements['capacity_limits']:
                req_text += f" • Max capacity: {requirements['capacity_limits']}"
                self.capacity_input.setValue(requirements['capacity_limits'])
            
            self.requirements_label.setText(req_text)
    
    def create_event(self):
        """Create the event"""
        # Validate inputs
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Validation Error", "Event title is required")
            return
        
        description = self.description_input.toPlainText().strip()
        if not description:
            QMessageBox.warning(self, "Validation Error", "Event description is required")
            return
        
        event_type = self.type_combo.currentData()
        event_datetime = self.datetime_input.dateTime().toString(Qt.ISODate)
        venue = self.venue_input.text().strip()
        capacity = self.capacity_input.value() if self.capacity_input.value() > 0 else None
        registration_required = self.registration_checkbox.isChecked()
        
        # Get current user
        user = SessionManager.get_current_user()
        if not user:
            QMessageBox.warning(self, "Authentication Error", "You must be logged in to create events")
            return
        
        # Prepare event data
        event_data = {
            'title': title,
            'type': event_type,
            'datetime': event_datetime,
            'description': description,
            'venue': {'address': venue} if venue else {},
            'capacity': capacity,
            'registration_required': registration_required
        }
        
        # Create event
        success, message, event_id = self.event_manager.create_event(event_data, user['email'])
        
        if success:
            QMessageBox.information(self, "Success", f"Event created successfully!\n\nEvent ID: {event_id}")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", f"Failed to create event:\n\n{message}")


class EventDetailsDialog(QDialog if PYQT_AVAILABLE else object):
    """Dialog for viewing and managing event details"""
    
    def __init__(self, event: Dict, parent=None):
        if not PYQT_AVAILABLE:
            raise RuntimeError("PyQt5 not available")
        
        super().__init__(parent)
        self.event = event
        self.event_manager = EventManager()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup event details dialog UI"""
        self.setWindowTitle(f"Event: {self.event['title']}")
        self.setMinimumSize(500, 600)
        
        layout = QVBoxLayout()
        
        # Event information group
        info_group = QGroupBox("Event Information")
        info_layout = QFormLayout()
        
        info_layout.addRow("Title:", QLabel(self.event['title']))
        info_layout.addRow("Type:", QLabel(self.event['type'].replace('_', ' ').title()))
        info_layout.addRow("Status:", QLabel(self.event['status'].upper()))
        
        event_datetime = datetime.fromisoformat(self.event['datetime'])
        info_layout.addRow("Date & Time:", QLabel(event_datetime.strftime("%B %d, %Y at %I:%M %p")))
        
        info_layout.addRow("Organizer:", QLabel(self.event['organizer_email']))
        
        if self.event.get('venue'):
            venue_text = self.event['venue'].get('address', 'Not specified')
            info_layout.addRow("Venue:", QLabel(venue_text))
        
        capacity = self.event.get('capacity')
        attendee_count = len(self.event.get('attendees', []))
        if capacity:
            capacity_text = f"{attendee_count} / {capacity} registered"
        else:
            capacity_text = f"{attendee_count} registered (No limit)"
        info_layout.addRow("Attendance:", QLabel(capacity_text))
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Description
        desc_group = QGroupBox("Description")
        desc_layout = QVBoxLayout()
        desc_text = QLabel(self.event.get('description', 'No description provided'))
        desc_text.setWordWrap(True)
        desc_layout.addWidget(desc_text)
        desc_group.setLayout(desc_layout)
        layout.addWidget(desc_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        # Register button
        user = SessionManager.get_current_user()
        if user and user['email'] not in self.event.get('attendees', []):
            if self.event['status'] == 'scheduled':
                register_button = QPushButton("Register for Event")
                register_button.clicked.connect(self.register_for_event)
                button_layout.addWidget(register_button)
        
        # Status update buttons (for organizer)
        if user and user['email'] == self.event['organizer_email']:
            if self.event['status'] == 'scheduled':
                start_button = QPushButton("Start Event")
                start_button.clicked.connect(lambda: self.update_status('in_progress'))
                button_layout.addWidget(start_button)
            
            if self.event['status'] == 'in_progress':
                complete_button = QPushButton("Complete Event")
                complete_button.clicked.connect(lambda: self.update_status('completed'))
                button_layout.addWidget(complete_button)
            
            if self.event['status'] in ['scheduled', 'in_progress']:
                cancel_button = QPushButton("Cancel Event")
                cancel_button.clicked.connect(lambda: self.update_status('cancelled'))
                button_layout.addWidget(cancel_button)
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def register_for_event(self):
        """Register current user for event"""
        user = SessionManager.get_current_user()
        if not user:
            QMessageBox.warning(self, "Authentication Error", "You must be logged in to register")
            return
        
        success, message = self.event_manager.register_attendee(self.event['id'], user['email'])
        
        if success:
            QMessageBox.information(self, "Success", "Successfully registered for event!")
            self.accept()  # Close dialog to refresh
        else:
            QMessageBox.warning(self, "Registration Failed", message)
    
    def update_status(self, new_status: str):
        """Update event status"""
        user = SessionManager.get_current_user()
        if not user:
            QMessageBox.warning(self, "Authentication Error", "You must be logged in")
            return
        
        success, message = self.event_manager.update_event_status(
            self.event['id'], new_status, user['email']
        )
        
        if success:
            QMessageBox.information(self, "Success", f"Event status updated to {new_status}")
            self.accept()  # Close dialog to refresh
        else:
            QMessageBox.warning(self, "Update Failed", message)


class CalendarUI(QWidget if PYQT_AVAILABLE else object):
    """Main calendar UI for event management"""
    
    def __init__(self, parent=None):
        if not PYQT_AVAILABLE:
            raise RuntimeError("PyQt5 not available")
        
        super().__init__(parent)
        self.event_manager = EventManager()
        self.setup_ui()
        self.refresh_events()
    
    def setup_ui(self):
        """Setup calendar UI"""
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("📅 Civic Events Calendar")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Create event button
        create_button = QPushButton("➕ Create Event")
        create_button.clicked.connect(self.create_event)
        header_layout.addWidget(create_button)
        
        # Refresh button
        refresh_button = QPushButton("🔄 Refresh")
        refresh_button.clicked.connect(self.refresh_events)
        header_layout.addWidget(refresh_button)
        
        layout.addLayout(header_layout)
        
        # Main content area with tabs
        tabs = QTabWidget()
        
        # Upcoming events tab
        upcoming_tab = QWidget()
        upcoming_layout = QVBoxLayout()
        
        self.upcoming_list = QListWidget()
        self.upcoming_list.itemDoubleClicked.connect(self.show_event_details)
        upcoming_layout.addWidget(self.upcoming_list)
        
        upcoming_tab.setLayout(upcoming_layout)
        tabs.addTab(upcoming_tab, "Upcoming Events")
        
        # My events tab
        my_events_tab = QWidget()
        my_events_layout = QVBoxLayout()
        
        self.my_events_list = QListWidget()
        self.my_events_list.itemDoubleClicked.connect(self.show_event_details)
        my_events_layout.addWidget(self.my_events_list)
        
        my_events_tab.setLayout(my_events_layout)
        tabs.addTab(my_events_tab, "My Events")
        
        # Calendar view tab
        calendar_tab = QWidget()
        calendar_layout = QVBoxLayout()
        
        self.calendar_widget = QCalendarWidget()
        self.calendar_widget.clicked.connect(self.on_date_selected)
        calendar_layout.addWidget(self.calendar_widget)
        
        self.date_events_list = QListWidget()
        self.date_events_list.itemDoubleClicked.connect(self.show_event_details)
        calendar_layout.addWidget(self.date_events_list)
        
        calendar_tab.setLayout(calendar_layout)
        tabs.addTab(calendar_tab, "Calendar View")
        
        layout.addWidget(tabs)
        
        self.setLayout(layout)
    
    def refresh_events(self):
        """Refresh event lists"""
        # Get all scheduled events
        upcoming_events = self.event_manager.list_events(filter_status='scheduled')
        
        # Clear lists
        self.upcoming_list.clear()
        self.my_events_list.clear()
        
        # Get current user
        user = SessionManager.get_current_user()
        user_email = user['email'] if user else None
        
        # Populate lists
        for event in upcoming_events:
            event_datetime = datetime.fromisoformat(event['datetime'])
            item_text = f"{event['title']} - {event_datetime.strftime('%b %d, %Y %I:%M %p')}"
            
            # Add to upcoming list
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, event)
            self.upcoming_list.addItem(item)
            
            # Add to my events if user is organizer or attendee
            if user_email:
                if (event['organizer_email'] == user_email or 
                    user_email in event.get('attendees', [])):
                    my_item = QListWidgetItem(item_text)
                    my_item.setData(Qt.UserRole, event)
                    self.my_events_list.addItem(my_item)
    
    def on_date_selected(self, date: QDate):
        """Handle date selection in calendar"""
        self.date_events_list.clear()
        
        # Get all events
        all_events = self.event_manager.list_events()
        
        # Filter events for selected date
        selected_date = date.toPyDate()
        for event in all_events:
            event_datetime = datetime.fromisoformat(event['datetime'])
            if event_datetime.date() == selected_date:
                item_text = f"{event['title']} - {event_datetime.strftime('%I:%M %p')}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, event)
                self.date_events_list.addItem(item)
    
    def create_event(self):
        """Open event creation dialog"""
        dialog = EventCreationDialog(self)
        if dialog.exec_():
            self.refresh_events()
    
    def show_event_details(self, item: QListWidgetItem):
        """Show event details dialog"""
        event = item.data(Qt.UserRole)
        if event:
            dialog = EventDetailsDialog(event, self)
            if dialog.exec_():
                self.refresh_events()


# Export main widget
__all__ = ['CalendarUI', 'EventCreationDialog', 'EventDetailsDialog']
