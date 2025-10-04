function toggleInput() {
    var listType = document.getElementById("list_type").value;
    var textBox = document.getElementById("textInputBox");
    var fileBox = document.getElementById("fileInputBox");
    
    if (listType === "udemy") {
        textBox.style.display = "block";
        fileBox.style.display = "none";
        textBox.classList.add("fade-in-section");
    } else {
        textBox.style.display = "none";
        fileBox.style.display = "block";
        fileBox.classList.add("fade-in-section");
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

document.addEventListener('DOMContentLoaded', function() {
    // File upload visual feedback
    const fileInput = document.querySelector('input[type="file"]');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const fileName = e.target.files[0]?.name;
            if (fileName) {
                const fileInfo = document.querySelector('.file-info');
                fileInfo.textContent = 'Selected file: ' + fileName;
                fileInfo.style.color = 'var(--dracula-green)';
            }
        });
    }
});

