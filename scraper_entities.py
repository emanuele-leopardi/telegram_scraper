#!/bin/python3

class Channel():
    """
    This class holds only the needed channel's infos
    """

    def __init__(self, dialog):
        self._id = dialog.id
        self._name = dialog.name
        self._message = dialog.message # last message available in the channel
        self._messageId = dialog.message.id
        self._PeerId = dialog.message.to_id
        self._Entity = dialog.entity.id
        self._unread_count = dialog.unread_count


class OriginChannel(Channel):
    """
    Child Class for all Channels
    """
    def __init__(self, dialog):
        super(OriginChannel, self).__init__(dialog)
        #self._messages = dict()
        self.do_something()

    def do_something(self):
        print(self._message.message)
        


class ForwardChannel(Channel):
    """
    Child class for specific forwarding channel
    """
    def __init__(self, dialog):
        super(ForwardChannel, self).__init__(dialog)
        #self._messages = dict()
        self.do_something()

    def do_something(self):
        print(self._message.message)
        