# YT Notes Maker 🚀

YT Notes Maker is an AI-powered full-stack application that automatically generates structured study notes, quizzes, and diagrams from YouTube videos using the YouTube Transcript API and Google's Gemini AI.

## 🛠️ How to Run Locally

If you're running this locally for an exam or studying, follow these steps. 

### Prerequisites
Make sure you have installed on your computer:
- **Python 3.8+**
- **Node.js 18+**
- **Git**

### Step 1: Get Your Free API Keys & Database
To run this application, you need three free credentials. Create them and keep them handy:

1. **Google Gemini API Key:** Go to [Google AI Studio](https://aistudio.google.com/app/apikey) and click "Create API Key".
2. **YouTube Data v3 API Key:** Go to [Google Cloud Console](https://console.cloud.google.com/), create a project, enable the "YouTube Data API v3", and generate an API Key.
3. **Database URL:** Go to [Neon.tech](https://neon.tech/), create a free account, make a new project, and copy the `Postgres connection string` (it looks like `postgresql://...`).

### Step 2: Set up the Backend (Python/FastAPI)

1. Clone the repository and open the folder:
   ```bash
   git clone https://github.com/starscreamwashere/YTNotesMaker.git
   cd YTNotesMaker
   ```

2. Create a Python Virtual Environment:
   - **Mac/Linux:** `python3 -m venv venv && source venv/bin/activate`
   - **Windows:** `python -m venv venv` and then `venv\Scripts\activate`

3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Go into the backend directory:
   ```bash
   cd backend/backend
   ```

5. Create a `.env` file inside this `backend/backend` folder and paste your keys:
   ```env
   YOUTUBE_API_KEY="your_youtube_api_key_here"
   GEMINI_API_KEY="your_gemini_api_key_here"
   DATABASE_URL="your_neon_postgres_url_here"
   ```

6. Start the server!
   ```bash
   uvicorn main:app --reload
   ```
   *(Keep this terminal open! The backend is now running at http://localhost:8000)*

### Step 3: Set up the Frontend UI (Next.js)

1. Open a **new, second terminal** window.
2. Navigate to the frontend directory:
   ```bash
   cd YTNotesMaker/backend/frontend
   ```
3. Install the Node packages:
   ```bash
   npm install
   ```
4. Start the frontend:
   ```bash
   npm run dev
   ```

### Step 4: Start Studying! 🧠
Open your browser and navigate to **`http://localhost:3000`**. You can now create an account, paste a YouTube link, and generate instant study guides!
