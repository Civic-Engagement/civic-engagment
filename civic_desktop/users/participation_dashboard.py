"""
Civic Participation Dashboard - Central hub for civic engagement
Provides quick access to all civic participation tools and metrics
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List

try:
    from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
        QLabel, QPushButton, QGroupBox, QFrame, QScrollArea,
        QListWidget, QListWidgetItem, QMessageBox, QProgressBar
    )
    from PyQt5.QtCore import Qt, pyqtSignal
    from PyQt5.QtGui import QFont
    PYQT_AVAILABLE = True
except ImportError:
    print("Warning: PyQt5 not available. GUI functionality disabled.")
    PYQT_AVAILABLE = False

# Import modules
sys.path.append(str(Path(__file__).parent.parent))
from users.auth import SessionManager
from blockchain.blockchain import search_user_actions
from events.event_manager import EventManager
from debates.backend import DebateBackend


class ParticipationDashboard(QWidget if PYQT_AVAILABLE else object):
    """Central civic participation dashboard"""
    
    # Signals for navigation
    navigate_to_debates = pyqtSignal()
    navigate_to_events = pyqtSignal()
    navigate_to_profile = pyqtSignal()
    
    def __init__(self, parent=None):
        if not PYQT_AVAILABLE:
            raise RuntimeError("PyQt5 not available")
        
        super().__init__(parent)
        self.event_manager = EventManager()
        self.debate_backend = DebateBackend()
        self.current_user = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup participation dashboard UI"""
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("🏛️ Civic Participation Dashboard")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Refresh button
        refresh_button = QPushButton("🔄 Refresh")
        refresh_button.clicked.connect(self.refresh_dashboard)
        header_layout.addWidget(refresh_button)
        
        layout.addLayout(header_layout)
        
        # Quick stats
        stats_frame = QFrame()
        stats_frame.setFrameStyle(QFrame.StyledPanel)
        stats_layout = QGridLayout()
        
        self.stats_labels = {}
        stats = [
            ("💬", "Active Debates", "debates_count"),
            ("📅", "Upcoming Events", "events_count"),
            ("✅", "Your Contributions", "contributions_count"),
            ("🏆", "Participation Score", "participation_score")
        ]
        
        for i, (emoji, label_text, key) in enumerate(stats):
            emoji_label = QLabel(emoji)
            emoji_label.setFont(QFont("Arial", 24))
            emoji_label.setAlignment(Qt.AlignCenter)
            
            text_label = QLabel(label_text)
            text_label.setAlignment(Qt.AlignCenter)
            
            value_label = QLabel("0")
            value_label.setFont(QFont("Arial", 20, QFont.Bold))
            value_label.setAlignment(Qt.AlignCenter)
            value_label.setStyleSheet("color: #2c3e50;")
            
            col = i % 4
            
            stats_layout.addWidget(emoji_label, 0, col)
            stats_layout.addWidget(value_label, 1, col)
            stats_layout.addWidget(text_label, 2, col)
            
            self.stats_labels[key] = value_label
        
        stats_frame.setLayout(stats_layout)
        layout.addWidget(stats_frame)
        
        # Quick actions
        actions_group = QGroupBox("⚡ Quick Actions")
        actions_layout = QGridLayout()
        
        # Action buttons
        actions = [
            ("💬 Join a Debate", self.navigate_to_debates.emit, "Participate in civic discussions"),
            ("📅 Attend an Event", self.navigate_to_events.emit, "Register for community events"),
            ("👤 Update Profile", self.navigate_to_profile.emit, "Manage your civic profile"),
        ]
        
        for i, (text, callback, tooltip) in enumerate(actions):
            button = QPushButton(text)
            button.setToolTip(tooltip)
            button.setMinimumHeight(50)
            button.clicked.connect(callback)
            row = i // 3
            col = i % 3
            actions_layout.addWidget(button, row, col)
        
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)
        
        # Participation progress
        progress_group = QGroupBox("📈 Your Civic Engagement Progress")
        progress_layout = QVBoxLayout()
        
        # Overall progress
        overall_label = QLabel("Overall Participation Level:")
        progress_layout.addWidget(overall_label)
        
        self.overall_progress = QProgressBar()
        self.overall_progress.setMinimum(0)
        self.overall_progress.setMaximum(100)
        self.overall_progress.setValue(0)
        progress_layout.addWidget(self.overall_progress)
        
        # Milestones
        milestones_label = QLabel("Milestones:")
        milestones_label.setFont(QFont("Arial", 10, QFont.Bold))
        progress_layout.addWidget(milestones_label)
        
        self.milestones_list = QListWidget()
        self.milestones_list.setMaximumHeight(120)
        progress_layout.addWidget(self.milestones_list)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # Recent activity
        activity_group = QGroupBox("📋 Recent Civic Activity")
        activity_layout = QVBoxLayout()
        
        self.recent_activity_list = QListWidget()
        self.recent_activity_list.setMaximumHeight(150)
        activity_layout.addWidget(self.recent_activity_list)
        
        activity_group.setLayout(activity_layout)
        layout.addWidget(activity_group)
        
        # Notifications
        notifications_group = QGroupBox("🔔 Notifications & Updates")
        notifications_layout = QVBoxLayout()
        
        self.notifications_list = QListWidget()
        self.notifications_list.setMaximumHeight(120)
        notifications_layout.addWidget(self.notifications_list)
        
        notifications_group.setLayout(notifications_layout)
        layout.addWidget(notifications_group)
        
        self.setLayout(layout)
    
    def refresh_dashboard(self):
        """Refresh dashboard data"""
        self.current_user = SessionManager.get_current_user()
        
        if not self.current_user:
            return
        
        # Update stats
        self.update_stats()
        
        # Update progress
        self.update_progress()
        
        # Update recent activity
        self.update_recent_activity()
        
        # Update notifications
        self.update_notifications()
    
    def update_stats(self):
        """Update quick stats"""
        if not self.current_user:
            return
        
        try:
            # Count active debates
            topics = self.debate_backend.list_topics()
            active_debates = len([t for t in topics if t.get('status') == 'approved'])
            self.stats_labels['debates_count'].setText(str(active_debates))
            
            # Count upcoming events
            events = self.event_manager.list_events(filter_status='scheduled')
            upcoming_events = len(events)
            self.stats_labels['events_count'].setText(str(upcoming_events))
            
            # Count user contributions
            user_activities = search_user_actions(self.current_user['email'], limit=1000)
            contribution_types = ['topic_created', 'argument_submitted', 'event_created', 'event_registered']
            contributions = len([a for a in user_activities if a.get('action_type') in contribution_types])
            self.stats_labels['contributions_count'].setText(str(contributions))
            
            # Calculate participation score (simple formula)
            participation_score = min(100, contributions * 2)
            self.stats_labels['participation_score'].setText(str(participation_score))
        
        except Exception as e:
            print(f"Error updating stats: {e}")
    
    def update_progress(self):
        """Update participation progress"""
        if not self.current_user:
            return
        
        try:
            # Get user activities
            user_activities = search_user_actions(self.current_user['email'], limit=1000)
            
            # Calculate progress based on different activity types
            activity_types = {
                'profile_updated': False,
                'topic_created': False,
                'argument_submitted': False,
                'event_created': False,
                'event_registered': False
            }
            
            for activity in user_activities:
                action_type = activity.get('action_type', '')
                if action_type in activity_types:
                    activity_types[action_type] = True
            
            # Calculate progress
            completed = sum(1 for v in activity_types.values() if v)
            total = len(activity_types)
            progress_percent = int((completed / total) * 100) if total > 0 else 0
            
            self.overall_progress.setValue(progress_percent)
            
            # Update milestones
            self.milestones_list.clear()
            
            milestones = [
                ("✅" if activity_types['profile_updated'] else "⬜", "Complete your profile"),
                ("✅" if activity_types['topic_created'] else "⬜", "Create a debate topic"),
                ("✅" if activity_types['argument_submitted'] else "⬜", "Submit an argument"),
                ("✅" if activity_types['event_created'] else "⬜", "Organize an event"),
                ("✅" if activity_types['event_registered'] else "⬜", "Register for an event")
            ]
            
            for emoji, text in milestones:
                item = QListWidgetItem(f"{emoji} {text}")
                self.milestones_list.addItem(item)
        
        except Exception as e:
            print(f"Error updating progress: {e}")
    
    def update_recent_activity(self):
        """Update recent activity list"""
        if not self.current_user:
            return
        
        self.recent_activity_list.clear()
        
        try:
            # Get recent activities
            activities = search_user_actions(self.current_user['email'], limit=10)
            
            if not activities:
                item = QListWidgetItem("No recent activity")
                item.setFlags(Qt.NoItemFlags)
                self.recent_activity_list.addItem(item)
                return
            
            for activity in activities[:5]:  # Show only last 5
                action_type = activity.get('action_type', 'unknown')
                timestamp = activity.get('timestamp', '')
                
                # Format timestamp
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        time_str = dt.strftime('%b %d, %I:%M %p')
                    except:
                        time_str = 'Recently'
                else:
                    time_str = 'Recently'
                
                item_text = f"{self._get_action_emoji(action_type)} {action_type.replace('_', ' ').title()} - {time_str}"
                item = QListWidgetItem(item_text)
                self.recent_activity_list.addItem(item)
        
        except Exception as e:
            print(f"Error updating recent activity: {e}")
    
    def update_notifications(self):
        """Update notifications"""
        self.notifications_list.clear()
        
        try:
            # Get upcoming events user is registered for
            events = self.event_manager.list_events(filter_status='scheduled', limit=20)
            user_events = []
            
            if self.current_user:
                user_email = self.current_user['email']
                user_events = [e for e in events if user_email in e.get('attendees', [])]
            
            # Add event notifications
            now = datetime.now()
            for event in user_events[:3]:  # Show only next 3 events
                event_datetime = datetime.fromisoformat(event['datetime'])
                time_until = event_datetime - now
                
                if time_until.days == 0:
                    time_text = "Today!"
                elif time_until.days == 1:
                    time_text = "Tomorrow"
                else:
                    time_text = f"In {time_until.days} days"
                
                item_text = f"📅 Upcoming: {event['title']} - {time_text}"
                item = QListWidgetItem(item_text)
                self.notifications_list.addItem(item)
            
            # Add general notifications
            if len(user_events) == 0:
                item = QListWidgetItem("💡 Tip: Register for upcoming civic events to stay engaged!")
                self.notifications_list.addItem(item)
            
            # Get active debates
            topics = self.debate_backend.list_topics()
            active_debates = [t for t in topics if t.get('status') == 'approved']
            
            if len(active_debates) > 0:
                item = QListWidgetItem(f"💬 {len(active_debates)} active debates need your input!")
                self.notifications_list.addItem(item)
            
            if self.notifications_list.count() == 0:
                item = QListWidgetItem("✨ All caught up! Great work on your civic participation.")
                item.setFlags(Qt.NoItemFlags)
                self.notifications_list.addItem(item)
        
        except Exception as e:
            print(f"Error updating notifications: {e}")
    
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
            'event_attendance': '👋',
            'crypto_transaction': '💰',
            'reward_earned': '🎁'
        }
        return emoji_map.get(action_type, '📋')


# Export main widget
__all__ = ['ParticipationDashboard']
