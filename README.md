
# ChatBot with GPT-4o mini

This project is a chat application that uses GPT-4o mini for conversation, along with integrations for fetching news, weather, and internet search results.

## Features

- **Chat with GPT-4o mini**: Interact with the GPT-4o mini model for various queries and conversations.
- **Google Custom Search**: Fetches search results from the internet using Google Custom Search API.
- **Weather Information**: Retrieves current weather information using OpenWeatherMap API.
- **News Fetching**: Fetches the latest news using NewsAPI.
- **Important Notes**: Marks and retrieves important notes and events.
- **Session Management**: Manages chat sessions and saves chat history in a SQLite database.
- **Font Adjustments**: Allows the user to adjust the font size of the chat window.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ChatBot.git
   cd ChatBot
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the environment variables. Create a `.env` file in the root of the project with the following content:
   ```plaintext
   OPENAI_API_KEY=your_openai_api_key
   NEWS_API_KEY=your_news_api_key
   WEATHER_API_KEY=your_weather_api_key
   GOOGLE_API_KEY=your_google_api_key
   GOOGLE_CSE_ID=your_google_cse_id
   GOOGLE_APPLICATION_CREDENTIALS=path_to_your_service_account_file.json
   BUCKET_NAME=your_bucket_name
   ```

5. Ensure you have your Google Cloud credentials file in the specified path.

## Usage

Run the application:
```bash
python main.py
```

This will open the chat window where you can start interacting with the GPT-4o mini model and use other features.

## Project Structure

```
ChatBot/
│
├── main.py                 # Main application script
├── chat_gpt.py             # Script containing GPT-4o mini interaction and API integration functions
├── requirements.txt        # List of required Python packages
├── .env                    # Environment variables
├── README.md               # Project documentation
└── chatbot.db              # SQLite database for storing chat history (auto-generated)
```

## Dependencies

- `openai`
- `python-dotenv`
- `requests`
- `google-auth`
- `google-auth-oauthlib`
- `google-auth-httplib2`
- `google-api-python-client`
- `tkinter`
- `sqlite3`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
