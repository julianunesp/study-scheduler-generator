"""Google API integration service for Calendar and Drive."""
import os
import json
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
    
    def __init__(self, session=None):
        """Initialize the Google API service.
        
        Args:
            session: Flask session object for storing credentials (serverless-compatible)
        """
        self.credentials = None
        self.session = session
    
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
        
        # Save credentials to session (serverless-compatible)
        if self.session is not None:
            self.session['google_credentials'] = {
                'token': self.credentials.token,
                'refresh_token': self.credentials.refresh_token,
                'token_uri': self.credentials.token_uri,
                'client_id': self.credentials.client_id,
                'client_secret': self.credentials.client_secret,
                'scopes': self.credentials.scopes
            }
        
        return self.credentials
    
    def load_credentials(self):
        """
        Load saved credentials from session (serverless-compatible).
        
        Returns:
            bool: True if credentials loaded successfully
        """
        if self.session is None or 'google_credentials' not in self.session:
            return False
        
        creds_data = self.session['google_credentials']
        
        # Reconstruct credentials from session data
        self.credentials = Credentials(
            token=creds_data.get('token'),
            refresh_token=creds_data.get('refresh_token'),
            token_uri=creds_data.get('token_uri'),
            client_id=creds_data.get('client_id'),
            client_secret=creds_data.get('client_secret'),
            scopes=creds_data.get('scopes')
        )
        
        # Refresh if expired
        if self.credentials.expired and self.credentials.refresh_token:
            try:
                self.credentials.refresh(Request())
                # Update session with refreshed token
                self.session['google_credentials']['token'] = self.credentials.token
            except Exception as e:
                # If refresh fails, credentials are invalid
                return False
        
        return True
    
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


def get_google_service(session=None):
    """
    Get a Google API service instance.
    
    Args:
        session: Flask session object for storing credentials
        
    Returns:
        GoogleAPIService: Service instance with session support
    """
    return GoogleAPIService(session=session)
