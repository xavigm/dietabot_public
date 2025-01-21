![alt text](dietbot.jpg "Title")
# This is dietabot

Dietabot is a Telegram bot made in Python, with Flask. It answers you with a diet each week and the following week, so you can shop for the ingredients, and uses Gemini's AI to break down the ingredients you should buy.
This BOT DOES NOT GENERATE DIETS, but uses the ones that your nutritionist has provided you (or created yourself with another AI), to deliver them to you randomly.

# Getting started
Download the repository to the host you want to use it on. Modify the following strings that you will find in the main.py file:

GEMINI_APIKEY: with a Google Gemini API KEY. You can get it for free: https://ai.google.dev/gemini-api/docs/api-key?hl=es-419

TELEGRAM_USERID: It is the user, or list of users that dietbot will respond to. If it's not on the list, you simply won't be able to receive responses from the bot.

TELEGRAM_BOT_TOKEN: It is the Telegram Bot Token. You have to generate a bot for this. You can see how it's done here: https://sendpulse.com/latam/knowledge-base/chatbot/telegram/create-telegram-chatbot

Once you have changed the variables, you can upload the diets.
This BOT DOES NOT GENERATE DIETS, but uses the ones that your nutritionist has provided you (or created yourself with another AI), to deliver them to you randomly.
The diets must be uploaded to the /opt/dietabot/static directory of the host, in jpg format, so that the Docker container can use them. They must have names from 1 to 27. If you have more diets, modify the loop in the main.py file to use them.
Once you have it, you can run the run.sh script, which will automatically generate the Docker Image from the Dockerfile and start the dietbot. You can now talk to your chatbot!

## Chatbot commands
You can run the following commands with the chatbot:

/dieta
It will return a diet for the current week and another for the next, so you can shop in advance. It will always return the same diets no matter what day of the week it is, so you don't make a mistake if you order two diets in a row.

/ingredientes
It will return the list of ingredients for the following week, so you can shop. This is the function that Gemini AI uses, sending the image of the diet as a prompt and having it break down into ingredients.

