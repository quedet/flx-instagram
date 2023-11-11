from channels.generic.websocket import JsonWebsocketConsumer
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from turbo_response import TurboStream

from .models import Media, Comment
from apps.accounts.models import User, Contact, SearchHistory


class InstagramConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.accept()

    def receive_json(self, content, **kwargs):
        action = content.get('action')
        data = content.get('data')
        user = self.scope['user']

        match action:
            case 'like a post':
                post_id = data.get('post_id')
                post_type = data.get('post_type')

                if post_type and post_id:
                    model = apps.get_model(app_label='assets', model_name=data.get('post_type'))
                    post = Media.objects.get(id=post_id, content_type=ContentType.objects.get_for_model(model))

                    users_like = post.users_like

                    if user in users_like.all():
                        users_like.remove(user)
                        html = TurboStream(f"{post_type}#{post_id}--like").update.template(
                            "components/blocks/post/like.html").render()
                    else:
                        users_like.add(user)
                        html = TurboStream(f"{post_type}#{post_id}--like").update.template(
                            "components/blocks/post/liked.html").render()

                    self.send(text_data=html)

                    likes_html = TurboStream(f"{post_type}#{post_id}--likes--count").update.template(
                        "components/blocks/post/likes_count.html", {'total_likes': post.total_likes}).render()

                    self.send(text_data=likes_html)

            case 'bookmark a post':
                post_id = data.get('post_id')
                post_type = data.get('post_type')

                if post_type and post_id:
                    model = apps.get_model(app_label='assets', model_name=data.get('post_type'))
                    post = Media.objects.get(id=post_id, content_type=ContentType.objects.get_for_model(model))

                    users_bookmarks = post.users_bookmarks

                    if user in users_bookmarks.all():
                        users_bookmarks.remove(user)
                        html = TurboStream(f"{post_type}#{post_id}--bookmark").update.template(
                            "components/blocks/post/icons/bookmark.html").render()
                    else:
                        users_bookmarks.add(user)
                        html = TurboStream(f"{post_type}#{post_id}--bookmark").update.template(
                            "components/blocks/post/icons/bookmarked.html").render()

                    self.send(text_data=html)

            case 'comment a post':
                post_id = data.get('post_id')
                post_type = data.get('post_type')
                post_comment = data.get('comment')

                if post_type and post_id and post_comment:
                    model = apps.get_model(app_label='assets', model_name=post_type)
                    post = Media.objects.get(content_type=ContentType.objects.get_for_model(model), id=post_id)
                    post.comments.create(user=user, content=post_comment)
                    html = TurboStream(f"{post_type}#{post_id}--comment--form").update \
                        .template("components/blocks/post/card/comment/form_inner.html", {'media': post}).render()
                    self.send(text_data=html)

            case 'follow a user':
                user_uid = data.get('user_uid', None)
                try:
                    current_user = self.scope['user']
                    target_user = User.objects.get(uid=user_uid)

                    if current_user != target_user:
                        contact, created = Contact.objects.get_or_create(user_from=current_user, user_to=target_user)

                        if created:
                            html = TurboStream(f"{ target_user.uid }--follow").remove.render()
                            self.send(text_data=html)
                        else:
                            contact.delete()
                    else:
                        print('You can not follow your own account.')

                except User.DoesNotExist:
                    pass

            case 'save into search history':
                try:
                    account = User.objects.get(uid=data.get('account_uid'))
                    current_user_history, created = SearchHistory.objects.get_or_create(account=self.scope['user'])

                    if account not in current_user_history.requested_users.all():
                        current_user_history.requested_users.add(account)

                except (User.DoesNotExist, User.MultipleObjectsReturned):
                    pass

            case "delete search history item":
                try:
                    my_searches = SearchHistory.objects.get(account=self.scope['user']).requested_users
                    account = User.objects.get(username=data.get('account_username'))

                    if account in my_searches.all():
                        my_searches.remove(account)

                        html = TurboStream(f"account#{ account.username }").remove.render()
                        self.send(text_data=html)

                except (User.DoesNotExist, User.MultipleObjectsReturned):
                    pass
