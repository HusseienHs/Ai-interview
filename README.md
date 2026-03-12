# AI Interview Assistant 🤖

An **AI-powered interview simulator** that helps users practice technical interviews.
The system generates interview questions, evaluates answers using an LLM, and provides feedback to improve performance.

Built with **Python, Streamlit, and LLM APIs**.

---

## Features

* 🎤 Simulated **technical interview experience**
* 🤖 **AI-generated interview questions**
* 🧠 **Automatic answer evaluation**
* 📊 **Score and feedback system**
* 💻 Clean **Streamlit interface**
* 🔐 Secure API token management with `.env`

---

## Tech Stack

* **Python**
* **Streamlit**
* **OpenAI Python SDK**
* **HuggingFace Router**
* **dotenv**

---

## Project Structure

```
AI-Interview/
│
├── app.py                # Main Streamlit application
├── interview_engine.py   # Interview logic and evaluation
├── utils.py              # Helper functions
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (not committed)
└── README.md
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/ai-interview.git
cd ai-interview
```

Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
```

or

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the root directory:

```
HF_TOKEN=your_huggingface_token
```

The project uses **HuggingFace Router API** to access LLM models.

---

## Run the Application

Start the Streamlit server:

```bash
streamlit run app.py
```

Then open in your browser:

```
http://localhost:8501
```

---

## Example Workflow

1. User starts the interview session
2. AI generates a technical question
3. User submits their answer
4. The AI evaluates the response
5. Feedback and score are displayed

---

## Example Interview Question

```
Explain what happens when you run the command:

ls -l
```

The system evaluates:

* correctness
* clarity
* completeness

---

## Future Improvements

* 🎙️ Voice-based interviews
* 📊 Performance analytics dashboard
* 🧑‍💻 Different interview tracks (Backend, Data, ML)
* 🧠 Better scoring algorithms
* 🗂 Interview history

---

## Author

**Husain and Dania**

4th Year Software & Information Systems Engineering Student
Ben-Gurion University

Interested in:

* AI
* Machine Learning
* Software Systems
* Backend Development

---

## License

This project is for **educational and portfolio purposes**.
