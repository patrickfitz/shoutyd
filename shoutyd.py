#!/usr/bin/python3
## Compilation mode, support OS-specific options
## nuitka-project-if: {OS} in ("Windows", "Linux", "Darwin", "FreeBSD"):
## nuitka-project: --onefile
## nuitka-project-else:
# nuitka-project: --mode=standalone

# Add local libs directory to sys.path
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "libs"))

import subprocess
from webui import webui
from markdown2 import Markdown

import feedparser
from babik.template1 import render_template, load_template
from settings import *
import http.client, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
import json
from datetime import datetime
from time import mktime
import logging

# Create logger
logger = logging.getLogger('shouty_logger')
logger.setLevel(logging.DEBUG)  # Set the lowest level you want to capture

# Create formatters
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)  # Log INFO and above to the console
console_handler.setFormatter(formatter)

# Create file handler
file_handler = logging.FileHandler('shouty.log')
file_handler.setLevel(logging.ERROR)  # Log DEBUG and above to the file
file_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)
shoutyb = webui.Window()

# Dictionary to store the mapping between element IDs and handler functions
element_handlers = {}
def webui_event(element_id):
    """
    Decorator to register a function as a handler for a specific UI element.
    If no element_id is provided, the function's name is used.
    """
    #global element_handlers = {}
    def decorator(func):
        key = element_id or func.__name__
        element_handlers[key] = func
        return func
    return decorator

def link_test(url):
    """
    returns HTTP status of url.
    use to:
     - show/hide links
     - determine online status
    """
    u = urllib.parse.urlparse(url)
    conn = http.client.HTTPSConnection(u.netloc)
    conn.request("HEAD", u.path or "/")
    return conn.getresponse().status

def pretty(d, indent=0):
   for key, value in d.items():
      print('\t' * indent + str(key))
      if isinstance(value, dict):
         pretty(value, indent+1)
      else:
         print('\t' * (indent+1) + str(value))

def load_latest(local_data=LOCAL_NEWS):
    """
    get local news file (in markdown format) and convert it to html.
    :param local_data: markdown
    :return: html
    """
    # open latest (local) news
    with open(local_data, 'r', encoding='utf-8') as f:
        latest_news_md = f.read()
        markdowner = Markdown()
        latest_news = {}
        latest_news['latest_news'] = markdowner.convert(latest_news_md)
        logger.info('loading local news')
        # output dict
    return latest_news


def parsefeed(feed=RSSFEED_URL):
    """
    parse RSS feed and return dictionary of items. Handle RSS 1.0 and Atom Feeds.
    """
    # Optional: store these somewhere (e.g., in a file or database)
    response = urllib.request.urlopen(feed)
    xml_data = response.read()
    # Parse the XML
    root = ET.fromstring(xml_data)
    entries = []
    # Get name via rss > channel > title
    feed_name = root.find("./channel").find("title").text
    # print(str(feed_name.find("title").text))
    # RSS feeds usually have the structure: rss > channel > item
    logger.info('parsing news feeds')
    for item in root.findall("./channel/item"):
        title = item.find("title").text if item.find("title") is not None else "No Title"
        description = item.find("description").text if item.find("description") is not None else "No Description"
        link = item.find("link").text if item.find("link") is not None else "No Link"

        entries.append({
            "title": title,
            "description": description,
            "url": link
        })
    #print('parsed '+feed_name)
    return entries, feed_name

def parse_os_release(file_path: str) -> dict:
    """
    parse os-release file for distro data
    :param file_path:
    :return: text
    """
    data = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue  # Skip empty lines and comments
            if '=' in line:
                key, val = line.split('=', 1)
                val = val.strip().strip('"')  # Remove quotes
                data[key.strip()] = val
    desktop = os.environ['XDG_SESSION_DESKTOP'].capitalize()
    data['DESKTOP'] = desktop
    logger.info('running on ' + desktop)
    return data


@webui_event('is_root')
def is_root():
    """
    determines if current user is root
    TODO: use to conditionally populate nav bar
    :return: boolean
    """
    return os.geteuid() == 0

@webui_event('has_sudo')
def has_sudo():
    """
    determines if current user has password less sudo rights
    TODO: use to conditionally populate nav bar
    :return: boolean
    """
    try:
        subprocess.check_call(['sudo', '-n', 'true'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logger.debug('I have sudo rights')
        return True   # sudo is allowed without password
    except subprocess.CalledProcessError:
        logger.debug('I have no sudo rights')
        return False  # sudo exists but password required or not allowed
    except FileNotFoundError:
        logger.debug('SUDO: File not found. Probably not installed!')
        return False  # sudo not installed

# decorating the webui.bind() call. inspired by:
# https://stackoverflow.com/questions/739654/how-do-i-make-function-decorators-and-chain-them-together/1594484#1594484
'''
def webui_event(window, event_name=None):
    """
    :param window:
    :param event_name:
    :return:
    decorator for functions triggered by webui actions
    """
    def decorator(func):
        name_to_bind = event_name if isinstance(event_name, str) else func.__name__
        window.bind(name_to_bind, func)
        logger.info(f'event bound {name_to_bind}')
        return func
    return decorator

# Store event bindings to apply later
#_deferred_binds = []

#def webui_event(event_name=None):
#    """
#    Decorator to register a function for a webui event.
#    Uses webui.bind() when the window is ready.
#    """
#    def decorator(func):
#        name = event_name if event_name else func.__name__
#        _deferred_binds.append((name, func))
#        return func
#    return decorator

#def bind_all_events(window):
#    for name, func in _deferred_binds:
#        window.bind(name, func)  # ✅ use the window’s bind method
'''
@webui_event('os_update')
def os_update():
    """
    webui trigger to run zupper update. Requires sudo
    TODO: move command to settings file to enable multi distro use
    :return: nono
    """
    logger.info('starting update')
    #webui.run('shoutyb','document.getElementById("loader").style.display = "block";')

    # Launch gnome-terminal and run the given command
    command = "zypper -n dup "
    process = subprocess.Popen(["pkexec", "bash", "-c", f"{command};"],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               text=True
                               )

    #for line in process.stdout:
    #    logger.info("OUTPUT:", line.strip())
    # Log output line by line
    for line in process.stdout:
        logger.info(line.strip())

    # Wait for the process to finish
    process.wait()
    logging.info("update completed.")
    #webui.run('shoutyb','document.getElementById("loader").style.display = "none";')

    # subprocess.Popen(["gnome-terminal", "--", "bash", "-c", f"{command};"])
    # rc=subprocess.run('nmon', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)



@webui_event(shoutyb)
def welcome(e: webui.Event):
    """
    webui trigger to run the welcome app
    :return:
    """
    subprocess.call(["opensuse-welcome"])


@webui_event(shoutyb)
def desktop_help(e: webui.Event):
    """
    webui trigger to run the desktop tour.
    TODO: enable KDE detection and update accordingly
    :return:
    """
    subprocess.call(["gnome-help"])

@webui_event('hardware_data')
def send_hardware():
    """
    run lshw to extract hardware info for upload.
    TODO: one way hash sensitive information such as UUID and MAC address
    :return:
    """
    p = subprocess.Popen(["sudo", "lshw", "-xml", "-quiet"], stdout=subprocess.PIPE)
    out, err = p.communicate()
    logger.info(out)

@webui_event('donate_now')
def donate_now(): #e: webui.Event):
    rc = webui.open_url("https://geekos.org/donate")
    logger.info(str(rc))

@webui_event('check_calendar')
def check_calendar(): #e: webui.Event):
    rc = webui.open_url("https://calendar.opensuse.org")
    #shoutyb.navigate("https://calendar.opensuse.org/")
    logger.info(str(rc))

@webui_event('go_meet')
def go_meet(): #e: webui.Event):
    rc = webui.open_url("https://meet.opensuse.org/bar")
    logger.info(str(rc))

@webui_event(shoutyb)
def process_form(e: webui.Event):
    #print(f"hello "+label)
    print(f"hello {e.element}")
    #print(f"Received type: {e.event_type}")
    #count = e.get_count()
    #print(f"The event has {count} arguments.")
    #for v in range(count):
    #    print(e.get_string_at(v))
    #    print(e.get_name_at(v))
    value = e.get_string()
    logger.debug(f"The first argument as a string is '{value}'.")
    #print(str(webui.ui_decode(value)))

    # print(f"Received value: {e.value}")
    # You can add further processing here, such as saving to a database


def test_form():
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Sample Form</title>
    <script src="webui.js"></script>
    <!--<script src="static/shouty.js"></script>-->
</head>
<body>
    <h1>Enter Your Details</h1>
    <button class="" id="theme-toggle" title="Color Mode">
        <span class="material-icons md-18">dark_mode</span>
    </button>

    <form id="userForm">
        <label for="name">Name:</label>
        <input type="text" id="name" name="name" required><br><br>
        <label for="email">Email:</label>
        <input type="email" id="email" name="email" required><br><br>
        <button type="submit">Submit</button>
    </form>
    <script>
        // Handle form submission
        //document.getElementById('userForm').addEventListener('submit', function(event) {
        //    event.preventDefault(); // Prevent default form submission
        //    const jsonData = getFormDataAsJSON(this);
        //    console.log(jsonData);
        //    // Call the Python function via WebUI
       //     webui.call('process_form', jsonData);
       // });
    </script>
    <script src="static/shouty.js"></script>

</body>
</html>
    """
    return html_content


@webui_event(shoutyb)
def settings_data(e: webui.Event):
    title = 'ShoutyB Settings...'
    message='''  
        <form id="userForm">
            <input type="radio" id="login" name="popup_frequency" value="LOGIN">
            <label for="login">On Login</label><br>
            <input type="radio" id="update" name="popup_frequency" value="UPDATE">
            <label for="update">On Update</label><br>
            <input type="radio" id="never" name="popup_frequency" value="NEVER">
            <label for="never">Never Show</label><br>            
            <label for="name">Name:</label>
            <input type="text" id="name" name="name" required><br><br>
            <div class="dialog-actions">
                <button class="dialog-btn dialog-cancel" onclick="hideDialog()">Cancel</button>
                <button class="dialog-btn dialog-confirm" type="submit" onclick="submitDialog()">Submit</button>
            </div>
        </form>
    '''
    rc=shoutyb.script(f"showDialog({json.dumps(title)},{json.dumps(message)});")
    #rc=shoutyb.script(f"showDialog({json.dumps(title)});")
    #print(rc)


@webui_event(shoutyb)
def about_data(e: webui.Event):
    title = '<b>About ShoutyB</b>'
    message = '''<p><strong>ShoutyD</strong> is "welcome" tool that gives you up to date information on updates and changes 
            to your favourite operating system. Launched at login, it gets the latest news and updates and puts the front and centre.</p>
            <p>Think of it as a marketing tool - for Linux.</p>

        <h3>What does it do?</h3>
        <ul>
            <li>📣 Displays newly added features after each update.</li>
            <li>📂 Provides a clean interface to browse release notes, changelogs, or upgrade logs.</li>
            <li>🛠️ It's hackable too: with a little bit of python and html you can display whatever you want.</li>
            <li>📊 Lightweight: the installed browser does the heavy lifting. Makes it Cross Desktop as well!</li>
        </ul>
        <h3>Creating a Hardware Database</h3>
        <p>If are root or you have sudo access, ShoutyD can create a (anonymized) snapshot of your hardware. Using this 
        information, with a bit of input from you (ie what works, what doesn't) we will be able to define "best of breed"
        hardware compatibility list - in other words, what works best with Linux. Hardware vendors: you want to be a part of this.
        <h3>But Why?</h3>
        I wrote this to scratch a number of itches:
        <ul>
            <li>Initially, I wanted to have greater visibility of new features as they were added to my system 
            (such as the latest version of Gnome) - without digging through release notes</li> 
            <li>Improve current welcome apps which are difficult to modify and are are static in nature</li> 
            <li>For greater adoption of Linux, the hardware database would prove incredibly useful</li>
            <li>I came across WebUI and I thought, why not?</li> 
         </ul>
        Have a lot of Fun - with ShoutyD!
    '''
    shoutyb.script(f"showDialog({json.dumps(title)},{json.dumps(message)});")


@webui_event(shoutyb)
def news_data(e: webui.Event,feed=RSSFEED_URL):
    logger.info('getting news feed')
    all_entries = []
    for url in feed:
        feed = feedparser.parse(url)
        logger.debug('feed title is '+feed['feed']['title'])
        for entry in feed.entries:
            # Try to get published_parsed or updated_parsed
            logger.debug(entry['title'])
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published = datetime.fromtimestamp(mktime(entry.published_parsed))
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                published = datetime.fromtimestamp(mktime(entry.updated_parsed))
            else:
                # If no date, set to very old date to avoid crashing
                published = datetime.min

            # Attach the parsed datetime to entry
            entry.published_datetime = published
            all_entries.append(entry)

    # Sort all entries by published_datetime descending (newest first)
    sorted_entries = sorted(all_entries, key=lambda e: e.published_datetime, reverse=True)

    # Example output
    for entry in sorted_entries:
        logger.info(f"{entry.published_datetime} - {entry.title} ({entry.link})")

    """
    def news_data(e: webui.Event, feed=RSSFEED_URL):
        logger.info('getting news feed')
        all_entries = []
        for url in feed:
            feed = feedparser.parse(url)
            logger.debug('feed title is ' + feed['feed']['title'])
            for entry in feed.entries:
                # Try to get published_parsed or updated_parsed
                logger.debug(entry['title'])
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published = datetime.fromtimestamp(mktime(entry.published_parsed))
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    published = datetime.fromtimestamp(mktime(entry.updated_parsed))
                else:
                    # If no date, set to very old date to avoid crashing
                    published = datetime.min

                # Attach the parsed datetime to entry
                entry.published_datetime = published
                all_entries.append(entry)

        # Sort all entries by published_datetime descending (newest first)
        sorted_entries = sorted(all_entries, key=lambda e: e.published_datetime, reverse=True)

        # Example output
        for entry in sorted_entries:
            logger.info(f"{entry.published_datetime} - {entry.title} ({entry.link})")
        """

#def get_news(e: webui.Event,feed=RSSFEED_URL):
#    logger.info('getting news feeds')
#    feeds = []
#    for url in feed:
#        feed = feedparser.parse(url)
#        logger.debug('feed title is '+feed['channel']['title'])
#        for entry in feed.entries:
#            logger.debug(entry['title'])
#            logger.debug(entry['description'])
#            logger.debug(entry['link'])
#        feeds.append(feed.entries)
#    return feeds


def get_news(e: webui.Event,feed_urls=RSSFEED_URL):
    result = {}
    for url in feed_urls:
        logger.debug(f"Getting news from {url}")
        feed = feedparser.parse(url)
        logger.debug(feed.feed.get("title", "Unknown Feed"))

        #logger.debug(feed.feed.get("title", "Unknown Feed"))
        # Skip invalid or empty feeds
        if feed.bozo or not feed.entries:
            continue

        #feed_name = feed.feed.get("title", "Unknown Feed")
        entries = []
        entries.append(feed.feed.get("title", "Untitled Feed"))
        #print(str(entries))
        entry_data={}
        #entries['title']+
        for entry in feed.entries:
            logger.debug(str(entry.title))
            logger.debug(str(entry.summary))
            logger.debug(str(entry.link))
            entry_data = {
                "title": entry.get("title", "No Title"),
                "description": entry.get("description", entry.get("summary", "No Description")),
                "url": entry.get("link", "#")
            }
            entries.append(entry_data)
        # Append to result under the feed name
        result = entries # = entries
        #result ={}
        #pretty(result, indent=4)
        #for f in feed:
        #    print(str(f)[0:80])
    return result


def home():
    homepage(shoutyb)

def foreground():
    subprocess.Popen(["wmctrl", "-a", "ShoutyD:"])
    # wmctrl - a
    # "ShoutyD:"


def events(e: webui.Event):
    """
    marshals and runs click events from webui
    :param e:
    :return:
    """
    logger.debug('event type: ' + str(e.event_type) + ' (type)')
    logger.debug('event type: ' + str(e.element) + ' (element)')
    logger.debug('event type: ' + str(e.get_string) + ' (string)')
    value = e.get_string()
    logger.debug(f"The first argument as a string is '{value}'.")
    if e.element in globals() and callable(globals()[e.element]):
        #logger.debug('>>> executing ' + str(e.element))
        globals()[e]()
        #logger.debug('>>> completed ' + str(e.element))

def events(e: webui.Event):
    """
    Dispatches events to the appropriate handler based on the element ID.
    """
    logger.debug(f"Event type: {e.event_type}, Element: {e.element}")
    value = e.get_string()
    logger.debug(f"The first argument as a string is '{value}'.")

    handler = element_handlers.get(e.element)
    if callable(handler):
        handler()
    else:
        logger.warning(f"No handler registered for element '{e.element}'")


def on_link_click(href):
    logger.debug("User clicked link to:", href)

def homepage(browser):
    #template = load_template('dialog.html')
    template = load_template("home.html")
    latest = load_latest()
    #print(osrel)
    feeds = get_news(RSSFEED_URL)
    #print(str(feeds)[:120])
    for feed in feeds:
        logger.debug(f'feed is {feed}')
        #print(str(feed.description)[:150])
        #print(str(feed.description)[:150])
    #latest={}
    #html_page = render_template(template, osrel, latest, feeds)
    html_page = render_template(template, {
        "is_root": is_root(),
        "has_sudo": has_sudo(),
        "osrel": osrel,
        "latest": latest,
        "feeds": feeds
    })
    #html_page = test_form()
    browser.bind("", events)
    browser.set_size(750, 900)
    #browser.set_profile("ShoutyD", "shouty-profile")
    browser.show(html_page)
    browser.show_browser(html_page, webui.Browser.Firefox)
    #success=browser.show_browser(html_page, webui.Browser.Chromium)
    #print(str(success))
    #browser.show_wv(html_page)
    url = browser.get_url()
    logger.info(f"Current URL: {url}")
    # browser.script("hide('welcome')")
    #browser.script("show('welcome')")
    # browser.script("window.addEventListener('contextmenu', event= > event.stopPropagation(), true);")
    #browser.script("alert('here is something');")
    #browser.script('document.getElementById("loader").style.display = "none";')

    webui.wait()
    logger.info('Browser Window closed. Shutting down.')
    #browser.delete_profile()


if __name__ == '__main__':
    try:
        webui.set_config(webui.Config.show_wait_connection, True)
        local_settings = os.path.join(PERSIST_PATH, 'user_settings', '.dat')
        osrel = parse_os_release(RELEASE_PATH)
        logger.info("running as root: " + str(is_root()))
        logger.info("has sudo rights: " + str(has_sudo()))
        logger.info("javascript logging is on.")
        # open dependencies - home page
        #HOMEPAGE='templates/bigtest.html'
        #with open(HOMEPAGE, 'r', encoding='utf-8') as f:
        #    home_page = f.read()
        #    osrel = parse_os_release(RELEASE_PATH)
        success = webui.set_default_root_folder(LOCAL_ROOT)
        if success:
            logger.info("Default root folder set successfully.")
        success = shoutyb.set_port(LOCAL_PORT)
        if not success:
            logger.warning('set port failed')
            port = webui.get_free_port()
            success = shoutyb.set_port(port)
            logger.warning(f"Running on from new port {port}")
            foreground()
            #shoutyb = webui.Window()
        else:
            logger.info('port set')
        homepage(shoutyb)
    except KeyboardInterrupt:
        logger.info("\nShoutyB interrupted by Ctrl+C, shutting down.")
        shoutyb.close()  # Optional, if cleanup is needed
        webui.exit()
        exit(0)

# open dependencies - hardware summary
# with open('hw.xml', 'r', encoding='utf-8') as f:
#    xml_data = f.read()
# open dependencies - javascript
# with open('viewer.js', 'r', encoding='utf-8') as f:
#    viewer_js = f.read()
    """"    
    news_feed = ''
    shoutyb.script("showDialog2();")
    #print('getting news')
    for f in feed:
        news = feedparser.parse(f)
        feed_title = news['feed']['title']
        for item in news['entries']:
            print(item['title']+'  '+str(item['published']))
            # print(item['description'])
            # print(item['link'])
            story = f'<div class="story"><h2>{item['title']}</h2><p>{item['description']}<a href="{item['link']}">(read more)</a></p></div><hr/>'
            # print(story)
            news_feed = news_feed + story
    #shoutyb.script(f"showDialog({json.dumps(feed_title)},{json.dumps(news_feed)});")
    #shoutyb.script(f"fillDialog({json.dumps(feed_title)},{json.dumps(news_feed)});")
    print('news got')
    # data,feed_name=parsefeed()
    # title='Latest News'+feed_name
    # title = feed_name
    # news_feed=''
    # for d in data:
    #    story=f'<div class="story"><h3>{d['title']}</h3><p>{d['description']}<a href="{d['url']}" target="_blank">&nbsp;(read more)</a></p></div><hr/>'
    #    news_feed = news_feed+story
    # shoutyb.script(f"showDialog({json.dumps(title)},{json.dumps(news_feed)});")
    """
