# A bot assistant for checking the status of homework

## Project Description
![Static Badge](https://img.shields.io/badge/EvgenyKlyukin-homework_bot-homework_bot)
![GitHub top language](https://img.shields.io/github/languages/top/EvgenyKlyukin/homework_bot)
![GitHub Repo stars](https://img.shields.io/github/stars/EvgenyKlyukin/homework_bot)
![GitHub issues](https://img.shields.io/github/issues/EvgenyKlyukin/homework_bot)

This project is a Telegram bot that interacts with the Practicum Homework service API to check the status of your homework. The bot polls the API every 10 minutes and sends status notifications to Telegram.

## Project status
The project is the final project of the "Bot assistant" sprint (Yandex Practicum). The project was completed in February 2025.

## Table of contents
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Logging](#logging)
- [Exceptions](#exceptions)
- [Tests](#tests)
- [Authors](#authors)

## Tech Stack:
The project uses the following technologies and tools:  

- **Python**: The primary programming language.  
- **pyTelegramBotAPI**: Library for interacting with the Telegram API.  
- **requests**: To interact with the Yandex API.  
- **logging**: Used for logging in the application.  
- **Pytest**: A framework for writing and running tests.  

## Installation
1. Ensure that Python 3.x is installed on your system.
2. Install the dependencies by running the command:
```bash
   pip install -r requirements.txt
```
3. Create a file .env in the root of the project and add the following environment variables to it:
```bash
    PRACTICUM_TOKEN
    TELEGRAM_TOKEN
    TELEGRAM_CHAT_ID
```

## Logging
The bot uses logging to track its work. Each message in the log contains:

- Date and time of the event
- The level of importance of the event
- Event Description

## Exceptions
The project uses its own exceptions, which are stored in a file. exceptions.py . This allows you to more accurately handle errors that occur during the operation of the bot.

## Tests
The project uses tests written with the pytest framework. To run the tests, execute the following command:
```bash
   pytest
```
The test configuration is located in the 'pytest.ini` file. The tests check the correct functioning of the main components of the game

---
## Authors
- [Evgeny Klyukin](https://github.com/EvgenyKlyukin) — lead developer.
