#!/bin/python3
from telethon import TelegramClient, events
from telethon.tl.functions.messages import SearchRequest
from telethon.tl.types import InputMessagesFilterEmpty
from telethon.tl.functions.messages import GetHistoryRequest
import datetime
import os
import logging
import yaml

path = os.getcwd()
config = []
try:
    with open(os.path.join(path + '/config.yaml'), 'r', encoding='utf8') as yaml_config:
        config = yaml.safe_load(yaml_config)
except yaml.YAMLError as exc:
    print(exc)

client = TelegramClient(config['config']['session'], int(
    config['config']['api_id']), config['config']['api_hash'])
file_list = config['config']['list']
#log_level = config['config']['log_level']
days = datetime.datetime.now() - \
    datetime.timedelta(config['config']['days_to_scrape'])
forward_channel = config['config']['forward_channel']
channelList = []

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)


class Channel():
    """
    This class holds only the needed channel's infos
    """

    def __init__(self, dialog):
        self.id = dialog.id
        self.name = dialog.name
        #self.Message = dialog.message
        self.PeerId = dialog.message.to_id
        self.Entity = dialog.entity.id
        self.unread_count = dialog.unread_count


async def createChannelList():
    """
    This function simply crete the list of channels
    amogts the one available on your chat list
    It does not scrape chats or groups.
    """
    async for dialog in client.iter_dialogs():
        if dialog.is_channel and dialog.name != forward_channel:
            channelList.append(Channel(dialog))
    return channelList


async def getForwardEntityId(forward_channel):
    """
    This function simply crete the list of channels
    amogts the one available on your chat list
    It does not scrape chats or groups.
    """
    async for dialog in client.iter_dialogs():
        if dialog.name == forward_channel:
            return dialog.entity.id

async def getItemList():
    """
    This function returns the item list
    """
    itemList = []
    try:
        with open(os.path.join(path + '/' + file_list), 'r') as file:
            lines = file.readlines()
            for line in lines:
                itemList.append(line.strip())
    except:
        pass
    return itemList

async def markAllAsRead(channelList):
    """
    Marks all new messages as read, who cares, right?
    """
    for channel in channelList:
        if channel.unread_count > 0:
            async for mexs in client.iter_messages(
                channel.id,
                limit=channel.unread_count
            ):
                await client.send_read_acknowledge(channel.id, mexs)


async def createSearchList(item):
    """
    This function create the list of items you want to
    be notified about and writes/reads them to/from a
    file
    """
    itemList = []
    if os.path.exists(os.path.join(path + '/' + file_list)):
        itemList = await getItemList()
        if item in itemList:
            return itemList
        else:
            with open(os.path.join(path + '/' + file_list), 'a') as file:
                file.write(item)
                file.write("\n")
            itemList.append(item)
            return itemList
    else:
        with open(os.path.join(path + '/' + file_list), 'w') as file:
            file.write(item)
            file.write("\n")
        itemList.append(item)
        return itemList


async def searchItems(itemList, channelList, limit=100000):
    """
    Research of all items in all channels since _days_ before

    """
    # Retrive messages that are already being forwarded to the
    # _forward_channel_
    messagesList = await getMessages()
    for channel in channelList:
        for item in itemList:
            result = await client(SearchRequest(
                peer=channel.id,      				# On which chat/conversation
                q=item,      						# What to search for
                filter=InputMessagesFilterEmpty(),  # Filter to use (maybe filter for media)
                min_date=days,		  			# Minimum date
                max_date=0,							# Maximum date
                offset_id=0,    					# ID of the message to use as offset
                add_offset=0,   					# Additional offset
                limit=limit,   						# How many results
                max_id=0,       					# Maximum message ID
                min_id=0,       					# Minimum message ID
                # from_id=None    					# Who must have sent the message (peer)
                hash=0
            ))
            if result.count > 0:
                for msgs in result.messages:
                    # if message id and channel id are different from  the ones in
                    # the forward channel message list then forward the new
                    # search result
                    if str(channel.id)[4:] + "|" + str(msgs.id) not in messagesList:
                        print(str(channel.id)[4:] + "|" + str(msgs.id))
                        await client.forward_messages(
                            entity=await getForwardEntityId(forward_channel),
                            from_peer=await client.get_entity(channel.id),
                            messages=msgs.id)
                        # update messagelist adding the new message to the
                        # existing list.
                        messagesList = await getMessages()


async def getMessages():
    """
    This function creates a list of all existing messages in the _forward_channel
    and returns it in the format "channel_id|channel_post"
    """
    Messages = []
    async for dialog in client.iter_dialogs():
        if dialog.name == forward_channel:
            posts = await client(GetHistoryRequest(
                peer=dialog.id,
                limit=100,
                offset_date=None,
                offset_id=0,
                max_id=0,
                min_id=0,
                add_offset=0,
                hash=0
            ))

            for messages in posts.messages:
                try:
                    Messages.append(
                        str(messages.fwd_from.channel_id) + "|" + str(messages.fwd_from.channel_post))
                except:
                    # not all messages are coming from a different channel (for
                    # example: the commands)
                    pass
    return list(dict.fromkeys(Messages))


@client.on(events.NewMessage)
async def handler(event):
    """
    This function handles incoming new messages and
    checks if any of them contains matching 
    item 
    """
    # Refresh Item List from file only
    itemList = await getItemList()
    if '/help' in event.raw_text:
        await event.reply('Available Commands are:' + '\n' +
                          '/addItem <(string) Item > ' + '\n' +
                          '/deleteItem <(string) Item > ' + '\n' +
                          '/getItems ' + '\n' +
                          '/isClientConnected' + '\n' +
                          '/getConfig' + '\n' +
                          '/getChannelList'
                          )
    if '/addItem' in event.raw_text:
        """
        When an Item is added:
        - it gets written to the file_list file
        - a full serch gets executed against all channels

        """
        await event.reply('Adding item ' + event.raw_text.split('/addItem')[1].strip())
        itemList = await createSearchList(event.raw_text.split('/addItem')[1].strip())
        await searchItems([event.raw_text.split('/addItem')[1].strip()], channelList)
    if '/deleteItem' in event.raw_text:
        """
        When an Item gets delete:
        - it gets removed from the file_list file
        - it gets removed from itemList list
        """
        del_item = event.raw_text.split('/deleteItem')[1].strip()
        if del_item in itemList:
            itemList.remove(del_item)
            with open(os.path.join(path + '/' + file_list), 'r') as f:
                lines = f.readlines()
            with open(os.path.join(path + '/' + file_list), 'w') as f:
                for line in lines:
                    if line.strip("\n") != del_item:
                        f.write(line)
            await event.reply('Item ' + del_item + ' removed')
        else:
            await event.reply('Item ' + del_item + ' not in list')
    if '/getItems' in event.raw_text:
        if itemList:
            await event.reply(' \n'.join(x for x in itemList))
        else:
            await event.reply('Item list is empty')
    if '/isClientConnected' in event.raw_text:
        await event.reply(str(client.is_connected()))
    if '/getConfig' in event.raw_text:
        try:
            with open(os.path.join(path + '/config.yaml'), 'r', encoding='utf8') as yaml_config:
                config = yaml.safe_load(yaml_config)
            await event.reply('Current Configuration:\n' +
                              '	api_hash: <omit>\n'
                              '	api_id: <omit>\n\n'
                              '	# Item List filename\n'
                              '	list: ' + str(config['config']['list']) + '\n'
                              '	days_to_scrape: ' +
                              str(config['config']['days_to_scrape']) + '\n\n'
                              '	# Channel to be used to interact with the app and to receive posts\n'
                              '	forward_channel: ' +
                              str(config['config']['forward_channel']) + '\n\n'
                              '	log_level: ' +
                              str(config['config']['log_level']) + '\n'
                              )
        except yaml.YAMLError as exc:
            print(exc)
    if '/getChannelList' in event.raw_text:
        cl = []
        for channel in channelList:
            cl.append(channel.name)
        await event.reply(' \n'.join(x for x in cl))
    # Check which channel has received the message
    index = -1
    for channel in channelList:
        # The message contains the id of the channel it was sent into.
        # If it's equal to one of the channels in the list saves which one it
        # is.
        if event.message.to_id == channel.PeerId:
            index = channelList.index(channel)
            await client.send_read_acknowledge(channel.id, event.message)
    # search all items in that channel
    await searchItems(itemList, [channelList[index]], limit=1)


async def main():

    # Create Channel list
    channelList = await createChannelList()
    # Create Search list
    itemList = await getItemList()
    # Mark all channel unread messages as read
    await markAllAsRead(channelList)
    await searchItems(itemList, channelList)


if __name__ == '__main__':
    with client:
        client.loop.create_task(main())
        client.run_until_disconnected()
