/* ============================================================================
   JOURNEY BUILDER - CHAT FUNCTIONALITY
   ============================================================================ */

let currentJourneyStructure = null;
let conversationTurns = 0;
const MAX_TURNS = 10;

document.addEventListener('DOMContentLoaded', initializeChat);

function initializeChat() {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    
    if (chatForm) {
        chatForm.addEventListener('submit', handleChatSubmit);
        
        // Auto-focus input
        userInput?.focus();
        
        // Allow Enter+Shift to submit
        userInput?.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                chatForm.dispatchEvent(new Event('submit'));
            }
        });
    }
}

async function handleChatSubmit(e) {
    e.preventDefault();
    
    const userInput = document.getElementById('user-input');
    const message = userInput.value.trim();
    
    if (!message) return;
    
    // Disable form
    const submitBtn = e.target.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    
    try {
        // Add user message to chat
        addMessageToChat('user', message);
        userInput.value = '';
        
        // Send to API
        const response = await fetch('/api/journey/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                session_id: getSessionId()
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Add assistant response
            addMessageToChat('assistant', data.response);
            conversationTurns++;
            
            // Update preview
            if (data.journey_structure) {
                currentJourneyStructure = data.journey_structure;
                updatePreview(data.journey_structure);
                
                // Show modal if journey is complete
                if (!data.needs_more_info && conversationTurns >= 3) {
                    showPublishModal();
                }
            }
            
            // Show status
            if (data.needs_more_info) {
                showStatus('Gathering more information...', 'info');
            }
            
        } else {
            addMessageToChat('assistant', '❌ Sorry, something went wrong. Please try again.');
            showStatus('Error processing message', 'error');
        }
    } catch (error) {
        console.error('Chat error:', error);
        addMessageToChat('assistant', '⚠️ Connection error. Please check your internet and try again.');
        showStatus('Network error', 'error');
    } finally {
        submitBtn.disabled = false;
        userInput.focus();
    }
}

function addMessageToChat(role, content) {
    const messagesContainer = document.getElementById('messages');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    messageContent.textContent = content;
    
    messageDiv.appendChild(messageContent);
    messagesContainer.appendChild(messageDiv);
    
    // Auto-scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function updatePreview(structure) {
    const previewDiv = document.getElementById('preview');
    
    if (!structure) {
        previewDiv.innerHTML = '<div class="empty-state"><p>Your journey structure will appear here...</p></div>';
        return;
    }
    
    let html = `
        <div class="preview-section">
            <h4>Journey Title</h4>
            <p><strong>${escapeHtml(structure.title || 'Untitled')}</strong></p>
        </div>
    `;
    
    if (structure.condition) {
        html += `
            <div class="preview-section">
                <h4>Condition/Procedure</h4>
                <p>${escapeHtml(structure.condition)}</p>
            </div>
        `;
    }
    
    if (structure.start_date) {
        html += `
            <div class="preview-section">
                <h4>Timeline</h4>
                <p>${escapeHtml(structure.start_date)} to ${escapeHtml(structure.end_date || 'ongoing')}</p>
            </div>
        `;
    }
    
    if (structure.summary) {
        html += `
            <div class="preview-section">
                <h4>Summary</h4>
                <p>${escapeHtml(structure.summary.substring(0, 150))}...</p>
            </div>
        `;
    }
    
    if (structure.stages && structure.stages.length > 0) {
        html += `
            <div class="preview-section">
                <h4>Journey Stages (${structure.stages.length})</h4>
                <ul>
                    ${structure.stages.map(s => `
                        <li>
                            <strong>${escapeHtml(s.name || '')}</strong>
                            <div style="color: #999; font-size: 0.9rem;">${escapeHtml(s.description || '')}</div>
                        </li>
                    `).join('')}
                </ul>
            </div>
        `;
    }
    
    if (structure.timeline_entries && structure.timeline_entries.length > 0) {
        html += `
            <div class="preview-section">
                <h4>Timeline Entries (${structure.timeline_entries.length})</h4>
                <ul>
                    ${structure.timeline_entries.slice(0, 5).map(e => `
                        <li>
                            <strong>[${escapeHtml(e.date || '')}]</strong>
                            ${escapeHtml(e.title || '')}
                        </li>
                    `).join('')}
                    ${structure.timeline_entries.length > 5 ? `<li><em>...and ${structure.timeline_entries.length - 5} more</em></li>` : ''}
                </ul>
            </div>
        `;
    }
    
    previewDiv.innerHTML = html;
}

function showPublishModal() {
    const modal = document.getElementById('structure-modal');
    if (modal) {
        modal.style.display = 'flex';
    }
}

function closeModal() {
    const modal = document.getElementById('structure-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

async function publishJourney() {
    if (!currentJourneyStructure) {
        showStatus('No journey structure to publish', 'error');
        return;
    }
    
    const publishBtn = event.target;
    publishBtn.disabled = true;
    publishBtn.textContent = 'Publishing...';
    
    try {
        const response = await fetch('/api/journey', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(currentJourneyStructure)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showStatus('Journey published! Redirecting...', 'success');
            setTimeout(() => {
                window.location.href = data.public_url;
            }, 1000);
        } else {
            showStatus('Error publishing: ' + (data.error || 'Unknown error'), 'error');
            publishBtn.disabled = false;
            publishBtn.textContent = 'Publish Journey';
        }
    } catch (error) {
        console.error('Publish error:', error);
        showStatus('Failed to publish journey', 'error');
        publishBtn.disabled = false;
        publishBtn.textContent = 'Publish Journey';
    }
}

function showStatus(message, type) {
    const toast = document.createElement('div');
    toast.className = `status-toast status-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? '#4caf50' : type === 'error' ? '#f44336' : '#2196F3'};
        color: white;
        border-radius: 4px;
        z-index: 3000;
        animation: slideInUp 0.3s ease;
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function getSessionId() {
    // Get from data attribute or return placeholder
    const builder = document.querySelector('.journey-builder-container');
    return builder?.getAttribute('data-session-id') || 'default-session';
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return String(text).replace(/[&<>"']/g, m => map[m]);
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Alt + N: New journey
    if (e.altKey && e.key === 'n') {
        e.preventDefault();
        const builderLink = document.querySelector('a[href*="/journey/builder"]');
        if (builderLink) builderLink.click();
    }
});

// Add some CSS for toasts dynamically
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInUp {
        from {
            transform: translateY(20px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);
