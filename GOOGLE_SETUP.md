# Google Integration Setup Guide

This guide will help you set up Google Calendar and Google Drive integration for the Study Schedule Generator.

## Quick Checklist

Before you start, make sure you have:
- ✅ A Google account
- ✅ Access to [Google Cloud Console](https://console.cloud.google.com/)
- ✅ 10-15 minutes to complete the setup

## What You'll Enable

By the end of this guide, users will be able to:
- 📊 **Create Google Sheets** - Convert extracted class lists into editable spreadsheets
- 📅 **Import to Google Calendar** - Automatically create study schedule events
- ☁️ **Cloud Storage** - Keep everything synchronized across devices

## Prerequisites

- A Google account
- Access to Google Cloud Console
- Basic understanding of OAuth (we'll guide you through it)

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top
3. Click "New Project"
4. Enter a project name (e.g., "Study Schedule Generator")
5. Click "Create"

## Step 2: Enable Required APIs

1. In the Google Cloud Console, go to **APIs & Services** > **Library**
2. Search for and enable the following APIs:
   - **Google Calendar API** - Required for importing study schedules to Google Calendar
   - **Google Drive API** - Required for creating Google Sheets spreadsheets
   - **Google Sheets API** (Optional but recommended) - For better Sheets integration

**Important:** Make sure all three APIs are enabled before proceeding to the next step.

## Step 3: Create OAuth 2.0 Credentials

1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth client ID**
3. If prompted, configure the OAuth consent screen:
   - Choose **External** user type (or **Internal** if you have a Google Workspace account)
   - Fill in the required fields:
     - App name: "Study Schedule Generator"
     - User support email: your email
     - Developer contact: your email
   - Click **Save and Continue**
   
   - **On the Scopes page:**
     - Click **Add or Remove Scopes**
     - Add the following scopes:
       - `https://www.googleapis.com/auth/calendar` (Google Calendar API)
       - `https://www.googleapis.com/auth/drive.file` (Google Drive API - Create files)
     - Click **Update** then **Save and Continue**
   
   - **On the Test users page:**
     - Click **Add Users**
     - Add your email and any other test users
     - Click **Save and Continue**
   
   - Review and click **Back to Dashboard**

4. Create OAuth Client ID:
   - Application type: **Web application**
   - Name: "Study Schedule Generator Web Client"
   - Authorized redirect URIs:
     - `http://localhost:5000/oauth2callback`
     - (Add your production URL when deploying)
   - Click **Create**

5. **Save your credentials:**
   - Copy the **Client ID**
   - Copy the **Client Secret**

## Step 4: Configure Environment Variables

1. Copy `env.example` to `.env`:
   ```bash
   cp env.example .env
   ```

2. Edit `.env` and add your credentials:
   ```
   GOOGLE_API_KEY=your_gemini_api_key
   GOOGLE_CLIENT_ID=your_client_id_here
   GOOGLE_CLIENT_SECRET=your_client_secret_here
   GOOGLE_REDIRECT_URI=http://localhost:5000/oauth2callback
   ```

## Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 6: Run the Application

```bash
python run.py
```

## Features Enabled

Once configured, users will be able to:

### 📊 Google Sheets Integration
- **Create Google Sheets**: Automatically converts the extracted class list into an editable Google Sheets spreadsheet
- **Direct editing**: Users can track their progress directly in Google Sheets
- **Automatic formatting**: Spreadsheet comes with headers, colors, and proper column widths

### 📅 Google Calendar Integration
- **Direct import**: Import study schedule directly to Google Calendar
- **Calendar selection**: Choose which calendar to import to (primary or secondary)
- **Automatic event creation**: All study blocks are created as calendar events with:
  - Course name in title
  - List of classes in description
  - Proper date, time, and duration
  - Checkboxes for tracking progress

## OAuth Flow

1. User clicks "Create Google Sheets" or "Import to Google Calendar"
2. If not authenticated, a popup window opens with Google login
3. User grants permissions to the app
4. Popup closes automatically after successful authentication
5. App proceeds with the requested action

## Scopes Required

The application requests the following OAuth scopes:

### 📅 Google Calendar API
- **Scope:** `https://www.googleapis.com/auth/calendar`
- **Purpose:** Create and manage calendar events
- **What it allows:**
  - Import study schedule events to user's calendar
  - List available calendars
  - Create events with title, description, date, and time

### 📊 Google Drive API
- **Scope:** `https://www.googleapis.com/auth/drive.file`
- **Purpose:** Create and manage files created by this app
- **What it allows:**
  - Convert Excel files to Google Sheets
  - Create new spreadsheets in user's Drive
  - **Note:** This scope only allows access to files created by the app, not all Drive files

### 🔒 Security Notes
- The app **cannot** read or modify existing files in your Drive
- The app **cannot** delete calendars or events not created by it
- All data stays in your Google account
- You can revoke access anytime at [Google Account Permissions](https://myaccount.google.com/permissions)

## API Quotas and Limits

### Free Tier Limits
Google provides generous free quotas for these APIs:

**Google Calendar API:**
- 1,000,000 queries per day
- Sufficient for thousands of users

**Google Drive API:**
- 20,000 queries per 100 seconds per user
- 1,000 queries per 100 seconds per project
- More than enough for typical usage

### What This Means for You
- **Personal use:** You'll never hit these limits
- **Small team (< 100 users):** No issues
- **Production app:** Monitor usage in Google Cloud Console
- **If you hit limits:** Request quota increase (usually approved quickly)

### Monitoring Usage
1. Go to Google Cloud Console
2. Navigate to **APIs & Services** > **Dashboard**
3. View usage statistics for each API
4. Set up alerts if approaching limits

## Additional Security Best Practices

- **Never commit** your `.env` file to version control
- The `token.pickle` file stores user credentials locally - add it to `.gitignore`
- For production, use HTTPS and update redirect URIs accordingly
- Rotate credentials periodically
- Use environment-specific credentials (dev, staging, production)

## Troubleshooting

### "Access blocked: This app's request is invalid"
- Make sure you've added your email as a test user in the OAuth consent screen
- Verify that the redirect URI matches exactly (including http/https)

### "The OAuth client was not found"
- Double-check your Client ID and Client Secret in `.env`
- Make sure there are no extra spaces or quotes

### "Insufficient permissions" or "Access Not Configured"
- Verify that all required APIs are enabled:
  - Google Calendar API
  - Google Drive API
  - Google Sheets API (optional but recommended)
- Check that the OAuth consent screen has the correct scopes:
  - `https://www.googleapis.com/auth/calendar`
  - `https://www.googleapis.com/auth/drive.file`
- Wait a few minutes after enabling APIs for changes to propagate

### Authentication popup doesn't close
- Check browser console for errors
- Make sure the redirect URI is correctly configured
- Verify that the Flask app is running on the correct port

## Production Deployment

When deploying to production:

1. Update the redirect URI in Google Cloud Console:
   - Add your production URL (e.g., `https://yourdomain.com/oauth2callback`)

2. Update `.env` with production URL:
   ```
   GOOGLE_REDIRECT_URI=https://yourdomain.com/oauth2callback
   ```

3. Publish your OAuth consent screen:
   - Go to OAuth consent screen settings
   - Click "Publish App"
   - Submit for verification if needed

4. Use environment variables in your hosting platform:
   - Set `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and `GOOGLE_REDIRECT_URI`
   - Never hardcode credentials in your code

## Useful Links

### Official Documentation
- 📖 [Google Calendar API Documentation](https://developers.google.com/calendar/api/guides/overview)
- 📖 [Google Drive API Documentation](https://developers.google.com/drive/api/guides/about-sdk)
- 📖 [Google Sheets API Documentation](https://developers.google.com/sheets/api/guides/concepts)
- 🔐 [OAuth 2.0 for Web Server Applications](https://developers.google.com/identity/protocols/oauth2/web-server)

### Google Cloud Console
- 🌐 [Google Cloud Console](https://console.cloud.google.com/)
- 🔑 [API Credentials](https://console.cloud.google.com/apis/credentials)
- 📊 [API Dashboard](https://console.cloud.google.com/apis/dashboard)
- 👥 [OAuth Consent Screen](https://console.cloud.google.com/apis/credentials/consent)

### Account Management
- 🔒 [Google Account Permissions](https://myaccount.google.com/permissions) - Manage app access
- 📧 [Google Account Security](https://myaccount.google.com/security) - Security settings
- 🔐 [App Passwords](https://myaccount.google.com/apppasswords) - If using 2FA

### Testing & Debugging
- 🧪 [OAuth 2.0 Playground](https://developers.google.com/oauthplayground/) - Test OAuth flow
- 🔍 [API Explorer](https://developers.google.com/apis-explorer) - Test API calls
- 📝 [Google API Python Client](https://github.com/googleapis/google-api-python-client) - Library docs

## Support

For issues related to:
- **Google Cloud Console**: [Google Cloud Support](https://cloud.google.com/support)
- **OAuth Setup**: [Google OAuth Documentation](https://developers.google.com/identity/protocols/oauth2)
- **API Issues**: [Google Calendar API](https://developers.google.com/calendar) | [Google Drive API](https://developers.google.com/drive)
- **This Application**: Open an issue on GitHub or contact the maintainer

## Summary

You've successfully configured:
- ✅ Google Cloud Project
- ✅ Google Calendar API
- ✅ Google Drive API  
- ✅ OAuth 2.0 Credentials
- ✅ Environment Variables

Your users can now:
- 📊 Create Google Sheets from course data
- 📅 Import study schedules to Google Calendar
- ☁️ Access everything from any device

**Next Steps:**
1. Test the OAuth flow with your account
2. Verify that Sheets and Calendar imports work
3. Add more test users if needed
4. Deploy to production when ready

Happy coding! 🚀
