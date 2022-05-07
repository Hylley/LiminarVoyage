import os
import tweepy
from datetime import datetime
from time import sleep
from dotenv import load_dotenv

import utils
from commands import private, public
from player import Player, player_exists
import database


class TwittiaWarriors:
    def __init__(self):
        self.api = self.twitter_api()

    def twitter_api(self):
        load_dotenv()

        return tweepy.API(tweepy.OAuth1UserHandler(
            os.environ.get("API_KEY"),
            os.environ.get("API_SECRET_KEY"),
            os.environ.get("ACCESS_TOKEN"),
            os.environ.get("ACCESS_TOKEN_SECRET")
        ))

    def check_mentions(self):
        mentions_list = self.api.mentions_timeline(count=50,
                                                   since_id=database.load_setting('system', 'last_mention_id'))
        # mentions_list.reverse()

        if not mentions_list:
            return

        for tweet in mentions_list:
            user = tweet.author.screen_name

            if player_exists(user):
                text = utils.filter_text(tweet.text)
                player = Player(user)

                self.execute_command(tweet.id, text, player, tweet, 'mention')
            else:
                if not utils.filter_text(tweet.text).split()[0] == 'register':
                    self.api.update_status(status='You don\'t have a registered account, please type \"register\" to start playing.', in_reply_to_status_id=tweet.id,
                                       auto_populate_reply_metadata=True)
                else:
                    self.api.update_status(status='Account successfully created.', in_reply_to_status_id=tweet.id,
                                           auto_populate_reply_metadata=True)

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

    ##

    def execute_command(self, request_tweet_id, request_tweet_text, request_player, tweet, source):
        print(request_tweet_text)

        if int(request_player.read_internal_data('Is Exploring')) == 1:
            current_time = tweet.created_at.replace(tzinfo=None)
            last_registered = datetime.strptime(request_player.read_internal_data('Last Exploring Datetime'),
                                                '%Y-%m-%d %H:%M:%S+00:00')

            delta_date = current_time - last_registered

            exploring_seconds = delta_date.total_seconds()

            #

            request_player.update_internal_data('Is Exploring', 0)

        split_text = request_tweet_text.split()

        if source == 'mention':
            #try:
            command_function = getattr(public, split_text[0])
            command_function(self,
                             request_tweet_id=request_tweet_id,
                             request_tweet_text=request_tweet_text,
                             request_player=request_player,
                             tweet=tweet)
            #except:
                #pass
                # print('err')
                # print('Could not complete the request because:', f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")

        elif source == 'direct':
            try:
                command_function = getattr(private, split_text[0])
                command_function(self, request_tweet_id, request_tweet_text, request_player, tweet)
            except:
                pass


bot = TwittiaWarriors()

while True:
    bot.check_mentions()
    sleep(30)
