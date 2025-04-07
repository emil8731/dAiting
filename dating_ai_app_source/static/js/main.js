// Main JavaScript for Dating App AI Assistant

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Conversation monitoring
    setupConversationMonitoring();

    // Notification checking
    setupNotificationChecking();

    // Message editing
    setupMessageEditing();
});

// Setup conversation monitoring
function setupConversationMonitoring() {
    const monitorButtons = document.querySelectorAll('.monitor-button');
    
    monitorButtons.forEach(button => {
        button.addEventListener('click', function() {
            const conversationId = this.dataset.conversationId;
            const action = this.dataset.action;
            const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
            
            // Create form data
            const formData = new FormData();
            formData.append('action', action);
            
            // Send request
            fetch(`/monitor/${conversationId}`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show success message
                    showAlert(data.message, 'success');
                    
                    // Update button
                    if (action === 'start') {
                        this.dataset.action = 'stop';
                        this.innerHTML = '<i class="bi bi-stop-circle"></i> Stop Monitoring';
                        this.classList.replace('btn-success', 'btn-danger');
                    } else {
                        this.dataset.action = 'start';
                        this.innerHTML = '<i class="bi bi-play-circle"></i> Start Monitoring';
                        this.classList.replace('btn-danger', 'btn-success');
                    }
                } else {
                    // Show error message
                    showAlert(data.message, 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('An error occurred', 'danger');
            });
        });
    });
}

// Setup notification checking
function setupNotificationChecking() {
    // Check for notifications every 30 seconds
    if (document.querySelector('#notification-badge')) {
        checkNotifications();
        setInterval(checkNotifications, 30000);
    }
}

// Check for new notifications
function checkNotifications() {
    fetch('/api/notifications')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.count > 0) {
                // Update notification badge
                const badge = document.querySelector('#notification-badge');
                badge.textContent = data.count;
                badge.classList.remove('d-none');
                
                // Update notification dropdown if it exists
                const dropdown = document.querySelector('#notification-dropdown');
                if (dropdown) {
                    updateNotificationDropdown(data.notifications);
                }
            }
        })
        .catch(error => console.error('Error checking notifications:', error));
}

// Update notification dropdown
function updateNotificationDropdown(notifications) {
    const dropdown = document.querySelector('#notification-dropdown');
    dropdown.innerHTML = '';
    
    notifications.forEach(notification => {
        const item = document.createElement('a');
        item.className = 'dropdown-item';
        item.href = getNotificationLink(notification);
        
        let icon = '';
        switch (notification.type) {
            case 'new_message':
                icon = '<i class="bi bi-chat-text-fill text-primary me-2"></i>';
                break;
            case 'new_match':
                icon = '<i class="bi bi-person-plus-fill text-success me-2"></i>';
                break;
            case 'conversation_inactive':
                icon = '<i class="bi bi-clock-fill text-warning me-2"></i>';
                break;
            case 'suggested_response':
                icon = '<i class="bi bi-lightbulb-fill text-info me-2"></i>';
                break;
        }
        
        item.innerHTML = `
            ${icon}
            <div class="d-flex flex-column">
                <span>${getNotificationText(notification)}</span>
                <small class="text-muted">${formatDateTime(notification.timestamp)}</small>
            </div>
        `;
        
        dropdown.appendChild(item);
    });
    
    // Add "See all" link
    const seeAll = document.createElement('a');
    seeAll.className = 'dropdown-item text-center text-primary';
    seeAll.href = '/notifications';
    seeAll.textContent = 'See all notifications';
    dropdown.appendChild(seeAll);
}

// Get notification link
function getNotificationLink(notification) {
    switch (notification.type) {
        case 'new_message':
        case 'conversation_inactive':
        case 'suggested_response':
            return `/conversation/${notification.conversation_id}`;
        case 'new_match':
            return `/match/${notification.match_id}`;
        default:
            return '#';
    }
}

// Get notification text
function getNotificationText(notification) {
    switch (notification.type) {
        case 'new_message':
            return `New message from ${notification.match_name}`;
        case 'new_match':
            return `New match: ${notification.match_name}`;
        case 'conversation_inactive':
            return `Conversation with ${notification.match_name} is inactive`;
        case 'suggested_response':
            return `Suggested response for ${notification.match_name}`;
        default:
            return 'New notification';
    }
}

// Setup message editing
function setupMessageEditing() {
    const editButtons = document.querySelectorAll('.edit-message-button');
    
    editButtons.forEach(button => {
        button.addEventListener('click', function() {
            const messageId = this.dataset.messageId;
            const messageContent = document.querySelector(`#message-content-${messageId}`).textContent;
            
            // Show edit form
            document.querySelector(`#message-display-${messageId}`).classList.add('d-none');
            document.querySelector(`#message-edit-${messageId}`).classList.remove('d-none');
            
            // Set textarea content
            document.querySelector(`#message-edit-textarea-${messageId}`).value = messageContent;
        });
    });
    
    const cancelButtons = document.querySelectorAll('.cancel-edit-button');
    
    cancelButtons.forEach(button => {
        button.addEventListener('click', function() {
            const messageId = this.dataset.messageId;
            
            // Hide edit form
            document.querySelector(`#message-display-${messageId}`).classList.remove('d-none');
            document.querySelector(`#message-edit-${messageId}`).classList.add('d-none');
        });
    });
}

// Show alert message
function showAlert(message, type = 'info') {
    const alertContainer = document.querySelector('#alert-container');
    if (!alertContainer) return;
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    alertContainer.appendChild(alert);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alert.classList.remove('show');
        setTimeout(() => alert.remove(), 150);
    }, 5000);
}

// Format date time
function formatDateTime(dateTimeStr) {
    if (!dateTimeStr) return '';
    
    const date = new Date(dateTimeStr);
    if (isNaN(date)) return dateTimeStr;
    
    const now = new Date();
    const diffMs = now - date;
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);
    const diffHour = Math.floor(diffMin / 60);
    const diffDay = Math.floor(diffHour / 24);
    
    if (diffSec < 60) {
        return 'just now';
    } else if (diffMin < 60) {
        return `${diffMin} minute${diffMin !== 1 ? 's' : ''} ago`;
    } else if (diffHour < 24) {
        return `${diffHour} hour${diffHour !== 1 ? 's' : ''} ago`;
    } else if (diffDay < 7) {
        return `${diffDay} day${diffDay !== 1 ? 's' : ''} ago`;
    } else {
        return date.toLocaleDateString();
    }
}

// Check for new messages in conversation
function checkNewMessages(conversationId, lastTimestamp) {
    fetch(`/api/check_messages/${conversationId}?last_timestamp=${encodeURIComponent(lastTimestamp)}`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.count > 0) {
                // Add new messages to the conversation
                const messagesContainer = document.querySelector('#messages-container');
                let newLastTimestamp = lastTimestamp;
                
                data.messages.forEach(message => {
                    const messageElement = createMessageElement(message);
                    messagesContainer.appendChild(messageElement);
                    
                    if (message.sent_at > newLastTimestamp) {
                        newLastTimestamp = message.sent_at;
                    }
                });
                
                // Scroll to bottom
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
                
                // Update last timestamp
                document.querySelector('#last-timestamp').value = newLastTimestamp;
                
                // Play notification sound
                playNotificationSound();
            }
        })
        .catch(error => console.error('Error checking new messages:', error));
}

// Create message element
function createMessageElement(message) {
    const div = document.createElement('div');
    div.className = `message ${message.sender_type === 'user' ? 'message-user' : 'message-match'}`;
    div.id = `message-${message.id}`;
    
    div.innerHTML = `
        <div id="message-display-${message.id}">
            <div id="message-content-${message.id}">${message.content}</div>
            <div class="message-time">${formatDateTime(message.sent_at)}</div>
        </div>
        <div id="message-edit-${message.id}" class="d-none">
            <textarea id="message-edit-textarea-${message.id}" class="form-control mb-2">${message.content}</textarea>
            <div class="d-flex justify-content-end">
                <button class="btn btn-sm btn-secondary cancel-edit-button me-2" data-message-id="${message.id}">Cancel</button>
                <button class="btn btn-sm btn-primary save-edit-button" data-message-id="${message.id}">Save</button>
            </div>
        </div>
    `;
    
    return div;
}

// Play notification sound
function playNotificationSound() {
    const audio = new Audio('/static/sounds/notification.mp3');
    audio.play().catch(error => console.error('Error playing notification sound:', error));
}

// Initialize charts
function initializeCharts() {
    // Message activity chart
    const activityCtx = document.getElementById('activity-chart');
    if (activityCtx) {
        const activityData = JSON.parse(activityCtx.dataset.activity);
        const labels = Object.keys(activityData);
        const data = Object.values(activityData);
        
        new Chart(activityCtx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Messages',
                    data: data,
                    borderColor: '#ff4b91',
                    backgroundColor: 'rgba(255, 75, 145, 0.1)',
                    tension: 0.3,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                }
            }
        });
    }
    
    // Hourly distribution chart
    const hourlyCtx = document.getElementById('hourly-chart');
    if (hourlyCtx) {
        const hourlyData = JSON.parse(hourlyCtx.dataset.hourly);
        const labels = Array.from({length: 24}, (_, i) => `${i}:00`);
        const data = labels.map((_, i) => hourlyData[i] || 0);
        
        new Chart(hourlyCtx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Messages',
                    data: data,
                    backgroundColor: '#ff9a8d'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                }
            }
        });
    }
    
    // Platform distribution chart
    const platformCtx = document.getElementById('platform-chart');
    if (platformCtx) {
        const platformData = JSON.parse(platformCtx.dataset.platforms);
        const labels = Object.keys(platformData);
        const data = Object.values(platformData);
        
        new Chart(platformCtx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: ['#ff4b91', '#ff9a8d', '#ffb8d9']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
}
