const checkSessionLocally = () => {
    const sessionExpiry = localStorage.getItem("session_expiry");
    if (sessionExpiry) {
        const expiryDate = new Date(sessionExpiry);
        const now = new Date();

        if (now >= expiryDate) {
            showSessionExpiredModal();
            clearSessionData(); 
        }
    }
}

const showSessionExpiredModal = () => {
    alert("Session expired. Please login again.");
    window.location.href = "/home/";
}

const clearSessionData = () => {
    localStorage.removeItem("session_expiry");
}

const CHECK_TIME = 5 * 60
setInterval(checkSessionLocally, CHECK_TIME * 1000); // Check every 5 minutes
