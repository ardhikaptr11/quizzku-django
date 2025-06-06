const passwordInput = document.querySelector(".password-input");
const passwordToggle = document.querySelector(".password-toggle");
const buttons = document.querySelectorAll(".button");
const loginBtn = document.querySelector(".input-group button");
const hamburgerIcon = document.querySelector(".hamburger-icon");
const icon1 = document.getElementById("a");
const icon2 = document.getElementById("b");
const icon3 = document.getElementById("c");
const menuItems = document.querySelector(".menu-items");

const profileImageNavbar = document.querySelector(".profile-image");
const subMenu = document.getElementById("sub-menu");

if (profileImageNavbar) {
    profileImageNavbar.addEventListener("click", () => {
        subMenu.classList.toggle("active");
    });
}

const navbar = document.querySelector(".navbar");
const progressCircleNavbar = navbar.querySelector(".progress-ring-fill");

const setProfileCompletionNavbar = (percentage) => {
    const radius = progressCircleNavbar.r.baseVal.value;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (percentage / 100) * circumference;

    progressCircleNavbar.style.strokeDasharray = `${circumference} ${circumference}`;
    progressCircleNavbar.style.strokeDashoffset = circumference;

    setTimeout(() => {
        progressCircleNavbar.style.transition = "stroke-dashoffset 1s ease";
        progressCircleNavbar.style.strokeDashoffset = offset;
    }, 50);
};


if (progressCircleNavbar) {
    const progressNavbar = navbar.getAttribute("data-progress");
    setProfileCompletionNavbar(progressNavbar);
}

document.addEventListener("click", (e) => {
    if (subMenu) {
        if (subMenu.classList.contains("active") && e.target !== profileImageNavbar) {
            subMenu.classList.remove("active");
        }
    }
});

const showPassword = (e) => {
    const toggle = e.target;
    passwordInput.type = toggle.checked ? "password" : "text";

    if (passwordInput.type === "password") {
        passwordInput.classList.remove("no-autofill");
    } else {
        passwordInput.classList.add("no-autofill");
    }
};

if (passwordToggle) {
    passwordToggle.addEventListener("change", showPassword);
}

menuItems.style.maxHeight = "0px";

hamburgerIcon.addEventListener("click", function () {
    icon1.classList.toggle("a");
    icon2.classList.toggle("c");
    icon3.classList.toggle("b");

    if (menuItems.style.maxHeight == "0px") {
        menuItems.style.maxHeight = "200px";
        menuItems.style.padding = "30px 0";
    } else {
        menuItems.style.maxHeight = "0px";
        menuItems.style.padding = "0";
    }
});

buttons.forEach(function (button) {
    button.addEventListener("mouseenter", function (e) {
        const parentOffset = button.getBoundingClientRect(),
            relX = e.pageX - parentOffset.left,
            relY = e.pageY - parentOffset.top;
        const span = button.querySelector("span");
        if (span) {
            span.style.top = relY + "px";
            span.style.left = relX + "px";
        }
    });

    button.addEventListener("mouseout", function (e) {
        const parentOffset = button.getBoundingClientRect(),
            relX = e.pageX - parentOffset.left,
            relY = e.pageY - parentOffset.top;
        const span = button.querySelector("span");
        if (span) {
            span.style.top = relY + "px";
            span.style.left = relX + "px";
        }
    });
});

const loginForm = document.querySelector(".login");

if (!loginForm) {
    throw new Error("Navbar changed, login form not found. Dismiss this error");
}

const csrfToken = loginForm.getAttribute("csrf-token");
const loginUrl = loginForm.getAttribute("action");
const gettingStartedUrl = document.querySelector(".register").getAttribute("action");

const login = async (e) => {
    e.preventDefault();

    const loginEmail = loginForm.querySelector(".email-input").value;
    const loginPassword = loginForm.querySelector(".password-input").value;

    try {
        const loginCredentials = JSON.stringify({ loginEmail, loginPassword });

        const response = await fetch(loginUrl, {
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
            window.location.href = gettingStartedUrl;
            localStorage.setItem("invalidLogin", "true");
            return;
        }
        window.location.href = data.redirect_url;
        localStorage.setItem("showModalAfterLogin", "true");
    } catch (error) {
        console.error(`Login failed: ${error}`);
    }
};

loginForm.addEventListener("submit", login);