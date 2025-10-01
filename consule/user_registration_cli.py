#!/usr/bin/env python3
"""
USER REGISTRATION CLI
Interactive command-line interface for user registration and management
"""

import sys
import json
from typing import List, Dict, Any
from user_manager import UserManager, PhoneType, AddressType

class UserRegistrationCLI:
    """Interactive CLI for user registration"""
    
    def __init__(self):
        self.user_manager = UserManager()
    
    def display_welcome(self):
        """Display welcome message"""
        print("=" * 60)
        print("🔗 BLOCKCHAIN PLATFORM - USER REGISTRATION")
        print("=" * 60)
        print("Welcome! Let's create your account.")
        print("You'll need to provide:")
        print("✓ Legal name and date of birth")
        print("✓ At least one email address")
        print("✓ At least one phone number (required)")
        print("✓ At least one residence address (required)")
        print("✓ Optional: countries of citizenship")
        print("✓ Cryptographic keys will be generated automatically")
        print("-" * 60)
    
    def get_input(self, prompt: str, required: bool = True, validate_func=None) -> str:
        """Get user input with validation"""
        while True:
            value = input(f"{prompt}: ").strip()
            
            if not value and required:
                print("❌ This field is required. Please try again.")
                continue
            
            if not value and not required:
                return ""
            
            if validate_func and not validate_func(value):
                print("❌ Invalid format. Please try again.")
                continue
            
            return value
    
    def get_yes_no(self, prompt: str, default: bool = False) -> bool:
        """Get yes/no input"""
        default_text = "Y/n" if default else "y/N"
        while True:
            response = input(f"{prompt} ({default_text}): ").strip().lower()
            if not response:
                return default
            if response in ['y', 'yes']:
                return True
            if response in ['n', 'no']:
                return False
            print("❌ Please enter 'y' for yes or 'n' for no.")
    
    def collect_basic_info(self) -> Dict[str, str]:
        """Collect basic user information"""
        print("\n📝 BASIC INFORMATION")
        print("-" * 30)
        
        info = {}
        info['username'] = self.get_input("Username (3-30 characters, letters/numbers/underscore only)")
        info['password'] = self.get_input("Password")
        
        print("\n👤 LEGAL NAME (as it appears on official documents)")
        info['legal_first_name'] = self.get_input("Legal First Name")
        info['legal_middle_name'] = self.get_input("Legal Middle Name (optional)", required=False)
        info['legal_last_name'] = self.get_input("Legal Last Name")
        
        print("\n📅 DATE OF BIRTH")
        info['date_of_birth'] = self.get_input("Date of Birth (YYYY-MM-DD format)")
        
        return info
    
    def collect_email_addresses(self) -> List[Dict]:
        """Collect email addresses"""
        print("\n📧 EMAIL ADDRESSES")
        print("-" * 30)
        print("You must provide at least one email address.")
        
        emails = []
        while True:
            email = self.get_input(f"Email Address #{len(emails) + 1}")
            is_primary = len(emails) == 0 or self.get_yes_no("Make this your primary email", default=len(emails) == 0)
            
            emails.append({
                "email": email,
                "is_primary": is_primary
            })
            
            if not self.get_yes_no("Add another email address", default=False):
                break
        
        return emails
    
    def collect_phone_numbers(self) -> List[Dict]:
        """Collect phone numbers - AT LEAST ONE REQUIRED"""
        print("\n📱 PHONE NUMBERS (Required)")
        print("-" * 30)
        print("You must provide at least one phone number.")
        
        phones = []
        phone_types = [e.value for e in PhoneType]
        
        while True:
            print(f"\nPhone number #{len(phones) + 1}")
            number = self.get_input("Phone Number")
            
            print(f"\nAvailable types:")
            for i, ptype in enumerate(phone_types, 1):
                print(f"  {i}. {ptype}")
            
            while True:
                try:
                    type_choice = int(self.get_input("Select phone type (1-5)"))
                    if 1 <= type_choice <= len(phone_types):
                        phone_type = phone_types[type_choice - 1]
                        break
                    else:
                        print("❌ Please select a number between 1-5")
                except ValueError:
                    print("❌ Please enter a valid number")
            
            country_code = self.get_input("Country Code (e.g., +1)", required=False)
            if not country_code:
                country_code = "+1"
            
            is_primary = len(phones) == 0 or self.get_yes_no("Make this your primary phone", default=len(phones) == 0)
            
            phones.append({
                "number": number,
                "type": phone_type,
                "country_code": country_code,
                "is_primary": is_primary
            })
            
            if len(phones) > 0 and not self.get_yes_no("Add another phone number", default=False):
                break
        
        return phones
    
    def collect_addresses(self) -> List[Dict]:
        """Collect addresses - RESIDENCE ADDRESS REQUIRED"""
        print("\n🏠 ADDRESSES (Required)")
        print("-" * 30)
        print("You must provide at least one residence address.")
        
        addresses = []
        address_types = [e.value for e in AddressType]
        has_residence = False
        
        while True:
            print(f"\nAddress #{len(addresses) + 1}")
            
            print(f"\nAvailable types:")
            for i, atype in enumerate(address_types, 1):
                print(f"  {i}. {atype}")
            
            while True:
                try:
                    type_choice = int(self.get_input("Select address type (1-4)"))
                    if 1 <= type_choice <= len(address_types):
                        addr_type = address_types[type_choice - 1]
                        break
                    else:
                        print("❌ Please select a number between 1-4")
                except ValueError:
                    print("❌ Please enter a valid number")
            
            if addr_type == "residence":
                has_residence = True
            
            street_address = self.get_input("Street Address")
            street_address_2 = self.get_input("Street Address 2 (optional)", required=False)
            city = self.get_input("City")
            state_province = self.get_input("State/Province")
            postal_code = self.get_input("Postal Code")
            country = self.get_input("Country")
            
            is_primary = len(addresses) == 0 or self.get_yes_no("Make this your primary address", default=len(addresses) == 0)
            
            addresses.append({
                "type": addr_type,
                "street_address": street_address,
                "street_address_2": street_address_2,
                "city": city,
                "state_province": state_province,
                "postal_code": postal_code,
                "country": country,
                "is_primary": is_primary
            })
            
            # Check if we can continue
            if has_residence and not self.get_yes_no("Add another address", default=False):
                break
            elif not has_residence:
                if len(addresses) > 0:
                    print("⚠️ You must provide at least one residence address to continue.")
                continue
        
        return addresses
    
    def collect_citizenship(self) -> List[str]:
        """Collect countries of citizenship"""
        print("\n🌍 COUNTRIES OF CITIZENSHIP (Optional)")
        print("-" * 30)
        
        if not self.get_yes_no("Would you like to specify countries of citizenship", default=True):
            return []
        
        countries = []
        while True:
            country = self.get_input(f"Country #{len(countries) + 1}")
            countries.append(country)
            
            if not self.get_yes_no("Add another country", default=False):
                break
        
        return countries
    
    def display_summary(self, registration_data: Dict) -> bool:
        """Display registration summary and confirm"""
        print("\n" + "=" * 60)
        print("📋 REGISTRATION SUMMARY")
        print("=" * 60)
        
        print(f"👤 Username: {registration_data['username']}")
        print(f"👤 Legal Name: {registration_data['legal_first_name']} {registration_data.get('legal_middle_name', '')} {registration_data['legal_last_name']}")
        print(f"📅 Date of Birth: {registration_data['date_of_birth']}")
        
        print(f"\n📧 Email Addresses ({len(registration_data['email_addresses'])}):")
        for i, email in enumerate(registration_data['email_addresses']):
            primary = " (PRIMARY)" if email['is_primary'] else ""
            print(f"   {i+1}. {email['email']}{primary}")
        
        if registration_data.get('phone_numbers'):
            print(f"\n📱 Phone Numbers ({len(registration_data['phone_numbers'])}):")
            for i, phone in enumerate(registration_data['phone_numbers']):
                primary = " (PRIMARY)" if phone['is_primary'] else ""
                print(f"   {i+1}. {phone['country_code']} {phone['number']} ({phone['type']}){primary}")
        
        if registration_data.get('addresses'):
            print(f"\n🏠 Addresses ({len(registration_data['addresses'])}):")
            for i, addr in enumerate(registration_data['addresses']):
                primary = " (PRIMARY)" if addr['is_primary'] else ""
                print(f"   {i+1}. {addr['street_address']}, {addr['city']}, {addr['state_province']} {addr['postal_code']}, {addr['country']} ({addr['type']}){primary}")
        
        if registration_data.get('countries_of_citizenship'):
            print(f"\n🌍 Countries of Citizenship: {', '.join(registration_data['countries_of_citizenship'])}")
        
        print(f"\n🔑 Cryptographic Keys: Will be generated automatically")
        print(f"📊 Blockchain Storage: All data will be stored on blockchain")
        
        print("-" * 60)
        return self.get_yes_no("Is this information correct? Proceed with registration", default=True)
    
    def register_user(self):
        """Main registration flow"""
        self.display_welcome()
        
        try:
            # Collect all information
            registration_data = self.collect_basic_info()
            registration_data['email_addresses'] = self.collect_email_addresses()
            registration_data['phone_numbers'] = self.collect_phone_numbers()
            registration_data['addresses'] = self.collect_addresses()
            registration_data['countries_of_citizenship'] = self.collect_citizenship()
            
            # Show summary and confirm
            if not self.display_summary(registration_data):
                print("\n❌ Registration cancelled.")
                return
            
            # Attempt registration
            print("\n🔄 Processing registration...")
            result = self.user_manager.register_user(registration_data)
            
            if result['success']:
                print("\n🎉 REGISTRATION SUCCESSFUL!")
                print("=" * 40)
                print(f"✓ User ID: {result['user_id']}")
                print("✓ Account created successfully")
                
                if result.get('verification_required'):
                    print("\n📧 NEXT STEPS:")
                    print("• Check your email for verification links")
                    print("• Verify your email addresses to activate full account features")
                    print("• You can log in immediately but some features require verification")
                
                print("\nWelcome to the blockchain platform! 🚀")
            else:
                print("\n❌ REGISTRATION FAILED!")
                print("=" * 40)
                for error in result.get('errors', []):
                    print(f"• {error}")
                print("\nPlease correct the errors and try again.")
                
        except KeyboardInterrupt:
            print("\n\n❌ Registration cancelled by user.")
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
    
    def login_user(self):
        """User login flow"""
        print("\n" + "=" * 40)
        print("🔐 USER LOGIN")
        print("=" * 40)
        
        try:
            username = self.get_input("Username")
            password = self.get_input("Password")
            
            print("\n🔄 Authenticating...")
            user = self.user_manager.authenticate_user(username, password)
            
            if user:
                print("\n✅ LOGIN SUCCESSFUL!")
                print("=" * 30)
                print(f"Welcome back, {user.legal_first_name}!")
                print(f"Account: {user.username}")
                print(f"Status: {'Verified' if user.is_verified else 'Unverified'}")
                print(f"Last login: {user.last_login}")
                
                return user
            else:
                print("\n❌ LOGIN FAILED!")
                print("Invalid username or password.")
                return None
                
        except KeyboardInterrupt:
            print("\n\n❌ Login cancelled by user.")
            return None
    
    def list_users(self):
        """List all users (admin function)"""
        print("\n" + "=" * 60)
        print("👥 ALL REGISTERED USERS")
        print("=" * 60)
        
        users = self.user_manager.list_all_users()
        
        if not users:
            print("No users registered yet.")
            return
        
        for i, user in enumerate(users, 1):
            status = "✅ Active" if user['is_active'] else "❌ Inactive"
            verified = "🔒 Verified" if user['is_verified'] else "🔓 Unverified"
            
            print(f"\n{i}. {user['username']} - {user['full_name']}")
            print(f"   📧 {user['primary_email'] or 'No email'}")
            print(f"   📅 Registered: {user['created_at'][:10]}")
            print(f"   🔄 Last login: {user['last_login'][:10] if user['last_login'] else 'Never'}")
            print(f"   📊 Status: {status}, {verified}")
    
    def main_menu(self):
        """Main menu interface"""
        while True:
            print("\n" + "=" * 50)
            print("🔗 BLOCKCHAIN PLATFORM - USER MANAGEMENT")
            print("=" * 50)
            print("1. 📝 Register New User")
            print("2. 🔐 Login")
            print("3. 👥 List All Users")
            print("4. 🚪 Exit")
            print("-" * 50)
            
            choice = input("Select an option (1-4): ").strip()
            
            if choice == '1':
                self.register_user()
            elif choice == '2':
                self.login_user()
            elif choice == '3':
                self.list_users()
            elif choice == '4':
                print("\n👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please select 1-4.")

if __name__ == "__main__":
    cli = UserRegistrationCLI()
    cli.main_menu()