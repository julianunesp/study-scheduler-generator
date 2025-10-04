"""Google API integration service for Calendar and Drive."""
import os
import pickle
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload


# OAuth 2.0 scopes
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/drive.file'
]

# OAuth configuration
OAUTH_CONFIG = {
    "web": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "redirect_uris": [os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:5000/oauth2callback")],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token"
    }
}


class GoogleAPIService:
    """Service for interacting with Google Calendar and Drive APIs."""
    
    def __init__(self):
        """Initialize the Google API service."""
        self.credentials = None
        self.token_file = 'token.pickle'
    
    def get_authorization_url(self, state=None):
        """
        Generate the Google OAuth authorization URL.
        
        Args:
            state (str): Optional state parameter for security
            
        Returns:
            str: Authorization URL for user to visit
        """
        flow = Flow.from_client_config(
            OAUTH_CONFIG,
            scopes=SCOPES,
            redirect_uri=OAUTH_CONFIG['web']['redirect_uris'][0]
        )
        
        if state:
            flow.state = state
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        return authorization_url, state
    
    def handle_oauth_callback(self, authorization_response):
        """
        Handle the OAuth callback and exchange code for credentials.
        
        Args:
            authorization_response (str): Full callback URL with code
            
        Returns:
            Credentials: Google OAuth credentials
        """
        flow = Flow.from_client_config(
            OAUTH_CONFIG,
            scopes=SCOPES,
            redirect_uri=OAUTH_CONFIG['web']['redirect_uris'][0]
        )
        
        flow.fetch_token(authorization_response=authorization_response)
        self.credentials = flow.credentials
        
        # Save credentials for future use
        with open(self.token_file, 'wb') as token:
            pickle.dump(self.credentials, token)
        
        return self.credentials
    
    def load_credentials(self):
        """
        Load saved credentials from file.
        
        Returns:
            bool: True if credentials loaded successfully
        """
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                self.credentials = pickle.load(token)
            
            # Refresh if expired
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
                with open(self.token_file, 'wb') as token:
                    pickle.dump(self.credentials, token)
            
            return True
        return False
    
    def import_excel_to_sheets(self, excel_data, filename):
        """
        Import an Excel file as a Google Sheets spreadsheet.
        
        Args:
            excel_data (bytes): Excel file content
            filename (str): Name for the spreadsheet (without extension)
            
        Returns:
            dict: Spreadsheet metadata including ID and webViewLink
        """
        if not self.credentials:
            raise ValueError("Not authenticated. Please authenticate first.")
        
        service = build('drive', 'v3', credentials=self.credentials)
        
        # Remove .xlsx extension if present
        if filename.endswith('.xlsx'):
            filename = filename[:-5]
        
        # File metadata - specify Google Sheets MIME type for conversion
        file_metadata = {
            'name': filename,
            'mimeType': 'application/vnd.google-apps.spreadsheet'  # Convert to Google Sheets
        }
        
        # Upload with Excel MIME type, but convert to Google Sheets
        media = MediaInMemoryUpload(
            excel_data,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            resumable=True
        )
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, webViewLink, mimeType'
        ).execute()
        
        return file
    
    def create_calendar_event(self, calendar_id, event_data):
        """
        Create an event in Google Calendar.
        
        Args:
            calendar_id (str): Calendar ID (use 'primary' for main calendar)
            event_data (dict): Event data with summary, start, end, description
            
        Returns:
            dict: Created event metadata
        """
        if not self.credentials:
            raise ValueError("Not authenticated. Please authenticate first.")
        
        service = build('calendar', 'v3', credentials=self.credentials)
        
        event = service.events().insert(
            calendarId=calendar_id,
            body=event_data
        ).execute()
        
        return event
    
    def import_ical_to_calendar(self, ical_data, calendar_id='primary'):
        """
        Import iCal data to Google Calendar.
        
        Args:
            ical_data (bytes): iCalendar file content
            calendar_id (str): Target calendar ID
            
        Returns:
            list: List of created event IDs
        """
        if not self.credentials:
            raise ValueError("Not authenticated. Please authenticate first.")
        
        from icalendar import Calendar
        
        service = build('calendar', 'v3', credentials=self.credentials)
        cal = Calendar.from_ical(ical_data)
        
        created_events = []
        
        for component in cal.walk():
            if component.name == "VEVENT":
                event = {
                    'summary': str(component.get('summary')),
                    'description': str(component.get('description', '')),
                    'start': {
                        'dateTime': component.get('dtstart').dt.isoformat(),
                        'timeZone': str(component.get('dtstart').dt.tzinfo) if hasattr(component.get('dtstart').dt, 'tzinfo') else 'America/Sao_Paulo',
                    },
                    'end': {
                        'dateTime': component.get('dtend').dt.isoformat(),
                        'timeZone': str(component.get('dtend').dt.tzinfo) if hasattr(component.get('dtend').dt, 'tzinfo') else 'America/Sao_Paulo',
                    },
                }
                
                created_event = service.events().insert(
                    calendarId=calendar_id,
                    body=event
                ).execute()
                
                created_events.append(created_event['id'])
        
        return created_events
    
    def list_calendars(self):
        """
        List all calendars for the authenticated user.
        
        Returns:
            list: List of calendar metadata
        """
        if not self.credentials:
            raise ValueError("Not authenticated. Please authenticate first.")
        
        service = build('calendar', 'v3', credentials=self.credentials)
        
        calendars_result = service.calendarList().list().execute()
        calendars = calendars_result.get('items', [])
        
        return calendars


# Singleton instance
_google_service = None


def get_google_service():
    """Get or create the Google API service singleton."""
    global _google_service
    if _google_service is None:
        _google_service = GoogleAPIService()
    return _google_service
