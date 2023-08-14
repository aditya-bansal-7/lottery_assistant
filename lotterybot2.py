# BNsl Boy 
from pymongo import MongoClient
from pyrogram import Client , filters ,enums 
import pyrogram.types as types2
import uuid
from datetime import datetime , timedelta
import threading
import time

API_ID = '1149607'

API_HASH = 'd11f615e85605ecc85329c94cf2403b5'

bot2 = Client("my_teszxascxt", api_id=API_ID, api_hash=API_HASH,bot_token="6074378866:AAFTSXBqm0zYC2YFgIkbH8br5JeBOMjW3hg")

password = 'VeJ7EH5TK13U4IQg'
cluster_url = 'mongodb+srv://bnslboy:' + \
    password + '@cluster0.avbmi1g.mongodb.net/'

# Create a MongoDB client
client = MongoClient(cluster_url)

# Access the desired database
db = client['main']

giveaways = db['giveaways']

invites = db['invites']

roles = db['roles']

owners = db['admins']

queries = db['query']

messages = db['messages']

dices = db['dices']

app = "not_set"

user_status = {}

score_board = {}

@bot2.on_message(filters.command(['start']) & filters.group)
def start_for_group(client , message):
    try:
        admins = bot2.get_chat_members(message.chat.id,filter=enums.ChatMembersFilter.ADMINISTRATORS)
        for admin in admins:
            user_id = admin.user.id
            list = owners.find_one({'chat_id': message.chat.id})
            if list:
                adminlist = list['admins']
                if user_id not in adminlist:
                    owners.update_one(
                        {'chat_id': message.chat.id},
                        {'$addToSet':{'admins': user_id},'$set':{'chat_title': message.chat.title}},upsert=True
                    )
            else:
                owners.update_one(
                        {'chat_id': message.chat.id},
                        {'$addToSet':{'admins': user_id}},upsert=True
                    )
    except Exception:
        pass
    msg_text = '✅ 机器人已启动\n✅ 管理员列表已更新'
    bot2.send_message(message.chat.id,msg_text)
          

@bot2.on_message(filters.command(['start']) & filters.private)
def start_for_private(client, message):
    if message.text == "/start":
        keyboard = types2.InlineKeyboardMarkup(
            [
                [
                    types2.InlineKeyboardButton(
                        text='Add Bot to Group',
                        url='https://telegram.me/Academy_lottery_assistant_bot?startgroup=start'
                    )
                ]
            ]
        )
        first_name = message.from_user.first_name
        msg_text = f"""👋🏻 你好，{first_name}！
    @Academy_lottery_assistant_bot 是最全面的机器人，可以帮助您轻松管理群组内的赠品活动！

    👉🏻 将我添加到一个超级群组中，并将我提升为管理员，让我开始工作吧！

    ❓ 有哪些命令可用？ ❓
    按下 /settings 查看所有命令以及它们的用法！"""
        bot2.send_message(message.chat.id, msg_text, reply_markup=keyboard)
    else:
        giveaway_id = message.text.split(" ")[1]
        giveaway = giveaways.find_one({'giveaway_id':giveaway_id})
        if giveaway is None:
            bot2.send_message(message.from_user.id, "抱歉，此赠品活动已不再有效。")
            return
        if giveaway:
            user_id = message.from_user.id
            giveaway = giveaways.find_one({'giveaway_id':giveaway_id})
            chat_id = giveaway['chat_id']
            role = giveaway["role"]
            if role == None:
                pass
            else:
                role_user = roles.find_one({'chat_id':chat_id,'user_id':user_id,'roles':role})
                if role_user is None:
                    bot2.send_message(user_id, f"要参加此抽奖，您必须拥有 {role} 角色。")
                    return
            if user_id in giveaway["participants"]:
                bot2.send_message(user_id, "您已经参加过了此赠品活动。")
                return
            giveaway["participants"].append(user_id)
            giveaways.update_one({"giveaway_id": giveaway_id}, {"$set": {"participants": giveaway["participants"],'is_edit':True}})
            bot2.send_message(user_id, "您已成功参加了赠品活动。")


@bot2.on_message(filters.command(['settings']) & filters.private)
def create_role(client,message):
    is_markup = False
    list = owners.find({'admins':message.from_user.id})
    #Select a Chat in which you want to create a role --
    msg_txt = """👉🏻 选择要获取其邀请数据的群组。

如果您作为管理员的组未显示在此处：
 • 在组中发送/启动，然后重试
 • 机器人不是该组中的管理员"""
    markup = types2.InlineKeyboardMarkup(inline_keyboard=[])
    if list:
        for list2 in list:
            chat = list2['chat_id']
            if 'chat_title' in list2:
                title = list2['chat_title']
            else:
                try:
                    details = bot2.get_chat(chat)
                    title = details.title
                except Exception:
                    continue
            markup.inline_keyboard.append([types2.InlineKeyboardButton(f"{title}",callback_data=f"settings:{chat}")])
            is_markup = True
    if is_markup:
        bot2.send_message(message.chat.id,msg_txt,reply_markup=markup)
    else:
        bot2.send_message(message.chat.id,msg_txt)

  
@bot2.on_callback_query()
def on_query(client,call):
    if call.data.startswith(("rolechat:")):
        chat_id = call.data.split(":")[1]
        user_id = call.data.split(":")[2]
        markup = types2.ReplyKeyboardMarkup(keyboard=[types2.KeyboardButton("cancle")])
        #Please provide me the name of role 
        bot2.send_message(user_id,"请提供我的角色名称 -->")
    elif call.data.startswith(("adduser:")):
        role_name = call.data.split(":")[1]
        chat_id = int(call.data.split(":")[2])
        data = roles.find_one({'chat_id':chat_id,'role_name':role_name})
        if data:
            markup = types2.ReplyKeyboardMarkup([[types2.KeyboardButton("🚫Cancle")]],resize_keyboard=True,one_time_keyboard=True)
            #<b>Send me username of users whom you want to give {role_name} role </b>\n\n<i>you can forward any message from that user you want to give role</i>
            msg2 = bot2.send_message(call.message.chat.id,f"<b>发送给我你想要赋予{role_name}角色的用户的用户名</b>\n\n<i>你可以转发想要赋予角色的用户的任何消息</i>",reply_markup=markup)
            user_id = call.from_user.id
            user_status[user_id] = {'chat_id':chat_id,'msg2_id':msg2.id,'msg2_chat_id':msg2.chat.id,'role_name':role_name,'call':"add_user"}
        else:
            bot2.answer_callback_query(call.id,f"This {role_name} does not exist anymore !!",show_alert=True,cache_time=3)
    elif call.data.startswith(("removeuser:")):
        role_name = call.data.split(":")[1]
        chat_id = int(call.data.split(":")[2])
        data = roles.find_one({'chat_id':chat_id,'role_name':role_name})
        if data:
            markup = types2.ReplyKeyboardMarkup([[types2.KeyboardButton("🚫Cancle")],[types2.KeyboardButton("Remove all ❗️")]],resize_keyboard=True,one_time_keyboard=True)
            msg2 = bot2.send_message(call.message.chat.id,f"<b>向我发送要删除 {role_name} 角色的用户的用户名 </b><i> 您可以将任何邮件转发给要授予角色的用户</i>",reply_markup=markup)
            user_id = call.from_user.id
            user_status[user_id] = {'chat_id':chat_id,'msg2_id':msg2.id,'msg2_chat_id':msg2.chat.id,'role_name':role_name,'call':"remove_user"}
        else:
            bot2.answer_callback_query(call.id,f"This {role_name} does not exist anymore !!",show_alert=True,cache_time=3)


@bot2.on_message(filters.dice)
def dice_handler(client, message):
    data = dices.find_one({'chat_id': message.chat.id, 'is_done': {'$exists': False}})
    
    if data:
        emoji = data['emoji']
        participants = data['participants']
        if emoji == "⚽️":
            emoji = "⚽"    
        if emoji == message.dice.emoji:
            user_id = str(message.from_user.id)
            value = message.dice.value
            chances = data['chances']
            if data['role'] is not None:
                role_name = data['role']
                data2 = roles.find_one({'chat_id': message.chat.id, 'roles': role_name})
                if data2 is None:
                    bot2.send_message(message.chat.id, f"🚫 你需要拥有 {role_name} 角色才能参加此活动。", reply_to_message_id=message.id)
                    return
            
            if user_id in participants and participants[user_id]['chances_used'] >= chances:
                bot2.send_message(message.chat.id, "⚠️ 你已经用完所有机会。", reply_to_message_id=message.id)
                return

            
            if user_id in participants:
                participants[user_id]['chances_used'] += 1
            else:
                participants[user_id] = {'chances_used': 1, 'score': 0}

            participants[user_id]['first_name'] = message.from_user.first_name
            participants[user_id]['username'] = message.from_user.username
            participants[user_id]['score'] += value
            dices.update_one(
                {'chat_id': message.chat.id, 'is_done': {'$exists': False}},
                {'$set': {'participants': participants}}
            )
            if str(message.chat.id) not in score_board:
                score_board[str(message.chat.id)] = []
            if user_id not in score_board[str(message.chat.id)]:
                score_board[str(message.chat.id)].append(user_id)
            if len(score_board[str(message.chat.id)]) >= chances:
                send_score_board(message.chat.id)

def send_score_board(chat_id):
    user_ids = score_board[str(chat_id)]
    data = dices.find_one({'chat_id': chat_id, 'is_done': {'$exists': False}})
    
    message_text = "🎲 积分榜更新 🎲\n\n"
    if data:
        participants = data['participants']
        for user_id in user_ids:
            score = participants[user_id]['score']
            first_name = participants[user_id]['first_name']
            message_text += f"🔹 <a href='tg://user?id={user_id}'>{first_name}</a> - 分数: {score}\n"
    
    message_text += "\n使用 /ranks 查看前十名 🏆"

    bot2.send_message(chat_id, message_text)
    del score_board[str(chat_id)]

@bot2.on_message(filters.command(['dices']))
def dice_handler(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    is_admin = False
    is_how_to = False

    try:
        admins = bot2.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS)
        for admin in admins:
            user_id2 = admin.user.id
            if user_id2 == user_id:
                is_admin = True
    except Exception as e:
        bot2.send_message(chat_id, "Error in fetching group admin.")
        print("Error fetching admins:", e)
        return

    if not is_admin:
        bot2.send_message(chat_id, "您必须是管理员才能使用此命令。", reply_to_message_id=message.id)
        return

    args = message.text.split()[1:]
    emoji_list = ["🎲", "🎯", "🏀", "⚽️", "🎳"]

    duration_units = {"d": 86400, "h": 3600, "m": 60, "s": 1}
    if len(args) >= 4:
        try:
            emoji, chances, reward, duration = args[:4]
            chances = int(chances)
            reward = reward.replace("_", " ")
            duration = int(duration[:-1]) * duration_units[duration[-1]]
            role = None
        except (ValueError, KeyError, IndexError):
            bot2.send_message(chat_id, "命令格式无效。用法：/dice <emoji> <chances> <获奖人数> <时长>")
            return
        except Exception:
            bot2.send_message(chat_id, "命令格式无效。用法：/dice <emoji> <chances> <获奖人数> <时长>")
            return

    if emoji not in emoji_list:
        bot2.send_message(chat_id, "Emoji not accepted. Try using one of these 🎲, 🎯, 🏀, ⚽️, 🎳")
        return

    if len(args) == 5:
        text = args[4]
        if text.startswith("role:"):
            role = text.split(":")[1]
            data = roles.find_one({'chat_id': chat_id, 'role_name': role})
            if data:
                if 'how_to_get' in data:
                    is_how_to = True
                    keyboard = types2.InlineKeyboardMarkup(
                        [
                            [
                                types2.InlineKeyboardButton(
                                    text=f'如何获得 {role}',
                                    callback_data=f"giveaway_how_to:{role}:{chat_id}"
                                )
                            ]
                        ]
                    )
                else:
                    bot2.send_message(chat_id, f"{role} 在此聊天中不存在。", reply_to_message_id=message.id)
                    return

    dice_id = str(uuid.uuid4())
    time_left = duration
    time_left_str = f"{time_left // 86400}d:{(time_left % 86400) // 3600}h:{(time_left % 3600) // 60}m:{time_left % 60}s"

    document = {
        "dice_id": dice_id,
        "emoji": emoji,
        "chat_id": chat_id,
        "reward": reward,
        "chances": chances,
        "duration": duration,
        "role": role,
        "participants": {},
        "start_time": datetime.now(),
        "winners": [],
        "message_id": message.id + 1
    }
    dices.insert_one(document)

    message_text = f"🎉 表情幸运抽奖 🎉\n\n🍀 发送 {emoji} 表情参与抽奖，获得积分 🍀\n\n🎁 加入 {reward} \n\n🏆 {chances} 次机会参与！🌟\n\n⏰ 倒计时 - {time_left_str} 🔥\n\n🎊 取得高分 & 赢得大奖！🎁\n\n💥 不要错过！🎉"

    if role:
        message_text += f"\n\n🌟要参加此幸运抽奖，您需要拥有 {role} 角色"

    if is_how_to:
        bot2.send_message(chat_id, message_text, reply_markup=keyboard)
    else:
        bot2.send_message(chat_id, message_text)
    bot2.send_dice(chat_id, emoji)
    bot2.delete_messages(chat_id, message.id)
    time_thread = threading.Thread(target=time_check)
    time_thread.start()

def end_dice(dice_id):
    dice = dices.find_one({'dice_id': dice_id})
    if dice:
        chat_id = dice["chat_id"]
        if dice["participants"] == {}:
            message_text = "无人参与此次抽奖，本次幸运抽奖已取消。🍀"
            dice_id2 = str(uuid.uuid4())
            dices.update_one({'dice_id': dice_id}, {'$set': {'dice_id': dice_id2, 'is_done': True}}, upsert=True)
            bot2.send_message(chat_id, message_text)
            return

        sorted_participants = sorted(dice["participants"].items(), key=lambda x: x[1]['score'], reverse=True)
        max_chars_per_message = 500  # Telegram character limit for messages
        message_chunks = []
        current_chunk = ""

        current_chunk += "<b>抽奖已结束🍀</b>\n<i>排行榜</i>\n\n"

        for i, (user_id, score) in enumerate(sorted_participants):
            first_name = score['first_name']
            if i == 0:
                current_chunk += f"🥇 - <a href='tg://user?id={user_id}'>{first_name}</a> - {score['score']}\n"
            elif i == 1:
                current_chunk += f"🥈 - <a href='tg://user?id={user_id}'>{first_name}</a> - {score['score']}\n"
            elif i == 2:
                current_chunk += f"🥉 - <a href='tg://user?id={user_id}'>{first_name}</a> - {score['score']}\n"
            else:
                current_chunk += f"🏅 - <a href='tg://user?id={user_id}'>{first_name}</a> - {score['score']}\n"

            if len(current_chunk) >= max_chars_per_message:
                message_chunks.append(current_chunk)
                current_chunk = ""

        if current_chunk:
            message_chunks.append(current_chunk)

        for chunk in message_chunks:
            bot2.send_message(chat_id, chunk)
        dice_id2 = str(uuid.uuid4())
        dices.update_one({'dice_id': dice_id}, {'$set': {'dice_id': dice_id2, 'is_done': True}}, upsert=True)
       
@bot2.on_message(filters.command(['ranks']))
def ranks_sender(client,message):
    data = dices.find_one({'chat_id': message.chat.id, 'is_done': {'$exists': False}})
    
    if data:
        if data["participants"] == {}:
            message_text = "没有任何用户参与。"
            bot2.send_message(message.chat.id, message_text)
            return

        sorted_participants = sorted(data["participants"].items(), key=lambda x: x[1]['score'], reverse=True)

        current_chunk = "🏆 前十名排行榜 - \n\n"

        for i, (user_id, score) in enumerate(sorted_participants):
            first_name = score['first_name']
            if i == 0:
                current_chunk += f"🥇 - <a href='tg://user?id={user_id}'>{first_name}</a> - {score['score']}\n"
            elif i == 1:
                current_chunk += f"🥈 - <a href='tg://user?id={user_id}'>{first_name}</a> - {score['score']}\n"
            elif i == 2:
                current_chunk += f"🥉 - <a href='tg://user?id={user_id}'>{first_name}</a> - {score['score']}\n"
            else:
                current_chunk += f"🏅 - <a href='tg://user?id={user_id}'>{first_name}</a> - {score['score']}\n"
            
            if i == 9:
                break
    
        bot2.send_message(message.chat.id, current_chunk)
    else:
        bot2.send_message(message.chat.id, "未找到进行中的抽奖活动。")

lock = threading.Lock()

def time_check():
    with lock:
        time.sleep(10)
        while True:
            dicess = dices.find()
            i = 1
            for giveaway in dicess:
                if 'is_done' in giveaway:
                    continue
                giveaway["duration"] -= 10
                time_left = giveaway["duration"]
                dice_id = giveaway['dice_id']
                i += 1
                dices.update_one({'dice_id': dice_id}, {'$set': {'duration': giveaway["duration"]}}) 
                if time_left <= 0:
                    end_dice(dice_id)
            if i == 1:
                return False
            time.sleep(10)


time_thread = threading.Thread(target=time_check)
time_thread.start()

def add_user_to_role(message,role_name,chat_id,msg2_id,msg2_chat_id):
    print(message)
    markup = types2.ReplyKeyboardRemove()
    try:
        username = message.text.split(" ")
        #User -  
        message_test = "用户-\n"
        if message.forward_from is not None:
            usser_id = message.forward_from.id
            usser_name = message.forward_from.username
            find = roles.find_one({'chat_id': chat_id, 'user_id': usser_id, 'roles': role_name})
            if find:
                    #{usser_name} already have {role_name} role
                    bot2.delete_messages(msg2_chat_id,msg2_id)
                    bot2.send_message(message.from_user.id, f"{usser_name} 已具有 {role_name} 角色", reply_to_message_id=message.id,reply_markup=markup)
                    del user_status[message.chat.id]
                    return
            roles.update_one({'chat_id': chat_id, 'user_id': usser_id},
                                {'$addToSet': {'roles': role_name},
                                '$set': {'first_name': usser_name}}, upsert=True)
            roles.update_one({'chat_id':chat_id,'role_name':role_name},
                             {'$inc':{'count':1}},upsert=True)
            
            message_test += f" • {usser_name}\n"
            message_test += f"n 已在此聊天中被赋予 {role_name} 角色"
            if "•" in message_test:
                bot2.send_message(message.from_user.id,message_test,reply_markup=markup)
                del user_status[message.chat.id]
            return
        for user in username:
            if not user.startswith("@"):
                for entity in message.entities:
                    if str(entity.type) == "MessageEntityType.TEXT_MENTION":
                        try:
                            name = entity.user.first_name
                            if name == user:
                                usser_id = entity.user.id
                                find = roles.find_one(
                                            {'chat_id': chat_id, 'user_id': usser_id, 'roles': role_name})
                                if find:
                                    bot2.delete_messages(msg2_chat_id,msg2_id)
                                    #{usser_name} already have {role_name} role
                                    bot2.send_message(
                                        message.from_user.id, f"{name} 已具有 {role_name} 角色", reply_to_message_id=message.id,reply_markup=markup)
                                    continue
                                message_test += f" • {user}\n"
                                roles.update_one({'chat_id': chat_id, 'user_id': usser_id},
                                                {'$addToSet': {'roles': role_name},
                                                '$set': {'first_name': name}}, upsert=True)
                                roles.update_one({'chat_id':chat_id,'role_name':role_name},
                             {'$inc':{'count':1}},upsert=True)
                        except Exception:
                            continue
                continue
            try:
                
                usser = bot2.get_chat(user)
                usser_id = usser.id
                usser_name = usser.username
                find = roles.find_one(
                    {'chat_id': chat_id, 'user_id': usser_id, 'roles': role_name})
                if find:
                    bot2.delete_messages(msg2_chat_id,msg2_id)
                    #{usser_name} already have {role_name} role
                    bot2.send_message(
                        message.from_user.id, f"{usser_name} 已具有 {role_name} 角色", reply_to_message_id=message.id,reply_markup=markup)
                    continue
                message_test += f" • {usser_name}\n"
                roles.update_one({'chat_id': chat_id, 'user_id': usser_id},
                                    {'$addToSet': {'roles': role_name},
                                    '$set': {'first_name': usser_name}}, upsert=True)
                roles.update_one({'chat_id':chat_id,'role_name':role_name},
                                {'$inc':{'count':1}},upsert=True)
            except Exception as e:
                bot2.send_message(message.chat.id,f"unexpected error happens \n{e}")
                continue
        message_test += f"\n已在此聊天中被赋予 {role_name} 角色"
        if "•" in message_test:
            bot2.delete_messages(msg2_chat_id,msg2_id)
            bot2.send_message(message.from_user.id,message_test,reply_markup=markup)
        del user_status[message.chat.id]
    except Exception:
        bot2.delete_messages(msg2_chat_id,msg2_id)
        bot2.send_message(message.chat.id,"Got an error forward message is in beta please try again after some time",reply_markup=markup)
        del user_status[message.chat.id]


def remove_user_to_role(message, role_name, chat_id,msg2_id,msg2_chat_id):
    markup = types2.ReplyKeyboardRemove()
    try:
        if message.text == "🚫Cancle":
            bot2.delete_messages(msg2_chat_id, msg2_id)
            bot2.delete_messages(message.chat.id, message.id)
            return
        elif message.text =="Remove all ❗️":
            users_with_role = roles.find({'chat_id': chat_id, 'roles': role_name})
            if not users_with_role:
                bot2.delete_messages(msg2_chat_id, msg2_id)
                bot2.delete_messages(message.chat.id, message.id)
                # No users have the specified role
                bot2.send_message(
                    message.chat.id, f"在此聊天中没有用户具有 {role_name} 角色", reply_to_message_id=message.id)
                return

            # Remove the role from all users with the specified role
            for user_data in users_with_role:
                user_id = user_data['user_id']
                user_name = user_data['first_name']
                roles.update_one({'chat_id': chat_id, 'user_id': user_id},
                                {'$pull': {'roles': role_name},
                                '$set': {'first_name': user_name}},
                                upsert=True)
            
            roles.update_one({'chat_id':chat_id,'role_name':role_name},
                                    {'$set':{'count':0}},upsert=True)
            bot2.delete_messages(msg2_chat_id, msg2_id)
            # Role {role_name} has been removed from all users in this chat
            bot2.send_message(
                message.chat.id, f"在此聊天中的所有用户都已被移除 {role_name} 角色", reply_to_message_id=message.id)
            return
        username = message.text.split(" ")
        # User -
        message_test = "用户-\n"
        
        if message.forward_from is not None:
            user_id = message.forward_from.id
            user_name = message.forward_from.first_name
            find = roles.find_one({'chat_id': chat_id, 'user_id': user_id, 'roles': role_name})
            if not find:
                # {user_name} does not have {role_name} role
                bot2.delete_messages(msg2_chat_id, msg2_id)
                bot2.send_message(message.from_user.id, f"{user_name} 没有 {role_name} 角色", reply_to_message_id=message.id, reply_markup=markup)
                return
            
            roles.update_one({'chat_id': chat_id, 'user_id': user_id}, {'$pull': {'roles': role_name}})
            roles.update_one({'chat_id':chat_id,'role_name':role_name},
                             {'$inc':{'count':-1}},upsert=True)
            message_test += f" • {user_name}\n"
            message_test += f"n 已在此聊天中被移除 {role_name} 角色"
            if "•" in message_test:
                bot2.send_message(message.from_user.id, message_test, reply_markup=markup)
            return

        for user in username:
            if not user.startswith("@"):
                for entity in message.entities:
                    if str(entity.type) == "MessageEntityType.TEXT_MENTION":
                        try:
                            name = entity.user.first_name
                            if name == user:
                                user_id = entity.user.id
                                find = roles.find_one({'chat_id': chat_id, 'user_id': user_id, 'roles': role_name})
                                if not find:
                                    # {user_name} does not have {role_name} role
                                    bot2.delete_messages(msg2_chat_id, msg2_id)
                                    bot2.send_message(message.from_user.id, f"{user_name} 没有 {role_name} 角色", reply_to_message_id=message.id, reply_markup=markup)
                                    continue
                                message_test += f" • {user}\n"
                                roles.update_one({'chat_id': chat_id, 'user_id': user_id}, {'$pull': {'roles': role_name}})
                                roles.update_one({'chat_id':chat_id,'role_name':role_name},
                             {'$inc':{'count':-1}},upsert=True)
                        except Exception:
                            continue
                continue
            try:
                bot2.start()
                user_obj = bot2.get_chat(user)
                user_id = user_obj.id
                user_name = user_obj.username

                find = roles.find_one({'chat_id': chat_id, 'user_id': user_id, 'roles': role_name})
                if not find:
                    # {user_name} does not have {role_name} role
                    bot2.delete_messages(msg2_chat_id, msg2_id)
                    bot2.send_message(message.from_user.id, f"{user_name} 没有 {role_name} 角色", reply_to_message_id=message.id, reply_markup=markup)
                    continue

                message_test += f" • {user_name}\n"
                roles.update_one({'chat_id': chat_id, 'user_id': user_id}, {'$pull': {'roles': role_name}})
                roles.update_one({'chat_id':chat_id,'role_name':role_name},
                                {'$inc':{'count':-1}},upsert=True)
                bot2.stop()

            except Exception as e:
                print(e)
                bot2.send_message(message.chat.id,f"Unexpected Error Happen - {e}")
                pass
        message_test += f"\n已在此聊天中被移除 {role_name} 角色"
        if "•" in message_test:
            bot2.delete_messages(msg2_chat_id, msg2_id)
            bot2.send_message(message.from_user.id, message_test, reply_markup=markup)

    except Exception as e:
        print(e)
        bot2.delete_message(msg2_chat_id, msg2_id)
        bot2.send_message(message.chat.id, "Got an error forward message is in beta please try again after some time", reply_markup=markup)
        pass

def role_giver(chat_id , user_id):
    data = roles.find({"chat_id":chat_id})
    is_give_role = False
    for da in data:
        if 'role_name' in da:
            role_name = da['role_name']
            if 'is_auto_invite' in da and da['is_auto_invite'] == True:
                
                count = da['invite_count']
                da2 = invites.find_one({'chat_id':chat_id,'user_id':user_id})
                if da2:
                    invite_count = da2['regular_count']
                    if invite_count >= count :
                        is_give_role = True
                    else:
                        is_give_role = False
                else:
                    is_give_role = False
            if 'is_auto_message' in da and da['is_auto_message'] == True:
                count = da['message_count']
                da2 = messages.find_one({'chat_id':chat_id,'user_id':user_id})
                if da2:
                    messages_count = da2['msg_count']
                    if messages_count >= count:
                        is_give_role = True
                    else:
                        is_give_role = False
                else:
                    is_give_role = False
            if is_give_role == True:
                data = roles.find_one({'chat_id': chat_id, 'user_id': user_id,'roles': role_name})
                if data:
                    return
                usser = bot2.get_users(user_id)
                usser_name = usser.username
                roles.update_one({'chat_id': chat_id, 'user_id': user_id}, {'$addToSet': {'roles': role_name},'$set': {'first_name': usser_name}}, upsert=True)
                roles.update_one({'chat_id':chat_id,'role_name':role_name},
                             {'$inc':{'count':1}},upsert=True)
                is_give_role = False

@bot2.on_message(filters.command(['role']))
def roles_given(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    is_admin = False
    try:
        admins = bot2.get_chat_members(message.chat.id,filter=enums.ChatMembersFilter.ADMINISTRATORS)
        for admin in admins:
            user_id2 = admin.user.id
            if user_id2 == user_id:
                is_admin = True
    except Exception:
        bot2.send_message(message.chat.id,"Error in fenching group admin .")
        return

    if not is_admin:
        bot2.send_message(message.chat.id, "您必须是管理员才能使用此命令。",reply_to_message_id=message.id)
        return
    
    reply = message.reply_to_message
    if reply:
        user = reply.from_user.id
        user_name = reply.from_user.username
        if user_name is None:
            user_name = reply.from_user.first_name
        role_name = message.text.split(" ")[1].lower()
        if role_name is None:
            #You did not provide me role name
            bot2.send_message(
                chat_id, "您没有提供我角色名称", reply_to_message_id=message.id)
            return

        data = roles.find_one({'chat_id':chat_id,'role_name':role_name})
        if data is None:
            bot2.send_message(chat_id,"此角色不存在。")
            return
        
        find = roles.find_one(
            {'chat_id': chat_id, 'user_id': user, 'roles': role_name})
        if find:
            #{user_name} already have {role_name} role
            bot2.send_message(
                chat_id, f"{user_name} 已具有 {role_name} 角色", reply_to_message_id=message.id)
            return
        roles.update_one({'chat_id': chat_id, 'user_id': user},
                         {'$addToSet': {'roles': role_name},
                          '$set': {'first_name': user_name}},
                         upsert=True)
        roles.update_one({'chat_id':chat_id,'role_name':role_name},
                             {'$inc':{'count':1}},upsert=True)
        #{user_name} has been given the role of {role_name} in this chat
        bot2.send_message(message.chat.id, f"{user_name} 在此聊天中被赋予了 {role_name} 的角色")
    else:
        role_name = message.text.split(" ")[1].lower()
        if role_name is None:
            #you did not provide me role name
            bot2.send_message(
                chat_id, "您没有提供我角色名称", reply_to_message_id=message.id)
            return
        
        data = roles.find_one({'chat_id':chat_id,'role_name':role_name})
        if data is None:
            bot2.send_message(chat_id,"此角色不存在。")
            return
        
        username = message.text.split(" ")[2:]
        if username is None:
            #You did not provide me users
            bot2.send_message(chat_id, "您没有为我提供用户",
                             reply_to_message_id=message.id)
            return
        #User -  
        message_test = "用户-\n"
        for user in username:
            if not user.startswith("@"):
                for entity in message.entities:
                    if str(entity.type) == "MessageEntityType.TEXT_MENTION":
                        try:
                            name = entity.user.first_name
                            if name == user:
                                usser_id = entity.user.id
                                find = roles.find_one(
                                            {'chat_id': chat_id, 'user_id': usser_id, 'roles': role_name})
                                if find:
                                    #{usser_name} already have {role_name} role
                                    bot2.send_message(
                                        chat_id, f"{usser_name} 已具有 {role_name} 角色", reply_to_message_id=message.id)
                                    continue
                                message_test += f" • {user}\n"
                                roles.update_one({'chat_id': chat_id, 'user_id': usser_id},
                                                {'$addToSet': {'roles': role_name},
                                                '$set': {'first_name': usser_name}}, upsert=True)
                                roles.update_one({'chat_id':chat_id,'role_name':role_name},
                             {'$inc':{'count':1}},upsert=True)
                        except Exception:
                            continue
                continue
            usser = bot2.get_chat(user)
            usser_id = usser.id
            usser_name = usser.username

            find = roles.find_one(
                {'chat_id': chat_id, 'user_id': usser_id, 'roles': role_name})
            if find:
                #{usser_name} already have {role_name} role
                bot2.send_message(
                    chat_id, f"{usser_name} 已具有 {role_name} 角色", reply_to_message_id=message.id)
                continue

            message_test += f" • {usser_name}\n"
            roles.update_one({'chat_id': chat_id, 'user_id': usser_id},
                             {'$addToSet': {'roles': role_name},
                              '$set': {'first_name': usser_name}}, upsert=True)
            roles.update_one({'chat_id':chat_id,'role_name':role_name},
                             {'$inc':{'count':1}},upsert=True)
        message_test += f"n 已在此聊天中被赋予 {role_name} 角色"
        if "•" in message_test:
            bot2.send_message(chat_id,message_test)

@bot2.on_message(filters.command(['remove_role']))
def remove_roles(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    is_admin = False
    try:
        admins = bot2.get_chat_members(message.chat.id,filter=enums.ChatMembersFilter.ADMINISTRATORS)
        for admin in admins:
            user_id2 = admin.user.id
            if user_id2 == user_id:
                is_admin = True
    except Exception:
        bot2.send_message(message.chat.id,"Error in fenching group admin .")
        return

    if not is_admin:
        bot2.send_message(message.chat.id, "您必须是管理员才能使用此命令。",reply_to_message_id=message.id)
        return
    
    reply = message.reply_to_message
    if reply:
        user = reply.from_user.id
        user_name = reply.from_user.username
        if user_name is None:
            user_name = reply.from_user.first_name
        role_name = message.text.split(" ")[1].lower()
        if role_name is None:
            # You did not provide me role name
            bot2.send_message(
                chat_id, "您没有提供我角色名称", reply_to_message_id=message.id)
            return

        data = roles.find_one({'chat_id': chat_id, 'role_name': role_name})
        if data is None:
            bot2.send_message(chat_id, "此角色不存在。")
            return

        find = roles.find_one(
            {'chat_id': chat_id, 'user_id': user, 'roles': role_name})
        if not find:
            # {user_name} does not have {role_name} role
            bot2.send_message(
                chat_id, f"{user_name} 没有 {role_name} 角色", reply_to_message_id=message.id)
            return
        roles.update_one({'chat_id': chat_id, 'user_id': user},
                         {'$pull': {'roles': role_name},
                          '$set': {'first_name': user_name}},
                         upsert=True)
        roles.update_one({'chat_id':chat_id,'role_name':role_name},
                             {'$inc':{'count':-1}},upsert=True)
        # {user_name} has lost the role of {role_name} in this chat
        bot2.send_message(message.chat.id, f"{user_name} 在此聊天中失去了 {role_name} 的角色")
    else:
        role_name = message.text.split(" ")[1].lower()
        if role_name is None:
            # you did not provide me role name
            bot2.send_message(
                chat_id, "您没有提供我角色名称", reply_to_message_id=message.id)
            return

        data = roles.find_one({'chat_id': chat_id, 'role_name': role_name})
        if data is None:
            bot2.send_message(chat_id, "此角色不存在。")
            return

        username = message.text.split(" ")[2:]
        if not username:
            # You did not provide me users
            bot2.send_message(chat_id, "您没有为我提供用户",
                              reply_to_message_id=message.id)
            return

        # User -
        message_test = "用户-\n"
        for user in username:
            if not user.startswith("@"):
                for entity in message.entities:
                    if str(entity.type) == "MessageEntityType.TEXT_MENTION":
                        try:
                            name = entity.user.first_name
                            if name == user:
                                usser_id = entity.user.id
                                find = roles.find_one(
                                    {'chat_id': chat_id, 'user_id': usser_id, 'roles': role_name})
                                if not find:
                                    # {usser_name} does not have {role_name} role
                                    bot2.send_message(
                                        chat_id, f"{usser_name} 没有 {role_name} 角色", reply_to_message_id=message.id)
                                    continue
                                message_test += f" • {user}\n"
                                roles.update_one({'chat_id': chat_id, 'user_id': usser_id},
                                                 {'$pull': {'roles': role_name},
                                                  '$set': {'first_name': usser_name}}, upsert=True)
                                roles.update_one({'chat_id':chat_id,'role_name':role_name},
                             {'$inc':{'count':-1}},upsert=True)
                        except Exception:
                            continue
                continue
            usser = bot2.get_chat(user)
            usser_id = usser.id
            usser_name = usser.first_name

            find = roles.find_one(
                {'chat_id': chat_id, 'user_id': usser_id, 'roles': role_name})
            if not find:
                # {usser_name} does not have {role_name} role
                bot2.send_message(
                    chat_id, f"{usser_name} 没有 {role_name} 角色", reply_to_message_id=message.id)
                continue

            message_test += f" • {usser_name}\n"
            roles.update_one({'chat_id': chat_id, 'user_id': usser_id},
                             {'$pull': {'roles': role_name},
                              '$set': {'first_name': usser_name}}, upsert=True)
            roles.update_one({'chat_id':chat_id,'role_name':role_name},
                             {'$inc':{'count':-1}},upsert=True)
        message_test += f"n 在此聊天中被移除了 {role_name} 角色"
        if "•" in message_test:
            bot2.send_message(chat_id, message_test)

@bot2.on_message(filters.command(['remove_all']))
def remove_all_roles(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    is_admin = False
    try:
        admins = bot2.get_chat_members(message.chat.id,filter=enums.ChatMembersFilter.ADMINISTRATORS)
        for admin in admins:
            user_id2 = admin.user.id
            if user_id2 == user_id:
                is_admin = True
    except Exception:
        bot2.send_message(message.chat.id,"Error in fenching group admin .")
        return

    if not is_admin:
        bot2.send_message(message.chat.id, "您必须是管理员才能使用此命令。",reply_to_message_id=message.id)
        return
    
    role_name = message.text.split(" ")[1].lower()
    if not role_name:
        # You did not provide me role name
        bot2.send_message(
            chat_id, "您没有提供我角色名称", reply_to_message_id=message.id)
        return

    data = roles.find_one({'chat_id': chat_id, 'role_name': role_name})
    if data is None:
        bot2.send_message(chat_id, "此角色不存在。")
        return

    users_with_role = roles.find({'chat_id': chat_id, 'roles': role_name})
    if not users_with_role:
        # No users have the specified role
        bot2.send_message(
            chat_id, f"在此聊天中没有用户具有 {role_name} 角色", reply_to_message_id=message.id)
        return

    # Remove the role from all users with the specified role
    for user_data in users_with_role:
        user_id = user_data['user_id']
        user_name = user_data['first_name']
        roles.update_one({'chat_id': chat_id, 'user_id': user_id},
                         {'$pull': {'roles': role_name},
                          '$set': {'first_name': user_name}},
                         upsert=True)
    
    roles.update_one({'chat_id':chat_id,'role_name':role_name},
                             {'$set':{'count':0}},upsert=True)

    # Role {role_name} has been removed from all users in this chat
    bot2.send_message(
        chat_id, f"在此聊天中的所有用户都已被移除 {role_name} 角色", reply_to_message_id=message.id)


@bot.on_message(filters.command(['invites']))
def invites_finder(client, message):
    chat_id = message.chat.id
    if len(message.text) == 8:
        user_id = message.from_user.id
        first_name = message.from_user.first_name
        inviter = collection.find_one(
            {'chat_id': chat_id, 'user_id': user_id})
        if inviter:
            invi_count = inviter.get('invi_count',0)
            t_count = inviter['total_count']
            r_count = inviter['regular_count']
            f_count = inviter['fake_count']
            l_count = inviter['left_count']
            text = f"User <a href='tg://user?id={user_id}'>{first_name}</a> currently have \n<b>{r_count}</b> invites. (<b>{t_count}</b> Regular,<b> {l_count}</b> left,<b> {f_count}</b> fake,{invi_count} link)"
        else:
            text = f"No data found for user <a href='tg://user?id={user_id}'>{first_name}</a>"
        bot.send_message(chat_id, text)
    else:
        args = message.text.split()[1:]
        text = "Here the requested Data\n\n"

        for user in args:
            try:
                member = bot.get_chat(user)
            except Exception:
                continue
            user_id = member.id
            first_name = member.first_name
            inviter = collection.find_one(
                {'chat_id': chat_id, 'user_id': user_id})
            if inviter:
                invi_count = inviter.get('invi_count',0)
                t_count = inviter['total_count']
                r_count = inviter['regular_count']
                f_count = inviter['fake_count']
                l_count = inviter['left_count']
                text += f"User <a href='tg://user?id={user_id}'>{first_name}</a> currently have \n<b>{r_count}</b> invites. (<b>{t_count}</b> Regular,<b> {l_count}</b> left,<b> {f_count}</b> fake,{invi_count} link)\n\n"
            else:
                text += f"No data found for user <a href='tg://user?id={user_id}'>{first_name}</a>\n\n"
        bot.send_message(chat_id, text)

@bot.on_message(filters.command(['topinvites']))
def top_invites(client, message):
    chat_id = message.chat.id
    top_invites = collection.find(
        {"chat_id": chat_id}
    ).sort("regular_count", -1).limit(10)
    response = "Top 10 Invites:\n\n"
    for index, invite in enumerate(top_invites):
        user_id = invite["user_id"]
        t_count = invite['total_count']
        r_count = invite['regular_count']
        f_count = invite['fake_count']
        l_count = invite['left_count']
        member = bot.get_chat(user_id)
        first_name = member.first_name
        last_name = member.last_name
        response += f"{index + 1}. <a href='tg://user?id={user_id}'>{first_name} {last_name}</a> , <b>{r_count}</b> Invites. (<b>{t_count}</b> Regular,<b> {l_count}</b> left,<b> {f_count}</b> fake)\n"
    if response == "Top 10 Invites:\n\n":
        response = "No Data Found"

    bot.send_message(chat_id, response)

@bot2.on_message(filters.command(['link']) & filters.group)
def create_invite_link(client, message):
    chat_id = message.chat.id
    bot_member = bot2.get_chat_member(chat_id, 6074378866)
    if bot_member.privileges.can_invite_users is False:
        bot2.send_message(chat_id,"❌ 机器人权限不足，请至少授予以下管理员权限：\n通过链接邀请成员")
        return
    
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    data = invites.find_one({'chat_id': chat_id, 'user_id': user_id,'invite_link': {'$exists': True}})

    if data:
            link = data['invite_link']
            invite_count = data['invi_count']
            
            message_text = f"""🔗 <a href='tg://user?id={user_id}'>{first_name}</a> 您的专属邀请链接是：
<code>{link}</code> (点击复制)

👉 当前邀请数量为{invite_count}人。"""
            bot2.send_message(chat_id, message_text)
    else:
            link = bot2.create_chat_invite_link(
                chat_id, f"{first_name}")
            invite_link = link.invite_link
            message_text = f"""🔗 <a href='tg://user?id={user_id}'>{first_name}</a> Your exclusive link:
<code>{invite_link}</code> (Click to copy)

👉 Current Total Invitations 0 Person ."""
            bot2.send_message(chat_id, message_text)
            invites.update_one(
                {'chat_id': chat_id, 'user_id': user_id},
                {'$set': {'invite_link': invite_link,'invi_count':0}},
                upsert=True
            )
            owners.update_one({'chat_id':chat_id},{'$inc':{'link_count':1}},upsert=True)

@bot2.on_chat_member_updated()
def members(client, message):
    chat_id = message.chat.id
    if message.invite_link:
        invite_link = message.invite_link.invite_link
        data = invites.find_one({'chat_id': chat_id, 'invite_link': invite_link})
        if data:
            user_id = data['user_id']
            update_invites(chat_id, user_id, message.new_chat_member.user, "invite")

@bot2.on_message(filters.new_chat_members)
def chatmember(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    new_members = message.new_chat_members

    for new_member in new_members:
        if user_id != new_member.id:
            update_invites(chat_id, user_id, new_member, "add")

def update_invites(chat_id, user_id, new_member, point):
    current_time = datetime.now()
    da = invites.find_one({'chat_id': chat_id, 'user_id': user_id})
    if da is None:
        da = {}
    users = da.get('users', {})
    try:
        us = bot2.get_users(user_id)
        username = us.username
        first_name = us.first_name
    except Exception:
        pass
    
    users[str(new_member.id)] = {
        'username': new_member.username,
        'first_name': new_member.first_name,
        'timestamp': current_time
    }

    status = str(new_member.status)

    common_update_data = {
        '$set': {'users': users,'timestamp':current_time}
    }
    if first_name is not None:
        common_update_data['$set']['username'] = username
        common_update_data['$set']['first_name'] = first_name
    if status in ["UserStatus.LAST_WEEK", "UserStatus.ONLINE", "UserStatus.OFFLINE", "UserStatus.RECENTLY"]:
        specific_update_data = {
            '$inc': {'total_count': 1, 'regular_count': 1, 'left_count': 0, 'fake_count': 0, 'g_count': 1},
            '$set': {'users': users}
        }
        if point == "invite":
            daa = owners.find_one({'chat_id':chat_id})
            if daa and 'send_msg' in daa and daa['send_msg'] is True:
                bot2.send_message(chat_id,f"<a href='tg://user?id={user_id}'>{first_name}</a> 邀请了 <a href='tg://user?id={new_member.id}'>{new_member.first_name}</a>")
            specific_update_data['$inc']['invi_count'] = 1
        update_data = {**specific_update_data, **common_update_data}
        role_giver(chat_id, user_id)
    else:
        update_data = {
            '$inc': {'total_count': 1, 'fake_count': 1, 'regular_count': 0, 'left_count': 0, 'g_count': 0},
            '$set': {'users': users}
        }

    invites.update_one(
        {'chat_id': chat_id, 'user_id': user_id},
        update_data,
        upsert=True
    )
    if point == "add" or point == "invite":
        owners.update_one({'chat_id': chat_id}, {'$inc': {'user_count': 1, f'{point}_count': 1}})
    
@bot2.on_message(filters.command(['me']))
def list_roles(client, message):
    chat_id = message.chat.id
    user = message.from_user
    user_name = user.username if user.username else user.first_name

    data = roles.find_one({'chat_id': chat_id, 'user_id': user.id})
    if data and 'roles' in data:
        user_roles = data['roles']
        roles_list = "\n • ".join(user_roles)
        bot2.send_message(chat_id, f"{user_name} 拥有以下角色:\n • {roles_list}")
    else:
        bot2.send_message(chat_id, f"{user_name} 没有被赋予任何角色。")


@bot2.on_message(filters.text)
def text_message_handler(client, message):
    if message.chat.id in user_status:
        data = user_status[message.chat.id]
        chat_id = data['chat_id']
        msg2_id = data['msg2_id']
        msg2_chat_id = data['msg2_chat_id']
        role_name = data['role_name']
        call = data['call']
        if message.text == "🚫Cancle":
            bot2.delete_messages(msg2_chat_id,msg2_id)
            bot2.delete_messages(message.chat.id,message.id)
            del user_status[message.chat.id]
            return
        if call == "add_user":
            add_user_to_role(message,role_name,chat_id,msg2_id,msg2_chat_id)
        elif call == "remove_user":
            remove_user_to_role(message, role_name, chat_id,msg2_id,msg2_chat_id)
    else:
        pass
        
bot2.run()
