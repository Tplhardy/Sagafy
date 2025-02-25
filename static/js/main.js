/**
 * Work History Documentation Tool
 * Main JavaScript file for general site functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Flash message handling
    const flashMessages = document.querySelectorAll('.flash-message');
    
    if (flashMessages.length > 0) {
        // Auto-hide flash messages after 5 seconds
        setTimeout(() => {
            flashMessages.forEach(message => {
                message.style.opacity = '0';
                message.style.transition = 'opacity 0.5s ease-out';
                
                // Remove from DOM after fade out
                setTimeout(() => {
                    message.parentNode.removeChild(message);
                }, 500);
            });
        }, 5000);
    }
    
    // Mobile menu toggle (if needed in the future)
    const menuToggle = document.querySelector('.menu-toggle');
    if (menuToggle) {
        const mobileMenu = document.querySelector('.mobile-menu');
        
        menuToggle.addEventListener('click', function() {
            mobileMenu.classList.toggle('active');
            menuToggle.classList.toggle('active');
        });
    }
    
    // Form validation for registration
    const registrationForm = document.getElementById('registration-form');
    if (registrationForm) {
        registrationForm.addEventListener('submit', function(e) {
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm-password').value;
            
            if (password !== confirmPassword) {
                e.preventDefault();
                alert('Passwords do not match!');
                return false;
            }
            
            if (password.length < 8) {
                e.preventDefault();
                alert('Password must be at least 8 characters long!');
                return false;
            }
            
            return true;
        });
    }
    
    // Auto-resize textarea in chat
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
        
        // Trigger once to set initial height
        textarea.dispatchEvent(new Event('input'));
    });
    
    // Document print button
    const printButton = document.getElementById('print-button');
    if (printButton) {
        printButton.addEventListener('click', function() {
            window.print();
        });
    }
    
    // Session data timeago formatting
    const timeElements = document.querySelectorAll('.timeago');
    if (timeElements.length > 0 && typeof timeago !== 'undefined') {
        timeago().render(timeElements);
    }
    
    // Document section navigation
    const tocLinks = document.querySelectorAll('.document-toc a');
    if (tocLinks.length > 0) {
        tocLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                
                const targetId = this.getAttribute('href');
                const targetElement = document.querySelector(targetId);
                
                window.scrollTo({
                    top: targetElement.offsetTop - 80,
                    behavior: 'smooth'
                });
            });
        });
    }
    
    // Tooltip initialization (if we add tooltips later)
    const tooltips = document.querySelectorAll('[data-tooltip]');
    if (tooltips.length > 0) {
        tooltips.forEach(tooltip => {
            tooltip.addEventListener('mouseenter', function() {
                const tooltipText = this.getAttribute('data-tooltip');
                const tooltipElement = document.createElement('div');
                tooltipElement.className = 'tooltip';
                tooltipElement.innerText = tooltipText;
                
                document.body.appendChild(tooltipElement);
                
                const rect = this.getBoundingClientRect();
                tooltipElement.style.top = `${rect.top - tooltipElement.offsetHeight - 10}px`;
                tooltipElement.style.left = `${rect.left + (rect.width / 2) - (tooltipElement.offsetWidth / 2)}px`;
                tooltipElement.style.opacity = '1';
            });
            
            tooltip.addEventListener('mouseleave', function() {
                const tooltipElement = document.querySelector('.tooltip');
                if (tooltipElement) {
                    tooltipElement.style.opacity = '0';
                    setTimeout(() => {
                        document.body.removeChild(tooltipElement);
                    }, 300);
                }
            });
        });
    }
});