---
aliases: Database manager
license: MIT
date: 2024-11-02
version: beta 1.0.0
author: Ilī-Yahu
contact: ili-yahu@pm.me
---
# Presentation
A bunch of python files that transfers `.json` files extracted from the CDLI to a SQLite database.
It is intended to work in conjunction with the CDLI API Client application I've developed that you can get [over here](https://github.com/ili-yahu/cdli-api-client-app). 

# Install
## Warning
As with my CDLI API client application, I've relied quite a lot on LLM to write the code for these Python files: first on ChatGPT-4 mini and now on Claude 3.5 Sonnet. The code has been reorganized into a more modular structure, but still needs some cleaning up. In the meantime, feel free to submit improvements, fork the repository, etc.

## Prerequisites
Just install the latest version of [Python 3.0](https://www.python.org/downloads/) in order to run the code. 
For Linux users, if I'm not mistaken, Python is shipped with most distributions, so you won't have to install anything else!

## Structure
The application is now organized into several modules:
database_manager/
├── database/ # Database operations
├── gui/ # User interface components
├── utils/ # Utility functions
├── main.py # Entry point
├── models.py # Database models
└── info.py # Version info

## Usage
1. Run `main.py` to start the application
2. Use the GUI to:
   - Select and clean JSON files
   - Create/select a SQLite database
   - Send the data to the database

The program will automatically clean up the JSON files and format them for proper database insertion.
