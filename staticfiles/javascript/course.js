document.addEventListener("DOMContentLoaded", () => {
    const searchBar = document.getElementById("searchBar");
    const courseItems = document.querySelectorAll(".course-item");
    const overlayPopupAuthenticated = document.querySelector(".overlay-popup-authenticated");
    const overlayPopupWarning = document.querySelector(".overlay-popup-warning");
    const popupAfterAuth = document.querySelector(".popup-after-auth");
    const popupWarningCard = document.querySelector("div.show.popup-warning-card");
    const closeBtns = document.querySelectorAll(".close-btn");
    const showModalLogin = localStorage.getItem("showModalAfterLogin");
    const showModalSignup = localStorage.getItem("showModalAfterSignup");

    if (popupWarningCard) {
        document.body.style.overflow = "hidden";
        overlayPopupWarning.style.display = "block";
    }

    if (searchBar) {
        const filterCourses = () => {
            const searchTerm = searchBar.value.toLowerCase();

            courseItems.forEach((item) => {
                const courseName = item.getAttribute("data-course-name");
                if (courseName.includes(searchTerm)) {
                    item.style.display = "grid";
                } else {
                    item.style.display = "none";
                }
            });
        };
        searchBar.addEventListener("input", filterCourses);
    }

    const showPopup = () => {
        overlayPopupAuthenticated.style.display = "block";
        document.body.style.overflow = "hidden";
        setTimeout(() => {
            popupAfterAuth.style.top = "50%";
        }, 300);
    };

    if (showModalLogin === "true" || showModalSignup === "true") {
        showPopup();
        localStorage.removeItem(showModalLogin === "true" ? "showModalAfterLogin" : "showModalAfterSignup");
    }

    closeBtns.forEach((closeBtn) => {
        closeBtn.addEventListener("click", () => {
            setTimeout(() => {
                overlayPopupWarning.style.display = "none";
                overlayPopupAuthenticated.style.display = "none";
                document.body.style.overflow = "auto";
            }, 500);

            if (closeBtn.parentNode === popupWarningCard) {
                popupWarningCard.classList.remove("show");
                popupWarningCard.classList.add("closed");
                overlayPopupWarning.style.opacity = "0";
                overlayPopupWarning.style.transition = "opacity 500ms ease";
            } else {
                popupAfterAuth.style.top = "-50%";
                overlayPopupAuthenticated.style.opacity = 0;
                overlayPopupAuthenticated.style.transition = "opacity 500ms ease";
            }
        });
    });

    const enrollNotAuthenticated = document.getElementById("enroll-not-authenticated");


    if (!enrollNotAuthenticated) {
        throw new Error("This error occurs because some elements has changed. Dismiss this error");
    }

    enrollNotAuthenticated.addEventListener("submit", () => {
        localStorage.setItem("notAuthenticated", "true");
    });
});
