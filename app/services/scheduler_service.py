"""Service for scheduling classes and creating calendar events."""
from datetime import datetime, timedelta
import math
import pytz
from icalendar import Calendar, Event


def apply_multiplier(classes, multiplier):
    """
    Apply time multiplier to all classes.
    
    Args:
        classes (list): List of [status, subject, duration] for each class
        multiplier (float): Time multiplier (e.g., 1.5 for 50% more time)
    
    Returns:
        list: List of classes with adjusted durations
    """
    return [[cls[0], cls[1], float(cls[2]) * float(multiplier)] for cls in classes]


def schedule_classes(classes, start_date, study_days, daily_study_limit_hours):
    """
    Schedule classes across available study days.
    
    Args:
        classes (list): List of [status, subject, duration] for each class
        start_date (date): First day to schedule
        study_days (list): List of weekday integers (0=Monday, 6=Sunday)
        daily_study_limit_hours (int): Maximum hours per day
    
    Returns:
        dict: Dictionary mapping dates to lists of classes scheduled for that day
        Each class entry is: [status, title, scheduled_duration, original_duration]
    """
    study_schedule = {}
    daily_study_limit_minutes = daily_study_limit_hours * 60
    current_date = start_date
    time_left = daily_study_limit_minutes

    for cls in classes:
        # Store original duration before modifying
        original_duration = cls[2]
        remaining_duration = original_duration
        
        while remaining_duration > 0:
            if current_date.weekday() in study_days:
                if time_left >= remaining_duration:
                    if current_date not in study_schedule:
                        study_schedule[current_date] = []
                    # Add class with scheduled duration and original duration
                    study_schedule[current_date].append([cls[0], cls[1], remaining_duration, original_duration])
                    time_left -= remaining_duration
                    remaining_duration = 0
                else:
                    if current_date not in study_schedule:
                        study_schedule[current_date] = []
                    # Split class - add portion that fits today, but keep original duration
                    study_schedule[current_date].append([cls[0], cls[1], time_left, original_duration])
                    remaining_duration -= time_left
                    time_left = 0
            if time_left == 0 or current_date.weekday() not in study_days:
                current_date += timedelta(days=1)
                time_left = daily_study_limit_minutes

    return study_schedule


def create_calendar_events(study_schedule, start_time_str, timezone, daily_study_limit_hours, course_name="Study"):
    """
    Create iCalendar events from study schedule.
    
    Args:
        study_schedule (dict): Dictionary mapping dates to lists of classes
        start_time_str (str): Start time in format 'HH:MM'
        timezone (str): Timezone name (e.g., 'America/Sao_Paulo')
        daily_study_limit_hours (int): Maximum hours per day
        course_name (str): Name of the course to include in event title
    
    Returns:
        bytes: iCalendar data in bytes format
    """
    cal = Calendar()
    cal.add('prodid', '-//Study Schedule Calendar//mxm.dk//')
    cal.add('version', '2.0')
    local_tz = pytz.timezone(timezone)

    for day, classes in study_schedule.items():
        start_datetime = datetime.combine(day, datetime.strptime(start_time_str, '%H:%M').time())
        start_datetime = local_tz.localize(start_datetime)
        end_datetime = start_datetime + timedelta(minutes=daily_study_limit_hours*60)

        event = Event()
        event.add('summary', f"📚 {course_name} - Study Block")
        event.add('dtstart', start_datetime)
        event.add('dtend', end_datetime)
        
        # Build description with formatted class list
        description_lines = ["Classes for today:\n"]
        for cls in classes:
            class_name = cls[1]
            # Use original duration (cls[3]) instead of scheduled duration (cls[2])
            original_duration_minutes = cls[3]
            
            # Convert duration from minutes to HH:MM:SS format without rounding
            total_seconds = original_duration_minutes * 60  # Convert minutes to seconds
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            seconds = int(total_seconds % 60)
            
            # Format as HH:MM:SS
            duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            
            description_lines.append(f"⬜ {class_name} ({duration_str})")
        
        description_lines.append("\n✏️ Update ⬜ to ✅ as you complete each class!")
        
        event.add('description', '\n'.join(description_lines))
        cal.add_component(event)

    return cal.to_ical()

