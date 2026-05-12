"""
Email fetcher module for retrieving Craigslist rental emails from iCloud
"""

import imaplib
import email
from email.header import decode_header
from datetime import datetime
import getpass
from config import EMAIL, IMAP_SERVER, IMAP_PORT, SEARCH_SENDER, MAILBOX


class EmailFetcher:
    def __init__(self, app_password=None):
        """Initialize the email fetcher with optional app password"""
        self.email = EMAIL
        self.imap_server = IMAP_SERVER
        self.imap_port = IMAP_PORT
        self.app_password = app_password
        self.connection = None

    def connect(self):
        """Connect to iCloud email via IMAP"""
        if not self.app_password:
            self.app_password = getpass.getpass(f"Enter app password for {self.email}: ")

        try:
            print(f"Connecting to {self.imap_server}...")
            self.connection = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            self.connection.login(self.email, self.app_password)
            print("✓ Successfully connected to iCloud")
            return True
        except imaplib.IMAP4.error as e:
            print(f"✗ Failed to connect: {e}")
            return False

    def disconnect(self):
        """Disconnect from email server"""
        if self.connection:
            try:
                self.connection.close()
                self.connection.logout()
                print("✓ Disconnected from iCloud")
            except:
                pass

    def fetch_craigslist_emails(self, since_date=None):
        """
        Fetch all Craigslist emails from inbox

        Args:
            since_date: Optional datetime to fetch emails from (default: fetch all)

        Returns:
            List of dictionaries containing email data
        """
        if not self.connection:
            raise ConnectionError("Not connected to email server. Call connect() first.")

        try:
            # Select the mailbox
            self.connection.select(MAILBOX)

            # Build search criteria
            search_criteria = f'(FROM "{SEARCH_SENDER}")'
            if since_date:
                date_str = since_date.strftime("%d-%b-%Y")
                search_criteria = f'(FROM "{SEARCH_SENDER}" SINCE {date_str})'

            # Search for emails using UID
            print(f"Searching for Craigslist emails...")
            status, messages = self.connection.uid('search', None, search_criteria)

            if status != 'OK':
                print("✗ No emails found")
                return []

            email_ids = messages[0].split()
            total_emails = len(email_ids)
            print(f"✓ Found {total_emails} Craigslist emails")

            emails = []
            for idx, email_id in enumerate(email_ids, 1):
                print(f"  Fetching email {idx}/{total_emails}...", end='\r')
                email_data = self._fetch_email_data(email_id)
                if email_data:
                    emails.append(email_data)

            print(f"\n✓ Successfully fetched {len(emails)} emails")
            return emails

        except Exception as e:
            print(f"✗ Error fetching emails: {e}")
            return []

    def _fetch_email_data(self, email_id):
        """Fetch and parse individual email"""
        try:
            # Use UID FETCH with BODY[] for iCloud compatibility
            status, msg_data = self.connection.uid('fetch', email_id, '(BODY.PEEK[])')

            if status != 'OK':
                print(f"\n✗ Fetch status not OK for email {email_id}: {status}")
                return None

            # Check if msg_data is valid
            if not msg_data or not msg_data[0]:
                print(f"\n✗ Invalid msg_data structure for email {email_id}")
                return None

            if len(msg_data[0]) < 2:
                print(f"\n✗ msg_data[0] has insufficient elements: {len(msg_data[0])}")
                print(f"   msg_data[0]: {msg_data[0]}")
                return None

            # Parse email message
            # The response format is typically: [(b'UID XXX BODY[] {size}', b'actual email content')]
            # We need to find the actual bytes content
            email_body = None

            for item in msg_data:
                if isinstance(item, tuple) and len(item) >= 2:
                    # The second element should be the email content
                    if isinstance(item[1], bytes):
                        email_body = item[1]
                        break

            if email_body is None:
                print(f"\n✗ Could not extract email body for {email_id}")
                print(f"   msg_data structure: {msg_data}")
                return None

            email_message = email.message_from_bytes(email_body)

            # Get subject
            subject = self._decode_header(email_message.get('Subject', ''))

            # Get date
            date_str = email_message.get('Date', '')
            received_date = self._parse_date(date_str)

            # Get email body
            body = self._get_email_body(email_message)

            # Handle email_id which could be bytes, int, or str
            if isinstance(email_id, bytes):
                email_id_str = email_id.decode()
            else:
                email_id_str = str(email_id)

            return {
                'id': email_id_str,
                'subject': subject,
                'received_date': received_date,
                'body': body,
                'raw_message': email_message
            }

        except Exception as e:
            print(f"\n✗ Error parsing email {email_id}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _decode_header(self, header):
        """Decode email header"""
        if not header:
            return ''

        decoded_parts = decode_header(header)
        decoded_header = ''

        for content, encoding in decoded_parts:
            if isinstance(content, bytes):
                decoded_header += content.decode(encoding or 'utf-8', errors='ignore')
            else:
                decoded_header += str(content)

        return decoded_header

    def _parse_date(self, date_str):
        """Parse email date string to datetime"""
        if not date_str:
            return datetime.now()

        try:
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_str)
        except:
            return datetime.now()

    def _get_email_body(self, email_message):
        """Extract email body content"""
        body = ""

        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))

                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        payload = part.get_payload(decode=True)
                        if isinstance(payload, bytes):
                            body += payload.decode('utf-8', errors='ignore')
                        elif payload:
                            body += str(payload)
                    except:
                        pass
                elif content_type == "text/html" and not body:
                    try:
                        payload = part.get_payload(decode=True)
                        if isinstance(payload, bytes):
                            body += payload.decode('utf-8', errors='ignore')
                        elif payload:
                            body += str(payload)
                    except:
                        pass
        else:
            try:
                payload = email_message.get_payload(decode=True)
                if isinstance(payload, bytes):
                    body = payload.decode('utf-8', errors='ignore')
                else:
                    body = str(email_message.get_payload())
            except:
                body = str(email_message.get_payload())

        return body


if __name__ == "__main__":
    # Test the email fetcher
    fetcher = EmailFetcher()
    if fetcher.connect():
        emails = fetcher.fetch_craigslist_emails()
        print(f"\nFetched {len(emails)} emails")
        if emails:
            print("\nFirst email:")
            print(f"  Subject: {emails[0]['subject']}")
            print(f"  Date: {emails[0]['received_date']}")
            print(f"  Body preview: {emails[0]['body'][:200]}...")
        fetcher.disconnect()
