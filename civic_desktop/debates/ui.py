"""
Debates UI - Democratic Discussion Platform Interface
Provides UI for debate topics, arguments, and voting
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

try:
    from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
        QLabel, QPushButton, QGroupBox, QFrame, QScrollArea,
        QListWidget, QListWidgetItem, QDialog, QLineEdit, QTextEdit,
        QComboBox, QMessageBox, QTabWidget, QRadioButton, QButtonGroup
    )
    from PyQt5.QtCore import Qt, pyqtSignal
    from PyQt5.QtGui import QFont
    PYQT_AVAILABLE = True
except ImportError:
    print("Warning: PyQt5 not available. GUI functionality disabled.")
    PYQT_AVAILABLE = False

# Import debate backend
sys.path.append(str(Path(__file__).parent.parent))
from debates.backend import DebateBackend, DebateStatus, ArgumentType
from users.auth import SessionManager


class TopicCreationDialog(QDialog if PYQT_AVAILABLE else object):
    """Dialog for creating new debate topics"""
    
    def __init__(self, parent=None):
        if not PYQT_AVAILABLE:
            raise RuntimeError("PyQt5 not available")
        
        super().__init__(parent)
        self.debate_backend = DebateBackend()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup topic creation dialog UI"""
        self.setWindowTitle("Create Debate Topic")
        self.setMinimumSize(600, 450)
        
        layout = QVBoxLayout()
        
        # Form for topic details
        form_layout = QFormLayout()
        
        # Topic title
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter debate topic title...")
        form_layout.addRow("Title*:", self.title_input)
        
        # Topic description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Enter detailed description of the debate topic...")
        self.description_input.setMaximumHeight(150)
        form_layout.addRow("Description*:", self.description_input)
        
        # Jurisdiction
        self.jurisdiction_combo = QComboBox()
        self.jurisdiction_combo.addItem("Local", "local")
        self.jurisdiction_combo.addItem("State", "state")
        self.jurisdiction_combo.addItem("Federal", "federal")
        self.jurisdiction_combo.addItem("Constitutional", "constitutional")
        form_layout.addRow("Jurisdiction*:", self.jurisdiction_combo)
        
        # Location
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("City, State")
        form_layout.addRow("Location*:", self.location_input)
        
        layout.addLayout(form_layout)
        
        # Requirements notice
        notice_label = QLabel(
            "Note: Topics on constitutional matters require Elder review. "
            "All topics are subject to constitutional compliance checking."
        )
        notice_label.setWordWrap(True)
        notice_label.setStyleSheet("color: blue; font-style: italic; padding: 10px;")
        layout.addWidget(notice_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        create_button = QPushButton("Create Topic")
        create_button.clicked.connect(self.create_topic)
        button_layout.addWidget(create_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def create_topic(self):
        """Create the debate topic"""
        # Validate inputs
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Validation Error", "Topic title is required")
            return
        
        description = self.description_input.toPlainText().strip()
        if not description:
            QMessageBox.warning(self, "Validation Error", "Topic description is required")
            return
        
        jurisdiction = self.jurisdiction_combo.currentData()
        location = self.location_input.text().strip()
        if not location:
            QMessageBox.warning(self, "Validation Error", "Location is required")
            return
        
        # Get current user
        user = SessionManager.get_current_user()
        if not user:
            QMessageBox.warning(self, "Authentication Error", "You must be logged in to create topics")
            return
        
        # Create topic
        success, message, topic_id = self.debate_backend.create_topic(
            title=title,
            description=description,
            jurisdiction=jurisdiction,
            location=location,
            creator_email=user['email']
        )
        
        if success:
            QMessageBox.information(
                self, "Success", 
                f"Topic created successfully!\n\nTopic ID: {topic_id}\n\n"
                "The topic is now available for community participation."
            )
            self.accept()
        else:
            QMessageBox.warning(self, "Error", f"Failed to create topic:\n\n{message}")


class ArgumentDialog(QDialog if PYQT_AVAILABLE else object):
    """Dialog for submitting arguments"""
    
    def __init__(self, topic_id: str, topic_title: str, parent=None):
        if not PYQT_AVAILABLE:
            raise RuntimeError("PyQt5 not available")
        
        super().__init__(parent)
        self.topic_id = topic_id
        self.topic_title = topic_title
        self.debate_backend = DebateBackend()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup argument submission dialog UI"""
        self.setWindowTitle(f"Submit Argument - {self.topic_title}")
        self.setMinimumSize(550, 400)
        
        layout = QVBoxLayout()
        
        # Topic info
        topic_label = QLabel(f"Topic: {self.topic_title}")
        topic_label.setFont(QFont("Arial", 11, QFont.Bold))
        topic_label.setWordWrap(True)
        layout.addWidget(topic_label)
        
        # Position selection
        position_group = QGroupBox("Your Position*")
        position_layout = QVBoxLayout()
        
        self.position_group = QButtonGroup()
        
        for_radio = QRadioButton("For - Support this topic")
        self.position_group.addButton(for_radio, 0)
        position_layout.addWidget(for_radio)
        
        against_radio = QRadioButton("Against - Oppose this topic")
        self.position_group.addButton(against_radio, 1)
        position_layout.addWidget(against_radio)
        
        neutral_radio = QRadioButton("Neutral - Provide balanced perspective")
        self.position_group.addButton(neutral_radio, 2)
        position_layout.addWidget(neutral_radio)
        
        for_radio.setChecked(True)
        
        position_group.setLayout(position_layout)
        layout.addWidget(position_group)
        
        # Argument text
        arg_label = QLabel("Your Argument*:")
        layout.addWidget(arg_label)
        
        self.argument_input = QTextEdit()
        self.argument_input.setPlaceholderText(
            "Enter your argument here. Be clear, respectful, and provide evidence to support your position..."
        )
        layout.addWidget(self.argument_input)
        
        # Sources
        sources_label = QLabel("Sources (optional):")
        layout.addWidget(sources_label)
        
        self.sources_input = QLineEdit()
        self.sources_input.setPlaceholderText("Enter sources or references (comma-separated)")
        layout.addWidget(self.sources_input)
        
        # Guidelines notice
        guidelines_label = QLabel(
            "Guidelines: Arguments must be respectful, factual, and constructive. "
            "Violation of community standards may result in moderation."
        )
        guidelines_label.setWordWrap(True)
        guidelines_label.setStyleSheet("color: gray; font-style: italic; font-size: 9pt;")
        layout.addWidget(guidelines_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        submit_button = QPushButton("Submit Argument")
        submit_button.clicked.connect(self.submit_argument)
        button_layout.addWidget(submit_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def submit_argument(self):
        """Submit the argument"""
        # Get position
        position_map = {0: 'for', 1: 'against', 2: 'neutral'}
        position = position_map.get(self.position_group.checkedId(), 'for')
        
        # Get argument text
        argument_text = self.argument_input.toPlainText().strip()
        if not argument_text:
            QMessageBox.warning(self, "Validation Error", "Argument text is required")
            return
        
        if len(argument_text) < 20:
            QMessageBox.warning(self, "Validation Error", "Argument must be at least 20 characters")
            return
        
        # Get sources
        sources_text = self.sources_input.text().strip()
        sources = [s.strip() for s in sources_text.split(',') if s.strip()] if sources_text else []
        
        # Get current user
        user = SessionManager.get_current_user()
        if not user:
            QMessageBox.warning(self, "Authentication Error", "You must be logged in to submit arguments")
            return
        
        # Submit argument
        success, message, arg_id = self.debate_backend.add_argument(
            topic_id=self.topic_id,
            position=position,
            text=argument_text,
            sources=sources,
            author_email=user['email']
        )
        
        if success:
            QMessageBox.information(
                self, "Success",
                "Your argument has been submitted successfully!\n\n"
                "It is now visible to the community for review and voting."
            )
            self.accept()
        else:
            QMessageBox.warning(self, "Error", f"Failed to submit argument:\n\n{message}")


class TopicDetailsWidget(QWidget if PYQT_AVAILABLE else object):
    """Widget for displaying topic details and arguments"""
    
    def __init__(self, topic: Dict, parent=None):
        if not PYQT_AVAILABLE:
            raise RuntimeError("PyQt5 not available")
        
        super().__init__(parent)
        self.topic = topic
        self.debate_backend = DebateBackend()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup topic details UI"""
        layout = QVBoxLayout()
        
        # Topic header
        header_layout = QVBoxLayout()
        
        title_label = QLabel(self.topic['title'])
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setWordWrap(True)
        header_layout.addWidget(title_label)
        
        # Topic metadata
        meta_text = f"Created by: {self.topic.get('creator_email', 'Unknown')} | "
        meta_text += f"Jurisdiction: {self.topic.get('jurisdiction', 'N/A').title()} | "
        meta_text += f"Status: {self.topic.get('status', 'unknown').upper()}"
        
        meta_label = QLabel(meta_text)
        meta_label.setStyleSheet("color: gray;")
        header_layout.addWidget(meta_label)
        
        layout.addLayout(header_layout)
        
        # Description
        desc_group = QGroupBox("Description")
        desc_layout = QVBoxLayout()
        
        desc_label = QLabel(self.topic.get('description', 'No description provided'))
        desc_label.setWordWrap(True)
        desc_layout.addWidget(desc_label)
        
        desc_group.setLayout(desc_layout)
        layout.addWidget(desc_group)
        
        # Arguments
        args_group = QGroupBox("Arguments")
        args_layout = QVBoxLayout()
        
        # Submit argument button
        submit_arg_button = QPushButton("➕ Submit Your Argument")
        submit_arg_button.clicked.connect(self.submit_argument)
        args_layout.addWidget(submit_arg_button)
        
        # Arguments list
        self.arguments_list = QListWidget()
        self.load_arguments()
        args_layout.addWidget(self.arguments_list)
        
        args_group.setLayout(args_layout)
        layout.addWidget(args_group)
        
        self.setLayout(layout)
    
    def load_arguments(self):
        """Load and display arguments"""
        self.arguments_list.clear()
        
        arguments = self.debate_backend.get_arguments(self.topic['id'])
        
        if not arguments:
            item = QListWidgetItem("No arguments yet. Be the first to contribute!")
            item.setFlags(Qt.NoItemFlags)
            self.arguments_list.addItem(item)
            return
        
        for arg in arguments:
            position_emoji = {
                'for': '✅',
                'against': '❌',
                'neutral': '⚖️'
            }.get(arg.get('position', 'neutral'), '⚖️')
            
            item_text = f"{position_emoji} {arg.get('position', 'neutral').upper()} - "
            item_text += f"{arg.get('text', '')[:100]}..."
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, arg)
            self.arguments_list.addItem(item)
    
    def submit_argument(self):
        """Open argument submission dialog"""
        dialog = ArgumentDialog(self.topic['id'], self.topic['title'], self)
        if dialog.exec_():
            self.load_arguments()


class DebateUI(QWidget if PYQT_AVAILABLE else object):
    """Main debate UI for civic discussions"""
    
    def __init__(self, parent=None):
        if not PYQT_AVAILABLE:
            raise RuntimeError("PyQt5 not available")
        
        super().__init__(parent)
        self.debate_backend = DebateBackend()
        self.setup_ui()
        self.refresh_topics()
    
    def setup_ui(self):
        """Setup debate UI"""
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("💬 Civic Debates & Discussions")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Create topic button
        create_button = QPushButton("➕ Create Topic")
        create_button.clicked.connect(self.create_topic)
        header_layout.addWidget(create_button)
        
        # Refresh button
        refresh_button = QPushButton("🔄 Refresh")
        refresh_button.clicked.connect(self.refresh_topics)
        header_layout.addWidget(refresh_button)
        
        layout.addLayout(header_layout)
        
        # Filter controls
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Filter by:"))
        
        self.jurisdiction_filter = QComboBox()
        self.jurisdiction_filter.addItem("All Jurisdictions", "all")
        self.jurisdiction_filter.addItem("Local", "local")
        self.jurisdiction_filter.addItem("State", "state")
        self.jurisdiction_filter.addItem("Federal", "federal")
        self.jurisdiction_filter.addItem("Constitutional", "constitutional")
        self.jurisdiction_filter.currentIndexChanged.connect(self.refresh_topics)
        filter_layout.addWidget(self.jurisdiction_filter)
        
        self.status_filter = QComboBox()
        self.status_filter.addItem("Active Topics", "approved")
        self.status_filter.addItem("Pending Review", "pending")
        self.status_filter.addItem("All Topics", "all")
        self.status_filter.currentIndexChanged.connect(self.refresh_topics)
        filter_layout.addWidget(self.status_filter)
        
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        # Topics list
        self.topics_list = QListWidget()
        self.topics_list.itemDoubleClicked.connect(self.show_topic_details)
        layout.addWidget(self.topics_list)
        
        # Topic details area (right side or bottom)
        self.details_container = QWidget()
        self.details_layout = QVBoxLayout()
        self.details_container.setLayout(self.details_layout)
        layout.addWidget(self.details_container)
        
        self.setLayout(layout)
    
    def refresh_topics(self):
        """Refresh topics list"""
        self.topics_list.clear()
        
        # Get filter values
        jurisdiction = self.jurisdiction_filter.currentData()
        status = self.status_filter.currentData()
        
        # Get topics
        topics = self.debate_backend.list_topics()
        
        # Apply filters
        if jurisdiction != "all":
            topics = [t for t in topics if t.get('jurisdiction') == jurisdiction]
        
        if status != "all":
            topics = [t for t in topics if t.get('status') == status]
        
        # Populate list
        if not topics:
            item = QListWidgetItem("No topics found. Create the first one!")
            item.setFlags(Qt.NoItemFlags)
            self.topics_list.addItem(item)
            return
        
        for topic in topics:
            item_text = f"{topic['title']} ({topic.get('jurisdiction', 'N/A').title()})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, topic)
            self.topics_list.addItem(item)
    
    def create_topic(self):
        """Open topic creation dialog"""
        dialog = TopicCreationDialog(self)
        if dialog.exec_():
            self.refresh_topics()
    
    def show_topic_details(self, item: QListWidgetItem):
        """Show topic details"""
        topic = item.data(Qt.UserRole)
        if not topic:
            return
        
        # Clear existing details
        for i in reversed(range(self.details_layout.count())):
            widget = self.details_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        # Add topic details widget
        details_widget = TopicDetailsWidget(topic, self)
        self.details_layout.addWidget(details_widget)


# Export main widget
__all__ = ['DebateUI', 'TopicCreationDialog', 'ArgumentDialog', 'TopicDetailsWidget']
