document.addEventListener("DOMContentLoaded", function () {
    let timerDisplay = document.getElementById("timer");
    let totalTime = 3 * 60 * 60; // 3 hours in seconds

    function updateTimer() {
        let hours = Math.floor(totalTime / 3600);
        let minutes = Math.floor((totalTime % 3600) / 60);
        let seconds = totalTime % 60;
        timerDisplay.textContent = 
            `${hours}:${minutes < 10 ? '0' : ''}${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
        
        if (totalTime > 0) {
            totalTime--;
        } else {
            clearInterval(timerInterval);
            alert("Time's up! Test will be auto submitted.....");
        }
    }

    let timerInterval = setInterval(updateTimer, 1000);
});
