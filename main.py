import os
import tweepy
from time import sleep
from dotenv import load_dotenv

from commands import private, public
from scripts import player as plr, database, utils


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
                                                   since_id=database.load_setting('system', 'last_mention_id'))
        if not mentions_list:
            return

        for tweet in mentions_list:
            user = tweet.author.screen_name

            text = utils.filter_text(tweet.text)

            if not plr.player_exists(user):
                return

            player = plr.Player(user)

            self.execute_command(tweet.id, text, player, tweet, 'mention')
            sleep(1)

        database.set_setting('last_mention_id', mentions_list[0].id)

    def check_dm(self):
        dm_list = self.api.get_direct_messages(count='50')
        dm_list.reverse()

        result = []

        for i in range(0, len(dm_list)):
            message_id = dm_list[i].id

            result.append(
                [message_id, dm_list[i].message_create['sender_id'], dm_list[i].message_create['message_data']['text']])

        print(result)

    def execute_command(self, request_tweet_id, request_tweet_text, request_player, tweet, source):
        print(request_tweet_text)

        if int(request_player.read_internal_data('Is Exploring')) == 1:
            current_time = tweet.created_at.replace(tzinfo=None)
            last_registered = utils.string_to_date(request_player.read_internal_data('Last Exploring Datetime'))

            delta_date = current_time - last_registered

            exploring_seconds = delta_date.total_seconds()

            #

            request_player.update_internal_data('Is Exploring', 0)

        split_text = request_tweet_text.split()

        if source == 'mention':
            try:
                text = 'Something went wrong. But don\'t worry, it wasn\'t your fault.'
                image_ids = None

                response = getattr(public, split_text[0])(self,
                                                          request_tweet_id=request_tweet_id,
                                                          request_tweet_text=request_tweet_text.lower(),
                                                          request_player=request_player,
                                                          tweet=tweet)

                if response:
                    text = utils.index(response, 0) or text
                    image_ids = utils.index(response, 1) or image_ids

                self.api.update_status(status=text, media_ids=image_ids,
                                       in_reply_to_status_id=request_tweet_id,
                                       auto_populate_reply_metadata=True)
            except:
                return

        elif source == 'direct':
            try:
                command_function = getattr(private, split_text[0])
                command_function(self, request_tweet_id, request_tweet_text, request_player, tweet)
            except:
                return

    # Gameplay


bot = LiminarVoyage()

while True:
    bot.check_mentions()
    sleep(10)
