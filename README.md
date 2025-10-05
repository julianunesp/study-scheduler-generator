# 📚 Study Schedule Generator

Web application to generate personalized study schedules from Udemy course lists or Excel spreadsheets, exporting calendars in iCalendar (.ics) format.

## 🚀 Features

- ✅ Import courses via Udemy list, Excel spreadsheet, or HTML file
- 🤖 **AI-Powered HTML Parsing:** Automatic course extraction using LangChain + Google Gemini
- 🌍 **Multilingual Support:** Handles content in English, Portuguese, and Spanish
- ✅ Configure study days of the week
- ✅ Set daily study hour limits
- ✅ Time multiplier for duration adjustment
- ✅ Generate .ics file compatible with Google Calendar, Outlook, Apple Calendar, etc.
- ✅ Download sample spreadsheet and HTML files

## 📋 Prerequisites

- Python 3.8+
- pip (Python package manager)

## 🔧 Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <directory-name>
```

2. Create and activate a virtual environment:
```bash
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. (Optional) Configure AI-powered HTML parsing:
```bash
# Copy the example environment file
cp env.example .env

# Edit .env and add your Google Gemini API key
# Get your API key from: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=your_actual_api_key_here
```

## 🏃 How to Run

### Local Development

```bash
python run.py
```

The application will be available at: `http://localhost:5001`

### Environment Variables

**Required for AI HTML Parsing:**
- `GOOGLE_API_KEY`: Google Gemini API key for AI-powered HTML parsing

**Optional:**
- `FLASK_CONFIG`: Flask configuration (`development`, `production`, `testing`)
- `PORT`: Server port (default: 5001)
- `SECRET_KEY`: Secret key for Flask sessions

## 📖 How to Use

1. Access the application in your browser
2. Choose the input type:
   - **Udemy List**: Paste the course list copied from Udemy
   - **Spreadsheet**: Upload an Excel spreadsheet (download the sample if needed)
   - **HTML Course Content (AI-Powered)**: Upload HTML file with course structure
     - Right-click on course page → "View Page Source"
     - Save as .html file and upload
     - AI agent automatically extracts modules, classes, and durations
     - Works with Udemy, Hotmart, Eduzz, Coursera, EdX, and other platforms
3. Configure the parameters:
   - Start date
   - Study days of the week
   - Class start time
   - Daily hour limit
   - Time multiplier (fine-tune duration)
4. Click "Generate Schedule"
5. Download the generated `.ics` file
6. Import into your favorite calendar application

## 📁 Project Structure

```
.
├── app/
│   ├── __init__.py           # Flask application factory
│   ├── config.py             # Application settings
│   ├── routes.py             # Routes and endpoints
│   ├── services/             # Business logic
│   │   ├── parser_service.py       # Data parsing
│   │   ├── scheduler_service.py    # Schedule generation
│   │   └── html_parser_agent.py    # AI-powered HTML parsing
│   ├── static/               # Static files (CSS, JS)
│   └── templates/            # HTML templates
├── data/                     # Data files/samples
│   ├── sample_spreadsheet.xlsx
│   └── sample_course.html    # Sample HTML for testing
├── deployment/               # Deployment configurations
│   ├── Dockerfile
│   └── kubernetes/
├── requirements.txt          # Python dependencies
├── run.py                    # Application entry point
└── vercel.json              # Vercel configuration

```

## 🤖 AI-Powered HTML Parsing

The application includes an intelligent agent built with **LangChain** and **Google Gemini** that can automatically extract course content from HTML files.

### How It Works

1. **Upload HTML**: User uploads the HTML source of a course page
2. **AI Analysis**: The LangChain agent analyzes the HTML structure
3. **Pattern Detection**: Identifies modules, classes, and durations automatically
4. **Structured Output**: Returns parsed data using Pydantic models
5. **Integration**: Seamlessly feeds into the existing scheduling pipeline

### Supported Platforms

The AI agent is designed to work with various course platforms:
- ✅ **Full Cycle / React Apps** (MUI-based platforms)
- ✅ **Udemy** (standard course structure)
- ✅ **Hotmart** (Brazilian platform)
- ✅ **Eduzz** (Brazilian platform)
- ✅ **Coursera** (MOOC platform)
- ✅ **EdX** (MOOC platform)
- ✅ **Custom platforms** with similar HTML structures

### Technical Details

- **Framework**: LangChain with Google Gemini (gemini-2.0-flash-exp)
- **Output Parsing**: Pydantic models for structured data
- **Prompt Engineering**: English-optimized system prompt covering multiple platform patterns
- **Multilingual Support**: Automatically handles content in English, Portuguese, and Spanish
- **Error Handling**: Graceful fallback if content cannot be extracted

### Example Prompt Structure

The agent uses a detailed English prompt that:
- Identifies common HTML patterns for course content
- Handles multiple duration formats (MM:SS, HH:MM:SS, HHH:MM)
- Extracts module/chapter organization
- Maintains original class ordering
- Never invents or omits classes
- Preserves original language of course content (EN/PT/ES)

## 🐳 Deployment

### Vercel

The project is configured for Vercel deployment with serverless-compatible OAuth:

```bash
vercel deploy
```

**Important Environment Variables for Vercel:**

1. **SECRET_KEY** (Required for OAuth sessions):
   ```bash
   # Generate a secure secret key
   python -c "import secrets; print(secrets.token_hex(32))"
   
   # Add to Vercel environment variables
   vercel env add SECRET_KEY
   ```

2. **GOOGLE_CLIENT_ID** (For Google Calendar/Drive integration):
   ```bash
   vercel env add GOOGLE_CLIENT_ID
   ```

3. **GOOGLE_CLIENT_SECRET** (For Google Calendar/Drive integration):
   ```bash
   vercel env add GOOGLE_CLIENT_SECRET
   ```

4. **GOOGLE_REDIRECT_URI** (OAuth callback URL):
   ```bash
   # Set to: https://your-domain.vercel.app/oauth2callback
   vercel env add GOOGLE_REDIRECT_URI
   ```

5. **GOOGLE_API_KEY** (For AI HTML parsing):
   ```bash
   vercel env add GOOGLE_API_KEY
   ```

**Note:** The application now uses cookie-based sessions instead of file-based storage, making it fully compatible with Vercel's read-only filesystem

### Docker

```bash
docker build -t study-schedule-generator .
docker run -p 5001:5001 study-schedule-generator
```

### Kubernetes

```bash
kubectl apply -f deployment/kubernetes/
```

## 🛠️ Technologies

- **Backend**: Flask 3.x
- **AI/ML**: LangChain, Google Gemini (gemini-2.0-flash-exp)
- **Parsing**: openpyxl (Excel), BeautifulSoup (HTML cleaning)
- **Calendar**: icalendar, pytz
- **Data Validation**: Pydantic
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)

## 📝 Spreadsheet Format

Download the sample spreadsheet from the application for reference.

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or pull requests.

## 📄 License

This project is under the MIT license.

## 👤 Author

Developed with ❤️ to make study planning easier.
