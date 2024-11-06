---
date-modified: 2024-11-06T18:18:17+01:00
date-created: 2024-10-22T11:01:39+02:00
---
![License](https://img.shields.io/badge/license-MIT-red)
![Platform](https://img.shields.io/badge/platform-Windows--MacOS--Linux-lightgrey)
![Version](https://img.shields.io/badge/pre--release-1.2.1-blue)
![Date](https://img.shields.io/badge/date-2024--11--06-lightblue)
![Author](https://img.shields.io/badge/author-Il%C4%AB--yahu-green)
[![Contact](https://img.shields.io/badge/contact-Ili--Yahu@pm.me-lightgreen)](mailto:Ili-Yahu@pm.me)

# Presentation
This application processes `.json` files extracted from the CDLI (Cuneiform Digital Library Initiative) and transfers the data to a SQLite database. The main goal is to provide a user-friendly interface to automatically clean up and process the data from the CDLI.
It is intended to work in conjunction with the CDLI API Client application I've developed that you can get [over here](https://github.com/ili-yahu/cdli-api-client-app). You can also directly use the official [CDLI framework API client](https://github.com/cdli-gh/framework-api-client).

# Install
## Warning
As with my CDLI API client application, I've relied quite a lot on LLM to write the code for these Python files: first on ChatGPT-4 mini and now on Claude 3.5 Sonnet. The code is organized into a more modular structure, but still needs some cleaning up. In the meantime, feel free to submit improvements, fork the repository, etc.

## Prerequisites
Just install Python 3.8 or higher from the official [website](https://www.python.org/downloads/) to run the code. 
For Linux users, if I'm not mistaken, Python is shipped with most distributions, so you won't have to install anything else!

## Installation
1. Clone the repository:
```sh
git clone https://github.com/ili-yahu/cdli-json-export-processor.git
cd cdli-json-export-processor
```
2. Install the required Python packages:
```sh
pip install -r requirements.txt
```

## Structure
The application is organized into several modules:

```bash
cdli-json-export-processor/
├── database/           # Database operations and models
│   ├── entity_config.py   
│   ├── processor.py    
│   └── tables_config.py
├── gui/               # User interface components  
│   ├── credits_tab.py
│   ├── help_tab.py
│   ├── home_tab.py
│   ├── import_tab.py
│   ├── main_window.py
│   └── options_tab.py
├── ui/                # Additional UI components
│   └── progress_tracker.py
├── utils/             # Utility functions
│   ├── config_manager.py
│   ├── file_handler.py
│   ├── logger.py
│   └── text_cleaner.py
├── .gitignore        # Git ignore file
├── config.json       # Configuration file
├── info.py          # Version info
├── main.py          # Entry point
├── README.md        # Documentation
└── requirements.txt  # Dependencies
```
## Usage
1. Run `main.py` to start the application
2. Use the GUI to:
   - Create/select a SQLite database
   - Select and clean JSON files
   - Send the data to the database

The program will automatically clean up the JSON files and format them for proper database insertion.

## Known Issues and Troubleshooting
- If you encounter any issues, please enable the logging options in the help tab and check the logs in the `/logs` directory.

