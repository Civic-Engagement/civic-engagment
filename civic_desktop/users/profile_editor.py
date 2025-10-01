"""
Profile Editor - User profile management and editing
Allows users to update their profile information and view activity history
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

try:
    from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
        QLabel, QPushButton, QGroupBox, QDialog,
        QLineEdit, QTextEdit, QMessageBox, QTabWidget,
        QListWidget, QListWidgetItem, QComboBox
    )
    from PyQt5.QtCore import Qt, pyqtSignal
    from PyQt5.QtGui import QFont
    PYQT_AVAILABLE = True
except ImportError:
    print("Warning: PyQt5 not available. GUI functionality disabled.")
    PYQT_AVAILABLE = False

# Import modules
sys.path.append(str(Path(__file__).parent.parent))
from users.backend import UserBackend
from users.auth import SessionManager
from blockchain.blockchain import add_user_action, search_user_actions


class ProfileEditDialog(QDialog if PYQT_AVAILABLE else object):
    """Dialog for editing user profile"""
    
    profile_updated = pyqtSignal()
    
    def __init__(self, current_user: Dict, parent=None):
        if not PYQT_AVAILABLE:
            raise RuntimeError("PyQt5 not available")
        
        super().__init__(parent)
        self.current_user = current_user
        self.user_backend = UserBackend()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup profile edit dialog UI"""
        self.setWindowTitle("Edit Profile")
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout()
        
        # Profile picture placeholder
        profile_pic_group = QGroupBox("Profile Picture")
        profile_pic_layout = QVBoxLayout()
        
        pic_label = QLabel("👤")
        pic_label.setFont(QFont("Arial", 48))
        pic_label.setAlignment(Qt.AlignCenter)
        profile_pic_layout.addWidget(pic_label)
        
        change_pic_button = QPushButton("Change Picture (Coming Soon)")
        change_pic_button.setEnabled(False)
        profile_pic_layout.addWidget(change_pic_button)
        
        profile_pic_group.setLayout(profile_pic_layout)
        layout.addWidget(profile_pic_group)
        
        # Editable fields
        form_layout = QFormLayout()
        
        # First name
        self.first_name_input = QLineEdit()
        self.first_name_input.setText(self.current_user.get('first_name', ''))
        form_layout.addRow("First Name:", self.first_name_input)
        
        # Last name
        self.last_name_input = QLineEdit()
        self.last_name_input.setText(self.current_user.get('last_name', ''))
        form_layout.addRow("Last Name:", self.last_name_input)
        
        # Email (read-only)
        email_label = QLabel(self.current_user.get('email', ''))
        email_label.setStyleSheet("color: gray;")
        form_layout.addRow("Email:", email_label)
        
        # City
        self.city_input = QLineEdit()
        self.city_input.setText(self.current_user.get('city', ''))
        form_layout.addRow("City:", self.city_input)
        
        # State
        self.state_input = QLineEdit()
        self.state_input.setText(self.current_user.get('state', ''))
        form_layout.addRow("State:", self.state_input)
        
        # Country
        self.country_input = QLineEdit()
        self.country_input.setText(self.current_user.get('country', ''))
        form_layout.addRow("Country:", self.country_input)
        
        # Bio (optional)
        self.bio_input = QTextEdit()
        self.bio_input.setPlaceholderText("Tell us about yourself...")
        self.bio_input.setMaximumHeight(80)
        if 'bio' in self.current_user:
            self.bio_input.setText(self.current_user['bio'])
        form_layout.addRow("Bio:", self.bio_input)
        
        layout.addLayout(form_layout)
        
        # Note about restricted fields
        note_label = QLabel(
            "Note: Email and role cannot be changed. Contact an administrator if you need to update these fields."
        )
        note_label.setWordWrap(True)
        note_label.setStyleSheet("color: gray; font-style: italic; font-size: 9pt;")
        layout.addWidget(note_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_button = QPushButton("Save Changes")
        save_button.clicked.connect(self.save_profile)
        button_layout.addWidget(save_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def save_profile(self):
        """Save profile changes"""
        # Validate inputs
        first_name = self.first_name_input.text().strip()
        last_name = self.last_name_input.text().strip()
        
        if not first_name or not last_name:
            QMessageBox.warning(self, "Validation Error", "First name and last name are required")
            return
        
        city = self.city_input.text().strip()
        state = self.state_input.text().strip()
        country = self.country_input.text().strip()
        
        if not city or not state or not country:
            QMessageBox.warning(self, "Validation Error", "Location information is required")
            return
        
        bio = self.bio_input.toPlainText().strip()
        
        # Prepare updated profile data
        updated_data = {
            'first_name': first_name,
            'last_name': last_name,
            'city': city,
            'state': state,
            'country': country,
            'bio': bio
        }
        
        # Track changes for blockchain
        changes = []
        for key, new_value in updated_data.items():
            old_value = self.current_user.get(key, '')
            if old_value != new_value:
                changes.append({
                    'field': key,
                    'old_value': old_value,
                    'new_value': new_value
                })
        
        if not changes:
            QMessageBox.information(self, "No Changes", "No changes were made to your profile")
            return
        
        # Update profile
        try:
            success = self.user_backend.update_user_profile(
                self.current_user['email'],
                updated_data
            )
            
            if success:
                # Record to blockchain
                try:
                    add_user_action(
                        action_type='profile_updated',
                        user_email=self.current_user['email'],
                        data={
                            'changes': changes,
                            'updated_at': datetime.now().isoformat()
                        }
                    )
                except Exception as e:
                    print(f"Warning: Failed to record profile update to blockchain: {e}")
                
                # Update session
                SessionManager.update_current_user(updated_data)
                
                QMessageBox.information(
                    self, "Success",
                    "Your profile has been updated successfully!"
                )
                self.profile_updated.emit()
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Failed to update profile. Please try again.")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while updating profile:\n\n{str(e)}")


class ActivityHistoryWidget(QWidget if PYQT_AVAILABLE else object):
    """Widget for displaying user activity history"""
    
    def __init__(self, user_email: str, parent=None):
        if not PYQT_AVAILABLE:
            raise RuntimeError("PyQt5 not available")
        
        super().__init__(parent)
        self.user_email = user_email
        self.setup_ui()
        self.load_activity()
    
    def setup_ui(self):
        """Setup activity history UI"""
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("📊 Activity History")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Refresh button
        refresh_button = QPushButton("🔄 Refresh")
        refresh_button.clicked.connect(self.load_activity)
        header_layout.addWidget(refresh_button)
        
        layout.addLayout(header_layout)
        
        # Activity type filter
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Filter by:"))
        
        self.activity_filter = QComboBox()
        self.activity_filter.addItem("All Activities", "all")
        self.activity_filter.addItem("Profile Updates", "profile_updated")
        self.activity_filter.addItem("Debates", "topic_created,argument_submitted")
        self.activity_filter.addItem("Events", "event_created,event_registered")
        self.activity_filter.addItem("Crypto", "crypto_transaction,reward_earned")
        self.activity_filter.currentIndexChanged.connect(self.load_activity)
        filter_layout.addWidget(self.activity_filter)
        
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        # Activity list
        self.activity_list = QListWidget()
        layout.addWidget(self.activity_list)
        
        self.setLayout(layout)
    
    def load_activity(self):
        """Load user activity from blockchain"""
        self.activity_list.clear()
        
        # Get filter
        filter_type = self.activity_filter.currentData()
        
        try:
            # Search blockchain for user actions
            if filter_type == "all":
                activities = search_user_actions(self.user_email, limit=100)
            else:
                # Handle multiple action types
                activities = []
                for action_type in filter_type.split(','):
                    activities.extend(search_user_actions(self.user_email, action_type, limit=50))
                
                # Sort by timestamp
                activities.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
                activities = activities[:100]
            
            if not activities:
                item = QListWidgetItem("No activity found")
                item.setFlags(Qt.NoItemFlags)
                self.activity_list.addItem(item)
                return
            
            # Display activities
            for activity in activities:
                action_type = activity.get('action_type', 'unknown')
                timestamp = activity.get('timestamp', '')
                
                # Format timestamp
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        time_str = dt.strftime('%b %d, %Y %I:%M %p')
                    except:
                        time_str = timestamp
                else:
                    time_str = 'Unknown time'
                
                # Create item text
                item_text = f"{self._get_action_emoji(action_type)} {action_type.replace('_', ' ').title()} - {time_str}"
                
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, activity)
                self.activity_list.addItem(item)
        
        except Exception as e:
            print(f"Error loading activity: {e}")
            item = QListWidgetItem(f"Error loading activity: {str(e)}")
            item.setFlags(Qt.NoItemFlags)
            self.activity_list.addItem(item)
    
    def _get_action_emoji(self, action_type: str) -> str:
        """Get emoji for action type"""
        emoji_map = {
            'user_registration': '👤',
            'user_login': '🔓',
            'profile_updated': '✏️',
            'topic_created': '💬',
            'argument_submitted': '📝',
            'event_created': '📅',
            'event_registered': '✅',
            'crypto_transaction': '💰',
            'reward_earned': '🎁'
        }
        return emoji_map.get(action_type, '📋')


# Export classes
__all__ = ['ProfileEditDialog', 'ActivityHistoryWidget']
