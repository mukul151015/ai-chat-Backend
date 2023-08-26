# FastAPI Backend Project

This project is a Python-based backend application developed using the FastAPI framework. It provides user registration, authentication, and text generation capabilities through WebSocket communication.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [WebSocket Text Generation](#websocket-text-generation)
- [Authentication](#authentication)
- [Database](#database)
- [Configuration](#configuration)
- [Dependencies](#dependencies)


## Features

- User registration and login
- JWT-based authentication
- WebSocket-based text generation

## Installation

1. Clone the repository:

- git clone <https://github.com/mukul151015/ai-chat-Backend>
-cd project-directory
2. Install dependencies:
- pip install -r requirements.txt
3. Set up the database:
- python migrate.py
4. Run the server:

- uvicorn main:app --host 0.0.0.0 --port 8000
## Usage
Start the server and access the provided endpoints for user registration, login, and text generation. WebSocket communication can be utilized for real-time text generation.

## API Endpoints
- POST /register: Register a new user.
- POST /login: Log in and obtain access and refresh tokens.
- POST /generate-text: Generate text using WebSocket communication.
## WebSocket Text Generation
The /generate-text endpoint utilizes WebSocket communication to generate text based on user input. The WebSocket connection allows real-time interaction with the text generation service.

## Authentication
User authentication is handled using JWT tokens. Access tokens are obtained upon successful login and should be included in headers for protected endpoints.

## Database
The project integrates with PostgreSQL to manage user information and token data.


## Dependencies
Python <3.11.4>
