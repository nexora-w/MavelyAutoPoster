# Telegram Media and Link Converter Bot

This is a Telegram bot that monitors specified channels, processes messages to convert specific links to Mavely format, and reposts the updated messages (with or without media) to other channels.

## Features

- Monitors multiple Telegram channels for new messages.
- Detects and converts specific URLs to a predefined format.
- Handles messages with or without media attachments.
- Reposts messages to multiple target channels.
- Ensures media files are deleted safely after processing.

## Requirements

- Python 3.8+
- A Telegram API ID and hash (get them from [my.telegram.org](https://my.telegram.org/)).
- The following libraries:
  - `telethon`
  - `aiofiles`
  - `tempfile`
  - `selenium`
  - `undetected-chromedriver`

## Installation

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Run the script:

   ```bash
   python bot.py
   ```
