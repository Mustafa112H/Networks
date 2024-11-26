# ENCS3320 Project #1

## Overview
This project consists of two main components:
1. **A Simple Web Server** implemented using socket programming that serves HTML pages with dynamic and static content.
2. **A UDP Client-Server Trivia Game** that allows multiple players to participate in a competitive, interactive quiz game.

## Features
### Task 2: Web Server
The web server listens on port `5698` and serves multiple HTML pages with support for both English and Arabic content. It includes:
- **Main English Webpage** (`main_en.html`): 
  - Displays team members' information, their photos, and a description of a topic related to computer networking.
  - Includes hyperlinks to supporting material, external resources (e.g., textbook and Ritaj websites), and an external CSS file for styling.
- **Supporting Material Page** (`supporting_material_en.html`):
  - Provides a form for users to request images or videos.
  - Redirects to Google or YouTube search results if the requested file is unavailable, using a `307 Temporary Redirect`.
- **Arabic Versions**:
  - Localized versions of the main and supporting material pages (`main_ar.html` and `supporting_material_ar.html`).

Additional server functionalities include:
- Error handling with custom 404 error pages.
- Logging HTTP request details to the terminal.
- Serving static assets such as images, videos, and CSS files.

### Task 3: UDP Trivia Game
The UDP-based server listens on port `5689` and manages a multiplayer trivia game with the following features:
- **Server Responsibilities**:
  - Maintains a list of active clients.
  - Initiates a round when at least two clients are connected.
  - Broadcasts questions to all clients and collects their answers within a time limit.
  - Tracks scores and announces winners after each round.
  - Displays game progress, scores, and leaderboard updates in the terminal.
- **Client Responsibilities**:
  - Connects to the server and registers with a username.
  - Listens for game updates and questions.
  - Submits answers within the designated time.

## Installation
### Prerequisites
- Python 3.x installed on your system.
- Knowledge of socket programming basics.
- HTML, CSS, and JavaScript for modifying webpage content.

### Files and Directory Structure
```plaintext
project/
│
├── webserver/
│   ├── server.py               # Python script for the web server
│   ├── main_en.html            # Main English webpage
│   ├── supporting_material_en.html # Supporting material page in English
│   ├── main_ar.html            # Arabic version of the main page
│   ├── supporting_material_ar.html # Arabic version of supporting material page
│   ├── style.css               # CSS file for styling
│   ├── assets/
│       ├── team_photos/        # Team member photos (.png)
│       ├── imgs/             # Additional images (.jpg)
│       └── vids/             # Videos for the supporting material
│
├── trivia_game/
│   ├── server.py               # Python script for the trivia game server
│   ├── client.py               # Python script for the trivia game client
│   ├── questions.json          # JSON file containing trivia questions
│
└── README.md                   # Documentation
