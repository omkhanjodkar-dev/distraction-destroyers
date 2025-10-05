from operator import is_
import os
import time
import string
from datetime import datetime
import json

os.system("pip install pywin32 pyautogui pywinauto keyboard transformers torch yt-dlp requests beautifulsoup4")

import pyautogui
from pywinauto import Desktop
import keyboard
from transformers import pipeline
import sys
import argparse
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re
from tkinter import messagebox



# os.environ["CUDA_VISIBLE_DEVICES"] = "1"
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
hashmap = {}

def get_current_datetime():
    return datetime.now().strftime("%d/%m/%y %H:%M:%S")

def search_youtube_video(title, max_results=10):
    try:
        encoded_title = urllib.parse.quote_plus(title)
        
        search_url = f"https://www.youtube.com/results?search_query={encoded_title}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        video_urls = []
        video_titles = []
        
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href and '/watch?v=' in href:
                video_id = href.split('/watch?v=')[1].split('&')[0]
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                
                video_title = link.get('title') or link.get_text(strip=True)
                
                if video_url not in video_urls and video_title:
                    video_urls.append(video_url)
                    video_titles.append(video_title)
                    
                    if len(video_urls) >= max_results:
                        break
        
        if not video_urls:
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    video_id_matches = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', script.string)
                    title_matches = re.findall(r'"title":{"runs":\[{"text":"([^"]+)"}', script.string)
                    
                    for i, video_id in enumerate(video_id_matches[:max_results]):
                        video_url = f"https://www.youtube.com/watch?v={video_id}"
                        video_title = title_matches[i] if i < len(title_matches) else "Unknown Title"
                        
                        if video_url not in video_urls:
                            video_urls.append(video_url)
                            video_titles.append(video_title)
        
        if not video_urls:
            return None
        
        try:
            for i in range(0, max_results):
                if video_titles[i] == title:
                    return video_urls[i], video_titles[i]
        except Exception as _:
            pass

        return video_urls[0], video_titles[0]
        
    except requests.exceptions.RequestException as e:
        print(f"A network error occurred: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def is_distracting(title: str) -> bool:
    labels = ["Gaming", "Drama", "Education", "Technology", "Programming", "Sports"] # Movie | News | Motivation | OTherwise it works + cap the desc if possible *
    # labels = ["Gaming", "Drama", "Science", "Mathematics", "Educational Content", "Technology", "Programming", "Sports"] # Movie | News | Motivation | OTherwise it works + cap the desc if possible *
    # labels = ["Chemistry", "Physics", "Mathematics", "Biology", "History", "Civics", "Geography", "Computer Science", "Timepass for Students"]

    #     youtube_labels = [
    #     "Music",
    #     "Gaming",
    #     "Technology",
    #     "Education",
    #     "Science",
    #     "Mathematics",
    #     "Programming / Coding",
    #     "Movies / TV / Trailers",
    #     "Podcasts / Talk Shows",
    #     "News & Current Affairs",
    #     "Sports",
    #     "Fitness & Health",
    #     "Food & Cooking",
    #     "Travel & Adventure",
    #     "History & Culture",
    #     "Art & Animation",
    #     "DIY & How-to Guides",
    #     "Finance & Business",
    #     "Motivation & Self-help",
    #     "Comedy & Entertainment"
    # ]


    if not title in hashmap:
        result = classifier(title, labels)
        hashmap[title] = result
    else:
        result = hashmap[title]
    return result

def wins():
    windows = Desktop(backend="uia").windows()
    return [w.window_text() for w in windows]

# def search_youtube(query):
#     ydl_opts = {"quiet": True, "noplaylist": True}
#     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#         info = ydl.extract_info(f"ytsearch1:{query}", download=False)
#         if "entries" in info and len(info["entries"]) > 0:
#             video = info["entries"][0]
#             return video["webpage_url"]
#     return None

def get_video_description(video_url):
    """
    Extract the description of a YouTube video from its URL using web scraping.
    
    Args:
        video_url (str): The YouTube video URL
        
    Returns:
        str: The video description, or None if not found
    """
    try:
        # Set headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        # Make the request to the video page
        response = requests.get(video_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Method 1: Look for description in meta tags
        # print(1)
        # description_meta = soup.find('meta', {'name': 'description'})
        # if description_meta and description_meta.get('content'):
        #     return description_meta.get('content').strip()
        
        # Method 2: Look for description in script tags (YouTube stores data here)
        # print(2)
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                # Look for description in various JSON patterns
                description_patterns = [
                    r'"description":"([^"]+)"',
                    r'"shortDescription":"([^"]+)"',
                    r'"description":{"simpleText":"([^"]+)"}',
                    r'"description":{"runs":\[{"text":"([^"]+)"}',
                ]
                
                for pattern in description_patterns:
                    matches = re.findall(pattern, script.string)
                    if matches:
                        # Clean up the description
                        description = matches[0]
                        # Decode HTML entities
                        description = description.replace('\\"', '"').replace('\\n', '\n').replace('\\/', '/')
                        # Remove excessive whitespace
                        description = re.sub(r'\s+', ' ', description).strip()
                        if len(description) > 50:  # Ensure it's a meaningful description
                            return description
        
        # Method 3: Look for description in specific div elements
        # print(3)
        # description_divs = soup.find_all('div', {'id': 'description'})
        # for div in description_divs:
        #     text_content = div.get_text(strip=True)
        #     if text_content and len(text_content) > 50:
        #         return text_content
        
        # # Method 4: Look for description in expandable content
        # print(4)
        # expandable_content = soup.find_all('div', class_=re.compile(r'.*expandable.*'))
        # for content in expandable_content:
        #     text_content = content.get_text(strip=True)
        #     if text_content and len(text_content) > 50:
        #         return text_content
        
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"A network error occurred while fetching description: {e}")
        return None
    except Exception as e:
        print(f"An error occurred while extracting description: {e}")
        return None

# while True:
#     windows = wins()
#     for title in windows:
#         if not title.strip():
#             continue
#         if 'youtube' in title.lower():
#             title = ' '.join(title.split(' ')[1:-4])
#             try:
#                 syv = search_youtube_video(title)
#                 if syv != None:
#                     url, title_searched = syv
#                 print(url, title_searched, title)
#                 if title_searched == title:
#                     try:
#                         description = get_video_description(url)
#                         res = is_distracting(f"{title}\n{description}")
#                     except Exception as e2:
#                         print("Couldn't fetch the description!")
#                         res = is_distracting(title)
#                 else:
#                     res = is_distracting(title)
#             except Exception as e:
#                 print("Couldn't fetch the URL!")
#                 res = is_distracting(title)

#             try:
#                 print(f"\n{res}\n")
#                 distracting = res["labels"][0]
#                 if not (res["scores"][res["labels"].index("Education")] > 0.2 or res["scores"][res["labels"].index("Programming")] > 0.2):
#                     print(f"\nDistracting window detected: {title}")
#                     try:
#                         pass
#                         # w = pyautogui.getWindowsWithTitle(title)[0]
#                         # w.activate()
#                     except Exception as e:
#                         print(f"\nError while focusing on {title}: {e}")
#                     print(f"\nClosing: {title}")
#                     # keyboard.press_and_release('ctrl+w')
#                 else:
#                     print(f"\nSafe window: {title}")
#                     pass
#             except Exception as e:
#                 print(f"\nError while the process {title}: {e}")

#     time.sleep(5)

def remove_links(text):
    updated_text = []
    for i in text.split(' '):
        if not 'http' in i:
            updated_text.append(i)
    return ' '.join(updated_text)


distracting_titles = [
    # Video Streaming
    "Netflix",
    "Prime Video",
    "JioHotstar",
    "Hulu",
    "Crunchyroll",
    "Twitch",

    # Social Media
    "Instagram",
    "Snapchat",
    "Facebook",
    "X. It’s what’s happening / X",
    "Threads",
    "Reddit",
    "Pinterest",
    "TikTok",
    "BeReal.",

    # Gaming Platforms
    "Welcome to Steam",
    "Epic Games Store | Download & Play PC Games, Mods, DLCs",
    "Roblox",
    "Riot Games",
    "Discord | Your Place to Talk and Hang Out",
    "Battle.net",
    "Xbox Official Site",
    "PlayStation® Official Site",

    # Chat & Meme Sites
    "9GAG: Go Fun The World",
    "Quora - A place to share knowledge and better understand the world",
    "Tumblr",
    "Imgur: The magic of the Internet",
    "Telegram Messenger",
    "WhatsApp Web",

    # Shopping
    "Online Shopping site in India: Shop Online for Mobiles, Books, Watches, Shoes and More - Amazon.in",
    "Online Shopping Site for Mobiles, Electronics, Furniture, Grocery, Lifestyle, Books & More. Best Offers!",
    "Online Shopping for Women, Men, Kids Fashion & Lifestyle - Myntra",
    "Meesho: Online Shopping Site for Fashion, Electronics, Home & More",
    "Online Shopping for Men, Women & Kids Fashion - AJIO",
    "AliExpress - Online Shopping for Popular Electronics, Fashion, Home & Garden",

    # Clickbait / News
    "BuzzFeed",
    "Home | Daily Mail Online",
    "TMZ"
]

hashmap = {}

hash_links = {}

hash_desc = {}

try:
    with open("userData.json", "r") as f:
        data = json.load(f)
    backendActive = data["backendActive"]
except PermissionError as e:
    time.sleep(5)
except OSError as e1:
    time.sleep(5)
except Exception as e2:
    print(f'Error: {e2}')


while backendActive == True:
    try:
        with open("userData.json", "r") as f:
            data = json.load(f)
        backendActive = data["backendActive"]
    except PermissionError as e:
        time.sleep(5)
    except OSError as e1:
        time.sleep(5)
    except Exception as e2:
        print(f'Error: {e2}')

    for t in wins():
        for i in distracting_titles:
            if i.lower() in t.lower():
                print(f'Title: {t}\n\n\n')
                print(f'Distracting window detected: {t}')
                try:
                    with open('distractionHistory.json', 'r') as f:
                        data = json.load(f)
                        data["Distractions"].append([t, get_current_datetime()])
                    with open('distractionHistory.json', 'w') as f:
                        json.dump(data, f, indent=4)
                except Exception as e:
                    print("Fatal Error: JSON file loading or dumping couldn't work. Rewriting the JSON file to its default.")
                    with open('distractionHistory.json', 'w') as f:
                        json.dump({"Distractions":[[t, get_current_datetime()]]}, f, indent=4)
                print(f'Focusing: {t}')
                with open("userData.json", 'r') as f:
                    intervention = json.load(f)["Intervention Style"]
                if intervention == 'auto-close':
                    try:
                        pyautogui.getWindowsWithTitle(t)[0].activate()
                        print(f'Successfully focused on: {t}')
                    except Exception as e:
                        print(f'Couldn\'t focus on: {t}')
                    print(f'Closing: {t}')
                    try:
                        keyboard.press_and_release('ctrl+w')
                        print(f'Successfully closed: {t}\n\n\n')
                    except Exception as e:
                        print(f"Couldn't close: {t}\n\n\n")
                else:
                    messagebox.showinfo("Information", "Distracting Window detected!!!")
        description = ''
        # browser based youtube tab closing
        title = t
        if 'Google Chrome' == title.split(' - ')[-1] or 'Opera' == title.split(' - ')[-1]:
            if 'YouTube' == title.split(' - ')[-2]:
                # handle the case where the title is like this: (1) Title - Youtube - Google Chrome
                t1 = time.time()
                title_tf = False;
                try:
                    if title.split(' ')[0][0] == '(' and title.split(' ')[0][-1] == ')':
                        title = ' '.join(' - '.join(title.split(' - ')[0:-2]).split(' ')[1::])
                    else:
                        title = ' - '.join(title.split(' - ')[0:-2])
                    print(f'Title: {title}')
                    title_tf = True;
                except Exception as e:
                    print(f'Error: {e}')

                if not t in wins():
                    break

                if not title in hashmap:
                    url_tf = False;
                    try:
                        if not title in hash_links:
                            url, title_searched = search_youtube_video(title)
                            hash_links[title] = (url, title_searched)
                        else:
                            url, title_searched = hash_links[title]
                        if not url == None:
                            url_tf = True;
                            print(f'URL: {url}')
                    except Exception as e:
                        print(f'Error: {e}')

                    if not t in wins():
                        break

                    desc_tf = False;
                    try:
                        if not url in hash_desc:
                            description = get_video_description(url)
                            hash_desc[url] = description
                        else:
                            description = hash_desc[url]
                        if not description == None:
                            desc_tf = True
                            print(f'Description: {description}')
                    except Exception as e:
                        print(f'Error: {e}')
                else:
                    description = 'Hello World!'

                if not t in wins():
                    break

                letters = list(string.ascii_letters)
                digits = list(string.digits)
                special_characters = list(string.punctuation)
                all_characters = letters + digits + special_characters + [' ']
                

                is_dist_tf = False;
                try:
                    if title_tf and url_tf and desc_tf:
                        if not f"{title}" in hashmap:
                            d = ''
                            for char in description:
                                if (char in all_characters):
                                    d = d + char

                            d = remove_links(d)

                            if len(d) > 501:
                                description = d[0:500]
                            is_dist = is_distracting(f"{title}\n{description}")
                            hashmap[f"{title}"] = is_dist
                        else:
                            is_dist = hashmap[f"{title}"]
                        is_dist_tf = True;
                    elif title_tf and url_tf:
                        if not title in hashmap:
                            is_dist = is_distracting(title)
                            hashmap[title] = is_dist
                        else:
                            is_dist = hashmap[title]
                        is_dist_tf = True;
                    elif title_tf:
                        if not title in hashmap:
                            is_dist = is_distracting(title)
                            hashmap[title] = is_dist
                        else:
                            is_dist = hashmap[title]
                        is_dist_tf = True;
                except Exception as e:
                    print(f'Error: {e}')

                try:
                    print(f'{is_dist}')
                except Exception as e:
                    print(e)

                print(time.time() - t1)

                print('\n\n\n')

                try:
                    if not (is_dist['scores'][is_dist["labels"].index('Education')] > 0.30 or is_dist['scores'][is_dist["labels"].index('Programming')] > 0.30):
                        if is_dist_tf and t in wins():
                            print(f'Distracting window detected: {t}')
                            try:
                                with open('distractionHistory.json', 'r') as f:
                                    data = json.load(f)
                                    data["Distractions"].append([t, get_current_datetime()])
                                with open('distractionHistory.json', 'w') as f:
                                    json.dump(data, f, indent=4)
                            except Exception as e:
                                print("Fatal Error: JSON file loading or dumping couldn't work. Rewriting the JSON file to its default.")
                                with open('distractionHistory.json', 'w') as f:
                                    json.dump({"Distractions":[[t, get_current_datetime()]]}, f, indent=4)
                            print(f'Focusing: {t}')
                            with open("userData.json", 'r') as f:
                                intervention = json.load(f)["Intervention Style"]
                            if intervention == 'auto-close':
                                try:
                                    pyautogui.getWindowsWithTitle(t)[0].activate()
                                    print(f'Successfully focused on: {t}')
                                except Exception as e:
                                    print(f'Couldn\'t focus on: {t}')
                                print(f'Closing: {t}')
                                try:
                                    keyboard.press_and_release('ctrl+w')
                                    print(f'Successfully closed: {t}\n\n\n')
                                except Exception as e:
                                    print(f"Couldn't close: {t}\n\n\n")
                            else:
                                messagebox.showinfo("Information", "Distracting Window detected!!!")
                    else:
                        print(f'Safe window: {title}\n\n\n')
                except Exception as e:
                    print(f'Error: {e}')

        if 'Microsoft​ Edge' == title.split(' - ')[-1].replace('\200b', ''):
            if 'YouTube' in title.split(' - ')[-3]:
                # handle the case where the title is like this: (1) Title - Youtube - Personal - Microsoft Edge
                t1 = time.time()
                title_tf = False;
                try:
                    if title.split(' ')[0][0] == '(' and title.split(' ')[0][-1] == ')':
                        title = ' '.join(' - '.join(title.split(' - ')[0:-3]).split(' ')[1::])
                    else:
                        title = ' - '.join(title.split(' - ')[0:-3])
                    print(f'Title: {title}')
                    title_tf = True;
                except Exception as e:
                    print(f'Error: {e}')

                if not t in wins():
                    break

                if not title in hashmap:
                    url_tf = False;
                    try:
                        if not title in hash_links:
                            url, title_searched = search_youtube_video(title)
                            hash_links[title] = (url, title_searched)
                        else:
                            url, title_searched = hash_links[title]
                        if not url == None:
                            url_tf = True;
                            print(f'URL: {url}')
                    except Exception as e:
                        print(f'Error: {e}')

                    if not t in wins():
                        break

                    desc_tf = False;
                    try:
                        if not url in hash_desc:
                            description = get_video_description(url)
                            hash_desc[url] = description
                        else:
                            description = hash_desc[url]
                        if not description == None:
                            desc_tf = True
                            print(f'Description: {description}')
                    except Exception as e:
                        print(f'Error: {e}')
                else:
                    description = 'Hello World!'

                if not t in wins():
                    break

                letters = list(string.ascii_letters)
                digits = list(string.digits)
                special_characters = list(string.punctuation)
                all_characters = letters + digits + special_characters + [' ']
                

                is_dist_tf = False;
                try:
                    if title_tf and url_tf and desc_tf:
                        if not f"{title}" in hashmap:
                            d = ''
                            for char in description:
                                if (char in all_characters):
                                    d = d + char

                            d = remove_links(d)

                            if len(d) > 501:
                                description = d[0:500]
                            is_dist = is_distracting(f"{title}\n{description}")
                            hashmap[f"{title}"] = is_dist
                        else:
                            is_dist = hashmap[f"{title}"]
                        is_dist_tf = True;
                    elif title_tf and url_tf:
                        if not title in hashmap:
                            is_dist = is_distracting(title)
                            hashmap[title] = is_dist
                        else:
                            is_dist = hashmap[title]
                        is_dist_tf = True;
                    elif title_tf:
                        if not title in hashmap:
                            is_dist = is_distracting(title)
                            hashmap[title] = is_dist
                        else:
                            is_dist = hashmap[title]
                        is_dist_tf = True;
                except Exception as e:
                    print(f'Error: {e}')

                try:
                    print(f'{is_dist}')
                except Exception as e:
                    print(e)

                print(time.time() - t1)

                print('\n\n\n')

                try:
                    if not (is_dist['scores'][is_dist["labels"].index('Education')] > 0.30 or is_dist['scores'][is_dist["labels"].index('Programming')] > 0.30):
                        if is_dist_tf and t in wins():
                            print(f'Distracting window detected: {t}')
                            try:
                                with open('distractionHistory.json', 'r') as f:
                                    data = json.load(f)
                                    data["Distractions"].append([t, get_current_datetime()])
                                with open('distractionHistory.json', 'w') as f:
                                    json.dump(data, f, indent=4)
                            except Exception as e:
                                print("Fatal Error: JSON file loading or dumping couldn't work. Rewriting the JSON file to its default.")
                                with open('distractionHistory.json', 'w') as f:
                                    json.dump({"Distractions":[[t, get_current_datetime()]]}, f, indent=4)
                            print(f'Focusing: {t}')
                            with open("userData.json", 'r') as f:
                                intervention = json.load(f)["Intervention Style"]
                            if intervention == 'auto-close':
                                try:
                                    pyautogui.getWindowsWithTitle(t)[0].activate()
                                    print(f'Successfully focused on: {t}')
                                except Exception as e:
                                    print(f'Couldn\'t focus on: {t}')
                                print(f'Closing: {t}')
                                try:
                                    keyboard.press_and_release('ctrl+w')
                                    print(f'Successfully closed: {t}\n\n\n')
                                except Exception as e:
                                    print(f"Couldn't close: {t}\n\n\n")
                            else:
                                messagebox.showinfo("Information", "Distracting Window detected!!!")
                    else:
                        print(f'Safe window: {title}\n\n\n')
                except Exception as e:
                    print(f'Error: {e}')



                
    time.sleep(0.25)