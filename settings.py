## settings for shoutyd
import os

LOCAL_ROOT = dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(LOCAL_ROOT)
# local port
LOCAL_PORT=42422
# local news page, this is updated with the live info on reboot / app restart / login.
LOCAL_NEWS = os.path.join(LOCAL_ROOT,'data/latest.md')

# location of the os-release file for system info
RELEASE_PATH = '/etc/os-release'

# application paths/names
DIST_HELP = "opensuse-welcome"
#GUI_HELP =

# html paths
HOMEPAGE = os.path.join(LOCAL_ROOT,'templates/home.html')
ABOUTPAGE = os.path.join(LOCAL_ROOT,'templates/about.html')
TESTPAGE = os.path.join(LOCAL_ROOT,'templates/test.html')

# path to persisted settings and data. location of local settings
PERSIST_PATH = '~/.config/shoutyd'

# this is appended with the distro name, ie "leap" etc to get latest news
# geekos will work for now.
BASE_TARGET = 'https://geekos.org/test/'

# only use standard RSS 1.0 or 2.0 feeds
RSSFEED_URL = [
               'https://news.opensuse.org/feed.xml',
               #'https://thisweek.gnome.org/index.xml',
               #'https://planet.opensuse.org/en/atom.xml',
               #'https://flathub.org/api/v2/feed/new'
]

RSSFEED_URL2 = {
    'openSUSE News': 'https://news.opensuse.org/feed.xml',
    'openSUSE Global': 'https://planet.opensuse.org/en/atom.xml',
    #'Gnome News': 'https://thisweek.gnome.org/index.xml',
    #'App News': 'https://flathub.org/api/v2/feed/new'
}
