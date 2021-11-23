#!/usr/bin/env python
import logging
import subprocess

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

counter = 0

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

def get_power(text: str) -> None:
    is_number = False
    num = ""
    result = 0.0
    for c in text:
        if c == '.' or c.isdigit():
            num += str(c)
            is_number = True

        else:
            if is_number:
                result += float(num)
                num = ""

            is_number = False
    
    return result

# metodo para revisar la potencia del rig
def callback_hour(context: CallbackContext) -> None:
    command = "nvidia-smi --query-gpu=power.draw --format=csv | grep '[0-9]'"
    chat_id = -1001775199662
    text = ""
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in p.stdout.readlines():
        text += str(line)

    global counter
    counter+=1

    result = get_power(text)
    if result < 480:
        context.bot.send_message(chat_id=chat_id, text='POTENCIA BAJA -> '+'Power draw: '+str(result)+'W')
    else:
        # enviamos el mensaje a telegram cada 50 min
        if counter % 5 == 0:
            context.bot.send_message(chat_id=chat_id, text='Total power draw: '+str(result)+'W')

#def callback_tenm(context: CallbackContext) -> None:
#    command = "nvidia-smi --query-gpu=power.draw --format=csv | grep '[0-9]'"
#    chat_id = -1001775199662
#    text = ""
#    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#    for line in p.stdout.readlines():
#        text += str(line)
#
#    result = get_power(text)
#        
#    context.bot.send_message(chat_id=chat_id, text=result)

def start(update: Update, context: CallbackContext) -> None:
    context.job_queue.run_repeating(callback_hour, interval=600, first=5)

# metodo de reinicio del rig
def restart(context: CallbackContext) -> None:
    command = "reboot"
    chat_id = -1001775199662
    context.bot.send_message(chat_id=chat_id, text="Reiniciando el RIG...")
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)




def init(context: CallbackContext) -> None:
    context.job_queue.run_once(restart)


def main() -> None:
    token = "2013997999:AAEjtfHPYNBmGHjflmWD2dzxLEU8l3_hvFc"
    updater = Updater(token)
    # comando para iniciar el bot
    updater.dispatcher.add_handler(CommandHandler("start", start))
    # comando para reiniciar el rig
    updater.dispatcher.add_handler(CommandHandler("restart", restart))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
