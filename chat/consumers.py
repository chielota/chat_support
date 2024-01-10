import json
import uuid

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from chat.models import Mymodel


@database_sync_to_async
def save_uuid(uuid):
    Mymodel.objects.create(uuid_field=uuid)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        new_uuid = uuid.uuid4()
        uuid_str= str(new_uuid)

        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        self.uuid= new_uuid

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await save_uuid(new_uuid)
        await self.accept()
        await self.send(text_data=json.dumps({"uuid": uuid_str}))


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        if message=='yes':
           status_id=text_data_json['status_id']
           await self.channel_layer.group_send(
               self.room_group_name, {"type": "typing.status", "message": message, "status_id": status_id}
           )
        elif message=='no':
           status_id=text_data_json['status_id']
           await self.channel_layer.group_send(
               self.room_group_name, {"type": "typing.status", "message": message, "status_id": status_id}
           )
        elif message:
            message_id = text_data_json["message_id"]
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat.message", "message": message, "message_id": message_id}
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        message_id = event['message_id']
        await self.send(text_data=json.dumps({"message": message, "message_id": message_id}))

    async def typing_status(self, event):
        message= event["message"]
        status_id= event['status_id']

        if message == 'yes':
            await self.send(text_data=json.dumps({"status": message, "status_id": status_id }))
        elif message == 'no':
            await self.send(text_data=json.dumps({"status": message, "status_id": status_id}))


