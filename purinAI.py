# -*- coding: utf-8 -*-
import tweepy
import datetime
import re
import config
import requests
from bs4 import BeautifulSoup
import time


# 天気を取得する関数
def fetch_weather():
    chiba = 120010
    url = 'http://weather.livedoor.com/forecast/rss/area/' + str(chiba)+'.xml'
    today = str(datetime.date.today().day)
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'html.parser')
    mes = ''
    for item in soup.find_all('item'):
        title = item.find('title').string
        if title.find(today + '日') != -1:
            mes = title
            break

    body = ''

    if mes.find('雨') != -1:
        body += 'なんだか雲行きが怪しいプリ...\n傘を持って出かけるプリ！\n'
    if mes.find('晴') != -1:
        body += '今日の天気は晴れプリ！\nいい日和だプリ！\n'

    return body


def tweet():


    # TweetをTweepyで取得用のAPI
    CK = config.CONSUMER_KEY
    CS = config.CONSUMER_SECRET
    AT = config.ACCESS_TOKEN
    AS = config.ACCESS_TOKEN_SECRET
    N = config.NAME # 監視したいユーザーのTwitterID

    print(fetch_weather())
    time.sleep(6)

    # Getting Tweet
    auth = tweepy.OAuthHandler(CK, CS)
    auth.set_access_token(AT, AS)

    api = tweepy.API(auth)
    # タイムラインを取得する
    u = api.get_user(screen_name=N)
    end_tweet_id = 0

    public_tweets = api.user_timeline(id=u.id)



    # --------------------------------------------------------------
    ID_LIST = []
    hazimete = True
    # つぶやかれた回数を記録しておく
    tweet_count =0

    # コメント反応用のテキストを読み込む
    lines = [line.rstrip() for line in open('puripuri_script.txt',encoding="utf-8")]
    while True:

        public_tweets = api.user_timeline(id=u.id)

        renew = False
        for tweet in public_tweets:
            if renew == False:
                TMP = tweet.id
                renew = True

            if tweet.id > end_tweet_id and hazimete == False:
                ID_LIST.append(tweet.id)
                print(tweet.id),
                print(":"),
                print(tweet.text)
            else:
                break

        end_tweet_id = TMP
        hazimete = False
        print("Latest tweet ID>>"),
        print(end_tweet_id)

        print("今回のTweet_IDリスト"),
        print(ID_LIST)
        while True:
            if ID_LIST == []:
                break
            tweet_ID = ID_LIST.pop()
            status = api.get_status(tweet_ID)
            # userから誰かにリプライが送られたら反応
            if status.in_reply_to_screen_name is not None and str(status.user.screen_name) == N:
                print("reply")
                tweet_count +=1
                # リプライ元のIDを取得
                replied_id = status.in_reply_to_status_id
                # リプライ元のステータスを取得
                try:
                    #いいねを飛ばす
                    api.create_favorite(status.id)
                    qkou_status = api.get_status(replied_id)
                    qkou_time = str(qkou_status.created_at)
                    stat_time = str(status.created_at)
                    new_qkou_time = datetime.datetime.strptime(qkou_time, "%Y-%m-%d %H:%M:%S")
                    new_stat_time = datetime.datetime.strptime(stat_time, "%Y-%m-%d %H:%M:%S")
                    sabun_time = new_stat_time - new_qkou_time #- datetime.timedelta(hours=9)
                    print(qkou_time)  # リプライ元のやつ
                    tweet = "@" + str(status.user.screen_name)
                    # ツイート元のセリフに応じて返答する
                    for i in range(int(len(lines)/2)):
                        if re.search(lines[i*2], str(qkou_status.text)):
                            tweet += "\n" + lines[i*2+1]

                    tweet += "\n反応までの時間は" + str(sabun_time) + "だったプリ"
                    # 1分以下なら
                    if new_stat_time < new_qkou_time + datetime.timedelta(minutes=1):
                        tweet += "\nすごく早いプリ！すごいプリ！"
                    # ちょうど1分なら
                    if new_stat_time - new_qkou_time == datetime.timedelta(minutes=1):
                        tweet += "\nちょうど1分プリ！すごいプリ！"
                    # ちょうど3分なら
                    if new_stat_time - new_qkou_time == datetime.timedelta(minutes=3):
                        tweet += "\nちょうど3分プリ！カップ麺ができたプリ！"
                    #15分以上なら
                    if new_stat_time - new_qkou_time > datetime.timedelta(minutes=15):
                        tweet += "\nこれは...人力botの波動を感じるプリ！"
                    api.update_status(status=tweet, in_reply_to_status_id=status.id)
                except tweepy.error.TweepError:
                    import traceback
                    traceback.print_exc()

        time.sleep(60)
        print("1分経過")

        # 0時頃、昨日のつぶやき回数をいう
        if datetime.datetime(2000, 1, 1, 0, 0, 0).time() <= datetime.datetime.today().time() < datetime.datetime(2000, 1, 1, 0, 1, 0).time():
            day_tweet="0時を過ぎたプリ！\n昨日のプリン反応回数は"+str(tweet_count)+"回だったプリ"
            day_tweet+="\nみんな早めに寝るプリ！ププリン～♪"
            api.update_status(day_tweet)
            tweet_count=0

        # 8時頃、天気を呟く
        if datetime.datetime(2000, 1, 1, 8, 0, 0).time() <= datetime.datetime.today().time() < datetime.datetime(2000, 1, 1, 8, 1, 0).time():
            day_tweet = "おはプリ！8時になったプリ！\n"
            day_tweet += fetch_weather()
            api.update_status(day_tweet)


    # --------------------------------------------------------------

