import re
import asyncio
from telethon import TelegramClient, events
from util import process_page
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
import time
import os

import json

with open('settings.json', 'r') as file:
    settings = json.load(file)

##########################################
# USER CONFIGURATION
##########################################

api_id = settings['api_id']
api_hash = settings['api_hash']
phone_number = settings['phone_number']

monitored_channels = settings['monitored_channels']
post_channels = settings['post_channels']

url_patterns = {
    "sylikes": r'https://go\.sylikes\.com/[^\s]+',
    "shopstyle": r'https://shopstyle\.it/[^\s]+',
    "mavely": r'https://mavely\.app\.link/[^\s]+'
}

##########################################
# LINK CONVERSION FUNCTION
##########################################

def convert_to_mavely(url):
    """
    Converts specific URLs to Mavely links.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--headless")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        
        WebDriverWait(driver, 10).until(lambda d: d.current_url != url)
        
        final_url = driver.current_url
        print("Final URL:", final_url)
        
        result = process_page(final_url)
        return result
            
    finally:
        driver.quit()

##########################################
# MESSAGE HANDLING
##########################################

async def handle_message(text):
    """
    Processes incoming messages to find and convert links.
    """
    print("Handling message...")
    for name, pattern in url_patterns.items():
        urls = re.findall(pattern, text)
        for url in urls:
            mavely_url = convert_to_mavely(url)
            if mavely_url:
                text = text.replace(url, mavely_url)
                print(f"Converted URL: {mavely_url}")
    return text

##########################################
# TELEGRAM CLIENT SETUP
##########################################

client = TelegramClient('session_name', api_id, api_hash)

@client.on(events.NewMessage(chats=monitored_channels))
async def new_message_handler(event):
    """
    Handles new messages from monitored channels.
    Reposts the entire message in exactly the same format with converted links (only if conversion happens).
    """
    try:
        print(f"New message from channel: {event.chat.title}")
        
        # Get original text
        message_text = event.message.message or ""
        print(f"Original message text: {message_text}")

        # Prepare updated message text and track if conversion happens
        updated_message = message_text
        link_converted = False  # Flag to track if any link was converted

        for key, pattern in url_patterns.items():
            matches = re.findall(pattern, message_text)
            for match in matches:
                print(f"Found URL ({key}): {match}")
                converted_link = convert_to_mavely(match)
                if converted_link:
                    updated_message = updated_message.replace(match, converted_link)
                    link_converted = True  # Set flag to True if conversion happens

        # If no link was converted, don't repost
        if not link_converted:
            print("No links were converted, not reposting.")
            return

        # Handle media
        media = None
        if event.message.media:
            print("Media detected, downloading...")
            media = await client.download_media(event.message.media)
            print(f"Media downloaded: {media}")

        # Create tasks for posting messages to multiple channels
        tasks = []
        for post_channel in post_channels:
            try:
                # Prepare the posting task
                if media:
                    # Repost with media and updated text
                    tasks.append(client.send_file(post_channel, media, caption=updated_message))
                    print(f"Task added to post updated message with media to {post_channel}")
                else:
                    # Repost text-only message
                    tasks.append(client.send_message(post_channel, updated_message))
                    print(f"Task added to post updated text-only message to {post_channel}")
            except Exception as e:
                print(f"Failed to create post task for {post_channel}: {e}")

        # Execute all tasks concurrently
        if tasks:
            await asyncio.gather(*tasks)

        # Cleanup temporary media file
        if media:
            os.remove(media)
            print(f"Deleted temporary media file: {media}")

    except Exception as e:
        print(f"Error in message handler: {e}")

async def main():
    """
    Main function to start the Telegram client.
    """
    print("Starting Telegram client...")
    try:
        await client.start(phone=phone_number)
        print("Userbot is running and monitoring channels...")
    except Exception as e:
        print(f"Error starting Telegram client: {e}")
        return  # Exit the function if there's an issue with starting the client

    await client.run_until_disconnected()

if __name__ == "__main__":
    print("Script started...")
    client.loop.run_until_complete(main())
