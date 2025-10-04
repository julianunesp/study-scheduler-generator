"""Services module for Study Schedule Generator."""
from .parser_service import parse_udemy_list, parse_spreadsheet
from .scheduler_service import apply_multiplier, schedule_classes, create_calendar_events
from .html_parser_agent import get_html_parser
from .google_service import get_google_service

__all__ = [
    'parse_udemy_list',
    'parse_spreadsheet',
    'apply_multiplier',
    'schedule_classes',
    'create_calendar_events',
    'get_html_parser',
    'get_google_service',
]

