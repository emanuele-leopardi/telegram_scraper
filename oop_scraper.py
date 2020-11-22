#!/bin/python3
from telethon import TelegramClient, events
from telethon.tl.functions.messages import SearchRequest
from telethon.tl.types import InputMessagesFilterEmpty
from telethon.tl.functions.messages import GetHistoryRequest
from concurrent.futures import ThreadPoolExecutor as tpe
import scraper_entities as se
import datetime
import time
import os
import logging
import yaml

path = os.getcwd()
config = []
try:
    with open(os.path.join(path + '/config.yaml'), 'r', encoding='utf8') as c:
        config = yaml.safe_load(c)
except yaml.YAMLError as exc:
    print(exc)

client = TelegramClient(config['config']['session'], int(
    config['config']['api_id']), config['config']['api_hash'])
file_list = config['config']['list']
#log_level = config['config']['log_level']
days = datetime.datetime.now() - \
    datetime.timedelta(config['config']['days_to_scrape'])
forward_channel = []
for channel in config['config']['forward_channel']:
    forward_channel.append(channel)
futureList = []


async def createChannelsThreads():
    """
    This function simply crete the list of channels
    amogts the one available on your chat list
    It does not scrape chats or groups.
    """
    future_list = []
    ffc = []
    executor = tpe(max_workers=8)
    async for dialog in client.iter_dialogs():
        if dialog.is_channel and dialog.name not in forward_channel:
            future_list.append(executor.submit(se.OriginChannel(dialog)))
        if dialog.is_channel and dialog.name in forward_channel:
            ffc.append(executor.submit(se.ForwardChannel(dialog)))
    return future_list, ffc


async def main():

    futureList, forwardChannelList = await createChannelsThreads()
    #for future in futureList, forwardChannelList:
    print(forwardChannelList[0].done())


if __name__ == '__main__':
    with client:
        client.loop.create_task(main())
        client.run_until_disconnected()
