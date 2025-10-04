"""Routes for Study Schedule Generator."""
import os
import io
from datetime import datetime
from flask import Blueprint, request, send_file, render_template

from .services import (
    parse_udemy_list,
    parse_spreadsheet,
    apply_multiplier,
    schedule_classes,
    create_calendar_events
)

main_bp = Blueprint('main', __name__)


@main_bp.route('/', methods=['GET'])
def index():
    """Render the main form page."""
    return render_template('index.html')


@main_bp.route('/download-sample')
def download_sample():
    """Serve the sample spreadsheet for download."""
    sample_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'sample_spreadsheet.xlsx')
    if os.path.exists(sample_path):
        return send_file(
            sample_path,
            as_attachment=True,
            download_name='sample_spreadsheet.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    else:
        return 'Sample file not found', 404


@main_bp.route('/', methods=['POST'])
def generate_schedule():
    """Process form data and generate study schedule."""
    # Extract form data
    start_date_str = request.form['start_date']
    study_days_list = request.form.getlist('study_days')
    start_time_str = request.form['start_time']
    daily_study_limit_hours = int(request.form['daily_study_limit_hours'])
    multiplier = float(request.form['multiplier'])
    list_type = request.form['list_type']

    # Parse classes based on input type
    if list_type == 'udemy':
        classes = parse_udemy_list(request.form['class_input'])
    else:  # spreadsheet
        if 'spreadsheet' not in request.files:
            return 'No file uploaded', 400
        file = request.files['spreadsheet']
        classes = parse_spreadsheet(file)

    # Apply time multiplier
    adjusted_classes = apply_multiplier(classes, multiplier)

    # Schedule classes
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    study_days = [int(day) for day in study_days_list]
    study_schedule = schedule_classes(
        adjusted_classes,
        start_date,
        study_days,
        daily_study_limit_hours
    )

    # Create iCalendar file
    ical_data = create_calendar_events(
        study_schedule,
        start_time_str,
        'America/Sao_Paulo',
        daily_study_limit_hours
    )

    # Send file to user
    ical_file = io.BytesIO(ical_data)
    ical_file.seek(0)
    return send_file(
        ical_file,
        as_attachment=True,
        download_name='study_schedule.ics',
        mimetype='text/calendar'
    )

