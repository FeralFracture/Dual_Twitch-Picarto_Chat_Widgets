const socket = io();
const chatContainer = document.getElementById("chat-container");
const maxMessages = 19;
const messageLifetime = 20000;

socket.on("Twitch_chat_message", (msg) => {
  const html = `${msg.badge_html}<span style="color:${msg.color}">${msg.display_name}:</span> ${msg.text}`;
  addChatMessage(html);
});

socket.on("delete_Twitch_message", (data) => {
  // Remove by message ID if tracked
  const messages = chatContainer.querySelectorAll(".message");
  messages.forEach(msg => {
    if (msg.dataset.msgId === data.id || msg.dataset.username === data.user) {
      removeChatMessage(msg);
    }
  });
});


function trimOverflowingMessages() {
  const containerTop = chatContainer.getBoundingClientRect().top;
  const containerBottom = chatContainer.getBoundingClientRect().bottom;

  for (let i = 0; i < chatContainer.children.length; i++) {
    const child = chatContainer.children[i];
    if (child.classList.contains("disappear")) continue;

    const childRect = child.getBoundingClientRect();

    // If top of message is above the container top, remove it
    if (childRect.top < (containerTop + childRect.height/2)) {
      removeChatMessage(child);
    }
  }
}

function addChatMessage(messageHTML, msgId, username) {
  const messageDiv = document.createElement("div");
  messageDiv.classList.add("message");
  messageDiv.innerHTML = messageHTML;
  messageDiv.dataset.msgId = msgId;
  messageDiv.dataset.username = username;
  // Add to container
  chatContainer.appendChild(messageDiv);

  // Remove messages that would overflow
  trimOverflowingMessages();

  // Trigger animation
  requestAnimationFrame(() =>
    requestAnimationFrame(() => {
      messageDiv.classList.add("show");
    })
  );

  // Remove oldest if exceeding max messages
  if (chatContainer.children.length > maxMessages) {
    for (let i = 0; i < chatContainer.children.length; i++) {
      const child = chatContainer.children[i];
      if (!child.classList.contains("disappear")) {
        removeChatMessage(child);
        break; // Remove only one
      }
    }
  }

  // Auto-remove after timeout
  setTimeout(() => removeChatMessage(messageDiv), messageLifetime);
}

function removeChatMessage(messageDiv) {
  if (!messageDiv) return;
  messageDiv.classList.add("disappear");

  // Remove from DOM after animation
  messageDiv.addEventListener("transitionend", () => {
    if (messageDiv.parentNode) {
      messageDiv.parentNode.removeChild(messageDiv);
    }
  });
}
