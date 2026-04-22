const panicBtn = document.getElementById("panicButton");
const audio = document.getElementById("alertSound");

function playSound() {
    if (!audio) return;
    audio.loop = true;
    audio.play().catch(() => {});
}

function stopSound() {
    if (!audio) return;
    audio.pause();
    audio.currentTime = 0;
}

function showToast(msg) {
    alert(msg); // simple for now
}

if (panicBtn) {
    panicBtn.addEventListener("click", () => {

        panicBtn.innerText = "SENDING...";
        panicBtn.disabled = true;

        playSound();

        if (!navigator.geolocation) {
            sendSOS(28.6139, 77.2090);
            return;
        }

        navigator.geolocation.getCurrentPosition(

            pos => {
                sendSOS(pos.coords.latitude, pos.coords.longitude);
            },

            () => {
                showToast("GPS blocked, using fallback");
                sendSOS(28.6139, 77.2090);
            }
        );
    });
}

function sendSOS(lat, lng) {

    fetch("/sos", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ lat, lng })
    })
    .then(res => res.json())
    .then(() => {
        showToast("SOS Sent!");
    })
    .catch(() => {
        showToast("Server Error");
    })
    .finally(() => {
        panicBtn.innerText = "SOS";
        panicBtn.disabled = false;
        stopSound();
    });
}