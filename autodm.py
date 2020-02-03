import tweepy
import webbrowser
import os
import time, threading

from asciimatics.effects import Cycle, Stars
from asciimatics.renderers import FigletText
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from func_timeout import func_timeout, FunctionTimedOut, func_set_timeout

class colors:

    RED = (245, 90, 66)
    ORANGE = (245, 170, 66)
    YELLOW = (245, 252, 71)
    GREEN = (92, 252, 71)
    BLUE = (71, 177, 252)
    PURPLE = (189, 71, 252)
    WHITE = (255, 255, 255)


def initColorIt():
    os.system("cls")

def color(text, rgb):
    return "\033[38;2;" + str(rgb[0]) + ";" + str(rgb[1]) + ";" + str(rgb[2]) +"m" + text + "\033[0m"
    
    
def background(text, rgb):
    return "\033[48;2;" + str(rgb[0]) + ";" + str(rgb[1]) + ";" + str(rgb[2]) +"m" + text + "\033[0m"

@func_set_timeout(2.5)
def demo(screen):
    effects = [
        Cycle(
            screen,
            FigletText("Twitter", font='big'),
            int(screen.height / 2 - 8)),
        Cycle(
            screen,
            FigletText("Bot!", font='big'),
            int(screen.height / 2 + 3)),
        Stars(screen, 200)
    ]
    screen.play([Scene(effects, 500)])
    


#Screen.wrapper(demo)


CONSUMER_KEY = ''#keep the quotes, replace this with your consumer key
CONSUMER_SECRET = ''#keep the quotes, replace this with your consumer secret key
ACCESS_TOKEN = ''#keep the quotes, replace this with your access token
ACCESS_SECRET = ''#keep the quotes, replace this with your access token secret


# set auth variables
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)


# create a new api
api = tweepy.API(auth)


# create an instance of the twitter api class
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth_url = auth.get_authorization_url()


# open the window for authorization, twitter will generate the pin
webbrowser.open(auth_url)
print ("Copy PIN from the window that opens")


# get the pin number from the user
verifier = input('PIN: ').strip()
auth.get_access_token(verifier)
print(auth.access_token)


# get the access key and secret returned from twitter
access_key = auth.access_token
access_secret = auth.access_token_secret


# set authorization token
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)


# make a tweet
def send_tweet():
    to_tweet = True
    tweet_text = input("Enter your tweet content below... Only the first 140 characters will be used.\n>>> ")
    api.update_status(tweet_text[0:140])
    print ("You tweeted \n'" + tweet_text[0:140] + "'")
    restart = input("Do you want to tweet again? (Y/N)\n>>> ")
    if restart.lower() == "y":
        send_tweet()
    else:
        print ("Returning to the Main Menu...\n")

def comment_on_post():
    search_phrase = input("What do you want to search for?\n>>> ").strip()
    search_number = input("How many results do you want to return?\n>>> ")
    search_type = input("Would you like to automate commenting? (Y/N)\n>>> ")
    search_result = api.search(search_phrase, rpp=search_number)
    pac = input("Type your message here? " + "\n>>> ")
    for i in search_result:
        print (str(i.user.name) + " said " + i.text + "\n")
        #to_follow = input("Do you want to comment? " + str(i.user.name) + "? (Y/N)\n>>> ")
        #if to_follow.lower() == "n":

        if search_type.lower() == "n":
            sn = i.user.screen_name
            
            m = "@"+sn + " "+ pac
            api.update_status( m, i.id)
            print ("You commented on " + str(i.user.name) + "for tweetid:"+ str(i.id)+ "!\n")

            # check if the user wants to search again
            restart = input("Do you want to search again? (Y/N)\n>>> ")
            if restart.lower() == "n":
                print ("Returning to the Main Menu...\n")
                return keyword_follow()
            else:
                return keyword_follow()
        else:
            sn = i.user.screen_name
            
            m = "@"+sn + " "+ pac
            api.update_status( m, i.id)
            print ("You commented on " + str(i.user.name) + "for tweetid:"+ str(i.id)+ "!\n")
    return keyword_follow()

# search twitter
def keyword_follow():
    search_phrase = input("What do you want to search for?\n>>> ").strip()
    search_number = input("How many results do you want to return?\n>>> ")
    search_result = api.search(search_phrase, rpp=search_number)
    for i in search_result:
        print (str(i.user.name) + " said " + i.text + "\n")
        to_follow = input("Do you want to follow " + str(i.user.name) + "? (Y/N)\n>>> ")
        if to_follow.lower() == "n":
            print (str(i.user.name) + " was not followed!")
        else:
            api.create_friendship(i.user)
            print ("You followed " + str(i.user.name) + "!\n")

    # check if the user wants to search again
    restart = input("Do you want to search again? (Y/N)\n>>> ")
    if restart.lower() == "n":
        print ("Returning to the Main Menu...\n")
    else:
        return keyword_follow()

def keyword_retweet():
    search_phrase = input("What do you want to search for?\n>>> ").strip()
    search_number = input("How many results do you want to return?\n>>> ")
    search_result = api.search(search_phrase, rpp=search_number)
    for i in search_result:
        print (str(i.user.name) + " said " + str(i.text) + "\n")
        to_retweet = input("Do you want to retweet" + str(i.user.name) + "? (Y/N)\n>>> ")
        if to_retweet.lower() == "n":
            print (str(i.user.name) + " was not retweeted!")
        else:
            api.retweet(i.id)
            print ("Retweeted!\n")
            again = input("See more? (Y/N)\n>>> ")
            if again.lower() == "n":
                break       
    # check if the user wants to search again
    restart = input("Do you want to search again? (Y/N)\n>>> ")
    if restart.lower() == "n":
        print ("Returning to the Main Menu...\n")
    else:
        return keyword_retweet()



def mass_unfollow():
    hits_left = api.rate_limit_status()['remaining_hits']
    print ("You can unfollow " + str(hits_left) + " people this hour...\n")
    print ("Checking who doesn't follow you back. This will take a minute.\n")
    # first, create some lists to hold the followers
    followers = []
    friends = []

    # we have to use a Cursor for pagination purposes
    for follower in tweepy.Cursor(api.followers).items():
        followers.append(follower)


    for friend in tweepy.Cursor(api.friends).items():
        friends.append(friend)

    # create a non_reciprocals list, these are non-followers (set - set)
    non_reciprocal = list(set(friends) - set(followers))
    print (str(len(non_reciprocal)) + " non-reciprocal followers.\n")


    # first, double check that we want to unfollow
    double_check = input("Unfollow them? (Y/N) ***WARNING, THIS ACTION CANNOT BE UNDONE***\n>>> " )


    if double_check.lower() == "y":
        # count the number of people we unfollow, just for fun
        counter = 0
        for i in non_reciprocal:
            if hits_left > 0:
                api.destroy_friendship(i.screen_name)
                print ("Successfully unfollowed " + i.screen_name)
                hits_left -= 1
            else:
                print ("You ran out of hits! Try again in an hour!")

            counter += 1
        print ("You unfollowed " + str(counter) + " people!\n")
        print ("Now returning to the Main Menu.")
    else:
        print ("Returning to the Main Menu...\n")

        #todo - automatically DM new followers      
def direct_messages():
    new_followers = api.followers(auth) 


    for i in new_followers:
        newDM = input (str(i.screen_name) + "send follower DM?" + "Y/N" )
        if newDM.lower() == "n":
            print (str(i.screen_name) + " was not messaged")
            print ("Now returning to the Main Menu.")
    else:
        api.send_direct_message(user_id = i.screen_name, text = "message text here")
        print ("You messaged " + str(i.screen_name))


# create the menu
keep_running = True
while keep_running:
    print ("Main Menu")
    print ("---------\n")
    selection = input("(1)Tweet | (2)Keyword Follow | (3)Keyword Retweet | (4)Mass Unfollow | (5)Direct Message | (6)Comment | (7)END \n\n>>> ")
    if selection == "1":
        print ("New Tweet")
        print ("---------\n")
        send_tweet()
    elif selection == "2":
        print ("Keyword Follow")
        print ("--------------\n")
        keyword_follow()
    elif selection == "3":
        print ("Keyword Retweet")
        print ("---------------\n")
        keyword_retweet()
    elif selection == "4":
        print ("Mass Unfollow")
        print ("-------------\n")
        print ("WARNING: MASS UNFOLLOW IS AGAINST THE TOS OF TWITTER. YOU'VE BEEN WARNED\n")
        mass_unfollow()
    elif selection == "5":
        print ("Direct Message")
        print ("------------\n")
        direct_messages()
    elif selection == "6":
        print ("Comment")
        print ("------------\n")
        comment_on_post()
    else:
        print ("BYE!\n\n")
keep_running = False