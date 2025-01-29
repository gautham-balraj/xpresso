---

# Xpresso 🚀

Xpresso is a powerful AI-driven tweet generation and posting tool. It allows users to input a topic, generates relevant tweets, and provides the ability to post them directly to Twitter. Built with a Python backend (FastAPI) and a modern React frontend, Xpresso is designed for simplicity and efficiency.

---

## Features ✨

- **Topic Input**: Enter any topic, and Xpresso will research and generate tweets for you.
- **Tweet Generation**: Automatically generates 10 high-quality tweets with virality scores and justifications.
- **Tweet Selection**: Choose which tweets to post.
- **Direct Posting**: Post selected tweets directly to your Twitter account.
- **Dark Mode**: A sleek, minimal dark theme for a better user experience.

---

## Tech Stack 🛠️

- **Frontend**: React (Vite + TypeScript + Tailwind CSS)
- **Backend**: FastAPI (Python)
- **Twitter API**: For posting tweets
- **AI Integration**: Custom research and summarization pipeline

---

## Prerequisites 📋

Before running the project, ensure you have the following installed:

- **Node.js** (v16 or higher)
- **Python** (v3.9 or higher)
- **pip** (Python package manager)
- **Twitter API Credentials** (stored in `.env` file)

---

## Setup and Installation 🛠️

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/xpresso.git
cd xpresso
```

### 2. Set Up the Backend
1. Navigate to the backend directory:
   ```bash
   cd src
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory and add your Twitter API credentials:
   ```env
   TWITTER_API_KEY=your_api_key
   TWITTER_API_SECRET=your_api_secret
   TWITTER_ACCESS_TOKEN=your_access_token
   TWITTER_ACCESS_SECRET=your_access_secret
   ```
4. Run the FastAPI server:
   ```bash
   uvicorn api:app --reload
   ```
   The backend will be available at `http://127.0.0.1:8000`.

### 3. Set Up the Frontend
1. Navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```
2. Install Node.js dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
   The frontend will be available at `http://localhost:5173`.

---

## Usage 🖥️

1. Open the frontend in your browser (`http://localhost:5173`).
2. Enter a topic in the input field and click **Generate Tweets**.
3. Review the generated tweets, select the ones you want to post, and click **Post Selected**.
4. The selected tweets will be posted to your Twitter account.

---

## Project Structure 📂

```
xpresso/
├── frontend/               # React frontend
│   ├── public/             # Static assets
│   ├── src/                # React source code
│   │   ├── App.tsx         # Main React component
│   │   ├── main.tsx        # React entry point
│   │   └── ...             # Other React files
│   ├── .env                # Environment variables (if any)
│   ├── package.json        # Frontend dependencies
│   └── ...                 # Other frontend config files
├── src/                    # Python backend source code
│   ├── assistant/          # AI research and summarization logic
│   ├── api.py              # FastAPI backend
│   ├── .env                # Twitter API credentials
│   └── ...                 # Other backend files
├── README.md               # Project documentation
└── ...                     # Other project files
```

---

## Contributing 🤝

Contributions are welcome! If you'd like to contribute to Xpresso, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a pull request.

