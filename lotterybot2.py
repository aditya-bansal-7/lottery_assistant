
from pymongo import MongoClient
from pyrogram import Client , filters ,enums 
import pyrogram.types as types2

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

app = "not_set"


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
                        {'$addToSet':{'admins': user_id}},upsert=True
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
            try:
                details = bot2.get_chat(chat)
            except Exception:
                continue
            title = details.title
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
            usser_name = usser.first_name

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


@bot2.on_message(filters.new_chat_members)
def chatmember(client, message):
    new_user = message.new_chat_members
    for user in new_user:
        new_member_id = user.id
        new_member_username = user.username
        new_member_firstname = user.first_name
        chat_id = message.chat.id
        user_id = message.from_user.id
        if user_id != new_member_id:
            status = str(user.status)
            statuses = ["UserStatus.LAST_WEEK", "UserStatus.ONLINE", "UserStatus.OFFLINE", "UserStatus.RECENTLY"]
            if status in statuses:
                invites.update_one(
                    {'chat_id': chat_id, 'user_id': user_id},
                    {
                        '$inc': {'total_count': 1, 'regular_count': 1, 'left_count': 0, 'fake_count': 0, 'g_count': 1},
                        '$addToSet': {'new_members_ids': new_member_id, 'new_member_username': new_member_username, 'new_member_firstname': new_member_firstname}
                    },
                    upsert=True
                )
                role_giver(chat_id,user_id)
            else:
                invites.update_one(
                    {'chat_id': chat_id, 'user_id': user_id},
                    {
                        '$inc': {'total_count': 1, 'fake_count': 1, 'regular_count': 0, 'left_count': 0, 'g_count': 0},
                        '$addToSet': {'fake_members_ids': new_member_id, 'fake_member_firstname': new_member_firstname, 'fake_member_username': new_member_username}
                    },
                    upsert=True
                )
        else:
            links = invites.find({'chat_id': chat_id})
            for link in links:
                if 'invite_link' in link:
                    invite_link = link['invite_link']
                    user_id = link['user_id']
                   
                    if 'invite_count' in link:
                        invi_count = link['invite_count']
                        try:
                            invi = app.get_chat_invite_link_joiners_count(chat_id, invite_link)
                            if invi_count != invi:
                                users = app.get_chat_invite_link_joiners(chat_id, invite_link)
                                for user in users:
                                    if user.user.id == new_member_id:
                                        invites.update_one(
                                            {'chat_id': chat_id, 'user_id': user_id},
                                            {
                                                '$inc': {'total_count': 1, 'regular_count': 1, 'left_count': 0, 'fake_count': 0, 'invite_count': 1, 'g_count': 1},
                                                '$addToSet': {'new_members_ids': new_member_id}
                                            },
                                            upsert=True
                                        )
                                        role_giver(chat_id,user_id)
                                        break
                        except Exception:
                            pass
                    else:
                        try:
                            users = app.get_chat_invite_link_joiners(chat_id, invite_link)
                            for user in users:
                                if user.user.id == new_member_id:
                                    invites.update_one(
                                        {'chat_id': chat_id, 'user_id': user_id},
                                        {
                                            '$inc': {'total_count': 1, 'regular_count': 1, 'left_count': 0, 'fake_count': 0, 'invite_count': 1, 'g_count': 1},
                                            '$addToSet': {'new_members_ids': new_member_id}
                                        },
                                        upsert=True
                                    )
                                    role_giver(chat_id,user_id)
                                    break
                        except Exception:
                            pass

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


bot2.run()
