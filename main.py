import json
import sys
import urllib.error
import urllib.request
from PySide6.QtCore import QThread, Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QScroller,
    QVBoxLayout,
    QWidget,
)

# Replace with your actual Groq API key from console.groq.com
GROQ_API_KEY = "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"


class APIWorker(QThread):
  finished = Signal(str)

  def __init__(self, messages, api_key):
    super().__init__()
    self.messages = messages
    self.api_key = api_key

  def run(self):
    try:
      url = "https://api.groq.com/openai/v1/chat/completions"
      headers = {
          "Authorization": f"Bearer {self.api_key}",
          "Content-Type": "application/json",
          "User-Agent": (
              "Mozilla/5.0 (Android; Mobile; rv:120.0) Gecko/120.0"
              " Firefox/120.0"
          ),
      }
      data = {"model": "openai/gpt-oss-20b", "messages": self.messages}
      req = urllib.request.Request(
          url,
          data=json.dumps(data).encode("utf-8"),
          headers=headers,
          method="POST",
      )
      with urllib.request.urlopen(req) as response:
        res_data = json.loads(response.read().decode("utf-8"))
        reply = res_data["choices"][0]["message"]["content"]
        self.finished.emit(reply)
    except urllib.error.HTTPError as e:
      err_body = e.read().decode("utf-8")
      self.finished.emit(f"HTTP Error {e.code}: {err_body}")
    except Exception as e:
      self.finished.emit(f"Error: {str(e)}")


class ChatWindow(QMainWindow):

  def __init__(self, user_name):
    super().__init__()
    self.user_name = user_name
    self.setWindowTitle("RudraCodes AI")
    self.resize(400, 700)

    # Initialize conversation history with system prompt
    self.conversation_history = [{
        "role": "system",
        "content": (
            "You are RudraCodes AI, an elite academic study and research"
            " mentor created and developed by Rudra Sharma. Your mission is to"
            " help students master any subject, break down complex topics"
            " step-by-step, explain concepts clearly, summarize research, and"
            " assist with exam preparation. CRITICAL INSTRUCTION: Never use LaTeX"
            " syntax like \\frac, \\[ \\], or \\rho. Always write formulas and"
            " math using clean plain text, Unicode symbols (like ρ, θ, Δ, °),"
            " and standard division slashes (e.g., P = F / A, P = P₀ + ρgh) so"
            " they display perfectly on mobile screens."
        ),
    }]

    self.setStyleSheet("""
            QMainWindow {
                background-color: #090d16;
            }
            QScrollArea {
                background: transparent;
                border: none;
            }
            QLineEdit {
                background-color: #111827;
                color: #f3f4f6;
                border: 1px solid #1f2937;
                border-radius: 22px;
                padding: 12px 18px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #6366f1;
            }
            QPushButton {
                background-color: #6366f1;
                color: #ffffff;
                font-weight: bold;
                border-radius: 22px;
                padding: 12px 22px;
                font-size: 14px;
            }
            QPushButton:pressed {
                background-color: #4f46e5;
            }
        """)

    central_widget = QWidget()
    self.setCentralWidget(central_widget)
    main_layout = QVBoxLayout(central_widget)
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.setSpacing(0)

    header = QFrame()
    header.setStyleSheet(
        "background-color: #0f172a; border-bottom: 1px solid #1e293b;"
    )
    header_layout = QHBoxLayout(header)
    header_layout.setContentsMargins(16, 12, 16, 12)

    title_label = QLabel("⚡ RudraCodes AI")
    title_label.setStyleSheet(
        "color: #818cf8; font-weight: bold; font-size: 16px; background:"
        " transparent;"
    )
    header_layout.addWidget(title_label)

    status_label = QLabel("● Online")
    status_label.setStyleSheet(
        "color: #10b981; font-weight: bold; font-size: 12px; background:"
        " transparent;"
    )
    status_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
    header_layout.addWidget(status_label)

    main_layout.addWidget(header)

    self.scroll_area = QScrollArea()
    self.scroll_area.setWidgetResizable(True)
    QScroller.grabGesture(
        self.scroll_area.viewport(), QScroller.TouchGesture
    )
    QScroller.grabGesture(
        self.scroll_area.viewport(), QScroller.LeftMouseButtonGesture
    )

    self.scroll_content = QWidget()
    self.scroll_content.setStyleSheet("background: transparent;")
    self.chat_layout = QVBoxLayout(self.scroll_content)
    self.chat_layout.setAlignment(Qt.AlignTop)
    self.chat_layout.setContentsMargins(16, 16, 16, 16)
    self.chat_layout.setSpacing(14)
    self.scroll_area.setWidget(self.scroll_content)
    main_layout.addWidget(self.scroll_area)

    input_container = QFrame()
    input_container.setStyleSheet(
        "background-color: #0f172a; border-top: 1px solid #1e293b;"
    )
    input_layout = QHBoxLayout(input_container)
    input_layout.setContentsMargins(16, 12, 16, 12)
    input_layout.setSpacing(10)

    self.user_input = QLineEdit()
    self.user_input.setPlaceholderText(
        "Ask a study question or research a topic..."
    )
    self.user_input.returnPressed.connect(self.send_message)
    input_layout.addWidget(self.user_input)

    self.send_btn = QPushButton("Send")
    self.send_btn.clicked.connect(self.send_message)
    input_layout.addWidget(self.send_btn)

    main_layout.addWidget(input_container)

    # Greeting using the user's entered name
    greeting_text = (
        f"Hello {self.user_name}! I am RudraCodes AI, your elite academic and"
        " research tutor, created by Rudra Sharma. How can I help you excel in"
        " your studies today?"
    )
    self.conversation_history.append(
        {"role": "assistant", "content": greeting_text}
    )
    self.add_message_bubble(greeting_text, is_user=False)
    self.typing_widget = None

  def add_message_bubble(self, text, is_user):
    bubble_frame = QFrame()
    bubble_layout = QVBoxLayout(bubble_frame)
    bubble_layout.setContentsMargins(14, 10, 14, 10)

    formatted_text = text.replace("\n", "<br>")
    label = QLabel(formatted_text)
    label.setWordWrap(True)

    if is_user:
      bubble_frame.setStyleSheet(
          "background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #6366f1,"
          " stop:1 #4f46e5); border-radius: 16px;"
      )
      label.setStyleSheet("color: #ffffff; font-size: 14px; background: none;")
      bubble_layout.addWidget(label)

      row_layout = QHBoxLayout()
      row_layout.addStretch()
      row_layout.addWidget(bubble_frame)
      self.chat_layout.addLayout(row_layout)
    else:
      bubble_frame.setStyleSheet(
          "background-color: #1e293b; border: 1px solid #334155; border-radius:"
          " 16px;"
      )
      label.setStyleSheet(
          "color: #f8fafc; font-size: 14px; background: none; line-height:"
          " 140%;"
      )
      bubble_layout.addWidget(label)

      row_layout = QHBoxLayout()
      row_layout.addWidget(bubble_frame)
      row_layout.addStretch()
      self.chat_layout.addLayout(row_layout)

    QTimer.singleShot(
        50,
        lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        ),
    )

  def show_typing(self):
    self.typing_widget = QFrame()
    layout = QVBoxLayout(self.typing_widget)
    layout.setContentsMargins(14, 10, 14, 10)
    label = QLabel("✨ Thinking...")
    label.setStyleSheet(
        "color: #94a3b8; font-weight: bold; font-size: 13px; background: none;"
    )
    layout.addWidget(label)
    self.typing_widget.setStyleSheet(
        "background-color: #1e293b; border: 1px dashed #6366f1; border-radius:"
        " 16px;"
    )

    row = QHBoxLayout()
    row.addWidget(self.typing_widget)
    row.addStretch()
    self.chat_layout.addLayout(row)

    QTimer.singleShot(
        50,
        lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        ),
    )

  def remove_typing(self):
    if self.typing_widget:
      self.chat_layout.removeWidget(self.typing_widget)
      self.typing_widget.setParent(None)
      self.typing_widget = None

  def send_message(self):
    user_text = self.user_input.text().strip()
    if not user_text:
      return

    self.add_message_bubble(user_text, is_user=True)
    self.user_input.clear()
    self.user_input.setEnabled(False)
    self.send_btn.setEnabled(False)

    self.conversation_history.append({"role": "user", "content": user_text})
    self.show_typing()

    self.worker = APIWorker(self.conversation_history, GROQ_API_KEY)
    self.worker.finished.connect(self.handle_response)
    self.worker.start()

  def handle_response(self, reply):
    self.remove_typing()
    self.conversation_history.append({"role": "assistant", "content": reply})
    self.add_message_bubble(reply, is_user=False)
    self.user_input.setEnabled(True)
    self.send_btn.setEnabled(True)
    self.user_input.setFocus()


if __name__ == "__main__":
  app = QApplication(sys.argv)

  # Centered separate input dialog box to get the user's name on startup
  name, ok = QInputDialog.getText(
      None,
      "RudraCodes AI - Welcome",
      "Enter your name to start your study session:",
  )
  user_name = name.strip() if (ok and name.strip()) else "Student"

  window = ChatWindow(user_name)
  window.show()
  sys.exit(app.exec())
