import praw 
import asyncio
from telegram import Bot
from datetime import datetime, timedelta, timezone
import time

REDDIT_CONFIG = {
    'client_id': '',
    'client_secret':'',
    'user_agent':''   #codes for reddit
}

TELEGRAM_CONFIG = {
    'token':'',
    'chat_id':'' #codes for chat and telegram
}

SEARCH_CONFIG = {
    'subreddits': ['TutorsHelpingTutors','tutor','mathhelp'],
    'keywords':['math','help','tutors','online'],
    'limit': 10,
    'hours_ago': 24,
}

def get_recent_posts():
    reddit = praw.Reddit(**REDDIT_CONFIG)
    time_interval = datetime.now(timezone.utc) - timedelta(hours = SEARCH_CONFIG['hours_ago'])

    matching_posts = []

    for subreddit_name in SEARCH_CONFIG['subreddits']:
        try:
            subreddit = reddit.subreddit(subreddit_name)

            for submission in subreddit.new(limit = SEARCH_CONFIG['limit']):
            
                post_time = datetime.fromtimestamp(submission.created_utc, timezone.utc)

                if post_time < time_interval:
                    continue
            
                title_lower = submission.title.lower()
                if any(keyword.lower() in title_lower for keyword in SEARCH_CONFIG['keywords']):
                    post_info = {
                        'title': submission.title,
                        'url': f"https://reddit.com{submission.permalink}",
                        'created': post_time.strftime('%Y-%m-%d %H:%M UTC'),
                        'subreddit': submission.subreddit.display_name,
                        'author': str(submission.author),
                        'score': submission.score
                    }

                    matching_posts.append(post_info)
        except:
            print("Error")

    return matching_posts

async def send_telegram_message_async(message):
    try:
        bot = Bot(token = TELEGRAM_CONFIG['token'])
        await bot.send_message(
            chat_id = TELEGRAM_CONFIG['chat_id'],
            text = message, 
            parse_mode = 'HTML',
        )
        return True
    except:
        print("Error")
        return False
    
def send_telegram_message(message):
    return asyncio.run(send_telegram_message_async(message))

def main():
    posts = get_recent_posts()

    if not posts:
        print("No such posts")
        return

    count = 0
    for post in posts:
        message = (
            f"<b>New Post in r/{post['subreddit']}</b>\n\n"
            f"<b>Title:</b> {post['title']}\n"
            f"<b>Author:</b> u/{post['author']}\n"
            f"<b>Score:</b> {post['score']} 👍\n"
            f"<b>Posted:</b> {post['created']}\n"
            f"<a href='{post['url']}'>📖 Read on Reddit</a>"
        )

        if send_telegram_message(message):
            count += 1
            time.sleep(10)


if __name__ == "__main__":
    main()
    
    




