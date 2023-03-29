from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

import openai

### Obtained from @BotFather
bot_token = "paste_your_bot_token_here"

### Obtained from OpenAI website
openai.api_key = "paste_your_api_key_here"

# Update contains the information about incoming messages
# Context contains the information about our application

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  """
    Execute on /start command.
    It reply with a welcome message to the user when /start command is executed
  """

  await context.bot.sendMessage(
    text="Welcome to telegram bot powered by OpenAI",
    chat_id=update.effective_chat.id
  )

### echo function is commented because there is a chat function to handle text messages
# async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
#    """
#     Execute on receiving a message.
#     It reply with same user message received.
#    """
#    await context.bot.sendMessage(
#      text=update.effective_message.text,
#      chat_id=update.effective_chat.id
#    )

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
  """ 
    Execute on receiving a message.
    It reply with a message generated using ChatGPT.
  """

  ### Use OpenAI API to generate chat response for a message
  chat = openai.ChatCompletion.create(
    model="gpt-3.5-turbo", ### GPT model used for generating response
    messages=[
      {
        "role": "system", ### Instruct the behavior of a assistant.
        "content": "You are Bot-E, a telegram bot powered by openai. You can answer questions and generate images. Image is generated using /img command following a prompt."
      },
      {
        "role": "user", ### The end user who chat with the assistant.
        "content": update.effective_message.text # Text send by the user
      }
    ],
    n=1 ### Number of different message choices
  )

  ### Get content of first (0th index) choice of messages
  reply_text = chat.choices[0].message.content

  ### Send a text message to the user.
  await context.bot.sendMessage(
    text=reply_text,
    chat_id=update.effective_chat.id
  )

async def caps(update: Update , context: ContextTypes.DEFAULT_TYPE):
  """ 
    Execute on /caps command which is followed by a text argument.
    It gets text with the command and sends its uppercase to the user.

  """

  ### context.args contains the argument passed with the command in the form of a list.
  ### join() function is used to convert the list of words into a string separated by spaces.
  text = ' '.join(context.args)

  ### upper() function is used for converting into uppercase.
  uppercase = text.upper()

  ### Send a text message to the user.
  await context.bot.sendMessage(
    text=uppercase,
    chat_id=update.effective_chat.id
  )

async def image(update: Update, context: ContextTypes.DEFAULT_TYPE):
  """ 
    Execute on /img command which is followed by a text argument.
    It generates a image using the openAI with the text gets with the command and send it to the user.
  """

  ### context.args contains the argument passed with the command in the form of a list.
  ### join() function is used to convert the list into a string separated by spaces
  prompt = ''.join(context.args)

  ### Use OpenAI API to generate image from a text
  image = openai.Image.create(
    prompt=prompt,
    size="1024x1024", ### Size of the image generated. Allowed sizes are 256x256, 512x512, 1024x1024(default)
    n=1 ### Number of images generated (default:1)
  )

  ### OpenAI returns url of the image
  image_url = image.data[0].url

  ### Send a photo to the user
  await context.bot.sendPhoto(
    photo=image_url,
    chat_id=update.effective_chat.id
  )

### check whether the current script is being run as the main program or if it is being imported as a module in another program
if __name__ == "__main__": 

  ### Create Application for Telegram Bot using the token
  app = ApplicationBuilder().token(bot_token).build()

  ### CommandHandler: Used to handle telegram commands.
  ### 1st argument is command name or list of commands.
  ### 2nd argument is callback function that should be called for a command.

  start_handler = CommandHandler("start",start)
  caps_handler = CommandHandler("caps",caps)
  image_handler = CommandHandler("img",image)

  ### MessageHandler: Used to handle telegram messages that include text, media and status updates
  ### 1st argument is filters that allows to specify conditions that incoming updates must match.
  ### 2nd argument is callback function that should be called for matched update.

  ### echo handler is commented because there is a chat handler to handle text messages
  # echo_handler = MessageHandler(
  #   filters.TEXT & (~filters.COMMAND), # message should be a text  and not command
  #   echo
  # )

  chat_handler = MessageHandler(
    filters.TEXT & (~filters.COMMAND), # message should be a text  and not command
    chat
  )

  ### Adding handlers to application.

  app.add_handler(start_handler)

  ### Following is commented because there is a chat function to handle text messages
  #app.add_handler(echo_handler)

  app.add_handler(caps_handler)
  app.add_handler(image_handler)
  app.add_handler(chat_handler)

  ### Initialize and start the application in polling mode.
  ### In polling the bot continuously sends HTTP requests to the Telegram server to check if there are any new updates that need to be processed. If there are updates, they are received by the bot and processed accordingly.
  app.run_polling()
