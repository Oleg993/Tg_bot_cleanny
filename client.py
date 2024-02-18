from telebot.types import (InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton)
import os
from datetime import datetime

from database import DataBase as db

# Список названий кнопок
client_btns = ['Рассчитать стоимость уборки', 'Мои заказы', 'Мы в соц. сетях', 'Связаться с администратором']