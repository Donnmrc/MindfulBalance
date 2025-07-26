# CPE106L_E01_3T24525
# 🌿 Mindful Balance

Mindful Balance is a minimalist desktop wellness application that allows users to log moods, write journal entries, and view emotional trends. Built using Python, Flet, and FastAPI, the app runs locally to prioritize privacy, simplicity, and ease of use.

---

## ⚙️ Setup Instructions

### 🔧 Ubuntu Virtual Machine (VM)

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd MindfulBalance

Install dependencies:
pip install fastapi uvicorn flet httpx bcrypt matplotlib

Start FastAPI backend:
uvicorn backend.api:app --reload

Run frontend:
python3 frontend/main.py


Windows Terminal
Clone the repository
:
git clone https://github.com/Donnmrc/CPE106L_E01_3T24525
cd MindfulBalance

Install dependencies:
pip install fastapi uvicorn flet httpx bcrypt matplotlib

Start FastAPI backend:
uvicorn backend.api:app --reload

How to Run the Application

    Ensure all dependencies are installed (see above).

    Run the backend server using Uvicorn.

    Launch the frontend using Python and Flet.

    The app opens directly to the mood input screen and follows a simple flow: Mood → Journal → Insights.
    
    
    Dependencies

    fastapi

    uvicorn

    flet

    httpx

    bcrypt

    matplotlib

    sqlite3 (built-in)
    
    
System Design
Frontend	Flet (Python)	Builds a simple desktop UI for mood input, journaling, and viewing insights.
Backend	FastAPI (Python)	Serves RESTful API endpoints for logging data and retrieving statistics.
Database	SQLite	Stores mood entries and journal logs locally without user authentication.
Communication	httpx (Python)	Facilitates HTTP requests between frontend and backend components.
Visualization	Matplotlib (optional)	Used for generating charts based on stored mood data.
Routing	Flet's View system	Enables screen transitions across Mood Input, Journal, and Insights views.
Design Theme	Minimalist, calm	Uses soft blues and greys, rounded inputs, and clean layout for focus and ease.

User Story:

Ancheta:
During development of Mindful Balance, one of the main challenges was ensuring that the backend and frontend components worked together seamlessly. The backend was built using FastAPI to handle data entry and retrieval, while the frontend used Flet to offer an intuitive desktop UI.

Initially, requests from the frontend weren’t reaching the backend correctly. After reviewing the architecture, I realized that the issue stemmed from mismatched routing paths, inconsistent server addresses, and incorrect working directories. To resolve this, I aligned all API endpoint URLs across both layers and standardized the base URL in the frontend’s httpx requests to match the backend’s local server.

I also verified each route individually, ensuring that mood and journal data were processed, stored in SQLite, and correctly returned via the /stats endpoint. Careful debugging revealed that launching the backend server outside of its intended working folder could prevent it from accessing database files or models properly. Reconfiguring launch commands and path references made the app fully operational.

Finally, I refactored key files to maintain modularity, including separating UI views by function and cleaning up error handling for smoother navigation. This full-stack integration allowed the app’s main features — mood tracking, journaling, and insights — to work consistently and reliably from end to end.

Lintag:
While doing the database for our project, I encountered a really weird bug while pushing the said database into GitHub. The bug said that there is a corrupted .git file with a specific hashkey. I decided to search up Google and ChatGPT for the cause of the problem and how to fix it. To fix the bug where I was stuck on the wrong Git branch and couldn’t switch to main, I first realized that untracked files in the working directory were blocking the checkout. The solution was to stash those changes safely using git stash push --include-untracked -m "Backup before switching to main". After that, I successfully switched to the main branch with git checkout main and continued working from the correct version of the project. This let me avoid losing progress while cleaning up the workspace for proper syncing.

Team Members and Roles
Name	Roles
Ancheta	Coding, Document Creation, Database Creation
Lintag	Coding, Document Creation, Database Creation



