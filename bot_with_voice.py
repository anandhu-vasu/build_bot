from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from telegram.constants import ChatAction
import openai

# Need to install ffmpeg on your system
import pydub # pip install pydub

bot_token = "paste_your_bot_token_here"

openai.api_key = "paste_your_api_key_here"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  
  await context.bot.sendMessage(
    text = "Welcome to OpenAI powered bot!",
    chat_id = update.effective_chat.id
  )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):

  await context.bot.sendMessage(
    text = update.effective_message.text,
    chat_id = update.effective_chat.id
  )

async def caps(update: Update,context: ContextTypes.DEFAULT_TYPE):
  text_caps = " ".join(context.args).upper()

  await context.bot.sendMessage(
    text = text_caps,
    chat_id = update.effective_chat.id
  )

async def image(update: Update, context: ContextTypes.DEFAULT_TYPE):
  
  await context.bot.sendChatAction(
    action = ChatAction.UPLOAD_PHOTO, # Show a photo uploading indicator
    chat_id = update.effective_chat.id
  )
  
  prompt = " ".join(context.args)
  
  if not prompt:
    await context.bot.sendMessage(
      text = "Please provide a prompt!", chat_id = update.effective_chat.id
    )
    
  else:
    response = openai.Image.create(
      prompt = prompt,
      n = 1,
      size = "256x256"
    )

    # ReplyKeyboardMarkup is used to create a custom keyboard to reply with custom messages

    await context.bot.sendPhoto(
      photo = response.data[0].url,
      chat_id = update.effective_chat.id,
      reply_markup = ReplyKeyboardMarkup(
        [["/img {}".format(prompt)]], # create button to reply previous /img command used
        resize_keyboard = True
      )
    )
  

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
  
  await context.bot.sendChatAction(
    action = ChatAction.TYPING, # Show a typing indicator
    chat_id = update.effective_chat.id
  )

  completion = openai.ChatCompletion.create(
    model = "gpt-3.5-turbo",
    messages = [
      {
        "role": "system",
        "content": "You are Bot-E, a telegram bot created by Anandhu, powered by OpenAI. You can answer questions, generate image from text. /img command followed by a prompt is used to generate image. "
      },
      {
        "role": "user",
        "content": update.effective_message.text
      }
    ]
  )
  
  await context.bot.sendMessage(
    text = completion.choices[0].message.content,
    chat_id = update.effective_chat.id,
    reply_markup = ReplyKeyboardRemove() # Remove reply keyboard when chat starts
  )
  
async def voice(update: Update, context: ContextTypes.DEFAULT_TYPE):

  await context.bot.sendChatAction(
    action = ChatAction.TYPING, # Show a typing indicator
    chat_id = update.effective_chat.id
  )
  
  # Download voice as ogg file format from telegram
  ogg_file = await update.effective_message.voice.get_file()
  await ogg_file.download_to_drive("voice.ogg")
  
  # Convert ogg to mp3 format and save as voice.mp3
  pydub.AudioSegment.from_file("voice.ogg", format = "ogg").export("voice.mp3", format = "mp3")
  
  # Reading from mp3 file
  mp3_file = open("voice.mp3","rb")
  
  # Send mp3 audio file to OpenAI Speech-to-Text
  transcript = openai.Audio.transcribe("whisper-1",mp3_file)
  

  completion = openai.ChatCompletion.create(
    model = "gpt-3.5-turbo",
    messages = [
      {
        "role": "system",
        "content": "You are Bot-E, a telegram bot created by Anandhu Vasu, powered by OpenAI. You can answer questions, generate image from text. /img command followed by a prompt is used to generate image. "
      },
      {
        "role": "user",
        "content": transcript.text # text returned by OpenAI for the audio file sent
      }
    ]
  )

  await context.bot.sendMessage(
    text = completion.choices[0].message.content,
    chat_id = update.effective_chat.id,
    reply_markup = ReplyKeyboardRemove()  # Remove reply keyboard on voice 
  )

if __name__ == "__main__":
  app = ApplicationBuilder().token(bot_token).build()

  start_handler = CommandHandler("start", start)
  caps_handler = CommandHandler("caps", caps)

  image_generate_handler = CommandHandler("img", image)
  
  echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
  chat_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), chat)
  voice_handler = MessageHandler(filters.VOICE, voice)


  app.add_handler(start_handler)
  # app.add_handler(echo_handler)
  app.add_handler(caps_handler)
  app.add_handler(chat_handler)
  app.add_handler(image_generate_handler)
  app.add_handler(voice_handler)
  
  app.run_polling()


