function toggleInput() {
    var listType = document.getElementById("list_type").value;
    var textBox = document.getElementById("textInputBox");
    var fileBox = document.getElementById("fileInputBox");
    var htmlBox = document.getElementById("htmlInputBox");
    var sheetSelectionBox = document.getElementById("sheetSelectionBox");

    // Hide all boxes first
    textBox.style.display = "none";
    fileBox.style.display = "none";
    if (htmlBox) {
        htmlBox.style.display = "none";
    }
    if (sheetSelectionBox) {
        sheetSelectionBox.style.display = "none";
    }

    // Show the appropriate box
    if (listType === "udemy") {
        textBox.style.display = "block";
        textBox.classList.add("fade-in-section");
    } else if (listType === "html") {
        if (htmlBox) {
            htmlBox.style.display = "block";
            htmlBox.classList.add("fade-in-section");
        }
    } else {
        fileBox.style.display = "block";
        fileBox.classList.add("fade-in-section");
        // Note: sheetSelectionBox will be shown/hidden by analyzeSpreadsheet()
    }
}

function toggleInfo(infoId, event) {
    // Prevent the click from propagating to parent elements
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    
    const infoElement = document.getElementById(infoId);
    if (infoElement) {
        // Toggle the 'active' class instead of changing display
        infoElement.classList.toggle('active');
    }
    
    return false; // Extra safety to prevent default behavior
}

// Loading and Modal Management
const LoadingManager = {
    overlay: null,
    spinner: null,
    text: null,
    subtext: null,
    
    init() {
        this.overlay = document.getElementById('loadingOverlay');
        this.spinner = document.getElementById('loadingSpinner');
        this.text = document.getElementById('loadingText');
        this.subtext = document.getElementById('loadingSubtext');
    },
    
    show(type = 'thinking') {
        if (!this.overlay) this.init();
        
        if (type === 'thinking') {
            this.spinner.innerHTML = '<div class="spinner-brain">🧠</div>';
            this.text.innerHTML = 'Analyzing course content<div class="loading-dots"><span></span><span></span><span></span></div>';
            this.subtext.textContent = 'Our AI is extracting all classes and durations from your course...';
        } else if (type === 'scheduling') {
            this.spinner.innerHTML = '<div class="spinner-calendar">📅</div>';
            this.text.innerHTML = 'Generating your schedule<div class="loading-dots"><span></span><span></span><span></span></div>';
            this.subtext.textContent = 'Creating optimized study blocks based on your preferences...';
        }
        
        this.overlay.classList.add('active');
    },
    
    hide() {
        if (this.overlay) {
            this.overlay.classList.remove('active');
        }
    }
};

const ModalManager = {
    currentModal: null,
    calendarData: null,
    spreadsheetData: null,
    modalHistory: [], // Stack to track modal navigation
    currentCalendarId: null, // Store calendar ID for duplicate flow
    duplicatesData: null, // Store duplicate events data
    pendingFormData: null, // Store form data for preview flow
    courseName: null, // Store course name for duplicate detection
    
    showSpreadsheetModal(addToHistory = true) {
        const modal = document.getElementById('spreadsheetModal');
        this.currentModal = modal;
        modal.classList.add('active');
        if (addToHistory) {
            this.modalHistory = ['spreadsheet']; // Reset history when starting
        }
    },
    
    showExportModal(addToHistory = true) {
        const modal = document.getElementById('exportModal');
        this.currentModal = modal;
        modal.classList.add('active');
        if (addToHistory) {
            this.modalHistory.push('export');
        }
    },
    
    showCalendarSelectionModal(addToHistory = true) {
        const modal = document.getElementById('calendarSelectionModal');
        this.currentModal = modal;
        modal.classList.add('active');
        if (addToHistory) {
            this.modalHistory.push('calendarSelection');
        }
    },
    
    goBack() {
        // Remove current modal from history
        this.modalHistory.pop();
        
        // Hide current modal
        if (this.currentModal) {
            this.currentModal.classList.remove('active');
            this.currentModal = null;
        }
        
        // Show previous modal if exists
        if (this.modalHistory.length > 0) {
            const previousModal = this.modalHistory[this.modalHistory.length - 1];
            
            switch(previousModal) {
                case 'spreadsheet':
                    this.showSpreadsheetModal(false); // Don't add to history
                    break;
                case 'export':
                    this.showExportModal(false); // Don't add to history
                    break;
                case 'calendarSelection':
                    this.showCalendarSelectionModal(false); // Don't add to history
                    break;
            }
        }
    },
    
    hide() {
        if (this.currentModal) {
            this.currentModal.classList.remove('active');
            this.currentModal = null;
        }
        this.modalHistory = []; // Clear history when explicitly hiding
    },
    
    downloadSpreadsheet() {
        if (this.spreadsheetData) {
            // Decode base64 data
            const binaryString = atob(this.spreadsheetData);
            const bytes = new Uint8Array(binaryString.length);
            for (let i = 0; i < binaryString.length; i++) {
                bytes[i] = binaryString.charCodeAt(i);
            }
            
            const blob = new Blob([bytes], { 
                type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
            });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'course_classes.xlsx';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            // Show success message but keep modal open
            alert('✅ Spreadsheet downloaded successfully!\n\nYou can now also upload it to Google Sheets or skip to export your calendar.');
        }
        // Don't hide or navigate - stay on spreadsheet modal
    },
    
    downloadCalendar() {
        if (this.calendarData) {
            // Decode base64 data
            const binaryString = atob(this.calendarData);
            const bytes = new Uint8Array(binaryString.length);
            for (let i = 0; i < binaryString.length; i++) {
                bytes[i] = binaryString.charCodeAt(i);
            }
            
            const blob = new Blob([bytes], { type: 'text/calendar' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'study_schedule.ics';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            // Show success message but keep modal open
            alert('✅ Calendar downloaded successfully!\n\nYou can now also import it directly to Google Calendar or close when done.');
        }
        // Don't hide - stay on export modal
    },
    
    async importToGoogleCalendar() {
        // Don't hide the modal, just show loading overlay
        LoadingManager.show('scheduling');
        LoadingManager.text.innerHTML = 'Connecting to Google<div class="loading-dots"><span></span><span></span><span></span></div>';
        LoadingManager.subtext.textContent = 'Opening authentication window...';
        
        try {
            // Check if already authenticated
            const calendarsResponse = await fetch('/google/calendars');
            
            if (calendarsResponse.status === 401) {
                // Need to authenticate
                const authResponse = await fetch('/google/auth');
                const authData = await authResponse.json();
                
                if (!authData.success) {
                    throw new Error(authData.error || 'Failed to initiate authentication');
                }
                
                // Open OAuth window
                const authWindow = window.open(
                    authData.authorization_url,
                    'Google Authentication',
                    'width=600,height=700,left=200,top=100'
                );
                
                // Wait for authentication
                await new Promise((resolve, reject) => {
                    const checkInterval = setInterval(() => {
                        if (authWindow.closed) {
                            clearInterval(checkInterval);
                            reject(new Error('Authentication window closed'));
                        }
                    }, 1000);
                    
                    window.addEventListener('message', function handler(event) {
                        if (event.data.type === 'google_auth_success') {
                            clearInterval(checkInterval);
                            window.removeEventListener('message', handler);
                            resolve();
                        }
                    });
                });
                
                // Retry getting calendars
                const retryResponse = await fetch('/google/calendars');
                const calendarsData = await retryResponse.json();
                
                if (!calendarsData.success) {
                    throw new Error('Failed to fetch calendars after authentication');
                }
                
                await this.selectCalendarAndImport(calendarsData.calendars);
            } else {
                const calendarsData = await calendarsResponse.json();
                if (calendarsData.success) {
                    await this.selectCalendarAndImport(calendarsData.calendars);
                } else {
                    throw new Error(calendarsData.error || 'Failed to fetch calendars');
                }
            }
        } catch (error) {
            LoadingManager.hide();
            // Show the export modal again on error
            this.showExportModal(false);
            alert('Error: ' + error.message);
        }
    },
    
    async selectCalendarAndImport(calendars) {
        LoadingManager.hide();
        
        // Show calendar selection modal with history tracking
        this.showCalendarSelectionModal(true);
        
        const calendarList = document.getElementById('calendarList');
        
        // Clear previous calendars
        calendarList.innerHTML = '';
        
        // Add calendars
        calendars.forEach(cal => {
            const option = document.createElement('div');
            option.className = 'export-option';
            option.onclick = () => this.importToSelectedCalendar(cal.id);
            option.innerHTML = `
                <div class="export-option-icon">${cal.primary ? '⭐' : '📅'}</div>
                <div class="export-option-content">
                    <h4>${cal.summary}</h4>
                    <p>${cal.primary ? 'Primary Calendar' : 'Secondary Calendar'}</p>
                </div>
            `;
            calendarList.appendChild(option);
        });
    },
    
    async importToSelectedCalendar(calendarId) {
        // Hide calendar selection modal
        this.hide();

        // Show loading for duplicate check
        LoadingManager.show('scheduling');
        LoadingManager.text.innerHTML = 'Checking for duplicates<div class="loading-dots"><span></span><span></span><span></span></div>';
        LoadingManager.subtext.textContent = 'Searching for existing events...';

        try {
            // Check for duplicate events
            const duplicates = await this.checkForDuplicates(calendarId);

            LoadingManager.hide();

            if (duplicates.count > 0) {
                // Store calendar ID for later use
                this.currentCalendarId = calendarId;
                this.duplicatesData = duplicates;

                // Show confirmation modal
                this.showDuplicateConfirmation(calendarId, duplicates);
            } else {
                // No duplicates, proceed with import
                await this.proceedWithImport(calendarId);
            }
        } catch (error) {
            LoadingManager.hide();
            // Show the export modal again on error
            this.showExportModal(false);
            alert('Error checking for duplicates: ' + error.message);
        }
    },

    async checkForDuplicates(calendarId) {
        // Use stored course name from form submission
        const courseName = this.courseName || 'Study';

        const response = await fetch('/google/search-duplicates', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                calendar_id: calendarId,
                course_name: courseName
            })
        });

        if (!response.ok) {
            throw new Error('Failed to check for duplicates');
        }

        return await response.json();
    },

    showDuplicateConfirmation(calendarId, duplicates) {
        const modal = document.getElementById('duplicateConfirmationModal');
        const message = document.getElementById('duplicateMessage');
        const eventsList = document.getElementById('duplicateEventsList');

        // Update message using stored course name
        const courseName = this.courseName || 'Study';
        message.textContent = `We found ${duplicates.count} existing event${duplicates.count > 1 ? 's' : ''} for "${courseName}" in this calendar.`;

        // Clear and populate events list
        eventsList.innerHTML = '';

        duplicates.events.forEach(event => {
            const eventItem = document.createElement('div');
            eventItem.className = 'duplicate-event-item';

            // Format date
            const eventDate = new Date(event.start);
            const formattedDate = eventDate.toLocaleString('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });

            eventItem.innerHTML = `
                <span class="event-date">${formattedDate}</span>
                <span class="event-summary">${event.summary}</span>
            `;

            eventsList.appendChild(eventItem);
        });

        // Show modal
        this.currentModal = modal;
        modal.classList.add('active');
        this.modalHistory.push('duplicateConfirmation');
    },

    async confirmDeleteDuplicates() {
        // Hide modal
        this.hide();

        // Show loading
        LoadingManager.show('scheduling');
        LoadingManager.text.innerHTML = 'Deleting old events<div class="loading-dots"><span></span><span></span><span></span></div>';
        LoadingManager.subtext.textContent = 'Removing duplicate events...';

        try {
            // Extract event IDs from duplicates
            const eventIds = this.duplicatesData.events.map(e => e.id);

            // Delete events
            const response = await fetch('/google/delete-duplicates', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    calendar_id: this.currentCalendarId,
                    event_ids: eventIds
                })
            });

            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error || 'Failed to delete events');
            }

            if (data.failed > 0) {
                LoadingManager.hide();
                const proceed = confirm(`⚠️ Deleted ${data.deleted} events, but ${data.failed} failed.\n\nDo you want to proceed with import anyway?`);
                if (!proceed) {
                    this.showExportModal(false);
                    return;
                }
                LoadingManager.show('scheduling');
            }

            // Proceed with import
            await this.proceedWithImport(this.currentCalendarId);

        } catch (error) {
            LoadingManager.hide();
            this.showExportModal(false);
            alert('Error deleting events: ' + error.message);
        }
    },

    cancelDuplicateCheck() {
        // Hide duplicate modal
        this.hide();

        // Show calendar selection modal again
        this.showCalendarSelectionModal(false);
    },

    async proceedWithImport(calendarId) {
        LoadingManager.show('scheduling');
        LoadingManager.text.innerHTML = 'Importing to Google Calendar<div class="loading-dots"><span></span><span></span><span></span></div>';
        LoadingManager.subtext.textContent = 'Creating events in your calendar...';

        try {
            const response = await fetch('/google/import-calendar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    calendar_data: this.calendarData,
                    calendar_id: calendarId
                })
            });

            const data = await response.json();

            LoadingManager.hide();

            if (data.success) {
                alert(`✅ Success! Imported ${data.event_count} events to your Google Calendar!`);
                // Show the export modal again to allow downloading iCal too
                this.showExportModal(false); // Don't reset history
                alert('You can now also download the iCal file or close when done.');
            } else {
                throw new Error(data.error || 'Failed to import calendar');
            }
        } catch (error) {
            LoadingManager.hide();
            // Show the export modal again even on error
            this.showExportModal(false);
            alert('Error: ' + error.message);
        }
    },
    
    async uploadToDrive() {
        LoadingManager.show('scheduling');
        LoadingManager.text.innerHTML = 'Creating Google Sheets<div class="loading-dots"><span></span><span></span><span></span></div>';
        LoadingManager.subtext.textContent = 'Converting Excel to Google Sheets...';
        
        try {
            // Check if authenticated
            const testResponse = await fetch('/google/calendars');
            
            if (testResponse.status === 401) {
                // Need to authenticate
                const authResponse = await fetch('/google/auth');
                const authData = await authResponse.json();
                
                if (!authData.success) {
                    throw new Error(authData.error || 'Failed to initiate authentication');
                }
                
                // Open OAuth window
                const authWindow = window.open(
                    authData.authorization_url,
                    'Google Authentication',
                    'width=600,height=700,left=200,top=100'
                );
                
                // Wait for authentication
                await new Promise((resolve, reject) => {
                    const checkInterval = setInterval(() => {
                        if (authWindow.closed) {
                            clearInterval(checkInterval);
                            reject(new Error('Authentication window closed'));
                        }
                    }, 1000);
                    
                    window.addEventListener('message', function handler(event) {
                        if (event.data.type === 'google_auth_success') {
                            clearInterval(checkInterval);
                            window.removeEventListener('message', handler);
                            resolve();
                        }
                    });
                });
            }
            
            // Get course name from form or use default
            const courseName = document.getElementById('course_name')?.value || 'Course Classes';
            
            // Import to Google Sheets
            const response = await fetch('/google/upload-drive', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    spreadsheet_data: this.spreadsheetData,
                    filename: courseName
                })
            });
            
            const data = await response.json();
            
            LoadingManager.hide();
            
            if (data.success) {
                const viewLink = data.file.webViewLink;
                if (confirm(`✅ Google Sheets created successfully!\n\n"${data.file.name}" is now available in your Google Drive.\n\nWould you like to open it?`)) {
                    window.open(viewLink, '_blank');
                }
                // Show the spreadsheet modal again to allow more actions
                this.showSpreadsheetModal(false); // Don't reset history
                alert('You can now download the Excel file locally or skip to export your calendar.');
            } else {
                throw new Error(data.error || 'Failed to create Google Sheets');
            }
        } catch (error) {
            LoadingManager.hide();
            // Show the spreadsheet modal again even on error
            this.showSpreadsheetModal(false);
            alert('Error: ' + error.message);
        }
    },

    showPreviewModal(previewData) {
        const modal = document.getElementById('schedulePreviewModal');

        // Populate course name
        document.getElementById('previewCourseName').textContent = previewData.course_name;

        // Populate stats
        document.getElementById('previewTotalHours').textContent = `${previewData.total_content_hours} hours`;
        document.getElementById('previewTotalClasses').textContent = `${previewData.total_classes} classes`;
        document.getElementById('previewStudyDays').textContent = `${previewData.total_study_days} days`;

        // Format end date
        const endDate = new Date(previewData.end_date);
        const formattedEndDate = endDate.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        });
        document.getElementById('previewEndDate').textContent = formattedEndDate;

        // Format start date for timeline
        const startDate = new Date(previewData.start_date);
        const formattedStartDate = startDate.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        });
        document.getElementById('previewStartDate').textContent = formattedStartDate;
        document.getElementById('previewCalendarDays').textContent = `${previewData.calendar_days} days`;
        document.getElementById('previewEndDateTimeline').textContent = formattedEndDate;

        // Show modal
        this.currentModal = modal;
        modal.classList.add('active');
    },

    adjustSchedule() {
        // Hide preview modal and allow user to adjust form
        this.hide();
        // Scroll back to form
        window.scrollTo({ top: 0, behavior: 'smooth' });
    },

    async confirmSchedule() {
        // Hide preview modal
        this.hide();

        // Show generating animation
        LoadingManager.show('scheduling');

        try {
            // Generate the full schedule using stored form data
            const response = await fetch('/generate', {
                method: 'POST',
                body: this.pendingFormData
            });

            const data = await response.json();

            if (data.success) {
                // Store the data
                this.calendarData = data.calendar;
                this.spreadsheetData = data.spreadsheet;

                LoadingManager.hide();
                this.showSpreadsheetModal();
            } else {
                LoadingManager.hide();
                alert('Error: ' + (data.error || 'Unknown error occurred'));
            }
        } catch (error) {
            LoadingManager.hide();
            alert('Error: ' + error.message);
        }
    }
};

// Form submission handler
function handleFormSubmit(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);
    const listType = formData.get('list_type');

    // Validate sheet selection for new format spreadsheets
    if (listType === 'spreadsheet') {
        const sheetSelectionBox = document.getElementById('sheetSelectionBox');
        const selectedSheets = formData.getAll('selected_sheets[]');

        // If sheet selection is visible and no sheets selected, show error
        if (sheetSelectionBox && sheetSelectionBox.style.display !== 'none' && selectedSheets.length === 0) {
            alert('Please select at least one course module to schedule.');
            return;
        }
    }

    // Store form data and course name for later use
    ModalManager.pendingFormData = formData;
    ModalManager.courseName = formData.get('course_name') || 'Study';

    // Show thinking animation
    LoadingManager.show('thinking');
    LoadingManager.text.innerHTML = 'Calculating schedule<div class="loading-dots"><span></span><span></span><span></span></div>';
    LoadingManager.subtext.textContent = 'Analyzing your study parameters...';

    // Call preview endpoint first
    fetch('/preview-schedule', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        LoadingManager.hide();

        if (data.success) {
            // Show preview modal with calculated data
            ModalManager.showPreviewModal(data.preview);
        } else {
            alert('Error: ' + (data.error || 'Unknown error occurred'));
        }
    })
    .catch(error => {
        LoadingManager.hide();
        alert('Error: ' + error.message);
    });
}

// Spreadsheet Analysis Functions
async function analyzeSpreadsheet(file) {
    const sheetSelectionBox = document.getElementById('sheetSelectionBox');
    const loadingDiv = document.getElementById('sheet-analysis-loading');
    const errorDiv = document.getElementById('sheet-analysis-error');
    const checkboxesDiv = document.getElementById('sheet-checkboxes');

    // Reset UI
    checkboxesDiv.innerHTML = '';
    errorDiv.style.display = 'none';
    loadingDiv.style.display = 'block';
    sheetSelectionBox.style.display = 'none';

    try {
        // Create form data
        const formData = new FormData();
        formData.append('spreadsheet', file);

        // Send to backend
        const response = await fetch('/analyze-spreadsheet', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!data.success) {
            throw new Error(data.error || 'Analysis failed');
        }

        // Hide loading
        loadingDiv.style.display = 'none';

        // If old format (single sheet), hide selection
        if (data.format === 'old') {
            sheetSelectionBox.style.display = 'none';
            return;
        }

        // Show sheet selection for new format
        sheetSelectionBox.style.display = 'block';
        sheetSelectionBox.classList.add('fade-in-section');

        // Populate checkboxes
        renderSheetCheckboxes(data.sheets);

    } catch (error) {
        console.error('Error analyzing spreadsheet:', error);
        loadingDiv.style.display = 'none';
        errorDiv.textContent = `Error: ${error.message}`;
        errorDiv.style.display = 'block';
    }
}

function renderSheetCheckboxes(sheets) {
    const container = document.getElementById('sheet-checkboxes');
    container.innerHTML = '';

    sheets.forEach((sheet, index) => {
        const item = document.createElement('div');
        item.className = 'sheet-checkbox-item';

        // Determine completion badge class
        const completionClass =
            sheet.completion_percentage >= 70 ? 'completion-high' :
            sheet.completion_percentage >= 30 ? 'completion-medium' :
            'completion-low';

        // Format duration as HH:MM
        const hours = Math.floor(sheet.total_duration_minutes / 60);
        const minutes = sheet.total_duration_minutes % 60;
        const durationStr = `${hours}h ${minutes}min`;

        item.innerHTML = `
            <input
                type="checkbox"
                name="selected_sheets[]"
                value="${sheet.name}"
                id="sheet-${index}"
                checked
            >
            <div class="sheet-info">
                <label for="sheet-${index}" class="sheet-name">
                    ${sheet.name}
                </label>
                <div class="sheet-stats">
                    <span class="sheet-stat">
                        <i class="fas fa-list"></i>
                        ${sheet.pending_classes} pending classes
                    </span>
                    <span class="sheet-stat">
                        <i class="fas fa-clock"></i>
                        ${durationStr}
                    </span>
                    <span class="completion-badge ${completionClass}">
                        ${sheet.completion_percentage.toFixed(0)}% complete
                    </span>
                </div>
            </div>
        `;

        container.appendChild(item);
    });
}

function selectAllSheets() {
    const checkboxes = document.querySelectorAll('#sheet-checkboxes input[type="checkbox"]');
    checkboxes.forEach(cb => cb.checked = true);
}

function clearAllSheets() {
    const checkboxes = document.querySelectorAll('#sheet-checkboxes input[type="checkbox"]');
    checkboxes.forEach(cb => cb.checked = false);
}

document.addEventListener('DOMContentLoaded', function() {
    // Initialize managers
    LoadingManager.init();
    
    // All features are enabled by default
    // Feature flag system removed for simplicity
    
    // File upload visual feedback for all file inputs
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(function(fileInput) {
        fileInput.addEventListener('change', function(e) {
            const fileName = e.target.files[0]?.name;
            if (fileName) {
                // Find the file-info element within the same parent container
                const container = fileInput.closest('.custom-file-upload');
                if (container) {
                    const fileInfo = container.querySelector('.file-info');
                    if (fileInfo) {
                        fileInfo.textContent = 'Selected file: ' + fileName;
                        fileInfo.style.color = 'var(--dracula-green)';
                    }
                }
            }
        });
    });

    // Spreadsheet file analysis trigger
    const spreadsheetInput = document.querySelector('input[type="file"][name="spreadsheet"]');
    if (spreadsheetInput) {
        spreadsheetInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Trigger analysis
                analyzeSpreadsheet(file);
            }
        });
    }
    
    // Form submission
    const form = document.getElementById('scheduleForm');
    if (form) {
        form.addEventListener('submit', handleFormSubmit);
    }
});

