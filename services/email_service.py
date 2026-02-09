"""
Email Automation Service
Handles automated email sending using SMTP
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import logging

class EmailService:
    def __init__(self):
        """
        Initialize the email service
        """
        # Common SMTP servers and ports
        self.smtp_servers = {
            'gmail.com': {'server': 'smtp.gmail.com', 'port': 587},
            'yahoo.com': {'server': 'smtp.mail.yahoo.com', 'port': 587},
            'outlook.com': {'server': 'smtp-mail.outlook.com', 'port': 587},
            'hotmail.com': {'server': 'smtp-mail.outlook.com', 'port': 587},
            'live.com': {'server': 'smtp-mail.outlook.com', 'port': 587},
        }
        
        print("✅ Email Service initialized successfully")

    def send_email(self, sender_email, sender_password, receiver_email, subject, message, attachments=None):
        """
        Send an email using SMTP
        
        Args:
            sender_email (str): Sender's email address
            sender_password (str): Sender's email password or app password
            receiver_email (str): Receiver's email address
            subject (str): Email subject
            message (str): Email message body
            attachments (list): List of file paths to attach (optional)
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Get SMTP configuration based on sender email
            smtp_config = self._get_smtp_config(sender_email)
            
            # Create message
            msg = self._create_message(sender_email, receiver_email, subject, message, attachments)
            
            # Send email
            success = self._send_via_smtp(smtp_config, sender_email, sender_password, receiver_email, msg)
            
            if success:
                print(f"✅ Email sent successfully from {sender_email} to {receiver_email}")
            else:
                print(f"❌ Failed to send email from {sender_email} to {receiver_email}")
            
            return success
            
        except Exception as e:
            print(f"❌ Email sending error: {e}")
            return False

    def _get_smtp_config(self, email):
        """
        Get SMTP server configuration based on email domain
        """
        try:
            domain = email.split('@')[1].lower()
            
            if domain in self.smtp_servers:
                return self.smtp_servers[domain]
            else:
                # Default to Gmail settings
                print(f"⚠️  Unknown email provider {domain}, using Gmail settings")
                return self.smtp_servers['gmail.com']
                
        except Exception as e:
            print(f"⚠️  Error determining SMTP config: {e}")
            return self.smtp_servers['gmail.com']

    def _create_message(self, sender_email, receiver_email, subject, message, attachments=None):
        """
        Create email message with optional attachments
        """
        try:
            # Create message container
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = receiver_email
            msg['Subject'] = subject
            
            # Add body to email
            msg.attach(MIMEText(message, 'plain'))
            
            # Add attachments if provided
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        self._add_attachment(msg, file_path)
                    else:
                        print(f"⚠️  Attachment not found: {file_path}")
            
            return msg
            
        except Exception as e:
            print(f"❌ Error creating message: {e}")
            raise

    def _add_attachment(self, msg, file_path):
        """
        Add file attachment to email message
        """
        try:
            with open(file_path, "rb") as attachment:
                # Create MIMEBase object
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            # Encode file in ASCII characters to send by email
            encoders.encode_base64(part)
            
            # Add header with filename
            filename = os.path.basename(file_path)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {filename}',
            )
            
            # Attach the part to message
            msg.attach(part)
            
        except Exception as e:
            print(f"⚠️  Error adding attachment {file_path}: {e}")

    def _send_via_smtp(self, smtp_config, sender_email, sender_password, receiver_email, msg):
        """
        Send email via SMTP server
        """
        try:
            # Create SMTP session
            server = smtplib.SMTP(smtp_config['server'], smtp_config['port'])
            
            # Enable security
            server.starttls()
            
            # Login with sender's email and password
            server.login(sender_email, sender_password)
            
            # Convert message to string
            text = msg.as_string()
            
            # Send email
            server.sendmail(sender_email, receiver_email, text)
            
            # Terminate the SMTP session
            server.quit()
            
            return True
            
        except smtplib.SMTPAuthenticationError:
            print("❌ Authentication failed. Please check your email and password.")
            print("💡 For Gmail, you may need to use an App Password instead of your regular password.")
            return False
        except smtplib.SMTPRecipientsRefused:
            print("❌ Recipient email address was refused by the server.")
            return False
        except smtplib.SMTPServerDisconnected:
            print("❌ Server unexpectedly disconnected.")
            return False
        except Exception as e:
            print(f"❌ SMTP error: {e}")
            return False

    def generate_professional_email(self, email_type, context_data):
        """
        Generate professional email templates
        
        Args:
            email_type (str): Type of email (meeting, follow_up, introduction, etc.)
            context_data (dict): Context data for email generation
            
        Returns:
            dict: Generated email with subject and body
        """
        try:
            templates = {
                'meeting_request': {
                    'subject': f"Meeting Request: {context_data.get('topic', 'Discussion')}",
                    'body': f"""Dear {context_data.get('recipient_name', 'Sir/Madam')},

I hope this email finds you well. I would like to schedule a meeting to discuss {context_data.get('topic', 'important matters')}.

Proposed Details:
- Date: {context_data.get('date', 'To be determined')}
- Time: {context_data.get('time', 'To be determined')}
- Duration: {context_data.get('duration', '1 hour')}
- Location/Platform: {context_data.get('location', 'To be determined')}

Please let me know if this works for your schedule, or suggest alternative times that would be more convenient.

Thank you for your time and consideration.

Best regards,
{context_data.get('sender_name', 'Your Name')}"""
                },
                'follow_up': {
                    'subject': f"Follow-up: {context_data.get('topic', 'Our Previous Discussion')}",
                    'body': f"""Dear {context_data.get('recipient_name', 'Sir/Madam')},

I hope you are doing well. I wanted to follow up on our previous discussion regarding {context_data.get('topic', 'the matter we discussed')}.

{context_data.get('follow_up_message', 'I wanted to check if you had any updates or if there are any next steps we should take.')}

Please let me know if you need any additional information from my side.

Looking forward to your response.

Best regards,
{context_data.get('sender_name', 'Your Name')}"""
                },
                'introduction': {
                    'subject': f"Introduction: {context_data.get('sender_name', 'Nice to Meet You')}",
                    'body': f"""Dear {context_data.get('recipient_name', 'Sir/Madam')},

I hope this email finds you well. My name is {context_data.get('sender_name', 'Your Name')}, and I am {context_data.get('sender_title', 'reaching out to introduce myself')}.

{context_data.get('introduction_message', 'I would like to connect with you and explore potential opportunities for collaboration.')}

I would be happy to schedule a brief call or meeting at your convenience to discuss this further.

Thank you for your time, and I look forward to hearing from you.

Best regards,
{context_data.get('sender_name', 'Your Name')}
{context_data.get('sender_contact', '')}"""
                },
                'thank_you': {
                    'subject': f"Thank You - {context_data.get('topic', 'Your Assistance')}",
                    'body': f"""Dear {context_data.get('recipient_name', 'Sir/Madam')},

I wanted to take a moment to express my sincere gratitude for {context_data.get('reason', 'your assistance and support')}.

{context_data.get('thank_you_message', 'Your help has been invaluable and greatly appreciated.')}

Please don't hesitate to reach out if there's anything I can do to return the favor.

Thank you once again.

Warm regards,
{context_data.get('sender_name', 'Your Name')}"""
                }
            }
            
            if email_type in templates:
                return templates[email_type]
            else:
                # Generic template
                return {
                    'subject': context_data.get('subject', 'Professional Correspondence'),
                    'body': f"""Dear {context_data.get('recipient_name', 'Sir/Madam')},

{context_data.get('message', 'I hope this email finds you well.')}

Thank you for your time and consideration.

Best regards,
{context_data.get('sender_name', 'Your Name')}"""
                }
                
        except Exception as e:
            print(f"❌ Error generating email template: {e}")
            return {
                'subject': 'Professional Email',
                'body': f"Dear Sir/Madam,\n\n{context_data.get('message', 'Thank you for your time.')}\n\nBest regards,\n{context_data.get('sender_name', 'Your Name')}"
            }

    def validate_email_address(self, email):
        """
        Basic email validation
        
        Args:
            email (str): Email address to validate
            
        Returns:
            bool: True if email format is valid
        """
        try:
            import re
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return bool(re.match(pattern, email))
        except Exception:
            return False

    def get_email_tips(self):
        """
        Get tips for successful email sending
        """
        return {
            'gmail_users': [
                "Use App Passwords instead of your regular password",
                "Enable 2-factor authentication and generate an app password",
                "Go to Google Account Settings > Security > App passwords"
            ],
            'general_tips': [
                "Make sure 'Less secure app access' is enabled (if applicable)",
                "Check that your email client allows SMTP access",
                "Verify recipient email address is correct",
                "Check spam folders if emails don't arrive",
                "Use professional email addresses for business communication"
            ]
        }