# MindfulBalance

A mental health tracking application built with Flet that helps users monitor their daily mood, create journal entries, and visualize their wellness journey through interactive analytics.

## Getting Started

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation

* Clone the repository:

```bash
git clone <your-repository-url>
```

* Navigate to the project directory:

```bash
cd MindfulBalance
```

* Create a virtual environment:

```bash
python -m venv venv
```

* Activate the virtual environment:

**On Windows:**
```bash
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
source venv/bin/activate
```

* Install dependencies:

```bash
pip install -r requirements.txt
```

### Running the Application

To start the MindfulBalance application, use the following command:

```bash
cd presentation_layer/flet_app
python main.py
```

The application will open in a new window where you can:
- Create an account or sign in
- Track your daily mood
- Write journal entries
- View analytics and mood trends

### Deactivating the Virtual Environment

When you're done using the application, you can deactivate the virtual environment:

```bash
deactivate
```

## Features

- **User Authentication**: Secure login and registration system
- **Mood Tracking**: Rate your mood on a 1-10 scale with emoji indicators
- **Journaling**: Write and save daily journal entries
- **Analytics**: View mood trends and wellness statistics with matplotlib charts
- **Data Persistence**: SQLite database for storing user data and mood history
