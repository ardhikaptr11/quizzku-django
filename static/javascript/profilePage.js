const phoneNumber = document.getElementById("phoneDisplay");
const phoneNumberCopy = phoneNumber.textContent;
const censoredPhoneNumber = phoneNumber.textContent.replace(/(\d{9})(\d{3})/, "$1***");
phoneNumber.textContent = censoredPhoneNumber;

const interest = document.getElementById("interest");
const acronym = interest.textContent;

const showNotification = (type, message) => {
    const notificationArea = document.getElementById("notificationArea");
    const notification = document.createElement("div");

    const errorIcon = document.querySelector(".error-icon").innerHTML;
    const successIcon = document.querySelector(".success-icon").innerHTML;

    notification.id = "notification-box";
    notification.className = type;

    notification.innerHTML = `
    <div class="notification-content">
    ${type === "error" ? errorIcon : successIcon}
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

const acronymToString = (acronym) => {
    const acronymMap = {
        IT: "Information Technology (IT)",
        EMP: "Engineering, Math, and Physics (EMP)",
        LNJ: "Law and Justice (LNJ)",
        HCS: "History and Cultural Studies (HCS)",
        SPE: "Sport and Physical Education (SPE)",
        SIS: "Social and International Studies (SIS)",
        HMB: "Health, Medicine, and Biological Sciences (HMB)",
        ENS: "Environmental Studies and Sustainability (ENS)",
    };

    return acronymMap[acronym];
};

interest.textContent = acronymToString(acronym);

if (window.location.pathname === "/home/account/profile/") {
    const subMenu = document.querySelector(".sub-menu");
    const dropdownInfo = subMenu.querySelector(".dropdown-info");
    const profileMenu = subMenu.querySelector("#profile");
    const logoutMenu = subMenu.querySelector("#logout");
    const divider = subMenu.querySelector("hr");

    divider.style.display = "none";
    dropdownInfo.style.display = "none";
    profileMenu.style.display = "none";
    logoutMenu.style.margin = "0";
}

const birthDate = document.getElementById("birth-date");
const dateJoined = document.getElementById("date-joined");

const formatDate = (date) => {
    const months = {};
    const fullMonths = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ];

    fullMonths.forEach((month, index) => {
        const shortMonth = month.substring(0, 3);
        const monthInNumber = (index + 1).toString().padStart(2, "0");
        months[shortMonth] = monthInNumber;
    });

    const dayMonth = date.textContent.split(",")[0];
    const year = date.textContent.split(",")[1].trim();

    if (date === birthDate) {
        let month, day;
        [month, day] = dayMonth.includes(".") ? dayMonth.split(". ") : dayMonth.split(" ");

        const daySuffix = (day) => {
            if (day > 3 && day < 21) return "th";
            switch (day % 10) {
                case 1:
                    return "st";
                case 2:
                    return "nd";
                case 3:
                    return "rd";
                default:
                    return "th";
            }
        };

        const fullMonth = fullMonths[months[month] - 1];
        const formattedDay = `${day}${daySuffix(day)}`;
        const formattedDate =
            month.length > 3 ? `${month} ${formattedDay}, ${year}` : `${fullMonth} ${formattedDay}, ${year}`;

        return formattedDate;
    }

    const monthInNumber = {
        Jan: "01",
        Feb: "02",
        Mar: "03",
        Apr: "04",
        May: "05",
        Jun: "06",
        Jul: "07",
        Aug: "08",
        Sep: "09",
        Oct: "10",
        Nov: "11",
        Dec: "12",
    };

    const [month, day] = dayMonth.split(". ");
    const formattedMonth = monthInNumber[month];

    const formattedDate = `${day}/${formattedMonth}/${year}`;
    return formattedDate;
};

dateJoined.textContent = formatDate(dateJoined);
birthDate.textContent = formatDate(birthDate);

const socialFieldWrapper = document.querySelector(".social-wrapper");
console.log(socialFieldWrapper);

const activateEditMode = (field) => {
    const editIcon = document.querySelector(`.info > #${field} ~ .edit-icon`);
    const inputElement = document.getElementById(field);
    const displayElement = document.getElementById(`${field}Display`);

    const linkElement = socialFieldWrapper ? socialFieldWrapper.querySelector(`#${field}Link`) : null;

    if (field === "social") {
        if (linkElement) {
            const linkData = linkElement.getAttribute("data-link");

            inputElement.value = linkData;
            socialFieldWrapper.style.display = "none";
            inputElement.style.display = "block";
            editIcon.style.pointerEvents = "none";

            inputElement.focus();
            return;
        }
    }

    if (field === "phone") {
        const uncensoredPhoneNumber = displayElement.textContent.replace(/\*/g, "");
        const lastThreeDigits = phoneNumberCopy.slice(-3);
        inputElement.value = `${uncensoredPhoneNumber}${lastThreeDigits}`;
    } else {
        inputElement.value = displayElement.textContent === "None" ? "" : displayElement.textContent;
    }

    inputElement.style.display = "block";
    displayElement.style.display = "none";
    editIcon.style.pointerEvents = "none";
    inputElement.focus();
};

const revealPhoneNumber = (display) => {
    const uncensoredPhoneNumber = display.textContent.replace(/\*/g, "");
    const lastThreeDigits = phoneNumberCopy.slice(-3);
    const fullPhoneNumber = `${phoneNumberCopy.slice(0, -3)}${lastThreeDigits}`;
    return fullPhoneNumber;
};

const checkSimilarity = (field) => {
    const inputElement = document.getElementById(field);
    const displayElement = document.getElementById(`${field}Display`);
    const linkElement = socialFieldWrapper ? socialFieldWrapper.querySelector(`#${field}Link`) : null;

    if (field === "address" || field === "profession") {
        if (inputElement.value === "" && displayElement.textContent === "None") {
            const isUnchanged = true;
            return isUnchanged;
        }
    }

    if (field === "social") {
        const linkData = socialFieldWrapper ? linkElement.getAttribute("data-link") : "";
        const isUnchanged = linkElement
            ? inputElement.value === linkData
            : inputElement.value === "" && displayElement.textContent === "None";
        return isUnchanged;
    }

    if (field === "phone") {
        displayElement.textContent = revealPhoneNumber(displayElement);
    }

    if (inputElement.value === displayElement.textContent) {
        const isUnchanged = true;
        return isUnchanged;
    }
};

const checkInputValue = (field) => {
    const inputElement = document.getElementById(field);
    const displayElement = document.getElementById(`${field}Display`);

    const linkElement = socialFieldWrapper ? socialFieldWrapper.querySelector(`#${field}Link`) : null;

    if (inputElement.value === "") {
        return true;
    }
    return false;
};

const resetInputState = (element) => {
    element.classList.contains("invalid") ? element.classList.remove("invalid") : element.classList.remove("valid");
};

const disableEditMode = (field) => {
    const inputElement = document.getElementById(field);
    const editIcon = document.querySelector(`.info > #${field} ~ .edit-icon`);

    if (field === "social") {
        const linkElement = socialFieldWrapper ? socialFieldWrapper.querySelector(`#${field}Link`) : null;

        if (linkElement) {
            socialFieldWrapper.style.display = "block";
            inputElement.style.display = "none";
            editIcon.style.pointerEvents = "auto";
            return;
        } else {
            const displayElement = document.getElementById(`${field}Display`);
            displayElement.style.display = "block";
            inputElement.style.display = "none";
            editIcon.style.pointerEvents = "auto";
            displayElement.textContent = "None";
            return;
        }
    }

    const displayElement = document.getElementById(`${field}Display`);

    if (field === "phone") {
        const censoredPhoneNumber = displayElement.textContent.replace(/(\d{9})(\d{3})/, "$1***");
        displayElement.textContent = censoredPhoneNumber;
    }

    inputElement.style.display = "none";
    displayElement.style.display = "block";
    editIcon.style.pointerEvents = "auto";
    resetInputState(inputElement);
};

const acceptedSocialPlatform = ["instagram.com", "linkedin.com", "facebook.com", "x.com", "github.com"];

const validateInput = (field) => {
    const inputElement = document.getElementById(field);

    if (field === "email") {
        const emailPattern = /^[\w\-\.]+@(?:[\w-]+\.)+[\w-]{2,3}$/;
        const isValidEmail = emailPattern.test(inputElement.value);
        return isValidEmail;
    }

    if (field === "phone") {
        const phonePattern = /^0+[0-9]{10,12}$/;
        const isValidPhone = phonePattern.test(inputElement.value);
        return isValidPhone;
    }

    if (field === "social") {
        const linkPattern =
            /^(?:https:\/\/)?(?:www\.)?(?:(?:instagram|x|facebook|github)\.com\/|linkedin\.com\/(?:in\/))[a-zA-Z0-9._]+\/?$/;

        const isLinkValid = linkPattern.test(inputElement.value);
        return inputElement.value === "" ? true : isLinkValid;
    }
};

const profileImage = document.querySelector("#profile-container .profile-image");
const staticLocation = "/static/media/course_images";

const userGender = profileImage.getAttribute("data-gender");

let defaultPhotoProfile;
if (userGender === "Male") {
    defaultPhotoProfile = `${staticLocation}/male-default-profile.jpg`;
} else {
    defaultPhotoProfile = `${staticLocation}/female-default-profile.jpg`;
}

const editNickname = document.querySelector(".info > #nickname ~ .edit-icon");
const editEmail = document.querySelector(".info > #email ~ .edit-icon");
const editPhone = document.querySelector(".info > #phone ~ .edit-icon");
const editAddress = document.querySelector(".info > #address ~ .edit-icon");
const editProfession = document.querySelector(".info > #profession ~ .edit-icon");
const editInstitution = document.querySelector(".info > #institution ~ .edit-icon");
const editSocial = document.querySelector(".info > #social ~ .edit-icon");

const nicknameInput = document.getElementById("nickname");
const emailInput = document.getElementById("email");
const phoneInput = document.getElementById("phone");
const addressInput = document.getElementById("address");
const professionInput = document.getElementById("profession");
const institutionInput = document.getElementById("institution");
const socialInput = document.getElementById("social");
const imageInput = document.getElementById("input-image");

const imageRemoverButton = document.querySelector(".cta-buttons > button:nth-child(2)");
const updateImageButton = document.querySelector(".cta-buttons > button:nth-child(1)");
const saveButton = document.querySelector(".save-btn > button");

const formDataObject = {};

const dataToBeUpdated = new FormData();
const inputsInvalid = {};

["imageFile", "nickname", "email", "phone", "address", "profession", "institution", "social"].forEach((field) => {
    dataToBeUpdated.set(field, "");
});

const isInputInvalid = (field) => {
    const input = document.getElementById(field);
    inputsInvalid[field] = input.classList.contains("invalid");
};

const updateSaveButtonState = (field) => {
    if (field === "onload") {
        saveButton.disabled = true;
        saveButton.style.cursor = "not-allowed";
        saveButton.classList.add("disabled");
        return;
    }

    isInputInvalid(field);

    const inputElement = document.getElementById(field);
    const [displayElement, linkElement] = [`${field}Display`, `${field}Link`].map((element) =>
        document.getElementById(element)
    );

    const isSameValue = [displayElement, linkElement].some((element) => {
        if (element) {
            return field === "phone"
                ? inputElement.value === revealPhoneNumber(element)
                : inputElement.value === element.textContent;
        }
        return false;
    });

    if (isSameValue) {
        delete inputsInvalid[field];
    }

    const isDefaultImage = dataToBeUpdated.get("imageFile") === defaultPhotoProfile;
    const inputsInvalidLength = Object.keys(inputsInvalid).length;
    
    // !BUG: NEED MORE ADJUSTMENT
    const noChanges = [...dataToBeUpdated.values()].every(
        (value) => value === "" || (value === defaultPhotoProfile && removeButtonClicked > 0 && isUpdateButtonClicked)
    );

    if (noChanges || Object.values(inputsInvalid).includes(true)) {
        saveButton.disabled = true;
        saveButton.style.cursor = "not-allowed";
        saveButton.classList.add("disabled");
    } else {
        saveButton.disabled = false;
        saveButton.style.cursor = "pointer";
        saveButton.classList.remove("disabled");
    }
};

let currentObjectURL;

if (!profileImage.src.includes(staticLocation)) {
    imageRemoverButton.style.pointerEvents = "auto";
} else {
    imageRemoverButton.style.pointerEvents = "none";
}
updateImageButton.style.pointerEvents = "none";

imageInput.addEventListener("change", (e) => {
    const file = e.target.files[0];

    if (!file) {
        return;
    }

    profileImage.style.opacity = 0;

    if (dataToBeUpdated.has("imageFile") && dataToBeUpdated.get("imageFile") !== "") {
        dataToBeUpdated.set("imageFile", "");
    }

    setTimeout(() => {
        // Delete the previous URL if it exists
        if (currentObjectURL) {
            URL.revokeObjectURL(currentObjectURL);
        }

        currentObjectURL = URL.createObjectURL(file);
        profileImage.src = currentObjectURL;

        profileImage.addEventListener("load", () => {
            profileImage.style.opacity = 1;
        });
    }, 500);

    updateImageButton.style.pointerEvents = "auto";
    imageRemoverButton.style.pointerEvents = "auto";
});

let removeButtonClicked = 0;
let isUpdateButtonClicked = false;

updateImageButton.addEventListener("click", () => {
    isUpdateButtonClicked = true;
    const field = updateImageButton.parentElement.previousElementSibling.querySelector("input").id;
    const imageFile = imageInput.files[0];

    dataToBeUpdated.set("imageFile", imageFile);
    updateImageButton.style.pointerEvents = "none";
    updateImageButton.textContent = "Updated";
    updateSaveButtonState(field);
});

imageRemoverButton.addEventListener("click", () => {
    const field = updateImageButton.parentElement.previousElementSibling.querySelector("input").id;
    dataToBeUpdated.set("imageFile", defaultPhotoProfile);
    removeButtonClicked++;

    // This is executed when the user already pressed "Update" button
    if (typeof dataToBeUpdated.get("imageFile") === "object") {
        dataToBeUpdated.set("imageFile", defaultPhotoProfile);
        removeButtonClicked++;
    }

    profileImage.style.opacity = 0;

    setTimeout(() => {
        profileImage.src = defaultPhotoProfile;
        profileImage.addEventListener("load", () => {
            profileImage.style.opacity = 1;
        });
    }, 500);

    imageInput.value = "";

    updateImageButton.style.pointerEvents = "none";
    updateImageButton.textContent = "Update";
    imageRemoverButton.style.pointerEvents = "none";
    updateSaveButtonState(field);
});

for (const edit of [editNickname, editEmail, editPhone, editAddress, editProfession, editInstitution, editSocial]) {
    edit.addEventListener("click", () => {
        const inputId = edit.previousElementSibling.id;
        activateEditMode(inputId);
    });
}

for (const input of [
    nicknameInput,
    emailInput,
    addressInput,
    phoneInput,
    professionInput,
    institutionInput,
    socialInput,
]) {
    if (input === phoneInput) {
        input.addEventListener("input", () => {
            const value = input.value;

            if (value.match(/\D/)) {
                input.value = input.value.slice(0, -1);
            } else if (value.length > 13) {
                input.value = input.value.slice(0, 13);
            }
        });
    }

    input.addEventListener("blur", () => {
        const field = input.id;
        const fieldName = field.charAt(0).toUpperCase() + field.slice(1);

        const isSimilar = checkSimilarity(field);
        const isInputEmpty = checkInputValue(field);
        const message = field === "social" ? "Social link cannot be empty" : `${fieldName} cannot be empty`;

        if (isSimilar) {
            dataToBeUpdated.set(field, "");
            disableEditMode(field);
            updateSaveButtonState(field);
            return;
        }

        if (field === "email" || field === "phone" || field === "social") {
            const validationResults = {};

            validationResults[`isValid${fieldName}`] = validateInput(field);

            if (!validationResults[`isValid${fieldName}`]) {
                const message = isInputEmpty
                    ? `${fieldName} cannot be empty`
                    : `Invalid ${fieldName.toLowerCase()} format`;
                input.classList.remove("valid");
                input.classList.add("invalid");
                dataToBeUpdated.set(field, "");

                const isLinkAccepted = acceptedSocialPlatform.some((platform) => input.value.includes(platform));
                field !== "social"
                    ? showNotification("error", message)
                    : showNotification("error", !isLinkAccepted ? "Platform not recognized" : "Invalid social link");

                updateSaveButtonState(field);

                return;
            }
        }

        if (!isInputEmpty) {
            input.classList.remove("invalid");
            input.classList.add("valid");
            dataToBeUpdated.set(field, input.value);
        } else {
            input.classList.remove("valid");
            input.classList.add("invalid");
            dataToBeUpdated.set(field, "");
            showNotification("error", message);
        }

        updateSaveButtonState(field);
    });
}

// If there's one invalid input (showed by an empty string in dataToBeUpdated) or there is no changes at all (showed by an empty string for all data in dataToBeUpdated), button should be disabled

const linkElement = document.getElementById("socialLink");

if (linkElement) {
    linkElement.href = linkElement.getAttribute("data-link").includes("https://")
        ? linkElement.getAttribute("data-link")
        : `https://${linkElement.getAttribute("data-link")}`;
}

const setProfileCompletion = (percentage) => {
    const progressCircle = document.querySelector("#profile-content .progress-ring-fill");

    const radius = progressCircle.r.baseVal.value;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (percentage / 100) * circumference;

    progressCircle.style.strokeDasharray = `${circumference} ${circumference}`;
    progressCircle.style.strokeDashoffset = circumference;

    setTimeout(() => {
        progressCircle.style.transition = "stroke-dashoffset 1s ease";
        progressCircle.style.strokeDashoffset = offset;
    }, 50);
};

const profileHeader = document.getElementById("profile-header");
const updateProfileUrl = profileHeader.getAttribute("data-url");
const dataCsrf = profileHeader.getAttribute("csrf-token");
const progress = parseInt(profileHeader.getAttribute("data-progress"));

const overlay = document.querySelector(".overlay");
const waveBackground = document.querySelector(".wave-background");
const wave = document.querySelector(".wave");
const progressStatus = document.querySelector(".progress-status");
const percentText = document.getElementById("percent-text");

const animateUp = async () => {
    let percentage = 0;

    const animationDuration = 2000;
    const intervalDuration = animationDuration / progress;

    percentText.innerHTML = "0%";

    waveBackground.style.transition = "opacity 0.5s ease";
    progressStatus.style.transition = "opacity 0.5s ease";
    progressStatus.style.opacity = 1;
    waveBackground.style.opacity = 1;

    return new Promise((resolve) => {
        wave.style.transition = `top ${animationDuration}ms linear`;
        wave.style.top = `${110 - progress * 1.1}%`;

        const interval = setInterval(() => {
            if (percentage < progress) {
                percentage += 1;
                percentText.innerHTML = `${percentage}%`;
            } else {
                clearInterval(interval);
                resolve();
            }
        }, intervalDuration);
    });
};

const animateDown = async () => {
    let percentage = progress;

    const animationDuration = 2000;
    const intervalDuration = animationDuration / progress;

    return new Promise((resolve) => {
        wave.style.transition = `top ${animationDuration}ms linear`;
        wave.style.top = "110%";

        const interval = setInterval(() => {
            if (percentage > 0) {
                percentage -= 1;
                percentText.innerHTML = `${percentage}%`;
            } else {
                clearInterval(interval);
                setTimeout(() => {
                    progressStatus.style.opacity = 0;
                    waveBackground.style.opacity = 0;
                    resolve();
                }, 50);
            }
        }, intervalDuration);
    });
};

// 1. When mouse enters the overlay, the animation up should be triggered.
//    if the mouse leaves when the animation is completely done, the animation down should be triggered.
// 2. If the mouse enters the overlay and leaves quickly before the animation up is done,
//    wait until the animation up is done then automatically trigger the animation down.
// 3. If the mouse enters the overlay and leaves quickly then enter overlay again before the animation up is done,
//    the animation up should continues until it's done. When the mouse leaves, it should behave as scenario 1.
// 4. If the mouse enters the overlay when the animation down is running, the animation down should
//    continue until it's done. Then  automatically trigger the animation up again.
// The process should be smooth and seamless.

let progressTimeout;
let isAnimatingUp = false;
let isAnimatingDown = false;
let isMouseInside = false;

const TIME = 50;

let animationAtFirstLoad;

document.addEventListener("DOMContentLoaded", async () => {
    updateSaveButtonState("onload");

    clearTimeout(animationAtFirstLoad);
    animationAtFirstLoad = setTimeout(async () => {
        isMouseInside = false;
        clearTimeout(progressTimeout);

        overlay.style.cursor = "default";

        if (!isAnimatingUp && !isAnimatingDown) {
            isAnimatingUp = true;
            await animateUp();
            isAnimatingUp = false;

            if (!isMouseInside) {
                progressTimeout = setTimeout(async () => {
                    isAnimatingDown = true;
                    await animateDown();
                    isAnimatingDown = false;
                }, 2000);
            }
        }
    }, 1000);
});

overlay.addEventListener("mouseenter", async () => {
    isMouseInside = true;
    clearTimeout(progressTimeout);

    if (isAnimatingDown) {
        const forAnimationDown = new Promise((resolve) => {
            const animationInterval = setInterval(() => {
                if (!isAnimatingDown) {
                    clearInterval(animationInterval);
                    resolve();
                }
            }, TIME);
        });

        await forAnimationDown;
    }

    if (!isAnimatingUp) {
        isAnimatingUp = true;

        await animateUp();

        isAnimatingUp = false;
        overlay.style.cursor = "default";

        if (!isMouseInside) {
            progressTimeout = setTimeout(async () => {
                isAnimatingDown = true;
                await animateDown();
                isAnimatingDown = false;
            }, TIME);
        }
    }
});

overlay.addEventListener("mouseleave", async () => {
    isMouseInside = false;

    if (isAnimatingUp) {
        return;
    }

    progressTimeout = setTimeout(async () => {
        if (!isMouseInside && !isAnimatingDown) {
            isAnimatingDown = true;
            await animateDown();
            isAnimatingDown = false;
        }
    }, TIME);
});

// const updatingMessage = [
//     "Connecting to the database",
//     "Retrieving your data"
//     "Data retrieved! Validating your data"
// ]

// saveButton.addEventListener("click", (e) => {
//     e.preventDefault();

//     for (const [key, value] of dataToBeUpdated.entries()) {
//         formDataObject[key] = value;
//     }
//     console.log(formDataObject);

//     // const formDataEntries = [...dataToBeUpdated.entries()].map(([key, value]) => `${key}: ${value}`).join("\n");

//     // alert(formDataObject);
// });

const loader = document.querySelector(".loader-container");
let loaderTimeout;

const showLoader = () => {
    return new Promise((resolve) => {
        loader.style.opacity = 1;

        clearTimeout(loaderTimeout);

        loaderTimeout = setTimeout(() => {
            loader.style.opacity = 0;
            resolve();
        }, 3000);
    });
};

const hideLoader = () => {
    loader.style.opacity = 0;
    clearTimeout(loaderTimeout);
};

let reloadTimeout;

const updateProfile = async (e) => {
    e.preventDefault();

    const editInputs = document.querySelectorAll(".edit-input");

    for (const input of editInputs) {
        if (input.classList.contains("invalid")) {
            showNotification("error", "Empty field cannot be accepted");
            return;
        }
    }

    try {
        await showLoader();
        const response = await fetch(updateProfileUrl, {
            method: "POST",
            headers: {
                "X-CSRFToken": dataCsrf,
            },
            body: dataToBeUpdated,
        });

        if (!response.ok) {
            throw new Error("Failed to update profile. Please try again later.");
        }

        const responseData = await response.json();

        if (!responseData.success) {
            throw new Error(responseData.message);
        }

        hideLoader();
        clearTimeout(reloadTimeout);
        showNotification("success", "Profile updated successfully");

        reloadTimeout = setTimeout(() => {
            window.location.reload();
        }, 5000);
    } catch (error) {
        hideLoader();
        showNotification("error", error.message);
    }
};

saveButton.addEventListener("click", updateProfile);

// saveButton.addEventListener("click", (e) => {
//     e.preventDefault();

//     for (const [key, value] of dataToBeUpdated.entries()) {
//         formDataObject[key] = value;
//     }
//     console.log(formDataObject);
// });

setProfileCompletion(progress);
