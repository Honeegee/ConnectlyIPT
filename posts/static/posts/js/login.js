function showForm(formType) {
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');
    const tabs = document.querySelectorAll('.tab');

    if (formType === 'login') {
        loginForm.style.display = 'block';
        signupForm.style.display = 'none';
        tabs[0].classList.add('active');
        tabs[1].classList.remove('active');
    } else {
        loginForm.style.display = 'none';
        signupForm.style.display = 'block';
        tabs[0].classList.remove('active');
        tabs[1].classList.add('active');
    }
}

// Password requirements validation
document.addEventListener('DOMContentLoaded', function() {
    const passwordInput = document.getElementById('signup-password');
    const requirements = document.querySelector('.password-requirements');
    const lengthReq = document.getElementById('length');
    const upperReq = document.getElementById('uppercase');
    const lowerReq = document.getElementById('lowercase');
    const numberReq = document.getElementById('number');
    const specialReq = document.getElementById('special');

    if (passwordInput) {
        passwordInput.addEventListener('focus', function() {
            requirements.classList.add('show');
        });

        passwordInput.addEventListener('input', function() {
            const password = this.value;
            
            // Validate length
            if(password.length >= 8) {
                lengthReq.classList.add('valid');
                lengthReq.classList.remove('invalid');
            } else {
                lengthReq.classList.add('invalid');
                lengthReq.classList.remove('valid');
            }
            
            // Validate uppercase
            if(/[A-Z]/.test(password)) {
                upperReq.classList.add('valid');
                upperReq.classList.remove('invalid');
            } else {
                upperReq.classList.add('invalid');
                upperReq.classList.remove('valid');
            }
            
            // Validate lowercase
            if(/[a-z]/.test(password)) {
                lowerReq.classList.add('valid');
                lowerReq.classList.remove('invalid');
            } else {
                lowerReq.classList.add('invalid');
                lowerReq.classList.remove('valid');
            }
            
            // Validate number
            if(/[0-9]/.test(password)) {
                numberReq.classList.add('valid');
                numberReq.classList.remove('invalid');
            } else {
                numberReq.classList.add('invalid');
                numberReq.classList.remove('valid');
            }
            
            // Validate special character
            if(/[^A-Za-z0-9]/.test(password)) {
                specialReq.classList.add('valid');
                specialReq.classList.remove('invalid');
            } else {
                specialReq.classList.add('invalid');
                specialReq.classList.remove('valid');
            }
        });
    }

    // Form validation
    const signupForm = document.getElementById('signup-form');
    if (signupForm) {
        signupForm.addEventListener('submit', function(event) {
            const username = document.getElementById('signup-username').value;
            const password = document.getElementById('signup-password').value;
            const confirmPassword = document.getElementById('signup-confirm-password').value;
            let isValid = true;
            let errorMessage = '';

            // Validate username length
            if (username.length < 3) {
                errorMessage += 'Username must be at least 3 characters long.\n';
                isValid = false;
            }

            // Validate password requirements
            if (password.length < 8) {
                errorMessage += 'Password must be at least 8 characters long.\n';
                isValid = false;
            }
            if (!/[A-Z]/.test(password)) {
                errorMessage += 'Password must contain at least one uppercase letter.\n';
                isValid = false;
            }
            if (!/[a-z]/.test(password)) {
                errorMessage += 'Password must contain at least one lowercase letter.\n';
                isValid = false;
            }
            if (!/[0-9]/.test(password)) {
                errorMessage += 'Password must contain at least one number.\n';
                isValid = false;
            }
            if (!/[^A-Za-z0-9]/.test(password)) {
                errorMessage += 'Password must contain at least one special character.\n';
                isValid = false;
            }

            // Check if passwords match
            if (password !== confirmPassword) {
                errorMessage += 'Passwords do not match!\n';
                isValid = false;
            }

            if (!isValid) {
                event.preventDefault();
                alert(errorMessage);
            }
        });
    }
});
