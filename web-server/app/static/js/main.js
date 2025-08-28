async function sendEmergencyStop() {
    const button = document.getElementById('emergencyStop');
    const statusDiv = document.getElementById('statusMessage');
    
    // Disable button to prevent multiple clicks
    button.disabled = true;
    button.textContent = 'Sending Emergency Stop...';
    
    try {
        const response = await fetch('/emergency_stop', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                command: 'M112'  // Emergency stop G-code
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            showStatus('Emergency stop sent successfully!', 'success');
        } else {
            const errorData = await response.json();
            showStatus(`Failed to send emergency stop: ${errorData.error || 'Unknown error'}`, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showStatus('Network error. Please check connection.', 'error');
    } finally {
        // Re-enable button
        button.disabled = false;
        button.textContent = '🛑 EMERGENCY STOP';
    }
}

function showStatus(message, type) {
    const statusDiv = document.getElementById('statusMessage');
    statusDiv.textContent = message;
    statusDiv.className = `status-message status-${type}`;
    statusDiv.style.display = 'block';
    
    // Hide message after 5 seconds
    setTimeout(() => {
        statusDiv.style.display = 'none';
    }, 5000);
}

// Initialize page when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Any initialization code can go here
    console.log('Farming Robot Control Panel loaded');
});
