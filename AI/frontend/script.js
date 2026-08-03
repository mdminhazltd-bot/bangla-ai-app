const API_URL = "https://bangla-ai-app-2ck2.onrender.com/...";

const chatBox = document.getElementById("chatBox");
const chatForm = document.getElementById("chatForm");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const typingIndicator = document.getElementById("typingIndicator");

function addMessage(text, sender) {
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${sender}-message`;

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = text;

    messageDiv.appendChild(bubble);
    chatBox.appendChild(messageDiv);

    chatBox.scrollTop = chatBox.scrollHeight;
}

chatForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    const question = userInput.value.trim();
    if (!question) return;

    addMessage(question, "user");
    userInput.value = "";
    sendBtn.disabled = true;
    typingIndicator.classList.remove("hidden");

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question: question })
        });

        const data = await response.json();

        if (response.ok) {
            addMessage(data.answer, "bot");
        } else {
            addMessage("দুঃখিত, একটা সমস্যা হয়েছে: " + (data.error || "অজানা ত্রুটি"), "bot");
        }
    } catch (err) {
        addMessage("সার্ভারের সাথে সংযোগ করা যাচ্ছে না। backend চালু আছে কিনা চেক করুন।", "bot");
    } finally {
        sendBtn.disabled = false;
        typingIndicator.classList.add("hidden");
        userInput.focus();
    }
});