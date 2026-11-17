#!/usr/bin/env python3
"""yog panel: the yog board in a layer-shell popover under the bar.

Clicking the waybar module runs this. The first run starts the panel and
leaves it resident; later runs find it through the pidfile and send SIGUSR1,
which shows or hides it at once. Cookies persist in ~/.local/share/yog-panel,
so the setup secret is typed once.

    yog-panel.py            toggle (start shown if not running)
    yog-panel.py --hidden   start hidden, e.g. from autostart
"""
import os
import signal
import sys
from urllib.parse import urlparse

import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
gi.require_version("GtkLayerShell", "0.1")
gi.require_version("WebKit2", "4.1")
from gi.repository import Gdk, GLib, Gtk, GtkLayerShell, WebKit2  # noqa: E402

try:  # PyGObject 3.52 moved the unix helpers out of GLib
    from gi.repository import GLibUnix

    signal_add = GLibUnix.signal_add
except ImportError:
    signal_add = GLib.unix_signal_add

URL = os.environ.get("YOG_URL", "https://yog.felipeafonso.com")
HOST = urlparse(URL).netloc
# The page is designed for a 400 px wide phone. On a 4K monitor at scale 1
# that is tiny next to the bar, so the panel zooms it and grows to match.
ZOOM = float(os.environ.get("YOG_ZOOM", "1.5"))
WIDTH, MAX_HEIGHT = round(400 * ZOOM), round(860 * ZOOM)
GRACE_US = 700_000
PIDFILE = os.path.join(os.environ.get("XDG_RUNTIME_DIR", "/tmp"), "yog-panel.pid")
DATA = os.path.join(GLib.get_user_data_dir(), "yog-panel")
CACHE = os.path.join(GLib.get_user_cache_dir(), "yog-panel")


def running_pid():
    try:
        pid = int(open(PIDFILE).read())
        with open(f"/proc/{pid}/cmdline", "rb") as f:
            return pid if b"yog-panel" in f.read() else None
    except (OSError, ValueError):
        return None


class Panel:
    def __init__(self):
        self.window = Gtk.Window()
        self.window.set_title("yog")
        GtkLayerShell.init_for_window(self.window)
        GtkLayerShell.set_namespace(self.window, "yog-panel")
        GtkLayerShell.set_layer(self.window, GtkLayerShell.Layer.TOP)
        GtkLayerShell.set_anchor(self.window, GtkLayerShell.Edge.TOP, True)
        GtkLayerShell.set_anchor(self.window, GtkLayerShell.Edge.RIGHT, True)
        GtkLayerShell.set_margin(self.window, GtkLayerShell.Edge.TOP, 4)
        GtkLayerShell.set_margin(self.window, GtkLayerShell.Edge.RIGHT, 20)
        GtkLayerShell.set_keyboard_mode(self.window, GtkLayerShell.KeyboardMode.ON_DEMAND)

        os.makedirs(DATA, exist_ok=True)
        manager = WebKit2.WebsiteDataManager(base_data_directory=DATA, base_cache_directory=CACHE)
        context = WebKit2.WebContext.new_with_website_data_manager(manager)
        context.get_cookie_manager().set_persistent_storage(
            os.path.join(DATA, "cookies.sqlite"), WebKit2.CookiePersistentStorage.SQLITE
        )
        self.view = WebKit2.WebView.new_with_context(context)
        paper = Gdk.RGBA()
        paper.parse("#efe6d2")
        self.view.set_background_color(paper)
        self.view.set_zoom_level(ZOOM)
        self.view.connect("decide-policy", self.on_policy)
        self.view.connect("create", self.on_create)
        self.window.add(self.view)

        self.window.connect("key-press-event", self.on_key)
        # Focus arrives and leaves again while the surface maps, so losing
        # focus only closes the panel once it has been up for a moment.
        self.shown_at = 0
        self.window.connect("focus-out-event", self.on_focus_out)
        self.window.connect("delete-event", lambda *_: self.hide() or True)
        self.view.load_uri(URL)

    def size(self):
        display = Gdk.Display.get_default()
        monitor = display.get_primary_monitor() or display.get_monitor(0)
        height = min(MAX_HEIGHT, monitor.get_geometry().height - 80) if monitor else MAX_HEIGHT
        self.window.set_size_request(WIDTH, height)

    def show(self):
        self.size()
        self.shown_at = GLib.get_monotonic_time()
        self.window.show_all()
        self.window.present()

    def hide(self):
        self.window.hide()

    def on_focus_out(self, *_):
        if GLib.get_monotonic_time() - self.shown_at > GRACE_US:
            self.hide()
        return False

    def toggle(self):
        self.hide() if self.window.get_visible() else self.show()
        return GLib.SOURCE_CONTINUE

    def on_key(self, _window, event):
        if event.keyval == Gdk.KEY_Escape:
            self.hide()
            return True
        return False

    def open_outside(self, uri):
        Gtk.show_uri_on_window(None, uri, Gdk.CURRENT_TIME)
        self.hide()

    def on_policy(self, _view, decision, kind):
        """Anything that is not yog itself opens in the real browser."""
        if kind == WebKit2.PolicyDecisionType.RESPONSE:
            return False
        uri = decision.get_navigation_action().get_request().get_uri()
        if kind == WebKit2.PolicyDecisionType.NEW_WINDOW_ACTION or urlparse(uri).netloc != HOST:
            decision.ignore()
            self.open_outside(uri)
            return True
        return False

    def on_create(self, _view, action):
        self.open_outside(action.get_request().get_uri())
        return None


def main():
    hidden = "--hidden" in sys.argv[1:]
    pid = running_pid()
    if pid:
        if not hidden:
            os.kill(pid, signal.SIGUSR1)
        return
    with open(PIDFILE, "w") as f:
        f.write(str(os.getpid()))
    panel = Panel()
    signal_add(GLib.PRIORITY_DEFAULT, signal.SIGUSR1, panel.toggle)
    signal_add(GLib.PRIORITY_DEFAULT, signal.SIGTERM, Gtk.main_quit)
    if not hidden:
        panel.show()
    try:
        Gtk.main()
    finally:
        try:
            os.unlink(PIDFILE)
        except OSError:
            pass


if __name__ == "__main__":
    main()
