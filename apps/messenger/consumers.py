from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import async_to_sync
from channels.auth import login, logout
from pprint import pprint

from .models import Client, Room, Message
from apps.accounts.models import User
from turbo_response import TurboStream


class MessengerConsumer(JsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room = None
        self.client = None

    def connect(self):
        """Event when client connects"""
        self.accept()

        # Get the current user
        user = self.scope['user']

        # Check if the client already exists, otherwise create one
        client, created = Client.objects.get_or_create(user=user)
        self.client = client

        if created:
            self.client.channel = self.channel_name
            self.client.save()

        # Gets the username to whom you are going to speak
        user_name = self.scope['url_route']['kwargs']['room_name']

        # Retrieve that user
        user_target = User.objects.filter(username=user_name).first()

        # Search for rooms where both users match
        self.room = Room.objects.filter(users_subscribed__in=[user])\
            .intersection(Room.objects.filter(users_subscribed__in=[user_target])).first()

        if self.room and user_target and self.room.users_subscribed.count() == 2:
            self.add_client_to_room(self.room.id, client=self.client)
        else:
            self.room = Room.objects.filter(
                users_subscribed__in=[user_target]
            ).last()

            if self.room and self.room.users_subscribed.count() == 1:
                self.add_client_to_room(self.room.id, client=self.client)
            else:
                self.add_client_to_room(user_target=user_target, client=self.client)

        # self.list_room_messages(self.room)

    def disconnect(self, code):
        """Event when client disconnects"""
        self.remove_client_from_current_room()
        # Room.objects.filter(users_subscribed__in=[self.scope['user']]).filter(messages__user=None).delete()

    def receive_json(self, content, **kwargs):
        data = content.get('data')

        match content['action']:
            case 'send message':
                new_message = self.save_message(data['message'], room=self.room)
                html = TurboStream("messenger--messages--container").append.template("pages/messenger/message/item.html", {
                    'm': new_message,
                    'current_user': self.scope['user']
                }).render()
                async_to_sync(self.channel_layer.group_send)(new_message.room.uid, {
                    'type': 'send_message', 'html': html
                })

    def send_message(self, event):
        html = event['html']
        self.send(text_data=html)

    def list_room_messages(self, room):
        """List all messages from a group"""
        # Get all messages from the room
        messages = Message.objects.filter(room=room).order_by('created_at')
        # Render HTML and send to client
        html = TurboStream("messenger--messages").update.template("pages/messenger/message/list.html",
                                                                  {'messages': messages, 'current_user': self.scope['user']}).render()
        async_to_sync(self.channel_layer.group_send)(room.uid, {
            'type': 'send_message',
            'html': html
        })

    def save_message(self, text, room):
        """Save a message in the database"""
        user = self.scope['user']

        message = Message.objects.create(user=user, room=room, text=text)

        html = TurboStream("messenger--form").update.template("pages/messenger/form/inner.html").render()
        self.send(text_data=html)

        return message

    def add_client_to_room(self, room_id=None, user_target=None, client=None):
        """Add customer to a room within channels and save the reference in the room model"""
        # Remove the client from the previous room
        self.remove_client_from_current_room()
        # Get or create room
        room, created = Room.objects.get_or_create(id=room_id)

        if created:
            room.users_subscribed.add(user_target)
            room.users_subscribed.add(client.user)

        room.clients_active.add(client)
        room.save()

        # Add client to room
        async_to_sync(self.channel_layer.group_add)(room.uid, self.channel_name)

    def remove_client_from_current_room(self):
        """Remove client from current group"""
        client = Client.objects.get(user=self.scope['user'])
        # Get the current group
        rooms = Room.objects.filter(clients_active__in=[client])

        for room in rooms:
            # Remove the client from the group
            async_to_sync(self.channel_layer.group_discard)(room.uid, self.channel_name)

            # Remove the client from the Room model
            room.clients_active.remove(client)
            room.save()
