class ChatApp {
    constructor() {
        this.API_URL = "http://127.0.0.1:8000";

        this.chatMessages = document.getElementById("chatMessages");
        this.chatInput = document.getElementById("chatInput");
        this.sendButton = document.getElementById("sendButton");

        this.fileInput = document.getElementById("fileInput");
        this.browseFileBtn = document.getElementById("browseFileBtn");
        this.fileList = document.getElementById("fileList");
        this.fileCountBadge = document.getElementById("fileCountBadge");
        this.clearFilesBtn = document.getElementById("clearFilesBtn");

        this.uploadedFiles = [];

        this.init();
    }

    init() {
        this.addMessage("bot", "Upload a PDF and ask questions.");

        this.browseFileBtn.onclick = () => this.fileInput.click();

        this.fileInput.onchange = (e) => {
            this.handleFiles(Array.from(e.target.files));
        };

        this.sendButton.onclick = () => this.sendMessage();

        this.chatInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        this.clearFilesBtn.onclick = () => this.clearFiles();
    }

    // ================= FILE UPLOAD =================
    async handleFiles(files) {
        for (const file of files) {
            await this.uploadFile(file);
        }
        this.renderFiles();
    }

    async uploadFile(file) {
        const formData = new FormData();
        formData.append("file", file);

        try {
            const res = await fetch(`${this.API_URL}/upload`, {
                method: "POST",
                body: formData
            });

            if (res.ok) {
                this.uploadedFiles.push(file.name);
            }
        } catch (err) {
            alert("Backend not reachable");
        }
    }

    renderFiles() {
        this.fileList.innerHTML = "";

        if (this.uploadedFiles.length === 0) {
            this.fileList.innerHTML = `<li class="empty-file-message">No files uploaded yet</li>`;
        } else {
            this.uploadedFiles.forEach(name => {
                const li = document.createElement("li");
                li.className = "file-item";
                li.innerHTML = `<span class="file-name">📄 ${name}</span>`;
                this.fileList.appendChild(li);
            });
        }

        this.fileCountBadge.textContent = this.uploadedFiles.length;
    }

    clearFiles() {
        this.uploadedFiles = [];
        this.renderFiles();
    }

    // ================= CHAT =================
    async sendMessage() {
        const text = this.chatInput.value.trim();
        if (!text) return;

        this.addMessage("user", text);
        this.chatInput.value = "";

        const typing = this.addTypingIndicator();

        try {
            const res = await fetch(`${this.API_URL}/chat`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ query: text })
            });

            const data = await res.json();
            typing.remove();

            if (data.error) {
                this.addMessage("bot", data.error);
            } else {
                this.typeMessage(data.answer);
            }

        } catch {
            typing.remove();
            this.addMessage("bot", "Backend error. Is server running?");
        }
    }

    // ================= TYPING =================
    addTypingIndicator() {
        const div = document.createElement("div");
        div.className = "message-bubble bot-message";

        div.innerHTML = `
            <div class="avatar">🤖</div>
            <div class="message-content">
                <div class="message-text typing-dots">
                    <span></span><span></span><span></span>
                </div>
            </div>
        `;

        this.chatMessages.appendChild(div);
        this.scroll();

        return div;
    }

    async typeMessage(text) {
        const div = document.createElement("div");
        div.className = "message-bubble bot-message";

        div.innerHTML = `
            <div class="avatar">🤖</div>
            <div class="message-content">
                <div class="message-text"></div>
            </div>
        `;

        this.chatMessages.appendChild(div);

        const el = div.querySelector(".message-text");

        let words = text.split(" ");
        let output = "";

        for (let i = 0; i < words.length; i++) {
            output += words[i] + " ";
            el.textContent = output;

            await new Promise(r => setTimeout(r, 20));
            this.scroll();
        }
    }

    addMessage(role, text) {
        const div = document.createElement("div");
        div.className = `message-bubble ${role === "user" ? "user-message" : "bot-message"}`;

        div.innerHTML = `
            <div class="avatar">${role === "user" ? "👤" : "🤖"}</div>
            <div class="message-content">
                <div class="message-text">${text}</div>
            </div>
        `;

        this.chatMessages.appendChild(div);
        this.scroll();
    }

    scroll() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
}

window.onload = () => new ChatApp();