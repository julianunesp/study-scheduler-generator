# 📚 Study Schedule Generator

Web application to generate personalized study schedules from Udemy course lists or Excel spreadsheets, exporting calendars in iCalendar (.ics) format.

## 🚀 Features

- ✅ Import courses via Udemy list or Excel spreadsheet
- ✅ Configure study days of the week
- ✅ Set daily study hour limits
- ✅ Time multiplier for duration adjustment
- ✅ Generate .ics file compatible with Google Calendar, Outlook, Apple Calendar, etc.
- ✅ Download sample spreadsheet

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

## 🏃 How to Run

### Local Development

```bash
python run.py
```

The application will be available at: `http://localhost:5001`

### Environment Variables (Optional)

- `FLASK_CONFIG`: Flask configuration (`development`, `production`, `testing`)
- `PORT`: Server port (default: 5001)
- `SECRET_KEY`: Secret key for Flask sessions

## 📖 How to Use

1. Access the application in your browser
2. Choose the input type:
   - **Udemy List**: Paste the course list copied from Udemy
   - **Spreadsheet**: Upload an Excel spreadsheet (download the sample if needed)
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
│   │   ├── parser_service.py     # Data parsing
│   │   └── scheduler_service.py  # Schedule generation
│   ├── static/               # Static files (CSS, JS)
│   ├── templates/            # HTML templates
│   └── utils/                # Utilities
├── data/                     # Data files/samples
│   └── sample_spreadsheet.xlsx
├── deployment/               # Deployment configurations
│   ├── Dockerfile
│   └── kubernetes/
├── requirements.txt          # Python dependencies
├── run.py                    # Application entry point
└── vercel.json              # Vercel configuration

```

## 🐳 Deployment

### Vercel

The project is configured for Vercel deployment:

```bash
vercel deploy
```

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
- **Parsing**: openpyxl (Excel)
- **Calendar**: icalendar, pytz
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)

## 📝 Spreadsheet Format

Download the sample spreadsheet from the application for reference.

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or pull requests.

## 📄 License

This project is under the MIT license.

## 👤 Author

Developed with ❤️ to make study planning easier.
