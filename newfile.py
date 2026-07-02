import requests
import json
import os

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock

# ==========================
# CONFIGURAÇÃO
# ==========================

API_KEY = "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"
URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"

MEMORY_FILE = "memoria.json"


# ==========================
# MEMÓRIA
# ==========================

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []


def save_memory(memory):
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memory, f, ensure_ascii=False, indent=4)
    except:
        pass


# ==========================
# IA (GROQ)
# ==========================

def ask_ai(question, memory):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    messages = [
        {
            "role": "system",
            "content": "És o Vansi AI V4 criado por Lil Vansi. Responde em português claro e útil."
        }
    ]

    messages.extend(memory)
    messages.append({"role": "user", "content": question})

    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1024
    }

    try:
        response = requests.post(URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()

        data = response.json()
        return data["choices"][0]["message"]["content"]

    except requests.exceptions.Timeout:
        return "⏳ Timeout: a resposta demorou demasiado."
    except requests.exceptions.ConnectionError:
        return "🌐 Sem internet ou ligação instável."
    except Exception as e:
        return f"❌ Erro: {str(e)}"


# ==========================
# APP KIVY
# ==========================

class VansiAI(App):

    def build(self):
        self.memory = load_memory()

        self.layout = BoxLayout(orientation="vertical")

        self.chat = Label(
            text="🤖 Vansi AI V4 iniciado",
            size_hint_y=8,
            halign="left",
            valign="top"
        )
        self.chat.bind(size=self.chat.setter("text_size"))

        self.layout.add_widget(self.chat)

        self.input = TextInput(
            hint_text="Escreve a tua mensagem...",
            size_hint_y=None,
            height=120,
            multiline=False
        )
        self.layout.add_widget(self.input)

        self.button = Button(
            text="Enviar 🚀",
            size_hint_y=None,
            height=60
        )
        self.button.bind(on_press=self.send_message)

        self.layout.add_widget(self.button)

        return self.layout

    def send_message(self, instance):
        msg = self.input.text.strip()

        if not msg:
            return

        self.chat.text += f"\n\n👤 Tu: {msg}"
        self.chat.text += "\n🤖 Vansi AI: A pensar..."

        self.input.text = ""

        Clock.schedule_once(lambda dt: self.process(msg), 0.5)

    def process(self, msg):
        response = ask_ai(msg, self.memory)

        self.chat.text = self.chat.text.replace("🤖 Vansi AI: A pensar...", "")

        self.chat.text += f"\n🤖 Vansi AI: {response}"

        self.memory.append({"role": "user", "content": msg})
        self.memory.append({"role": "assistant", "content": response})

        save_memory(self.memory)


# ==========================
# START
# ==========================

if __name__ == "__main__":
    VansiAI().run()