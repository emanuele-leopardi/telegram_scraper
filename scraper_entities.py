class Channel():
    """
    This class holds only the needed channel's infos
    """

    def __init__(self, dialog):
        self.id = dialog.id
        self.name = dialog.name
        # self.Message = dialog.message
        self.PeerId = dialog.message.to_id
        self.Entity = dialog.entity.id
        self.unread_count = dialog.unread_count


class OriginChannel(Channel):
    pass


class ForwardChannel(Channel):

    def __init__(self, dialog):
        super(ForwardChannel, self).__init__(dialog)
        self._messages = dict()



