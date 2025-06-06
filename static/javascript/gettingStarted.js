const signIn = document.getElementById("signin");
const signUp = document.getElementById("signup");
const button = document.getElementById("btn");
const loginBtn = document.querySelector(".login");

const password = document.querySelectorAll(".password-input");
const passwordToggle = document.querySelectorAll(".password-toggle");
const passwordInput = document.getElementById("password");
const passwordIndicator = document.getElementById("password-indicator");
const strengthContainer = document.getElementById("strength-container");
const strengthPercent = document.getElementById("strength-percent");
const strengthBarInner = document.getElementById("strength-bar-inner");

const lengthCheck = document.getElementById("length-check");
const lowerCheck = document.getElementById("lower-check");
const upperCheck = document.getElementById("upper-check");
const numberCheck = document.getElementById("number-check");
const specialCharCheck = document.getElementById("specialchar-check");

const signinMessageIndicator = document.querySelector(".signin-message-indicator");
const signupMessageIndicator = document.querySelector(".signup-message-indicator");

const slideToSignIn = () => {
    signIn.style.left = "50px";
    signUp.style.left = "450px";
    button.style.left = "0";
    if (signinMessageIndicator) {
        signupMessageIndicator.style.display = "none";
    }
};

const slideToSignUp = () => {
    signIn.style.left = "-350px";
    signUp.style.left = "50px";
    button.style.left = "110px";
    if (signupMessageIndicator) {
        signinMessageIndicator.style.display = "none";
    }
};

const showPassword = (e) => {
    const toggle = e.target;
    const index = Array.from(passwordToggle).indexOf(toggle);

    password[index].type = toggle.checked ? "password" : "text";

    if (password[index].type === "password") {
        password[index].classList.remove("no-autofill");
    } else {
        password[index].classList.add("no-autofill");
    }
};

passwordToggle.forEach((toggle, index) => {
    toggle.addEventListener("change", showPassword);
});

passwordInput.addEventListener("focus", function () {
    passwordIndicator.style.display = "block";
    strengthContainer.style.display = "block";
});

passwordInput.addEventListener("blur", () => {
    passwordIndicator.style.display = "none";
    strengthContainer.style.display = "none";
});

const updateCheck = (element, isValid) => {
    if (isValid) {
        element.classList.remove("invalid");
        element.classList.add("valid");
    } else {
        element.classList.remove("valid");
        element.classList.add("invalid");
    }
};

const updatePasswordStrength = () => {
    const password = passwordInput.value;
    let strength = 0;

    const isLongEnough = /^.{8,32}$/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasUpperCase = /[A-Z]/.test(password);
    const hasNumber = /[0-9]/.test(password);
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);

    // Update the check marks
    updateCheck(lengthCheck, isLongEnough);
    updateCheck(lowerCheck, hasLowerCase);
    updateCheck(upperCheck, hasUpperCase);
    updateCheck(numberCheck, hasNumber);
    updateCheck(specialCharCheck, hasSpecialChar);

    // Calculate strength
    if (isLongEnough) strength += 25;
    if (hasNumber) strength += 25;
    if (hasLowerCase && hasUpperCase) strength += 25;
    if (hasSpecialChar) strength += 25;

    // Update the color of the text and strength bar based on strength
    strengthBarInner.style.width = `${strength}%`;
    strengthPercent.textContent = `${strength}%`;
    if (strength == 25) {
        strengthPercent.style.color = "#f39c12";
        strengthBarInner.style.backgroundColor = "#f39c12";
    } else if (strength == 50) {
        strengthPercent.style.color = "#f1c40f";
        strengthBarInner.style.backgroundColor = "#f1c40f";
    } else if (strength == 75) {
        strengthPercent.style.color = "#27ae60";
        strengthBarInner.style.backgroundColor = "#27ae60";
    } else if (strength == 100) {
        strengthPercent.style.color = "#008000";
        strengthBarInner.style.backgroundColor = "#008000";
    } else {
        strengthPercent.style.color = "#fefefe";
    }
};

const signInForm = document.getElementById("signin");
const signUpForm = document.getElementById("signup");
const navigationButton = document.querySelector(".button-group > #btn");
const emailInfo = document.querySelector(".email > .info-detail");
const usernameInfo = document.querySelector(".username > .info-detail");

const loginURL = signInForm.getAttribute("action");
const registerURL = signUpForm.getAttribute("action");
const csrfToken = signInForm.getAttribute("csrf-token");

const showNotification = (type, message) => {
    const notificationArea = document.getElementById("notificationArea");
    const errorIcon = document.querySelector(".error-icon").innerHTML;
    const infoIcon = document.querySelector(".info-icon").innerHTML;

    const notification = document.createElement("div");
    notification.id = "notification-box";
    notification.className = type;

    notification.innerHTML = `
        <div class="notification-content">
            ${type === "error" ? errorIcon : infoIcon}
            <div class="message">
                <p>${message}</p>
            </div>
        </div>
        <div class="timer"></div>
    `;

    notification.style.animation = "open 0.3s cubic-bezier(.47,.02,.44,2) forwards";

    notificationArea.appendChild(notification);

    const timer = notification.querySelector(".timer");
    timer.classList.add("timer-animation");

    let timeLeft = 5;

    const timerInterval = setInterval(() => {
        timeLeft--;

        if (timeLeft === 0) {
            clearInterval(timerInterval);

            notification.style.animation = "close 0.3s cubic-bezier(.47,.02,.44,2) forwards";

            setTimeout(() => {
                notification.remove();
            }, 300);
        }
    }, 1000);
};

const handleSession = (response) => {
    const sessionExpiry = new Date(response.session_expiry);
    localStorage.setItem("session_expiry", sessionExpiry);
};

const login = async (e) => {
    e.preventDefault();
    const loginEmail = signInForm.querySelector(".email-input").value;
    const loginPassword = signInForm.querySelector(".password-input").value;

    try {
        const loginCredentials = JSON.stringify({ loginEmail, loginPassword });

        const response = await fetch(loginURL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
            },
            body: loginCredentials,
        });

        if (!response.ok) {
            throw new Error("Network problem occurred");
        }

        const data = await response.json();
        if (!data.success) {
            showNotification("error", data.message);
            return;
        }
        window.location.href = data.redirect_url;
        localStorage.setItem("showModalAfterLogin", "true");
        handleSession(data);
    } catch (error) {
        console.error(`Login failed: ${error.message}`);
    }
};

const register = async (e) => {
    e.preventDefault();
    const signUpEmail = signUpForm.querySelector(".email-input").value;
    const signUpUsername = signUpForm.querySelector(".username-input").value;
    const signUpPassword = signUpForm.querySelector("input[name='password']").value;
    const confirmationPassword = signUpForm.querySelector("input[name='confirm-password']").value;

    try {
        const registerCredentials = JSON.stringify({
            signUpEmail,
            signUpUsername,
            signUpPassword,
            confirmationPassword,
        });

        const response = await fetch(registerURL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
            },
            body: registerCredentials,
        });

        if (!response.ok) {
            throw new Error("Network problem occurred");
        }

        const data = await response.json();
        if (!data.success) {
            showNotification("error", data.message[0]);
            setTimeout(() => {
                showNotification("error", data.message[1]);
            }, 1000);
            return;
        }
        window.location.href = data.redirect_url;
    } catch (error) {
        console.error(`Registration failed: ${error.message}`);
    }
};

signInForm.addEventListener("submit", login);
signUpForm.addEventListener("submit", register);

document.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
        const computedStyle = window.getComputedStyle(navigationButton);
        computedStyle.left === "0px" ? login(e) : register(e);
    }
});

const isInvalidLogin = localStorage.getItem("invalidLogin") === "true";
const notAuthenticated = localStorage.getItem("notAuthenticated") === "true";

const message = isInvalidLogin ? "Invalid login credentials" : "Oops! You're not logged in";

if (notAuthenticated) {
    showNotification("error", message);
    setTimeout(() => {
        showNotification("error", "Please log in to continue");
    }, 1000);
    localStorage.removeItem("notAuthenticated");
} else if (isInvalidLogin) {
    showNotification("error", message);
    localStorage.removeItem("invalidLogin");
}

const signupForm = document.getElementById("signup");
const signupPasswordInput = signupForm.querySelector("input[name='password']");
const signupConfirmPasswordInput = signupForm.querySelector("input[name='confirm-password']");

let debounceTimer;

const checkMatchedPassword = () => {
    const passwordChecker = document.querySelector(".password-checker");
    const spinner = document.getElementById("loadingSpinner");
    const resultMessage = document.querySelector("#resultMessage p");
    const matchedIcon = document.getElementById("matched");
    const unmatchedIcon = document.getElementById("unmatched");

    clearTimeout(debounceTimer);

    resultMessage.textContent = "Checking...";
    resultMessage.style.color = "";
    spinner.classList.remove("hidden");
    matchedIcon.classList.add("hidden");
    matchedIcon.classList.remove("show");
    unmatchedIcon.classList.add("hidden");
    unmatchedIcon.classList.remove("show");

    debounceTimer = setTimeout(() => {
        const signupPasswordValue = signupPasswordInput.value;
        const signupConfirmPasswordValue = signupConfirmPasswordInput.value;

        if (!signupPasswordValue || !signupConfirmPasswordValue) {
            passwordChecker.classList.add("hidden");
            return;
        }

        passwordChecker.classList.remove("hidden");

        setTimeout(() => {
            if (signupPasswordValue === signupConfirmPasswordValue) {
                matchedIcon.classList.remove("hidden");
                matchedIcon.classList.add("show");
                unmatchedIcon.classList.remove("show");
                unmatchedIcon.classList.add("hidden");
                spinner.classList.add("hidden");
                resultMessage.textContent = "Password matched!";
                resultMessage.style.color = "#2e8b57";
            } else {
                unmatchedIcon.classList.remove("hidden");
                unmatchedIcon.classList.add("show");
                matchedIcon.classList.remove("show");
                matchedIcon.classList.add("hidden");
                spinner.classList.add("hidden");
                resultMessage.textContent = "Password does not match!";
                resultMessage.style.color = "#ff4d4d";
            }

            setTimeout(() => {
                passwordChecker.classList.add("hidden");
            }, 1800);
        }, 1000);
    }, 800);
};

signupPasswordInput.addEventListener("input", checkMatchedPassword);
signupConfirmPasswordInput.addEventListener("input", checkMatchedPassword);

emailInfo.addEventListener("click", () => {
    const message = "Use valid email format<br />e.g. example@domain.com";
    showNotification("info", message);
});

usernameInfo.addEventListener("click", () => {
    const message = "Use 8-12 alphanumeric characters";
    showNotification("info", message);
});

passwordInput.addEventListener("input", updatePasswordStrength);

if (loginBtn) {
    loginBtn.addEventListener("click", () => {
        localStorage.setItem("showModalAfterLogin", "true");
    });
}
