/* ============================================================================
   SURGERY DAY BUILDER - MAIN JAVASCRIPT
   ============================================================================ */

// Mobile menu toggle
document.addEventListener('DOMContentLoaded', () => {
    const navbarToggle = document.getElementById('navbar-toggle');
    const navbarMenu = document.getElementById('navbar-menu');
    
    if (navbarToggle) {
        navbarToggle.addEventListener('click', () => {
            navbarMenu.classList.toggle('active');
            navbarToggle.classList.toggle('active');
        });
    }
    
    // Close menu when clicking a link
    const navbarItems = document.querySelectorAll('.navbar-item');
    navbarItems.forEach(item => {
        item.addEventListener('click', () => {
            navbarMenu.classList.remove('active');
            navbarToggle?.classList.remove('active');
        });
    });
    
    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.navbar')) {
            navbarMenu?.classList.remove('active');
            navbarToggle?.classList.remove('active');
        }
    });
});

// Dropdown menu functionality
document.addEventListener('DOMContentLoaded', () => {
    const dropdowns = document.querySelectorAll('.dropdown');
    
    dropdowns.forEach(dropdown => {
        const trigger = dropdown.querySelector('.dropdown-trigger');
        const menu = dropdown.querySelector('.dropdown-menu');
        
        if (trigger && menu) {
            trigger.addEventListener('click', (e) => {
                e.stopPropagation();
                menu.classList.toggle('active');
            });
        }
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', () => {
        document.querySelectorAll('.dropdown-menu.active').forEach(menu => {
            menu.classList.remove('active');
        });
    });
});

// Auto-hide alerts after 5 seconds
document.addEventListener('DOMContentLoaded', () => {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
});

// Form validation helper
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;
    
    let isValid = true;
    const inputs = form.querySelectorAll('input[required], textarea[required]');
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('error');
            isValid = false;
        } else {
            input.classList.remove('error');
        }
    });
    
    return isValid;
}

// Utility: Escape HTML
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Utility: Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Utility: Show toast notification
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Scroll to top button
const scrollToTopBtn = document.getElementById('scroll-to-top');
if (scrollToTopBtn) {
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            scrollToTopBtn.style.display = 'block';
        } else {
            scrollToTopBtn.style.display = 'none';
        }
    });
    
    scrollToTopBtn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}

// Handle loading states on buttons
document.addEventListener('DOMContentLoaded', () => {
    const buttons = document.querySelectorAll('button[type="submit"]');
    
    buttons.forEach(button => {
        const form = button.closest('form');
        if (form) {
            form.addEventListener('submit', (e) => {
                if (form.checkValidity() !== false) {
                    button.disabled = true;
                    button.setAttribute('data-original', button.textContent);
                    button.textContent = 'Loading...';
                }
            });
        }
    });
});

export { validateForm, escapeHtml, formatDate, showToast };
