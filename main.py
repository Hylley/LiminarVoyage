import os
import tweepy
from time import sleep
from dotenv import load_dotenv

from commands import private, public
from scripts import player, database, utils


class LiminarVoyage:
    def __init__(self):
        self.api = self.twitter_api()

    # Auth.

    def twitter_api(self):
        load_dotenv()

        return tweepy.API(tweepy.OAuth1UserHandler(
            os.environ.get("API_KEY"),
            os.environ.get("API_SECRET_KEY"),
            os.environ.get("ACCESS_TOKEN"),
            os.environ.get("ACCESS_TOKEN_SECRET")
        ))

    # Basic command processing.

    def check_mentions(self):
        mentions_list = self.api.mentions_timeline(count=50,
                                                   since_id=database.private('last_mention_id'))

        if not mentions_list:
            return

        mentions_list.reverse()

        for tweet in mentions_list:
            user = tweet.author.screen_name.lower()

            if not player.exists(user):
                return

            plr = player.Player(user)

            self.execute_command(tweet, plr, 'mention')
            database.private('last_mention_id', tweet.id)
            sleep(1)

    def check_dm(self):
        dm_list = self.api.get_direct_messages(count='50')
        dm_list.reverse()

        result = []

        for i in range(0, len(dm_list)):
            message_id = dm_list[i].id

            result.append(
                [message_id, dm_list[i].message_create['sender_id'], dm_list[i].message_create['message_data']['text']])

        print(result)

    def execute_command(self, tweet, request_player, source):
        text = utils.filter_text(tweet.text)
        split_text = text.split()

        print(text)

        if source == 'mention':
            command = split_text[0]

            if hasattr(public, command):
                default = 'Something went wrong. But don\'t worry, it wasn\'t your fault.'

                response = getattr(public, command)(self,
                                   request_tweet_id=tweet.id,
                                   request_tweet_text=text.lower(),
                                   request_player=request_player,
                                   tweet=tweet)

                self.api.update_status(status=response['text'] or default, media_ids=response['images'] or None,
                                       in_reply_to_status_id=tweet.id,
                                       auto_populate_reply_metadata=True)

            return

        elif source == 'direct':
            return
            # try:
            #    command_function = getattr(private, split_text[0])
            #    command_function(self, request_tweet_id, request_tweet_text, request_player, tweet)
            # except:
            #    return


bot = LiminarVoyage()

while True:
    bot.check_mentions()
    sleep(10)
