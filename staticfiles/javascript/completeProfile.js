const progress = document.getElementById("progress");
const formSteps = document.querySelectorAll(".form-step");
const nextButtons = document.querySelectorAll(".next");
const prevButton = document.querySelector(".prev");
const submitButton = document.querySelector(".submit");
const formNo = document.querySelector(".form-no h3");
const greetingText = document.querySelector(".greeting h1");
const subGreetingText = document.querySelector(".sub-greeting p");
const icons = document.querySelectorAll(".icon");

// Input fields
const nameInput = document.querySelectorAll("input[type='text']");
const dateInput = document.querySelector("input[type='date']");
const phoneInput = document.querySelector("input[type='tel']");
// Username from the backend
const username = document.querySelector("input[type='hidden']").value;

let currentStep = 0;
let selectedOptionValue = null;
let greetingAdded = false;
let isFormChanged = false;

window.addEventListener("load", () => {
    isFirstTimeLoad = true;
});

dateInput.addEventListener("input", (e) => {
    const value = dateInput.value;
    const year = value.split("-")[0];

    if (year.length > 4) {
        dateInput.value = value.slice(0, 10);
        console.warn("Year cannot be more than 4 digits.");
    }

    dateInput.style.color = dateInput.value ? "#fdf6f7" : "#b1b1b1";
});

dateInput.addEventListener("invalid", (e) => {
    e.preventDefault();
});

phoneInput.addEventListener("input", () => {
    let value = phoneInput.value.replace(/\D/g, "");

    if (value.length <= 2) {
        value = `${value}`;
    } else if (value.length <= 6) {
        value = `${value.slice(0, 2)}-${value.slice(2, 6)}`;
    } else if (value.length <= 10) {
        value = `${value.slice(0, 2)}-${value.slice(2, 6)}-${value.slice(6, 10)}`;
    } else if (value.length === 11) {
        value = `${value.slice(0, 3)}-${value.slice(3, 7)}-${value.slice(7, 11)}`;
    } else if (value.length === 12) {
        value = `${value.slice(0, 3)}-${value.slice(3, 6)}-${value.slice(6, 9)}-${value.slice(9)}`;
    } else {
        value = `${value.slice(0, 3)}-${value.slice(3, 7)}-${value.slice(7, 10)}-${value.slice(10)}`;
    }

    phoneInput.value = value;

    if (value.length > 16) {
        phoneInput.value = value.slice(0, 16);
    }
});

const validateNameInput = (name) => {
    const namePattern = /^[A-Za-z]+(?!\s$)(?:\s[A-Za-z]+)*$/;
    return namePattern.test(name);
};

const validateDateFormat = (dateInput) => {
    const datePattern = /^\d{4}-\d{2}-\d{2}$/;
    if (datePattern.test(dateInput)) {
        const [year, month, day] = dateInput.split("-");

        // Check if the year is between 1900 and the current year
        if (year < 1900 || year > new Date().getFullYear()) return false;
        // Check if the month is between 1 and 12
        if (month < 1 || month > 12) return false;

        // Get total days in given month
        // Ensure the day is between 1 and the total days in the month
        // So "2024-02-30" would be invalid, because February only has 29 days in a leap year
        const daysInMonth = new Date(year, month, 0).getDate();
        if (day < 1 || day > daysInMonth) return false;

        // Otherwise, if all checks pass, return true
        return true;
    }

    return false;
};

const validatePhoneNumber = (number) => {
    const phonePattern = /^(?!0)[1-9]{2,3}[-\s\.]?[0-9]{3,4}[-\s\.]?[0-9]{3,4}?([-\s\.][0-9]{3})?$/;
    return phonePattern.test(number) && number.length > 11;
};

const greetingTexts = [
    `Hey, ${username}! Great to have you here.`,
    "Thanks! Now, what should we call you?",
    "That's great! Next, what number can we contact you at?",
    "Awesome! What is interest you the most?",
    "Almost done! Finally, could you share your birth date with us?",
];

const subGreetingTexts = [
    "Let's get to know you a bit better, shall we? You can start by sharing your full name with us.",
    "This will help to greet you in the future.",
    "Could you let us know your gender? This will help us personalize your experience even more!",
    "No worries! It's just between you and us.",
    "This will help us provide resources tailored to your needs.",
    "We might have something special for you on your special day!",
];

const loadingMessages = [
    "Hang tight! We're connecting you to the database",
    "Data in transit! Please wait",
    "Ready in a few seconds! Saving your information.",
    "Your data is now in safe hands! Redirecting you to the homepage",
];

if (currentStep === 0) {
    greetingText.textContent = greetingTexts[currentStep];
    subGreetingText.textContent = subGreetingTexts[currentStep];
    formNo.textContent = currentStep + 1;
}

// Workflows
// 1. User clicks on the next button or press enter
// 2. Get the input on the current active form step
// 3. Validate the input
// 4. If the input is is not valid (empty or does not meet the validation criteria), show a warning message and next button is not clickable (pointer-events: none). While user is typing valid input, the warning message should disappear and next button is clickable again.
// 5. User clicks on the next button or press enter again then they will go to the next step

// Workflows for updating greeting text
// 1. User is on the nickname step
// 2. If user enter a valid nickname then press enter or click on the next button, greeting text "Nice to meet you, [nickname]!" will be added to the greeting text list at index 2
// 3. If user goes back to the nickname step and change the nickname, the greeting text will be updated accordingly

const resetPointerEvents = (enable, isLastStep = false) => {
    if (isLastStep) {
        submitButton.style.pointerEvents = enable ? "auto" : "none";
    } else {
        nextButtons.forEach((nextButton) => {
            nextButton.style.pointerEvents = enable ? "auto" : "none";
        });
    }
};

const validateInput = (step) => {
    const currentActiveForm = formSteps[step];
    const input = currentActiveForm.querySelector("input");
    const warningMessage = currentActiveForm.querySelector(".warning-message");
    const noDirectInput = !currentActiveForm.querySelector(".form-step > input");

    const isLastStep = step === formSteps.length - 1;

    if (!input.value && input.type !== "hidden") {
        warningMessage.textContent = "⚠ Please fill out this field correctly.";
        const isValid = false;

        isLastStep ? resetPointerEvents(isValid, isLastStep) : resetPointerEvents(isValid);

        return false;
    }

    if (input.type === "text") {
        const isValidName = validateNameInput(input.value);
        warningMessage.textContent = isValidName ? "" : "⚠ Please enter a valid name.";
        const isValid = isValidName && input.value ? true : false;
        resetPointerEvents(isValid);

        return isValidName;
    }

    if (noDirectInput) {
        const childElement = currentActiveForm.firstElementChild;

        if (childElement.classList.contains("card-container")) {
            const isGenderSelected = childElement.querySelector("input:checked");
            warningMessage.textContent = isGenderSelected ? "" : "⚠ Please select your gender";
            const isValid = isGenderSelected ? true : false;
            resetPointerEvents(isValid);

            return isGenderSelected;
        }

        if (childElement.classList.contains("custom-dropdown")) {
            warningMessage.textContent = selectedOptionValue ? "" : "⚠ Please select your interest.";
            const isValid = selectedOptionValue ? true : false;
            resetPointerEvents(isValid);

            return selectedOptionValue;
        }
    }

    if (input.type === "tel") {
        const isValidNumber = validatePhoneNumber(input.value);
        warningMessage.textContent = isValidNumber ? "" : "⚠ Please enter a number in the correct format.";
        const isValid = isValidNumber && input.value ? true : false;
        resetPointerEvents(isValid);

        return isValidNumber;
    }

    if (input.type === "date") {
        const isValidDate = validateDateFormat(input.value);
        warningMessage.textContent = isValidDate ? "" : "⚠ Please enter a valid date.";
        const isValid = isValidDate && input.value ? true : false;
        const isLastStep = step === formSteps.length - 1;

        resetPointerEvents(isValid, isLastStep);

        return isValidDate;
    }
};

// Workflow for validation selected option on dropdown
// 1. User clicks on the submit button or press enter
// 2. Check if the selected option is not null. If so, show a warning message and submit button is not clickable (pointer-events: none).
// 3. If user select an option, error message will disappear and submit button is clickable again.

const updateProgress = () => {
    const containerWidth = document.querySelector(".progress-bar").offsetWidth;
    const progressBarWidthPercentage = (currentStep / (formSteps.length - 1)) * 100;
    const widthInPx = (progressBarWidthPercentage / 100) * containerWidth;

    if (currentStep === formSteps.length - 1) {
        progress.style.width = `${progressBarWidthPercentage}%`;
    } else {
        const adjustedWidth = widthInPx - 8;
        const backToPercentage = (adjustedWidth / containerWidth) * 100;
        progress.style.width = `${adjustedWidth < 0 ? 0 : backToPercentage}%`;
    }
};

const toggleButtons = () => {
    if (currentStep === 0) {
        prevButton.style.pointerEvents = "none";
        icons[2].style.color = "#b1b1b1";
    } else if (currentStep === formSteps.length - 1) {
        nextButtons[0].style.display = "none";
        submitButton.style.display = "flex";
        icons[2].style.color = "#fdf6f7";
        prevButton.style.pointerEvents = "auto";
        icons[3].style.color = "#b1b1b1";
        nextButtons[1].style.pointerEvents = "none";
    } else {
        nextButtons[0].style.display = "flex";
        submitButton.style.display = "none";
        icons[2].style.color = "#fdf6f7";
        icons[3].style.color = "#fdf6f7";
        prevButton.style.pointerEvents = "auto";
    }
};

const goToNextStep = () => {
    formSteps[currentStep].classList.remove("active");

    currentStep++;

    formSteps[currentStep].classList.add("active");
    formNo.textContent = currentStep + 1;

    if (formSteps[currentStep - 1].querySelector("input[name='nickname']") && !greetingAdded) {
        const nickname = formSteps[currentStep - 1].querySelector("input[name='nickname']").value;
        greetingTexts.splice(2, 0, `Nice to meet you, ${nickname}!`);
        greetingAdded = true;
    }

    greetingText.textContent = greetingTexts[currentStep];
    subGreetingText.textContent = subGreetingTexts[currentStep];
    updateProgress();
    toggleButtons();
};

nextButtons.forEach((nextButton) => {
    nextButton.addEventListener("click", (e) => {
        const isInputValid = validateInput(currentStep);

        if (isInputValid) {
            if (currentStep === 0) {
                isFormChanged = true;
                isFirstTimeLoad = false;
            }
            currentStep < formSteps.length - 1 ? goToNextStep() : null;
        }
    });
});

prevButton.addEventListener("click", () => {
    if (currentStep === 0) {
        progress.style.width = "0px";
    }

    if (!validateInput(currentStep) || validateInput(currentStep)) {
        resetPointerEvents(true);
    }

    const inputs = formSteps[currentStep].querySelectorAll("input");

    inputs.forEach((input) => {
        const warningMessage = formSteps[currentStep].querySelector(".warning-message");
        if (!input.value) {
            warningMessage.textContent = "";
        }
    });

    formSteps[currentStep].classList.remove("active");

    if (formSteps[currentStep].querySelector(".card-container")) {
        greetingAdded = false;
        greetingTexts.splice(2, 1);
    }

    currentStep--;

    formNo.textContent = currentStep + 1;
    greetingText.textContent = greetingTexts[currentStep];
    subGreetingText.textContent = subGreetingTexts[currentStep];
    formSteps[currentStep].classList.add("active");
    updateProgress();
    toggleButtons();
});

toggleButtons();

const selected = document.querySelector(".selected");
const selectedOption = document.getElementById("selectedOption");
const optionsContainer = document.getElementById("options");

selectedOption.addEventListener("click", () => {
    optionsContainer.classList.toggle("show");
    if (!optionsContainer.classList.contains("show")) {
        selected.style.borderBottom = "2px solid #b1b1b1";
    } else {
        selected.style.borderBottom = "2px solid #4f9e86";
    }
});

const options = document.querySelectorAll(".option");

options.forEach((option) => {
    option.addEventListener("click", () => {
        const interestInput = document.getElementById("interestInput");
        interestInput.value = option.getAttribute("data-value");
        selectedOptionValue = option.textContent;
        selectedOption.querySelector("h3").textContent = option.textContent;
        selectedOption.style.color = "#fdf6f7";
        selectedOption.style.fontSize = "1.5rem";
        optionsContainer.classList.remove("show");
        selected.style.borderBottom = "2px solid #b1b1b1";
        selectedOption.querySelector(".icon").style.display = "block";

        const warningMessage = formSteps[currentStep].querySelector(".warning-message");
        warningMessage.textContent = "";
        resetPointerEvents(true);
    });
});

window.addEventListener("click", (event) => {
    if (!event.target.closest(".custom-dropdown")) {
        optionsContainer.classList.remove("show");
        selected.style.borderBottom = "2px solid #b1b1b1";
    }
});

formSteps.forEach((step, index) => {
    const inputs = step.querySelectorAll("input:not([type='hidden'])");

    inputs.forEach((input) => {
        if (input.type === "text" || input.type === "date" || input.type === "tel") {
            input.addEventListener("input", () => {
                validateInput(index);
            });
        }

        if (input.type === "radio") {
            input.addEventListener("change", () => {
                const isValidInput = validateInput(index);

                if (isValidInput) {
                    // Get selected gender card
                    const selectedGender = document.querySelector("input[name='gender']:checked");
                    const genderCard = selectedGender.parentElement;
                    genderCard.classList.add("blink");

                    setTimeout(() => {
                        goToNextStep();
                        genderCard.classList.remove("blink");
                    }, 2000);
                }
            });
        }
    });
});

const overlay = document.querySelector(".overlay");
const loader = document.querySelector(".loader");
const loadingText = document.querySelector(".loading-text");

const showLoader = () => {
    return new Promise((resolve) => {
        let messageCounter = 0;
        loadingText.textContent = loadingMessages[messageCounter];

        overlay.style.display = "block";
        loader.style.display = "flex";

        const loadingInterval = setInterval(() => {
            messageCounter++;
            if (messageCounter < loadingMessages.length) {
                loadingText.textContent = loadingMessages[messageCounter];
            } else {
                messageCounter = 0;
                clearInterval(loadingInterval);
                loader.style.display = "none";
                overlay.style.display = "none";
                resolve();
            }
        }, 1500);
    });
};

const form = document.getElementById("multiStepForm");

const submitFormData = async (e) => {
    e.preventDefault();

    const formData = new FormData(form);
    const submitUrl = form.getAttribute("action");
    const csrfToken = form.getAttribute("csrf-token");
    const method = form.getAttribute("method");
    const dataToBeSubmitted = Object.fromEntries(formData);

    try {
        await showLoader();
        const response = await fetch(submitUrl, {
            method: method,
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
            },
            body: JSON.stringify(dataToBeSubmitted),
        });

        if (!response.ok) {
            throw new Error("Failed to submit data into database.");
        }

        const data = await response.json();
        if (!data.success) {
            throw new Error("Error submitting user data.");
        }

        window.location.href = data.homepage_url;
    } catch (error) {
        console.error(error);
    } finally {
        // isRedirection = true;
        // isFormChanged = false;
        overlay.style.display = "none";
        loader.style.display = "none";
        localStorage.setItem("showModalAfterSignup", "true");
    }
};

form.addEventListener("submit", submitFormData);

document.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
        e.preventDefault();
        const isInputValid = validateInput(currentStep);

        if (isInputValid) {
            if (currentStep === 0) {
                isFormChanged = true;
            }
            currentStep === formSteps.length - 1 ? submitFormData(e) : goToNextStep();
        }
    }
});

submitButton.addEventListener("click", () => {
    const isInputValid = validateInput(currentStep);

    if (isInputValid) {
        submitFormData(e);
    }
});
