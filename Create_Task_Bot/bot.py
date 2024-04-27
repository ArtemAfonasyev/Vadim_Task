#########################################################################
#                              IMPORTS                                  #
#########################################################################

import gspread
import asyncio
import discord  # основной модуль для работы с ботом
import random
import re  # регулярные выражения
from discord.ext import commands, tasks  # команды
from discord import Option
from datetime import datetime, timedelta
import json  # для работы с json
from src import text_file, links  # нужные ссылки и текстовые файлы
from src import feedback_v2
import test

#########################################################################
#                              SETTINGS                                 #
#########################################################################

config = json.load(open('config/config.json', 'r'))
bot = commands.Bot(config['prefix'], intents=discord.Intents.all())

#########################################################################
#                              LINKS                                    #
#########################################################################

icon_rts = links.LINKS[5]["icon_rts"]
readme = links.LINKS[6]["readme"]
TEST_LESSONS = links.TEST_LESSONS
REG_LESSONS = links.REG_LESSONS
LINKS = links.LINKS

#########################################################################
#                              TEXT                                     #
#########################################################################

EMBED_FOOTER = text_file.EMBED_FOOTER

@bot.slash_command(name="alarm_lessons", description="Поиск замены уроку по роли предмета в alarm_lessons")
async def alarm_lessons(interaction: discord.Interaction,
                        role: Option(discord.Role, description="Роль предмета по которому будет урок", required=True,
                                     name="роль"),
                        date: Option(str, description="Дата проведения урока (dd.mm)", required=True, name="дата"),
                        time: Option(str, description="Дата проведения урока (dd.mm)", required=True, name="время"),
                        language: Option(str, description="RU/ENG/UKR/другой язык", required=True,
                                         choices=["RU", "ENG", "UKR", "другой язык"], name="язык-урока"),
                        type_lessons: Option(str, description="Регулярный/Пробный", required=True,
                                             choices=["Рег - ИНД25","Рег - ИНД50", "Рег - ИНД80", "Рег - ГРУППА", "Рег - GrPRO", "ПУ",
                                                      "ГПУ"], name="тип-урока"),
                        add_info: Option(str, description="Любая доп. информация", required=True, name="доп-инфо"),
                        link: Option(str, description="Ссылка в любом формате (teacher/company не имеет значения)",
                                     required=True, name="ссылка-альфа")):
    interaction.response.defer()
    if not_dm_message(interaction):
        embed = discord.Embed(
            title="❌ К сожалению, ты не можешь использовать эту команду в личных сообщениях. Ее могут использовать только менеджеры или администраторы в канале alarm_lessons",
            color=discord.Color.blue())
        embed.set_footer(text=random.choice(EMBED_FOOTER), icon_url=icon_rts)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    date_pattern = re.compile(r'\d{2}\.\d{2}$')
    time_pattern = re.compile(r'\d{2}:\d{2}$')

    if not date_pattern.match(date):
        await interaction.response.send_message("❌ Неправильный формат даты. Используйте dd.mm", ephemeral=True)
        return

    if not time_pattern.match(time):
        await interaction.response.send_message("❌ Неправильный формат времени. Используйте hh:mm", ephemeral=True)
        return

    if language.lower() != "ru" and language.lower() != "eng" and language.lower() != "ukr" and language.lower() != "другой язык":
        await interaction.response.send_message(
            "❌ Неправильный формат языка. Используйте RU (ru), ENG (eng), UKR (ukr) или ETC (etc)", ephemeral=True)
        return

    await interaction.response.send_message("✅", ephemeral=True)
    user = interaction.user
    embed = discord.Embed(title="🅰️ ALARM LESSON", color=discord.Color.orange())

    if language.lower() == "eng":
        sdt_label = "Subject/Date/Time:"
        type_label = "Type lesson:"
        language_label = "Language:"
        link_label = "Link:"
        addInf_label = "Additional Information:"
        text = f'{role.mention} {interaction.user.mention} waiting for your responses in this thread!'
    else:
        sdt_label = "Предмет/Дата/Время:"
        type_label = "Тип урока:"
        language_label = "Язык урока:"
        link_label = "Ссылка:"
        addInf_label = "Дополнительная информация:"
        text = f'{role.mention} {interaction.user.mention} ждем ваших ответов в ветке!'

    embed.add_field(name=sdt_label, value=f"{role.mention} / {date} / {time}")
    embed.add_field(name=type_label, value=f"{type_lessons}")
    embed.add_field(name=language_label, value=f"{language}")
    embed.add_field(name=addInf_label, value=f"{add_info}")
    embed.add_field(name=link_label, value=f"{link}".replace("https://rtschool.s20.online/company",
                                                             "https://rtschool.s20.online/teacher"))

    message = await interaction.channel.send(embed=embed)

    new_thread = await interaction.channel.create_thread(name=f"{role.name} {date} {time}", message=message,
                                                         type=discord.ChannelType.public_thread)

    await new_thread.send(text)

    message_link = f"https://discord.com/channels/{interaction.guild.id}/{new_thread.id}/{message.id}"
    
    print(2)
    
    gc = gspread.service_account(filename=r'/home/gs_bot_token.json')
    sh = gc.open("Alarm Lessons")
    worksheet = sh.worksheet("Analytics")
    
    worksheet.append_row(
        [str(message_link), str(date), str(time), str(role.name), str(type_lessons), str(language), str(link)])

    for member in role.members:
        try:
            if language.lower() == "eng":
                new_embed = modify_embed_field(embed, "Subject/Date/Time:", f"{role.name} / {date} / {time}")
                new_embed.add_field(name="Link to message:", value=message_link)
            else:
                new_embed = modify_embed_field(embed, "Предмет/Дата/Время:", f"{role.name} / {date} / {time}")
                new_embed.add_field(name="Ссылка на сообщение:", value=message_link)
            await member.send(embed=new_embed)
            await asyncio.sleep(20)  # Пауза в 20 секунд
        except Exception as e:
            await user.send(f"❌ Не могу отправить сообщение пользователю {member.name}: {str(e)}")

    await user.send("✅ Рассылка окончена")


@bot.slash_command(name="set_teacher", description="Поставить педагога alarm урока")
async def set_teacher(interaction: discord.Interaction,
                      link: Option(str, description="Ссылка на ответ педагога", required=True)):
    
    # interaction.response.defer()
    if not_dm_message(interaction):
        embed = discord.Embed(
            title="❌ К сожалению, ты не можешь использовать эту команду в личных сообщениях. Ее могут использовать только менеджеры или администраторы в канале alarm_lessons",
            color=discord.Color.blue())
        embed.set_footer(text=random.choice(EMBED_FOOTER), icon_url=icon_rts)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    gc = gspread.service_account(filename=r'/home/gs_bot_token.json')
    sh = gc.open("Alarm Lessons")
    worksheet = sh.worksheet("Analytics")
    print(0)
    all_values = worksheet.col_values(1)
    print(all_values)
    new_link = '/'.join(link.split('/')[:-1])
    # Поиск значения в листе и определение номера строки
    row_number = None
    print(new_link)
    for index, row in enumerate(all_values, start=1):
        if new_link in row:
            row_number = index
            break
    print('ROW NUMBER!',row_number)
    parts = link.split("/")
    print(parts)
    if row_number != None:
        guild_id = int(parts[4])
        thread_id = int(parts[5])

        message_id = int(parts[6])
        guild = bot.get_guild(guild_id)
        thread = guild.get_thread(thread_id)
        # Получаем сообщение по его ID
        print(guild,thread)
        message = await thread.fetch_message(int(message_id))
        user = message.author
        await interaction.response.send_message(f"✅ Педагог {user} поставлен. Не забудь поставить задачу в AlfaCRM!\nИспользуемая ссылка:{link}",
                                                ephemeral=False)
        # Получаем сервер (guild) и канал

        # Получаем информацию о пользователе, отправившем сообщение

        if guild is not None:
            # Получаем объект сообщения (message)

            if thread:
                message = await thread.fetch_message(message_id)
                if message:
                    # Получаем имя отправителя и время отправления сообщения
                    row_data = worksheet.row_values(row_number)
                    author_name = message.author.name
                    print(author_name)
                    date = row_data[1]
                    time = row_data[2]
                    date_str1 = f"{date} {time}"  # data_str1
                    message_time = message.created_at.strftime("%d.%m %H:%M")  # data_str2
                    message_time_gs = moskow_time(message_time)
                    print(message_time,date_str1)
                    time_difference_var = time_difference(date_str1, message_time)
                    worksheet.update_cell(row_number, 8, message_time_gs)  # Время
                    worksheet.update_cell(row_number, 9, author_name)  # Имя
                    worksheet.update_cell(row_number, 10, str(time_difference_var))  # разница во времени
    else:
        print('❌ Cсылка {')
        await interaction.response.send_message(f"❌ Cсылка {link} неверная!\nCкопируйте ссылку на сообщение педагога в ветке",
                                                ephemeral=False)




bot.run('token')

