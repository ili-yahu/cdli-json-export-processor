---
aliases: Database manager
license: MIT
date: 2024-10-22
version: beta 0.8.1
author: Ilī-Yahu
contact: ili-yahu@pm.me
---
# Presentation
A bunch of python files that transfers `.json` files extracted from the CDLI to a SQLite database.
It is intended to work in conjunction with the CDLI API Client application I've developed that you can get [over here](https://github.com/ili-yahu/cdli-api-client-app). 

# Install
## Warning
As with my CDLI API client application, I've relied quite a lot on the LLM ChatGPT-4 mini to write the code for these Python files. This means that the code still needs a lot of cleaning up to improve it, and I have yet to do it. In the meantime, feel free to submit improvements, fork the repository, etc.

## Prerequisites
Just install the latest version of [Python 3.0](https://www.python.org/downloads/) in order to run the code. 
For Linux users, if I'm not mistaken, Python is shipped with most distributions, so you won't have to install anything else!
The `database_creator.py` file relies on the `models.py` file, so you have to keep them in the same directory.
