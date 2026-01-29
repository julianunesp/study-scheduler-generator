"""Service for parsing different input formats (Udemy list and Excel spreadsheet)."""
import io
from openpyxl import load_workbook


def parse_udemy_list(class_input):
    """
    Parse Udemy class list from text input.
    
    Args:
        class_input (str): Text input containing classes in format:
            status
            subject
            duration in minutes
    
    Returns:
        list: List of [status, subject, duration] for each class
    """
    classes = []
    lines = class_input.split('\n')

    i = 0
    while i < len(lines):
        status = lines[i].strip()
        if i + 2 < len(lines):
            subject = lines[i + 1].strip()
            duration_line = lines[i + 2].strip()
            if 'min' in duration_line:
                duration_str = duration_line.replace('min', '')
                try:
                    duration = int(duration_str)
                    classes.append([status, subject, duration])
                    i += 3
                except ValueError:
                    i += 1
            else:
                i += 1
        else:
            break
    return classes


def detect_format(workbook):
    """
    Detect whether spreadsheet is old format (single sheet) or new format (10 sheets).

    Args:
        workbook: openpyxl Workbook object

    Returns:
        str: 'old' or 'new'

    Raises:
        ValueError: If format cannot be determined
    """
    sheet_count = len(workbook.sheetnames)

    # Check for new format (10 sheets with Dashboard)
    if sheet_count == 10:
        # Validate new format indicators
        first_sheet_name = workbook.sheetnames[0].lower()
        if 'dashboard' in first_sheet_name:
            # Check second sheet for expected headers
            second_sheet = workbook[workbook.sheetnames[1]]
            headers = [cell.value for cell in second_sheet[1]]
            # Expected headers: "#", "Module/Class", "Duration (HH:MM:SS)", "Status", "Notes"
            if headers and len(headers) >= 4:
                return 'new'

    # Check for old format (single sheet)
    if sheet_count == 1:
        return 'old'

    # If we have a small number of sheets (2-9), try to detect based on structure
    if 1 <= sheet_count <= 9:
        # Default to old format for backward compatibility
        return 'old'

    # Cannot determine format
    raise ValueError(f"Unable to determine spreadsheet format. Found {sheet_count} sheets. "
                     f"Expected 1 sheet (old format) or 10 sheets (new format).")


def parse_old_format(workbook):
    """
    Parse old format Excel spreadsheet (single sheet, 5 columns).

    Expected columns:
    - A: Day/category (e.g., "Dia 1")
    - B: Title
    - C: Link (URL)
    - D: Duration (time object or decimal hours)
    - E: Completed flag ('x' or empty)

    Args:
        workbook: openpyxl Workbook object

    Returns:
        list: List of ["Not Started", subject, duration_in_minutes] for each non-completed class
    """
    classes = []
    ws = workbook.active

    for row in ws.iter_rows(min_row=2):  # Skip header row
        if not row[0].value:  # Skip empty rows
            continue

        day = row[0].value
        title = row[1].value
        duration = row[3].value  # Column D: duration
        completed = row[4].value == 'x' if row[4].value else False

        # Skip completed classes
        if completed:
            continue

        try:
            # Handle duration as time object
            if hasattr(duration, 'hour') and hasattr(duration, 'minute'):
                # Convert time object to minutes
                duration_minutes = duration.hour * 60 + duration.minute
                if duration.second > 0:
                    duration_minutes += 1  # Round up if there are seconds
            elif isinstance(duration, (int, float)):
                # Handle decimal hours (Excel stores as fraction of day)
                duration_minutes = int(duration * 24 * 60)
                if duration_minutes == 0:
                    continue  # Skip zero durations
            elif isinstance(duration, str) and ':' in duration:
                # Fallback for string format
                h, m, s = map(int, duration.split(':'))
                duration_minutes = h * 60 + m + (1 if s > 0 else 0)
            else:
                continue  # Skip if no valid duration

            # Format the title with the day
            subject = f"🚗 {day}: {title}" if "Pista Rápida" in title else f"{day}: {title}"
            classes.append(["Not Started", subject, duration_minutes])
        except (ValueError, AttributeError, TypeError):
            continue  # Skip invalid duration formats

    return classes


def parse_new_format(workbook, selected_sheets=None):
    """
    Parse new format Excel spreadsheet (10 sheets: Dashboard + 9 course sheets).

    Expected structure:
    - Sheet 0: Dashboard (skipped)
    - Sheets 1-9: Course sheets

    Each course sheet has columns:
    - A: Sequence number (1.0, 2.0, ...)
    - B: Module/Class title
    - C: Duration (timedelta or time object)
    - D: Status ("✅ Completed" or "⬜ Not Started")
    - E: Notes (optional, ignored)

    Args:
        workbook: openpyxl Workbook object
        selected_sheets: Optional list of sheet names to parse. If None, parse all.

    Returns:
        list: List of ["Not Started", subject, duration_in_minutes] for each non-completed class
    """
    classes = []

    # Process sheets 1-9 (skip sheet 0 which is Dashboard)
    for sheet_idx in range(1, min(10, len(workbook.sheetnames))):
        sheet = workbook[workbook.sheetnames[sheet_idx]]
        sheet_name = workbook.sheetnames[sheet_idx]

        # Skip if sheet not in selected_sheets (when filter provided)
        if selected_sheets is not None and sheet_name not in selected_sheets:
            continue

        # Process rows starting from row 2 (row 1 is header)
        for row in sheet.iter_rows(min_row=2):
            # Extract values
            title = row[1].value if len(row) > 1 else None  # Column B
            duration = row[2].value if len(row) > 2 else None  # Column C
            status = row[3].value if len(row) > 3 else None  # Column D

            # Skip if no title or duration
            if not title or not duration:
                continue

            # Skip completed classes (status contains ✅)
            if status and "✅" in str(status):
                continue

            try:
                # Convert duration to minutes
                if hasattr(duration, 'total_seconds'):
                    # Handle timedelta objects (HH:MM:SS format in Excel)
                    total_seconds = duration.total_seconds()
                    duration_minutes = int(total_seconds / 60)
                    if total_seconds % 60 > 0:
                        duration_minutes += 1  # Round up if there are remaining seconds
                    if duration_minutes == 0:
                        continue  # Skip zero durations
                elif hasattr(duration, 'hour') and hasattr(duration, 'minute'):
                    # Handle time object
                    duration_minutes = duration.hour * 60 + duration.minute
                    if hasattr(duration, 'second') and duration.second > 0:
                        duration_minutes += 1  # Round up if there are seconds
                    if duration_minutes == 0:
                        continue  # Skip zero durations
                elif isinstance(duration, (int, float)):
                    # Handle decimal hours stored as fraction of day (rare case)
                    duration_minutes = int(duration * 24 * 60)
                    if duration_minutes == 0:
                        continue  # Skip zero or very small durations
                else:
                    continue  # Skip if no valid duration

                # Format subject: use sheet name as category
                subject = f"🚗 {sheet_name}: {title}" if "Pista Rápida" in str(title) else f"{sheet_name}: {title}"
                classes.append(["Not Started", subject, duration_minutes])

            except (ValueError, AttributeError, TypeError):
                continue  # Skip invalid duration formats

    return classes


def analyze_spreadsheet_sheets(file_storage):
    """
    Analyze Excel spreadsheet and return metadata for each sheet.

    Args:
        file_storage: FileStorage object from Flask request

    Returns:
        dict: {
            'format': 'old' | 'new',
            'sheets': [
                {
                    'name': str,
                    'index': int,
                    'pending_classes': int,
                    'completed_classes': int,
                    'total_duration_minutes': int,
                    'completion_percentage': float
                }
            ]
        }

    Raises:
        ValueError: If spreadsheet cannot be analyzed
    """
    try:
        wb = load_workbook(filename=io.BytesIO(file_storage.read()))
        format_type = detect_format(wb)
        sheets_metadata = []

        if format_type == 'old':
            # Analyze single sheet
            ws = wb.active
            pending = 0
            completed = 0
            total_duration = 0

            for row in ws.iter_rows(min_row=2):  # Skip header
                if not row[0].value:  # Skip empty rows
                    continue

                duration = row[3].value  # Column D
                is_completed = row[4].value == 'x' if row[4].value else False

                if is_completed:
                    completed += 1
                else:
                    pending += 1
                    # Calculate duration
                    try:
                        if hasattr(duration, 'hour') and hasattr(duration, 'minute'):
                            duration_minutes = duration.hour * 60 + duration.minute
                            if duration.second > 0:
                                duration_minutes += 1
                        elif isinstance(duration, (int, float)):
                            duration_minutes = int(duration * 24 * 60)
                        elif isinstance(duration, str) and ':' in duration:
                            h, m, s = map(int, duration.split(':'))
                            duration_minutes = h * 60 + m + (1 if s > 0 else 0)
                        else:
                            duration_minutes = 0

                        total_duration += duration_minutes
                    except (ValueError, AttributeError, TypeError):
                        pass

            total_classes = pending + completed
            completion_pct = (completed / total_classes * 100) if total_classes > 0 else 0

            sheets_metadata.append({
                'name': wb.sheetnames[0],
                'index': 0,
                'pending_classes': pending,
                'completed_classes': completed,
                'total_duration_minutes': total_duration,
                'completion_percentage': completion_pct
            })

        else:  # 'new' format
            # Analyze sheets 1-9 (skip Dashboard at index 0)
            for sheet_idx in range(1, min(10, len(wb.sheetnames))):
                sheet = wb[wb.sheetnames[sheet_idx]]
                sheet_name = wb.sheetnames[sheet_idx]

                pending = 0
                completed = 0
                total_duration = 0

                # Process rows starting from row 2 (row 1 is header)
                for row in sheet.iter_rows(min_row=2):
                    title = row[1].value if len(row) > 1 else None  # Column B
                    duration = row[2].value if len(row) > 2 else None  # Column C
                    status = row[3].value if len(row) > 3 else None  # Column D

                    # Skip if no title or duration
                    if not title or not duration:
                        continue

                    # Check if completed
                    is_completed = status and "✅" in str(status)

                    if is_completed:
                        completed += 1
                    else:
                        pending += 1
                        # Calculate duration
                        try:
                            if hasattr(duration, 'total_seconds'):
                                # Handle timedelta
                                total_seconds = duration.total_seconds()
                                duration_minutes = int(total_seconds / 60)
                                if total_seconds % 60 > 0:
                                    duration_minutes += 1
                            elif hasattr(duration, 'hour') and hasattr(duration, 'minute'):
                                # Handle time object
                                duration_minutes = duration.hour * 60 + duration.minute
                                if hasattr(duration, 'second') and duration.second > 0:
                                    duration_minutes += 1
                            elif isinstance(duration, (int, float)):
                                # Handle decimal
                                duration_minutes = int(duration * 24 * 60)
                            else:
                                duration_minutes = 0

                            total_duration += duration_minutes
                        except (ValueError, AttributeError, TypeError):
                            pass

                total_classes = pending + completed
                completion_pct = (completed / total_classes * 100) if total_classes > 0 else 0

                sheets_metadata.append({
                    'name': sheet_name,
                    'index': sheet_idx,
                    'pending_classes': pending,
                    'completed_classes': completed,
                    'total_duration_minutes': total_duration,
                    'completion_percentage': completion_pct
                })

        return {
            'format': format_type,
            'sheets': sheets_metadata
        }

    except Exception as e:
        raise ValueError(f"Failed to analyze spreadsheet: {str(e)}")


def parse_spreadsheet(file_storage, selected_sheets=None):
    """
    Parse Excel spreadsheet with class information.
    Supports both old format (single sheet) and new format (10 sheets).

    Args:
        file_storage: FileStorage object from Flask request
        selected_sheets: Optional list of sheet names to include (new format only)

    Returns:
        list: List of [status, subject, duration] for each class

    Raises:
        ValueError: If spreadsheet format cannot be determined
    """
    try:
        wb = load_workbook(filename=io.BytesIO(file_storage.read()))

        # Detect format
        format_type = detect_format(wb)

        # Parse based on format
        if format_type == 'old':
            return parse_old_format(wb)
        else:  # 'new'
            return parse_new_format(wb, selected_sheets=selected_sheets)

    except ValueError as e:
        # Re-raise format detection errors with context
        raise ValueError(f"Spreadsheet parsing error: {str(e)}")
    except Exception as e:
        # Catch other errors and provide clear message
        raise ValueError(f"Failed to parse spreadsheet: {str(e)}")

