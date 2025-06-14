<!DOCTYPE html>
<html lang="id">
  <head>
    <meta charset="UTF-8" />
    <title>Chatal – Chat Kesehatan Mental</title>
    <link
      href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css"
      rel="stylesheet"
    />
    <link
      href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap"
      rel="stylesheet"
    />
    <style>
      body {
        font-family: "Inter", sans-serif;
        background-color: #f0f4f8;
      }

      .hero {
        background: linear-gradient(to right, #a0c4ff, #bdb2ff);
        padding: 60px 20px;
        text-align: center;
        border-radius: 15px;
        margin-bottom: 40px;
        color: #fff;
      }

      #chat-box {
        height: 420px;
        overflow-y: auto;
        border: none;
        padding: 20px;
        background-color: #ffffff;
        border-radius: 15px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
      }

      .user,
      .bot {
        display: flex;
        margin-bottom: 16px;
        align-items: flex-start;
      }

      .user .avatar,
      .bot .avatar {
        width: 36px;
        height: 36px;
        margin-right: 12px;
        font-size: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        flex-shrink: 0;
      }

      .user .avatar {
        background-color: #d0ebff;
        color: #1c7ed6;
      }

      .bot .avatar {
        background-color: #f1f3f5;
        color: #6c757d;
      }

      .message-content {
        max-width: 80%;
        background-color: #f8f9fa;
        padding: 10px 14px;
        border-radius: 10px;
      }

      .user .message-content {
        background-color: #d0ebff;
        margin-left: auto;
      }

      .bot .message-content {
        background-color: #f8f9fa;
      }

      #chat-box::-webkit-scrollbar {
        width: 8px;
      }

      #chat-box::-webkit-scrollbar-thumb {
        background: #ced4da;
        border-radius: 4px;
      }

      footer {
        font-size: 0.875rem;
        color: #6c757d;
      }
    </style>
  </head>
  <body class="container py-5">
    <!-- Hero Section -->
    <section class="hero">
      <h1 class="display-5 fw-bold">Chatal</h1>
      <p class="lead">
        Teman ngobrol virtual yang siap dengerin kamu, kapan pun kamu butuh.
      </p>
      <p class="mb-4">
        Kamu bisa cerita bebas di sini, tanpa takut dihakimi. Yuk mulai ngobrol
        bareng Chatal!
      </p>
      <a href="#chat-section" class="btn btn-light btn-lg">Mulai Curhat</a>
    </section>

    <!-- Chat Section -->
    <section id="chat-section" class="mb-5">
      <h2 class="mb-3">Curhat Sekarang 💬</h2>
      <div id="chat-box" class="mb-3"></div>

      <div class="input-group mb-4">
        <input
          type="text"
          id="user-input"
          class="form-control"
          placeholder="Tulis curhatanmu di sini..."
        />
        <button class="btn btn-primary" onclick="sendMessage()">Kirim</button>
      </div>
    </section>

    <footer class="text-center border-top pt-3">
      <small>© 2025 Chatal – PT. Solusi Sehat Digital</small>
    </footer>

    <script>
      function appendMessage(sender, message) {
        const div = document.createElement("div");
        div.className = sender;

        const avatar = document.createElement("div");
        avatar.className = "avatar";
        avatar.innerText = sender === "user" ? "🧑" : "🤖";

        const messageContent = document.createElement("div");
        messageContent.className = "message-content";
        messageContent.textContent = message;

        div.appendChild(avatar);
        div.appendChild(messageContent);

        document.getElementById("chat-box").appendChild(div);
        document.getElementById("chat-box").scrollTop =
          document.getElementById("chat-box").scrollHeight;
      }

      async function sendMessage() {
        const input = document.getElementById("user-input");
        const text = input.value.trim();
        if (!text) return;

        appendMessage("user", text);
        input.value = "";

        const formData = new FormData();
        formData.append("message", text);

        try {
          const res = await fetch("/chat", {
            method: "POST",
            body: formData,
          });

          const data = await res.json();
          appendMessage("bot", data.reply);
        } catch (err) {
          appendMessage("bot", "❌ Terjadi error saat mengirim.");
        }
      }

      // Auto greet Chatalers on page load
      window.onload = () => {
        appendMessage(
          "bot",
          "Hai Chatalers! 😊 Chatal di sini buat dengerin kamu. Cerita apa aja, ya?"
        );
      };
    </script>
  </body>
</html>
