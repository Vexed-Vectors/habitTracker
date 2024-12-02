document.addEventListener('DOMContentLoaded', () => {
    const signupForm = document.getElementById('signup-form');
    const errorMessages = {
        email: document.getElementById('email-error'),
        password: document.getElementById('password-error'),
        confirmPassword: document.getElementById('confirm-password-error')
    };

    signupForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Reset previous error messages
        Object.values(errorMessages).forEach(el => {
            if (el) el.textContent = '';
        });
        
        // Get form values
        const email = document.querySelector('input[name="email"]').value;
        const password = document.querySelector('input[name="password"]').value;
        const confirmPassword = document.querySelector('input[name="confirm_password"]').value;
        
        try {
            const response = await fetch("/signup/api/", {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),
              },
              body: JSON.stringify({
                email,
                password,
                confirm_password: confirmPassword,
              }),
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Successful signup - redirect to dashboard or login
                window.location.href = "/dashboard";
            } else {
                // Handle validation errors
                const errors = data.errors || {};
                
                if (errors.email) {
                    if (errorMessages.email) 
                        errorMessages.email.textContent = errors.email;
                }
                if (errors.password) {
                    if (errorMessages.password)
                        errorMessages.password.textContent = errors.password;
                }
                if (errors.confirm_password) {
                    if (errorMessages.confirmPassword)
                        errorMessages.confirmPassword.textContent = errors.confirm_password;
                }
            }
        } catch (error) {
            console.error('Signup error:', error);
            // Optional: show a generic error message
        }
    });
});

// CSRF Token retrieval function
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}