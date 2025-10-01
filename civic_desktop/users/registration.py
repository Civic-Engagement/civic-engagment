
try:
    from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QStackedWidget,
        QLabel, QLineEdit, QPushButton, QCheckBox, QMessageBox, QTextEdit,
        QProgressBar, QFrame, QGroupBox, QFileDialog, QComboBox,
        QWizard, QWizardPage, QGridLayout, QSpacerItem, QSizePolicy
    )
    from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot
    from PyQt5.QtGui import QFont, QPalette, QPixmap
    PYQT_AVAILABLE = True
except ImportError:
    print("Warning: PyQt5 not available. GUI functionality disabled.")
    PYQT_AVAILABLE = False

# Import modules
sys.path.append(str(Path(__file__).parent.parent))
from users.auth import AuthenticationService
from users.backend import UserBackend
from users.keys import RSAKeyManager
from utils.validation import DataValidator

class RegistrationWorker(QThread if PYQT_AVAILABLE else object):
    """Worker thread for registration operations"""
    
    if PYQT_AVAILABLE:
        registration_completed = pyqtSignal(bool, str)
        key_generation_progress = pyqtSignal(str)
    
    def __init__(self, auth_service: AuthenticationService, registration_data: Dict[str, Any]):
        if PYQT_AVAILABLE:
            super().__init__()
        self.auth_service = auth_service
        self.registration_data = registration_data
        self.key_manager = RSAKeyManager()
    
    def run(self):
        """Execute registration in background thread"""
        if PYQT_AVAILABLE:
            try:
                # Step 1: Register user
                self.key_generation_progress.emit("Creating user account...")
                success, message = self.auth_service.register(self.registration_data)
                
                if success:
                    # Step 2: Generate RSA keys
                    self.key_generation_progress.emit("Generating cryptographic keys...")
                    user = self.auth_service.get_current_user()
                    if user:
                        key_success, key_msg, key_info = self.key_manager.generate_key_pair(user['user_id'])
                        if key_success:
                            self.key_generation_progress.emit("Registration complete!")
                        else:
                            message = f"{message} Warning: Key generation failed - {key_msg}"
                
                self.registration_completed.emit(success, message)
                
            except Exception as e:
                self.registration_completed.emit(False, f"Registration error: {str(e)}")

class PersonalInfoPage(QWizardPage if PYQT_AVAILABLE else object):
    """Step 1: Personal Information"""
    
    def __init__(self):
        if not PYQT_AVAILABLE:
            return
        super().__init__()
        self.setTitle("Personal Information")
        self.setSubTitle("Please provide your basic personal information")
        
        layout = QFormLayout()
        
        # First Name
        self.first_name_input = QLineEdit()
        self.first_name_input.setPlaceholderText("Enter your first name")
        self.first_name_input.textChanged.connect(self.validate_page)
        
        # Last Name  
        self.last_name_input = QLineEdit()
        self.last_name_input.setPlaceholderText("Enter your last name")
        self.last_name_input.textChanged.connect(self.validate_page)
        
        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email address")
        self.email_input.textChanged.connect(self.validate_page)
        
        layout.addRow("👤 First Name:", self.first_name_input)
        layout.addRow("👤 Last Name:", self.last_name_input)
        layout.addRow("📧 Email:", self.email_input)
        
        self.setLayout(layout)
    
    def validate_page(self):
        """Validate current page inputs"""
        if not PYQT_AVAILABLE:
            return True
            
        first_name = self.first_name_input.text().strip()
        last_name = self.last_name_input.text().strip()
        email = self.email_input.text().strip()
        
        # Validate each field
        validations = [
            DataValidator.validate_name(first_name, "First name"),
            DataValidator.validate_name(last_name, "Last name"), 
            DataValidator.validate_email(email)
        ]
        
        all_valid = all(valid for valid, _ in validations)
        
        # Show validation feedback
        if not all_valid:
            for valid, message in validations:
                if not valid:
                    # Could show specific field errors here
                    break
        
        return all_valid
    
    def isComplete(self):
        """Check if page is complete"""
        return self.validate_page()

class LocationPage(QWizardPage if PYQT_AVAILABLE else object):
    """Step 2: Location Details"""
    
    def __init__(self):
        if not PYQT_AVAILABLE:
            return
        super().__init__()
        self.setTitle("Location Information")
        self.setSubTitle("Your location determines your voting jurisdiction")
        
        layout = QFormLayout()
        
        # City
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("Enter your city")
        self.city_input.textChanged.connect(self.validate_page)
        
        # State/Province
        self.state_input = QLineEdit()
        self.state_input.setPlaceholderText("Enter your state or province")
        self.state_input.textChanged.connect(self.validate_page)
        
        # Country
        self.country_combo = QComboBox()
        self.country_combo.setEditable(True)
        self.setup_countries()
        self.country_combo.currentTextChanged.connect(self.validate_page)
        
        layout.addRow("🏙️ City:", self.city_input)
        layout.addRow("🗺️ State/Province:", self.state_input)
        layout.addRow("🌍 Country:", self.country_combo)
        
        # Info label
        info_label = QLabel("ℹ️ Your location information is used to determine your electoral jurisdiction and local governance participation.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #7f8c8d; font-style: italic; margin-top: 10px;")
        
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(info_label)
        
        self.setLayout(main_layout)
    
    def setup_countries(self):
        """Setup country dropdown with common countries"""
        countries = [
            "", "United States", "Canada", "United Kingdom", "Australia", 
            "Germany", "France", "Japan", "Brazil", "Mexico", "India",
            "South Africa", "Nigeria", "Argentina", "Chile", "Sweden",
            "Norway", "Denmark", "Netherlands", "Belgium", "Switzerland"
        ]
        self.country_combo.addItems(countries)
    
    def validate_page(self):
        """Validate location information"""
        if not PYQT_AVAILABLE:
            return True
            
        city = self.city_input.text().strip()
        state = self.state_input.text().strip()
        country = self.country_combo.currentText().strip()
        
        is_valid, message = DataValidator.validate_location(city, state, country)
        return is_valid
    
    def isComplete(self):
        """Check if page is complete"""
        return self.validate_page()

class DocumentUploadPage(QWizardPage if PYQT_AVAILABLE else object):
    """Step 3: ID Document Upload"""
    
    def __init__(self):
        if not PYQT_AVAILABLE:
            return
        super().__init__()
        self.setTitle("Identity Verification")
        self.setSubTitle("Upload a government-issued ID for verification")
        
        layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel("""
        📋 Please upload a clear photo or scan of one of the following documents:
        
        • Driver's License
        • Passport
        • National ID Card
        • State ID Card
        
        ⚠️ Ensure the document is:
        • Clearly visible and readable
        • Not expired
        • Shows your full name matching the information provided
        """)
        instructions.setWordWrap(True)
        instructions.setStyleSheet("background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 15px;")
        
        # File selection
        file_layout = QHBoxLayout()
        
        self.file_path_label = QLabel("No file selected")
        self.file_path_label.setStyleSheet("padding: 10px; border: 1px solid #ddd; border-radius: 3px; background-color: white;")
        
        self.browse_button = QPushButton("📎 Browse Files")
        self.browse_button.clicked.connect(self.browse_file)
        
        file_layout.addWidget(self.file_path_label, 3)
        file_layout.addWidget(self.browse_button, 1)
        
        # Privacy notice
        privacy_notice = QLabel("""
        🔒 Privacy Notice: Your ID document is used only for identity verification and is stored securely. 
        We do not share your personal information with third parties.
        """)
        privacy_notice.setWordWrap(True)
        privacy_notice.setStyleSheet("color: #7f8c8d; font-size: 10pt; margin-top: 15px;")
        
        layout.addWidget(instructions)
        layout.addLayout(file_layout)
        layout.addWidget(privacy_notice)
        layout.addStretch()
        
        self.setLayout(layout)
        
        self.selected_file_path = None
    
    def browse_file(self):
        """Open file browser for ID document"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select ID Document",
            "",
            "Image Files (*.png *.jpg *.jpeg);;PDF Files (*.pdf);;All Files (*)"
        )
        
        if file_path:
            # Validate file
            is_valid, message = DataValidator.validate_file_upload(file_path)
            
            if is_valid:
                self.selected_file_path = file_path
                file_name = Path(file_path).name
                self.file_path_label.setText(f"✅ {file_name}")
                self.file_path_label.setStyleSheet("padding: 10px; border: 1px solid #27ae60; border-radius: 3px; background-color: #d5f4e6; color: #27ae60;")
            else:
                QMessageBox.warning(self, "Invalid File", message)
                self.selected_file_path = None
                self.file_path_label.setText("❌ Invalid file")
                self.file_path_label.setStyleSheet("padding: 10px; border: 1px solid #e74c3c; border-radius: 3px; background-color: #fdf2f2; color: #e74c3c;")
        
        self.completeChanged.emit()
    
    def isComplete(self):
        """Check if page is complete"""
        return self.selected_file_path is not None

class PasswordPage(QWizardPage if PYQT_AVAILABLE else object):
    """Step 4: Password Creation"""
    
    def __init__(self):
        if not PYQT_AVAILABLE:
            return
        super().__init__()
        self.setTitle("Create Secure Password")
        self.setSubTitle("Choose a strong password to protect your account")
        
        layout = QVBoxLayout()
        
        # Password requirements
        requirements = QLabel("""
        🔐 Password Requirements:
        • At least 8 characters long
        • Contains uppercase and lowercase letters
        • Contains at least one number
        • Contains at least one special character (!@#$%^&*)
        • Does not contain common words or patterns
        """)
        requirements.setWordWrap(True)
        requirements.setStyleSheet("background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 15px;")
        
        # Password fields
        form_layout = QFormLayout()
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.textChanged.connect(self.validate_passwords)
        
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm your password")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.textChanged.connect(self.validate_passwords)
        
        self.show_password_checkbox = QCheckBox("Show passwords")
        self.show_password_checkbox.toggled.connect(self.toggle_password_visibility)
        
        form_layout.addRow("🔒 Password:", self.password_input)
        form_layout.addRow("🔒 Confirm Password:", self.confirm_password_input)
        form_layout.addRow("", self.show_password_checkbox)
        
        # Password strength indicator
        self.strength_label = QLabel("")
        self.strength_label.setWordWrap(True)
        
        layout.addWidget(requirements)
        layout.addLayout(form_layout)
        layout.addWidget(self.strength_label)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def toggle_password_visibility(self, checked):
        """Toggle password visibility"""
        mode = QLineEdit.Normal if checked else QLineEdit.Password
        self.password_input.setEchoMode(mode)
        self.confirm_password_input.setEchoMode(mode)
    
    def validate_passwords(self):
        """Validate password and show strength"""
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        
        if not password:
            self.strength_label.setText("")
            self.completeChanged.emit()
            return
        
        # Check password strength
        is_valid, message = DataValidator.validate_password(password, confirm_password if confirm_password else None)
        
        if is_valid:
            if confirm_password and password == confirm_password:
                self.strength_label.setText("✅ Strong password - passwords match")
                self.strength_label.setStyleSheet("color: #27ae60; font-weight: bold;")
            else:
                self.strength_label.setText("✅ Strong password")
                self.strength_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        else:
            self.strength_label.setText(f"❌ {message}")
            self.strength_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        
        self.completeChanged.emit()
    
    def isComplete(self):
        """Check if passwords are valid and match"""
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        
        if not password or not confirm_password:
            return False
        
        is_valid, _ = DataValidator.validate_password(password, confirm_password)
        return is_valid

class TermsPage(QWizardPage if PYQT_AVAILABLE else object):
    """Step 5: Terms Agreement & Final Confirmation"""
    
    def __init__(self):
        if not PYQT_AVAILABLE:
            return
        super().__init__()
        self.setTitle("Terms of Service & Privacy Agreement")
        self.setSubTitle("Review and accept the platform terms")
        
        layout = QVBoxLayout()
        
        # Terms text
        terms_text = QTextEdit()
        terms_text.setReadOnly(True)
        terms_text.setMaximumHeight(200)
        terms_text.setHtml("""
        <h3>Civic Engagement Platform Terms of Service</h3>
        
        <p><strong>1. Platform Purpose:</strong> This platform facilitates democratic participation 
        through secure, transparent civic engagement tools.</p>
        
        <p><strong>2. User Responsibilities:</strong> Users agree to participate respectfully, 
        provide accurate information, and follow constitutional governance principles.</p>
        
        <p><strong>3. Privacy Protection:</strong> Personal information is protected using 
        enterprise-grade security. Identity verification is required for platform integrity.</p>
        
        <p><strong>4. Blockchain Recording:</strong> Civic actions are recorded on an immutable 
        blockchain for transparency and audit purposes.</p>
        
        <p><strong>5. Democratic Participation:</strong> All users have equal rights to participate 
        in governance processes according to their role and jurisdiction.</p>
        
        <p><strong>6. Constitutional Compliance:</strong> Platform governance follows constitutional 
        principles with checks and balances to prevent abuse.</p>
        """)
        
        # Agreement checkboxes
        self.terms_checkbox = QCheckBox("✅ I have read and agree to the Terms of Service")
        self.terms_checkbox.toggled.connect(self.validate_agreements)
        
        self.privacy_checkbox = QCheckBox("✅ I agree to the Privacy Policy and data collection practices")
        self.privacy_checkbox.toggled.connect(self.validate_agreements)
        
        self.age_checkbox = QCheckBox("✅ I confirm that I am at least 18 years old and eligible to participate")
        self.age_checkbox.toggled.connect(self.validate_agreements)
        
        # Key generation notice
        key_notice = QLabel("""
        🔑 Cryptographic Key Generation Notice:
        Upon registration completion, a unique RSA key pair will be automatically generated for your account. 
        This enables secure blockchain participation and cryptographic verification of your civic actions.
        Your private key will be stored securely on your device and never transmitted.
        """)
        key_notice.setWordWrap(True)
        key_notice.setStyleSheet("background-color: #e3f2fd; padding: 15px; border-radius: 5px; margin: 10px 0;")
        
        layout.addWidget(terms_text)
        layout.addWidget(self.terms_checkbox)
        layout.addWidget(self.privacy_checkbox) 
        layout.addWidget(self.age_checkbox)
        layout.addWidget(key_notice)
        
        self.setLayout(layout)
    
    def validate_agreements(self):
        """Validate that all agreements are checked"""
        self.completeChanged.emit()
    
    def isComplete(self):
        """Check if all agreements are accepted"""
        return (self.terms_checkbox.isChecked() and 
                self.privacy_checkbox.isChecked() and
                self.age_checkbox.isChecked())

