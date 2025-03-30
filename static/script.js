document.addEventListener("DOMContentLoaded", () => {
  const generateButton = document.getElementById("generate-briefing");
  const loadingElement = document.getElementById("loading");
  const briefingContent = document.getElementById("briefing-content");
  const briefingText = document.querySelector(".briefing-text");
  const briefingAudio = document.getElementById("briefing-audio");
  const errorMessage = document.getElementById("error-message");
  const placeholderText = document.getElementById("placeholder-text");
  const dateElement = document.getElementById("current-date");

  const updateDate = () => {
    dateElement.textContent = new Date().toLocaleDateString("en-US", {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  updateDate();
  setInterval(updateDate, 60000);

  generateButton.addEventListener("click", generateBriefing);

  async function generateBriefing() {
    loadingElement.classList.remove("hidden");
    briefingContent.classList.add("hidden");
    errorMessage.classList.add("hidden");
    placeholderText.classList.add("hidden");
    generateButton.disabled = true;

    try {
      const response = await fetch("/api/generate-briefing", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });

      const data = await response.json();

      if (data.success) {
        briefingText.innerHTML = data.text.replace(/\n/g, "<br>");

        if (data.audio_url) {
          briefingAudio.src = data.audio_url;
          briefingAudio.load();

          try {
            await briefingAudio.play();
          } catch (e) {
            console.log(
              "Auto-play prevented. User must interact with the page first."
            );
          }
        }

        briefingContent.classList.remove("hidden");
      } else {
        errorMessage.classList.remove("hidden");
        placeholderText.classList.remove("hidden");
        console.error("Error:", data.error);
      }
    } catch (error) {
      errorMessage.classList.remove("hidden");
      placeholderText.classList.remove("hidden");
      console.error("Error:", error);
    } finally {
      loadingElement.classList.add("hidden");
      generateButton.disabled = false;
    }
  }
});
