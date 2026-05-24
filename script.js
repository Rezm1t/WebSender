/**
 * JavaScript for PS4/PS5 Payload Sender
 * Handles form submission, file upload, and socket communication via Flask
 */

document.addEventListener('DOMContentLoaded', function() {
    const payloadForm = document.getElementById('payloadForm');
    const fileInput = document.getElementById('payloadFile');
    const fileNameDisplay = document.getElementById('fileName');
    const fileInputLabel = document.querySelector('.file-input-label');
    const statusMessage = document.getElementById('statusMessage');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const sendBtn = document.getElementById('sendBtn');

    // Click на div щоб відкрити file picker
    fileInputLabel.addEventListener('click', function(e) {
        e.preventDefault();
        fileInput.click();
    });

    // Update file name display when file is selected
    fileInput.addEventListener('change', function(e) {
        if (this.files && this.files[0]) {
            fileNameDisplay.textContent = this.files[0].name;
        } else {
            fileNameDisplay.textContent = 'Choose file...';
        }
    });

    // Handle form submission
    payloadForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Get form values
        const ipAddress = document.getElementById('ipAddress').value.trim();
        const port = document.getElementById('port').value.trim();
        const file = fileInput.files[0];

        // Validate inputs
        if (!ipAddress || !port || !file) {
            showStatus('Please fill in all fields', 'error');
            return;
        }

        // Validate IP format (basic check)
        if (!isValidIP(ipAddress)) {
            showStatus('Invalid IP address format', 'error');
            return;
        }

        // Validate port range
        const portNum = parseInt(port);
        if (portNum < 1 || portNum > 65535) {
            showStatus('Port must be between 1 and 65535', 'error');
            return;
        }

        // Send payload via Fetch API
        await sendPayload(ipAddress, port, file);
    });

    /**
     * CORE FUNCTION: Send payload through socket via Flask backend
     * This function coordinates the payload transmission
     */
    async function sendPayload(ipAddress, port, file) {
        // Show loading indicator and hide status message
        loadingIndicator.style.display = 'flex';
        statusMessage.style.display = 'none';
        sendBtn.disabled = true;

        try {
            // Create FormData to send file and parameters
            const formData = new FormData();
            formData.append('ip_address', ipAddress);
            formData.append('port', port);
            formData.append('payload_file', file);

            // Send POST request to Flask backend
            // The backend will read the binary file and transmit via socket
            const response = await fetch('/send-payload', {
                method: 'POST',
                body: formData
            });

            // Parse response
            const result = await response.json();

            // Handle response from backend
            if (result.status === 'success') {
                showStatus(
                    `✓ Success! ${result.message}`,
                    'success'
                );
                // Reset form on successful send
                payloadForm.reset();
                fileNameDisplay.textContent = 'Choose file...';
            } else {
                showStatus(`✗ Error: ${result.message}`, 'error');
            }

        } catch (error) {
            showStatus(`Network error: ${error.message}`, 'error');
            console.error('Payload send error:', error);
        } finally {
            // Hide loading indicator and re-enable button
            loadingIndicator.style.display = 'none';
            sendBtn.disabled = false;
        }
    }

    /**
     * Display status message to user
     */
    function showStatus(message, type) {
        statusMessage.textContent = message;
        statusMessage.className = `status-message ${type}`;
        statusMessage.style.display = 'block';

        // Auto-hide success messages after 5 seconds
        if (type === 'success') {
            setTimeout(() => {
                statusMessage.style.display = 'none';
            }, 5000);
        }
    }

    /**
     * Validate IP address format (IPv4)
     */
    function isValidIP(ip) {
        const ipRegex = /^(\d{1,3}\.){3}\d{1,3}$/;
        if (!ipRegex.test(ip)) return false;

        // Check each octet is 0-255
        const parts = ip.split('.');
        return parts.every(part => {
            const num = parseInt(part);
            return num >= 0 && num <= 255;
        });
    }
});
