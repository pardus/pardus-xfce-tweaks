#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import subprocess
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Xfconf", "0")
import locale
from locale import gettext as _

from gi.repository import Gdk, GdkPixbuf, Gio, GLib, Gtk, Xfconf, GObject

import version

# Translation Constants:
APPNAME = "pardus-xfce-tweaks"
TRANSLATIONS_PATH = "/usr/share/locale"

# Translation functions:
locale.bindtextdomain(APPNAME, TRANSLATIONS_PATH)
locale.textdomain(APPNAME)

LOCALE_CHANGER_PY = "/usr/share/pardus/pardus-xfce-tweaks/src/xfce/locale_changer.py"
CWD = os.path.dirname(os.path.abspath(__file__))


def getenv(str):
    env = os.environ.get(str)
    return env if env else ""


if (
    "xfce" in getenv("SESSION").lower()
    or "xfce" in getenv("XDG_CURRENT_DESKTOP").lower()
):
    Xfconf.init()

    import pardus_lib_xfce.ApplicationManager as ApplicationManager
    import pardus_lib_xfce.DatetimeManager as DatetimeManager
    import pardus_lib_xfce.FontManager as FontManager
    import pardus_lib_xfce.KeyboardManager as KeyboardManager
    import pardus_lib_xfce.LocaleManager as LocaleManager
    import pardus_lib_xfce.PanelManager as PanelManager
    import pardus_lib_xfce.PowerManager as PowerManager
    import pardus_lib_xfce.ScaleManager as ScaleManager
    import pardus_lib_xfce.ThemeManager as ThemeManager
    import pardus_lib_xfce.ThunarManager as ThunarManager
    import pardus_lib_xfce.WallpaperManager as WallpaperManager

else:
    print("This program requires XFCE desktop.")
    exit(0)


class Language(GObject.GObject):
    lang = GObject.Property(type=str, default="")
    encode_type = GObject.Property(type=str, default="")
    is_installed = GObject.Property(type=bool, default=False)
    is_default = GObject.Property(type=bool, default=False)

    def clone(self):
        return Language(
            lang=GObject.Property(type=str, default=self.lang),
            encode_type=GObject.Property(type=str, default=self.encode_type),
            is_installed=GObject.Property(type=bool, default=self.is_installed),
            is_default=GObject.Property(type=bool, default=self.is_default),
        )


class MainWindow:
    def __init__(self, application):
        # Gtk Builder
        self.builder = Gtk.Builder()

        # Translate things on glade:
        self.builder.set_translation_domain(APPNAME)

        # Import UI file:
        self.builder.add_from_file(CWD + "/../ui/MainWindow.glade")
        self.builder.connect_signals(self)

        # Window
        self.window = self.builder.get_object("window")
        self.window.set_position(Gtk.WindowPosition.CENTER)
        self.window.set_application(application)
        self.window.connect("destroy", self.on_destroy)
        self.define_components()

        # Set application:
        self.application = application

        self.define_variables()

        # Custom css
        self.set_css()

        # Put Wallpapers on a Grid
        self.get_wallpapers()

        # Set theme to system-default:
        self.get_theme_defaults()

        # Set scales to system-default:
        self.get_scaling_defaults()

        # Keyboard
        self.get_keyboard_defaults()

        # Fonts
        self.get_font_defaults()

        # Languages
        self.get_locales()

        # Panel
        self.get_panel_preferences()

        # Power Management
        self.get_power_defaults()

        # Startup Applications
        self.get_startup_applications()

        # Default Applications
        # self.getDefaultApplications()

        self.set_show_default_apps()

        # Set later signals:
        self.set_signals_later()

        # Show Screen:
        self.window.show_all()

    def define_variables(self):
        self.restore_type = ""

        self.list_languages = Gio.ListStore.new(Language)
        self.list_installed_languages = Gio.ListStore.new(Language)

    # Custom css
    def set_css(self):
        cssProvider = Gtk.CssProvider()
        cssProvider.load_from_path(CWD + "/../css/style.css")
        screen = Gdk.Screen.get_default()
        styleContext = Gtk.StyleContext()
        styleContext.add_provider_for_screen(
            screen, cssProvider, Gtk.STYLE_PROVIDER_PRIORITY_USER
        )

    # Window methods:
    def on_destroy(self, action):
        self.window.get_application().quit()

    def on_ui_about_button_clicked(self, button):
        self.ui_about_dialog.run()
        self.ui_about_dialog.hide()

    def define_components(self):
        def UI(str):
            return self.builder.get_object(str)

        self.ui_about_dialog = UI("ui_about_dialog")
        self.ui_about_dialog.set_program_name(_("Pardus Xfce Tweaks"))
        self.ui_about_dialog.set_version(version.VERSION)

        if self.ui_about_dialog.get_titlebar() is None:
            about_headerbar = Gtk.HeaderBar.new()
            about_headerbar.set_show_close_button(True)
            about_headerbar.set_title(_("About Pardus Xfce Tweaks"))
            about_headerbar.pack_start(
                Gtk.Image.new_from_icon_name(
                    "pardus-xfce-tweaks", Gtk.IconSize.LARGE_TOOLBAR
                )
            )
            about_headerbar.show_all()
            self.ui_about_dialog.set_titlebar(about_headerbar)

        # default apps appchoser
        self.cmb_default_video = UI("cmb_default_video")
        self.cmb_default_music = UI("cmb_default_music")
        self.cmb_default_image = UI("cmb_default_image")
        self.cmb_default_editor = UI("cmb_default_editor")

        self.nb_pages = UI("nb_pages")

        # Dialogs
        self.dialogs_window = UI("dialogs_window")
        self.dialogs_stack = UI("dialogs_stack")

        # Wallpapers
        self.flow_wallpapers = UI("flow_wallpapers")

        # Theme
        self.rb_dark_theme = UI("rb_dark_theme")
        self.rb_light_theme = UI("rb_light_theme")
        self.rb_default_icons = UI("rb_default_icons")
        self.rb_brown_icons = UI("rb_brown_icons")
        self.rb_gray_icons = UI("rb_gray_icons")

        # Display
        self.sli_cursor = UI("sli_cursor")
        self.sli_scaling = UI("sli_scaling")
        self.sli_desktopIcon = UI("sli_desktopIcon")
        self.sli_panel = UI("sli_panel")

        # Keyboard
        self.stk_trf = UI("stk_trf")
        self.stk_trq = UI("stk_trq")
        self.stk_en = UI("stk_en")
        self.btn_trf_remove = UI("btn_trf_remove")
        self.btn_trq_remove = UI("btn_trq_remove")
        self.btn_en_remove = UI("btn_en_remove")
        self.sw_lang_indicator = UI("sw_lang_indicator")

        # Fonts
        self.font_system = UI("font_system")
        self.font_monospace = UI("font_monospace")

        # Languages
        self.revealer_language = UI("revealer_language")
        self.revealer_lang_save_changes = UI("revealer_lang_save_changes")
        self.box_revealer_language = UI("box_revealer_language")

        self.window_languages = UI("window_languages")
        self.lb_languages = UI("lb_languages")
        self.btn_select_language = UI("btn_select_language")
        self.lb_langs_installed = UI("lb_langs_installed")

        # Panel Preferences
        self.cb_panel_action_lockscreen = UI("cb_panel_action_lockscreen")
        self.cb_panel_action_switchuser = UI("cb_panel_action_switchuser")
        self.cb_panel_action_suspend = UI("cb_panel_action_suspend")
        self.cb_panel_action_hibernate = UI("cb_panel_action_hibernate")
        self.cb_panel_action_shutdown = UI("cb_panel_action_shutdown")
        self.cb_panel_action_restart = UI("cb_panel_action_restart")
        self.cb_panel_action_logout = UI("cb_panel_action_logout")
        self.cb_panel_action_logoutdialog = UI("cb_panel_action_logoutdialog")
        self.cb_panel_action_hybridsleep = UI("cb_panel_action_hybridsleep")

        # Power Management
        self.stk_power_management = UI("stk_power_management")
        self.cmb_laptop_screen_closed_bat = UI("cmb_laptop_screen_closed_bat")
        self.cmb_screen_off_after_bat = UI("cmb_screen_off_after_bat")
        self.cmb_put_to_sleep_after_bat = UI("cmb_put_to_sleep_after_bat")
        self.cmb_laptop_screen_closed = UI("cmb_laptop_screen_closed")
        self.cmb_screen_off_after = UI("cmb_screen_off_after")
        self.cmb_put_to_sleep_after = UI("cmb_put_to_sleep_after")
        self.cmb_screen_off_after2 = UI("cmb_screen_off_after2")
        self.cmb_put_to_sleep_after2 = UI("cmb_put_to_sleep_after2")
        self.cmb_xscreen_off_after = UI("cmb_xscreen_off_after")

        # Startup Applications
        self.lb_startup_applications = UI("lb_startup_applications")
        self.revealer_startup_applications = UI("revealer_startup_applications")
        self.dialog_applications = UI("dialog_applications")
        self.appchooser_startup = UI("appchooser_startup")

        # Default Applications
        self.lst_default_browser = UI("lst_default_browser")
        self.lst_default_filemanager = UI("lst_default_filemanager")
        self.lst_default_email = UI("lst_default_email")
        self.lst_default_terminal = UI("lst_default_terminal")

    def set_signals_later(self):
        self.rb_light_theme.connect("toggled", self.on_rb_theme_toggled, "light")
        self.rb_dark_theme.connect("toggled", self.on_rb_theme_toggled, "dark")

        self.rb_default_icons.connect(
            "toggled", self.on_rb_icons_toggled, "pardus-xfce"
        )
        self.rb_brown_icons.connect(
            "toggled", self.on_rb_icons_toggled, "pardus-xfce-brown"
        )
        self.rb_gray_icons.connect(
            "toggled", self.on_rb_icons_toggled, "pardus-xfce-gray"
        )

    def set_show_default_apps(self):
        self.cmb_default_video.set_show_default_item(True)
        self.cmb_default_music.set_show_default_item(True)
        self.cmb_default_image.set_show_default_item(True)
        self.cmb_default_editor.set_show_default_item(True)

    def addSliderMarks(self):
        self.sli_scaling.add_mark(0, Gtk.PositionType.BOTTOM, "%100")
        self.sli_scaling.add_mark(1, Gtk.PositionType.BOTTOM, "%125")
        self.sli_scaling.add_mark(2, Gtk.PositionType.BOTTOM, "%150")
        self.sli_scaling.add_mark(3, Gtk.PositionType.BOTTOM, "%175")
        self.sli_scaling.add_mark(4, Gtk.PositionType.BOTTOM, "%200")

    def generate_locales(self, task, source_object, task_data, cancellable):
        if not self.new_locales:
            task.return_boolean(False)
            return

        process = subprocess.run(
            [
                "pkexec",
                LOCALE_CHANGER_PY,
                "setlocales",
                self.new_locales,
                self.default_locale,
            ]
        )

        task.return_boolean(process.returncode == 0)

    def on_generate_locales_finished(self, source, task):
        success = task.propagate_boolean()

        if success:
            self.revealer_lang_save_changes.set_reveal_child(False)
            self.dialogs_stack.set_visible_child_name("success")
        else:
            self.dialogs_stack.set_visible_child_name("error")

        self.dialogs_window.show_all()
        self.lb_langs_installed.show_all()

    def get_wallpapers(self):
        task = Gio.Task.new()
        task.run_in_thread(self.get_wallpapers_async)

    def get_wallpapers_async(self, task, source_object, task_data, cancellable):
        wallpaper_paths = WallpaperManager.get_wallpapers()

        for w in wallpaper_paths:
            self.append_wallpaper(w)

    def get_theme_defaults(self):
        theme = ThemeManager.get_theme()

        if theme == "pardus-xfce":
            self.rb_light_theme.set_active(True)
        elif theme == "pardus-xfce-dark":
            self.rb_dark_theme.set_active(True)

    def get_scaling_defaults(self):
        self.sli_panel.set_value(ScaleManager.get_panel_size())
        self.sli_desktopIcon.set_value(ScaleManager.get_desktop_icon_size())

        current_scale = int((ScaleManager.get_scale() / 0.25) - 4)
        self.sli_scaling.set_value(current_scale)
        self.sli_cursor.set_value((ScaleManager.get_pointer_size() / 16) - 1)

    # Keyboard Settings:
    def get_keyboard_defaults(self):
        KeyboardManager.init()

        layouts = KeyboardManager.get_layouts()

        if "tr-" in layouts:
            self.stk_trq.set_visible_child_name("remove")
        else:
            self.stk_trq.set_visible_child_name("add")

        if "tr-f" in layouts:
            self.stk_trf.set_visible_child_name("remove")
        else:
            self.stk_trf.set_visible_child_name("add")

        if "us-" in layouts:
            self.stk_en.set_visible_child_name("remove")
        else:
            self.stk_en.set_visible_child_name("add")

        self.keyboard_selection_disabling_check()

        keyboard_plugin = PanelManager.find_plugin("xkb")
        self.sw_lang_indicator.set_active(True if keyboard_plugin else False)

    def keyboard_selection_disabling_check(self):
        self.btn_trf_remove.set_sensitive(
            self.stk_trq.get_visible_child_name() == "remove"
            or self.stk_en.get_visible_child_name() == "remove"
        )
        self.btn_trq_remove.set_sensitive(
            self.stk_trf.get_visible_child_name() == "remove"
            or self.stk_en.get_visible_child_name() == "remove"
        )
        self.btn_en_remove.set_sensitive(
            self.stk_trq.get_visible_child_name() == "remove"
            or self.stk_trf.get_visible_child_name() == "remove"
        )

    def get_font_defaults(self):
        system_font = FontManager.get_system_font()
        monospace_font = FontManager.get_monospace_font()

        if system_font != "":
            self.font_system.set_font(system_font)

        if monospace_font != "":
            self.font_monospace.set_font(monospace_font)

    # Set Sorting function for listboxes
    def sort_langs(self, a, b):
        return locale.strcoll(a.lang.split(".")[0], b.lang.split(".")[0])

    def get_flag_emoji(self, country_code):
        """2 harfli ISO ülke kodunu bayrak emojisine dönüştürür."""
        if not country_code or len(country_code) != 2:
            return ""
        country_code = country_code.upper()
        # 127397, normal ASCII harfler ile Regional Indicator sembolleri arasındaki farktır
        return chr(ord(country_code[0]) + 127397) + chr(ord(country_code[1]) + 127397)

    def create_row(self, item):
        lang = item.lang
        lang_core = lang.split(".")[0]  # tr_TR.UTF-8 -> tr_TR
        lang_info = LocaleManager.get_locale_info(lang_core)

        box = Gtk.Box(orientation="vertical", spacing=7, tooltip_text=lang_core)
        box._lang = lang_info["language"]
        box._item = item

        label_box = Gtk.Box(
            orientation="vertical",
            hexpand=True,
            spacing=5,
        )

        language = lang_info["language"]
        language_native = lang_info["language_native"]

        if not language or not language_native:
            return

        # Native Name
        if lang_info["country_native"]:
            language_native = language_native + f" ({lang_info['country_native']})"

        label_box.add(
            Gtk.Label(
                label=language_native,
                halign="start",
            )
        )

        # Name
        if language:
            if lang_info["country"]:
                language = language + f" ({lang_info['country']})"

            lang_lbl = Gtk.Label(label=language, halign="start")
            lang_lbl.get_style_context().add_class("dimmed")
            lang_lbl.get_style_context().add_class("dim-label")
            lang_lbl.get_style_context().add_class("caption")
            label_box.add(lang_lbl)

        hbox = Gtk.Box(
            spacing=7,
            margin_top=7,
            margin_start=7,
            margin_end=7,
        )
        # Country Flag
        if lang_core == "tr_CY":
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(
                f"{CWD}/../assets/turkish-cyprus-flag.svg"
            )
            img_cy = Gtk.Image.new_from_pixbuf(pixbuf)
            hbox.add(img_cy)
        elif lang_info["country_ab2"]:
            hbox.add(
                Gtk.Label(
                    label=f'<span size="150%">{self.get_flag_emoji(lang_info["country_ab2"])}</span>',
                    use_markup=True,
                )
            )
        else:
            hbox.add(Gtk.Image(icon_name="image-missing-symbolic", pixel_size=24))

        hbox.add(label_box)

        # Default Logo
        if item.is_default:
            default_img = Gtk.Image.new_from_icon_name(
                "selection-mode-symbolic", Gtk.IconSize.BUTTON
            )
            default_img.get_style_context().add_class("success")
            default_img.set_tooltip_text(_("Default System Language"))
            default_img.set_margin_end(7)

            hbox.pack_end(default_img, False, False, 0)

        box.add(hbox)
        box.add(Gtk.Separator())

        return box

    def get_locales(self):
        # Get Available Locales
        available_locales = LocaleManager.get_available_locales()
        installed_locales = LocaleManager.get_installed_locales()
        self.default_locale = LocaleManager.get_default_locale()

        for lang, encode_type in available_locales:
            if encode_type == "UTF-8":
                is_installed = (
                    True if (lang, encode_type) in installed_locales else False
                )

                lang_core = lang.split(".")[0]  # tr_TR.UTF-8 -> tr_TR
                lang_info = LocaleManager.get_locale_info(lang_core)
                if not lang_info["language"] or not lang_info["language_native"]:
                    continue

                new_item = Language(
                    lang=lang,
                    encode_type=encode_type,
                    is_installed=is_installed,
                    is_default=self.default_locale == lang,
                )
                already_found, pos = self.list_languages.find_with_equal_func(
                    new_item, lambda a, b: a.lang == b.lang
                )

                if not already_found:
                    self.list_languages.insert_sorted(new_item, self.sort_langs)

        for lang, encode_type in installed_locales:
            if encode_type == "UTF-8":
                lang_core = lang.split(".")[0]  # tr_TR.UTF-8 -> tr_TR
                lang_info = LocaleManager.get_locale_info(lang_core)
                if not lang_info["language"] or not lang_info["language_native"]:
                    continue

                new_item = Language(
                    lang=lang,
                    encode_type=encode_type,
                    is_installed=True,
                    is_default=self.default_locale == lang,
                )
                already_found, pos = self.list_installed_languages.find_with_equal_func(
                    new_item, lambda a, b: a.lang == b.lang
                )

                if not already_found:
                    self.list_installed_languages.insert_sorted(
                        new_item, self.sort_langs
                    )

        # Bind model
        self.lb_languages.bind_model(self.list_languages, self.create_row)
        self.lb_langs_installed.bind_model(
            self.list_installed_languages, self.create_row
        )

    def get_panel_preferences(self):
        PanelManager.restore_default_actions()
        items = PanelManager.get_actions_items()
        self.cb_panel_action_lockscreen.set_active(items["lock-screen"])
        self.cb_panel_action_switchuser.set_active(items["switch-user"])
        self.cb_panel_action_suspend.set_active(items["suspend"])
        self.cb_panel_action_hibernate.set_active(items["hibernate"])
        self.cb_panel_action_shutdown.set_active(items["shutdown"])
        self.cb_panel_action_restart.set_active(items["restart"])
        self.cb_panel_action_logout.set_active(items["logout"])
        self.cb_panel_action_logoutdialog.set_active(items["logout-dialog"])
        self.cb_panel_action_hybridsleep.set_active(items["hybrid-sleep"])

    def append_wallpaper(self, path):
        # Image
        bitmap = GdkPixbuf.Pixbuf.new_from_file(path)
        bitmap = bitmap.scale_simple(240, 135, GdkPixbuf.InterpType.BILINEAR)

        img_wallpaper = Gtk.Image.new_from_pixbuf(bitmap)
        img_wallpaper.img_path = path

        tooltip = path.split("pardus23-0_")[-1].split("pardus25-0_")[-1]
        img_wallpaper.set_tooltip_text(tooltip)

        GLib.idle_add(self.flow_wallpapers.insert, img_wallpaper, -1)
        GLib.idle_add(self.flow_wallpapers.show_all)

    def change_window_theme(self, isHdpi, isDark):
        if isHdpi:
            if isDark:
                GLib.idle_add(
                    ThemeManager.set_window_theme, "pardus-xfce-dark-default-hdpi"
                )
            else:
                GLib.idle_add(ThemeManager.set_window_theme, "pardus-xfce-default-hdpi")
        else:
            if isDark:
                GLib.idle_add(ThemeManager.set_window_theme, "pardus-xfce-dark")
            else:
                GLib.idle_add(ThemeManager.set_window_theme, "pardus-xfce")

    def get_power_defaults(self):
        self.cmb_laptop_screen_closed_bat.set_active_id(
            str(PowerManager.get_battery_laptop_screen_closed())
        )
        self.cmb_screen_off_after_bat.set_active_id(
            str(PowerManager.get_battery_screen_off())
        )
        self.cmb_put_to_sleep_after_bat.set_active_id(
            str(PowerManager.get_battery_screen_sleep())
        )
        self.cmb_laptop_screen_closed.set_active_id(
            str(PowerManager.get_ac_laptop_screen_closed())
        )
        self.cmb_screen_off_after.set_active_id(str(PowerManager.get_ac_screen_off()))
        self.cmb_put_to_sleep_after.set_active_id(
            str(PowerManager.get_ac_screen_sleep())
        )
        self.cmb_screen_off_after2.set_active_id(str(PowerManager.get_ac_screen_off()))
        self.cmb_put_to_sleep_after2.set_active_id(
            str(PowerManager.get_ac_screen_sleep())
        )

        self.cmb_xscreen_off_after.set_active_id(str(PowerManager.get_blank_screen_timeout()))

        pageName = "laptop" if PowerManager.is_laptop() else "pc"
        self.stk_power_management.set_visible_child_name(pageName)

    def append_startup_application_to_list(self, app):
        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 7)
        box.props.margin = 7

        img_icon = Gtk.Image.new_from_icon_name(app["icon"], Gtk.IconSize.DND)
        box.add(img_icon)

        lbl_name = Gtk.Label.new(app["name"])
        box.add(lbl_name)

        box.set_name(app["application_file"])

        self.lb_startup_applications.add(box)
        self.lb_startup_applications.show_all()

    def add_application_to_autostart(self, app):
        app_path = app.get_filename()
        app_id = app.get_id()
        app_new_path = f"{ApplicationManager.STARTUP_PATH}/{app_id}"

        try:
            if not os.path.exists(app_new_path):
                shutil.copy2(app_path, app_new_path)
                return True
        except Exception as e:
            print("app copy to autostart error:", e)

        return False

    def get_startup_applications(self):
        startup_list = ApplicationManager.get_startup_applications()

        for app in startup_list:
            self.append_startup_application_to_list(app)

    def getDefaultApplications(self):
        browser_list = ApplicationManager.get_application_list_from_category(
            "webbrowser"
        )
        filemanager_list = ApplicationManager.get_application_list_from_category(
            "filemanager"
        )
        email_list = ApplicationManager.get_application_list_from_category("email")
        terminal_list = ApplicationManager.get_application_list_from_category(
            "terminalemulator"
        )

        # name, executable, icon
        for a in browser_list:
            self.lst_default_browser.append([a["name"], a["executable"], a["icon"]])

        for a in filemanager_list:
            self.lst_default_filemanager.append([a["name"], a["executable"], a["icon"]])

        for a in email_list:
            self.lst_default_email.append([a["name"], a["executable"], a["icon"]])

        for a in terminal_list:
            self.lst_default_terminal.append([a["name"], a["executable"], a["icon"]])

        # set default app
        # self.cmb_default_browser.set_active_id(     ApplicationManager.getDefaultXFCEApp("WebBrowser")["name"])
        # self.cmb_default_filemanager.set_active_id( ApplicationManager.getDefaultXFCEApp("FileManager")["name"])
        # self.cmb_default_email.set_active_id(       ApplicationManager.getDefaultXFCEApp("MailReader")["name"])
        # self.cmb_default_terminal.set_active_id(    ApplicationManager.getDefaultXFCEApp("TerminalEmulator")["name"])

    def refresh_panel(self):
        subprocess.call(["xfce4-panel", "-r"])

    # SIGNALS
    def on_window_hide(self, window, e):
        window.hide()
        return True

    def on_lb_rows_row_activated(self, rows, a):
        page = rows.get_selected_row().get_index()
        self.nb_pages.set_current_page(page)

    # - Wallpaper Select:
    def on_wallpaper_selected(self, flowbox, wallpaper):
        filename = str(wallpaper.get_children()[0].img_path)
        WallpaperManager.set_wallpaper(filename)

    # - Theme Selection:
    def on_rb_theme_toggled(self, btn, theme):
        if not btn.get_active():
            return

        # Icon theme
        current_icon_theme = ThemeManager.get_icon_theme()

        if theme == "light":
            GLib.idle_add(ThemeManager.set_theme, "pardus-xfce")
            GLib.idle_add(
                PanelManager.set_startup_icon,
                "/usr/share/icons/pardus-xfce/statusbar/start-pardus-25.svg",
            )

            if "-dark" in current_icon_theme:
                new_icon_theme = current_icon_theme[:-5]  # remove -dark suffix
                GLib.idle_add(ThemeManager.set_icon_theme, new_icon_theme)

            # Window Theme
            self.change_window_theme(ScaleManager.get_scale() == 2.0, False)
        elif theme == "dark":
            GLib.idle_add(ThemeManager.set_theme, "pardus-xfce-dark")
            GLib.idle_add(
                PanelManager.set_startup_icon,
                "/usr/share/icons/pardus-xfce-dark/statusbar/start-pardus-25.svg",
            )

            if "-dark" not in current_icon_theme:
                new_icon_theme = current_icon_theme + "-dark"  # remove -dark suffix
                GLib.idle_add(ThemeManager.set_icon_theme, new_icon_theme)

            # Window Theme
            self.change_window_theme(ScaleManager.get_scale() == 2.0, True)

        # self.refresh_panel()

    def on_rb_icons_toggled(self, btn, icon_theme):
        if btn.get_active():
            current_theme = ThemeManager.get_icon_theme()

            if "-dark" in current_theme:
                icon_theme += "-dark"

            GLib.idle_add(ThemeManager.set_icon_theme, icon_theme)

    # - Scale Changed:
    def on_sli_scaling_button_release(self, slider, b):
        value = int(slider.get_value()) * 0.25 + 1
        self.change_window_theme(
            value == 2.0, ThemeManager.get_theme() == "pardus-xfce-dark"
        )
        ScaleManager.set_scale(value)

    def on_sli_scaling_format_value(self, sli, value):
        return f"%{int(value * 25 + 100)}"

    def on_sli_panel_value_changed(self, sli):
        ScaleManager.set_panel_size(int(sli.get_value()))

    def on_sli_desktopIcon_value_changed(self, sli):
        ScaleManager.set_desktop_icon_size(int(sli.get_value()))

    def on_sli_cursor_format_value(self, sli, value):
        return f"{int(value + 1) * 16}"

    def on_sli_cursor_value_changed(self, sli):
        ScaleManager.set_pointer_size(int(sli.get_value() + 1) * 16)

    # - Keyboard Layout Changed:
    def on_btn_trf_add_clicked(self, button):
        KeyboardManager.add_layout("tr-f")

        self.stk_trf.set_visible_child_name("remove")
        self.keyboard_selection_disabling_check()

    def on_btn_trf_remove_clicked(self, button):
        KeyboardManager.remove_layout("tr-f")

        self.stk_trf.set_visible_child_name("add")
        self.keyboard_selection_disabling_check()

    def on_btn_trq_add_clicked(self, button):
        KeyboardManager.add_layout("tr-")

        self.stk_trq.set_visible_child_name("remove")
        self.keyboard_selection_disabling_check()

    def on_btn_trq_remove_clicked(self, button):
        KeyboardManager.remove_layout("tr-")

        self.stk_trq.set_visible_child_name("add")
        self.keyboard_selection_disabling_check()

    def on_btn_en_add_clicked(self, button):
        KeyboardManager.add_layout("us-")

        self.stk_en.set_visible_child_name("remove")
        self.keyboard_selection_disabling_check()

    def on_btn_en_remove_clicked(self, button):
        KeyboardManager.remove_layout("us-")

        self.stk_en.set_visible_child_name("add")
        self.keyboard_selection_disabling_check()

    def on_sw_lang_indicator_state_set(self, switch, state):
        if state:
            KeyboardManager.create_keyboard_plugin()
        else:
            KeyboardManager.remove_keyboard_plugin()

    # Fonts
    def on_font_system_font_set(self, fontbutton):
        FontManager.set_system_font(fontbutton.get_font())

    def on_font_monospace_font_set(self, fontbutton):
        FontManager.set_monospace_font(fontbutton.get_font())

    # Language
    def on_btn_lang_delete_clicked(self, btn):
        if len(self.lb_langs_installed.get_children()) <= 1:
            return

        row = self.lb_langs_installed.get_selected_row()
        if not row:
            return

        self.list_installed_languages.remove(row.get_index())

        self.revealer_language.set_reveal_child(False)
        self.revealer_lang_save_changes.set_reveal_child(True)

    def on_btn_lang_set_default_clicked(self, btn):
        row = self.lb_langs_installed.get_selected_row()
        if not row:
            return

        # Remove old default flag
        item_len = self.list_installed_languages.get_n_items()
        for i in range(item_len):
            it = self.list_installed_languages.get_item(i)
            it.is_default = False

        item = self.list_installed_languages.get_item(row.get_index())
        item.is_default = True

        self.list_installed_languages.sort(self.sort_langs)

        self.default_locale = f"{item.lang} {item.encode_type}"

        self.revealer_language.set_reveal_child(False)
        self.revealer_lang_save_changes.set_reveal_child(True)

        self.lb_langs_installed.show_all()

    def print_installed_langs(self):
        print("installed_languages:")
        item_len = self.list_installed_languages.get_n_items()
        for i in range(item_len):
            it = self.list_installed_languages.get_item(i)
            print(f"{it.lang} {it.encode_type}, is_default:{it.is_default}")

    def on_btn_languages_save_changes_clicked(self, btn):
        installed_languages = []

        item_len = self.list_installed_languages.get_n_items()
        for i in range(item_len):
            it = self.list_installed_languages.get_item(i)
            installed_languages.append(f"{it.lang} {it.encode_type}")

        self.new_locales = "|".join(installed_languages)

        self.dialogs_window.show_all()
        self.dialogs_stack.set_visible_child_name("generating")
        self.revealer_language.set_reveal_child(False)

        task = Gio.Task.new(callback=self.on_generate_locales_finished)
        task.run_in_thread(self.generate_locales)

    def on_btn_show_languages_clicked(self, btn):
        self.window_languages.show_all()

    def on_lb_languages_row_selected(self, listbox, row):
        if row:
            self.btn_select_language.set_sensitive(True)

    def on_lb_languages_row_activated(self, listbox, row):
        if row:
            self.on_btn_select_language_clicked(None)

    def on_lb_langs_installed_row_selected(self, listbox, row):
        if row:
            item = self.list_installed_languages.get_item(row.get_index())

            self.box_revealer_language.set_sensitive(not item.is_default)

            self.revealer_language.set_reveal_child(True)

    def on_btn_select_language_clicked(self, btn):
        self.window_languages.hide()

        row = self.lb_languages.get_selected_row()

        item = self.list_languages.get_item(row.get_index())
        item.is_installed = True

        already_found, pos = self.list_installed_languages.find_with_equal_func(
            item, lambda a, b: a.lang == b.lang
        )

        if not already_found:
            self.list_installed_languages.insert_sorted(item, self.sort_langs)

            self.revealer_lang_save_changes.set_reveal_child(True)

        self.lb_langs_installed.show_all()

    def on_btn_close_languages_window_clicked(self, btn):
        self.window_languages.hide()

    # Clock
    def on_btn_clock_time_only_clicked(self, btn):
        DatetimeManager.set("layout", "3")
        DatetimeManager.set("time_font", "Quicksand Medium, Bold 16")
        DatetimeManager.set("time_format", "%H:%M")

        DatetimeManager.set_panel_clock("digital-layout", "3")
        DatetimeManager.set_panel_clock(
            "digital-time-font", "Quicksand Medium, Bold 16"
        )
        DatetimeManager.set_panel_clock("digital-time-format", "%H:%M")

        DatetimeManager.save_file()

    def on_btn_clock_date_time_clicked(self, btn):
        DatetimeManager.set("layout", "1")
        DatetimeManager.set("date_font", "Quicksand Medium, Bold 8")
        DatetimeManager.set("time_font", "Quicksand Medium, Bold 9")
        DatetimeManager.set("date_format", "%d.%m.%Y")
        DatetimeManager.set("time_format", "%H:%M")

        DatetimeManager.set_panel_clock("digital-layout", "1")
        DatetimeManager.set_panel_clock(
            "digital-time-font", "Quicksand Medium, Bold 15"
        )
        DatetimeManager.set_panel_clock("digital-time-format", "%H:%M")
        DatetimeManager.set_panel_clock(
            "digital-date-font", "Quicksand Medium, Bold 10"
        )
        DatetimeManager.set_panel_clock("digital-date-format", "%d.%m.%Y")

        DatetimeManager.save_file()

    # Panel Preferences
    def on_panel_action_icon_clicked(self, btn):
        PanelManager.set_actions_item(btn.get_name(), "+" if btn.get_active() else "-")

    def on_btn_panel_actions_reset_clicked(self, btn):
        PanelManager.restore_default_actions()
        self.get_panel_preferences()

    # Power Management
    def on_cmb_laptop_screen_closed_bat_changed(self, combobox):
        tree_iter = combobox.get_active_iter()
        if tree_iter:
            model = combobox.get_model()
            value = int(
                model[tree_iter][0]
            )  # 0:Switch Off Display, 1:Suspend, 2:Hibernate, 3:Lock Screen

            PowerManager.set_battery_laptop_screen_closed(value)

    def on_cmb_screen_off_after_bat_changed(self, combobox):
        tree_iter = combobox.get_active_iter()
        if tree_iter:
            model = combobox.get_model()
            value = int(model[tree_iter][0])

            PowerManager.set_battery_screen_off(value)

    def on_cmb_put_to_sleep_after_bat_changed(self, combobox):
        tree_iter = combobox.get_active_iter()
        if tree_iter:
            model = combobox.get_model()
            value = int(model[tree_iter][0])

            PowerManager.set_battery_screen_sleep(value)

    def on_cmb_laptop_screen_closed_changed(self, combobox):
        tree_iter = combobox.get_active_iter()
        if tree_iter:
            model = combobox.get_model()
            value = int(
                model[tree_iter][0]
            )  # 0:Switch Off Display, 1:Suspend, 2:Hibernate, 3:Lock Screen

            PowerManager.set_ac_laptop_screen_closed(value)

    def on_cmb_screen_off_after_changed(self, combobox):
        tree_iter = combobox.get_active_iter()
        if tree_iter:
            model = combobox.get_model()
            value = int(model[tree_iter][0])

            PowerManager.set_ac_screen_off(value)

    def on_cmb_put_to_sleep_after_changed(self, combobox):
        tree_iter = combobox.get_active_iter()
        if tree_iter:
            model = combobox.get_model()
            value = int(model[tree_iter][0])

            PowerManager.set_ac_screen_sleep(value)

    def on_cmb_xscreen_off_after_changed(self, combobox):
        tree_iter = combobox.get_active_iter()
        if tree_iter:
            model = combobox.get_model()
            value = int(model[tree_iter][0])

            PowerManager.set_blank_screen_timeout(value)

    # Startup Applications
    def on_lb_startup_applications_selected_rows_changed(self, listbox):
        rows = listbox.get_selected_rows()
        if len(rows) > 0:
            self.revealer_startup_applications.set_reveal_child(True)
        else:
            self.revealer_startup_applications.set_reveal_child(False)

    def on_btn_startup_clear_clicked(self, button):
        self.lb_startup_applications.unselect_all()

    def on_btn_startup_delete_clicked(self, button):
        rows = self.lb_startup_applications.get_selected_rows()
        for row in rows:
            # name of the widget is the application path
            application_path = row.get_children()[0].get_name()

            if os.path.exists(application_path):
                os.remove(application_path)

            self.lb_startup_applications.remove(row)

    # Add Startup Applications
    def on_btn_startup_add_application_clicked(self, button):
        self.lb_startup_applications.unselect_all()
        self.dialog_applications_selected_app = None

        res = self.dialog_applications.run()

        if res == Gtk.ResponseType.OK and self.dialog_applications_selected_app:
            app = self.dialog_applications_selected_app

            if self.add_application_to_autostart(app):
                app_id = app.get_id()
                app_new_path = f"{ApplicationManager.STARTUP_PATH}/{app_id}"
                app_info = ApplicationManager.get_application_info(app_new_path)

                self.append_startup_application_to_list(app_info)

        self.dialog_applications.hide()

    def on_appchooser_startup_application_selected(self, widget, app):
        self.dialog_applications_selected_app = app

    def on_appchooser_startup_application_activated(self, widget, app):
        if self.add_application_to_autostart(app):
            app_id = app.get_id()
            app_new_path = f"{ApplicationManager.STARTUP_PATH}/{app_id}"
            app_info = ApplicationManager.get_application_info(app_new_path)
            self.append_startup_application_to_list(app_info)

        self.lb_startup_applications.unselect_all()
        self.dialog_applications.hide()

    # Default Applications:
    def _get_cmb_executable(self, combobox):
        tree_iter = combobox.get_active_iter()
        if tree_iter:
            model = combobox.get_model()
            executable = model[tree_iter][1]
            return executable
        return None

    def on_cmb_default_browser_changed(self, combobox):
        app = combobox.get_app_info()
        executable = app.get_executable().split("/")[-1]

        ApplicationManager.set_default_xfce_app("WebBrowser", executable)

    # def on_cmb_default_filemanager_changed(self, combobox):
    #     exe = self._get_cmb_executable(combobox)
    #     ApplicationManager.setDefaultXFCEApp("FileManager", exe)
    #
    # def on_cmb_default_email_changed(self, combobox):
    #     exe = self._get_cmb_executable(combobox)
    #     ApplicationManager.setDefaultXFCEApp("MailReader", exe)
    #
    # def on_cmb_default_terminal_changed(self, combobox):
    #     exe = self._get_cmb_executable(combobox)
    #     ApplicationManager.setDefaultXFCEApp("TerminalEmulator", exe)

    def _get_cmb_application(self, combobox):
        tree_iter = combobox.get_active_iter()
        if tree_iter:
            model = combobox.get_model()
            desktop_file = model[tree_iter][0].get_filename().split("/")[-1]
            return desktop_file
        return None

    def on_cmb_default_video_changed(self, combobox):
        if combobox.get_active_iter() is None:
            return

        desktop_file = self._get_cmb_application(combobox)

        ApplicationManager.set_default_app("video/mp4", desktop_file)
        ApplicationManager.set_default_app("video/quicktime", desktop_file)
        ApplicationManager.set_default_app("video/webm", desktop_file)
        ApplicationManager.set_default_app("video/ogg", desktop_file)
        ApplicationManager.set_default_app("video/msvideo", desktop_file)
        ApplicationManager.set_default_app("video/x-msvideo", desktop_file)
        ApplicationManager.set_default_app("video/flv", desktop_file)

    def on_cmb_default_music_changed(self, combobox):
        if combobox.get_active_iter() is None:
            return

        desktop_file = self._get_cmb_application(combobox)

        ApplicationManager.set_default_app("audio/mp4", desktop_file)
        ApplicationManager.set_default_app("audio/mpeg", desktop_file)
        ApplicationManager.set_default_app("audio/acc", desktop_file)
        ApplicationManager.set_default_app("audio/flac", desktop_file)
        ApplicationManager.set_default_app("audio/ogg", desktop_file)
        ApplicationManager.set_default_app("audio/x-mp3", desktop_file)
        ApplicationManager.set_default_app("audio/x-mpeg", desktop_file)
        ApplicationManager.set_default_app("audio/x-m4a", desktop_file)

    def on_cmb_default_image_changed(self, combobox):
        if combobox.get_active_iter() is None:
            return

        desktop_file = self._get_cmb_application(combobox)

        ApplicationManager.set_default_app("image/bmp", desktop_file)
        ApplicationManager.set_default_app("image/gif", desktop_file)
        ApplicationManager.set_default_app("image/jpeg", desktop_file)
        ApplicationManager.set_default_app("image/jpg", desktop_file)
        ApplicationManager.set_default_app("image/pjpeg", desktop_file)
        ApplicationManager.set_default_app("image/png", desktop_file)
        ApplicationManager.set_default_app("image/svg+xml", desktop_file)
        ApplicationManager.set_default_app("image/svg+xml-compressed", desktop_file)
        ApplicationManager.set_default_app("image/x-bmp", desktop_file)
        ApplicationManager.set_default_app("image/x-gray", desktop_file)
        ApplicationManager.set_default_app("image/x-icb", desktop_file)
        ApplicationManager.set_default_app("image/x-ico", desktop_file)
        ApplicationManager.set_default_app("image/x-pcx", desktop_file)
        ApplicationManager.set_default_app("image/x-png", desktop_file)
        ApplicationManager.set_default_app("image/x-portable-anymap", desktop_file)
        ApplicationManager.set_default_app("image/x-portable-bitmap", desktop_file)
        ApplicationManager.set_default_app("image/x-portable-graymap", desktop_file)
        ApplicationManager.set_default_app("image/x-portable-pixmap", desktop_file)
        ApplicationManager.set_default_app("image/x-xbitmap", desktop_file)
        ApplicationManager.set_default_app("image/x-xpixmap", desktop_file)
        ApplicationManager.set_default_app("image/vnd.wap.wbmp", desktop_file)
        ApplicationManager.set_default_app("image/webp", desktop_file)

    def on_cmb_default_editor_changed(self, combobox):
        if combobox.get_active_iter() is None:
            return

        desktop_file = self._get_cmb_application(combobox)

        ApplicationManager.set_default_app("text/plain", desktop_file)
        ApplicationManager.set_default_app("text/css", desktop_file)
        ApplicationManager.set_default_app("text/javascript", desktop_file)
        ApplicationManager.set_default_app("text/mathml", desktop_file)
        ApplicationManager.set_default_app("text/x-c++hdr", desktop_file)
        ApplicationManager.set_default_app("text/x-c++src", desktop_file)
        ApplicationManager.set_default_app("text/x-csrc", desktop_file)
        ApplicationManager.set_default_app("text/x-chdr", desktop_file)
        ApplicationManager.set_default_app("text/x-dtd", desktop_file)
        ApplicationManager.set_default_app("text/x-java", desktop_file)
        ApplicationManager.set_default_app("text/x-javascript", desktop_file)
        ApplicationManager.set_default_app("text/x-makefile", desktop_file)
        ApplicationManager.set_default_app("text/x-moc", desktop_file)
        ApplicationManager.set_default_app("text/x-pascal", desktop_file)
        ApplicationManager.set_default_app("text/x-patch", desktop_file)
        ApplicationManager.set_default_app("text/x-perl", desktop_file)
        ApplicationManager.set_default_app("text/x-php", desktop_file)
        ApplicationManager.set_default_app("text/x-python", desktop_file)
        ApplicationManager.set_default_app("text/x-python3", desktop_file)
        ApplicationManager.set_default_app("text/x-sql", desktop_file)
        ApplicationManager.set_default_app("text/x-tcl", desktop_file)
        ApplicationManager.set_default_app("text/x-tex", desktop_file)
        ApplicationManager.set_default_app("text/xml", desktop_file)
        ApplicationManager.set_default_app("application/javascript", desktop_file)
        ApplicationManager.set_default_app("application/x-cgi", desktop_file)
        ApplicationManager.set_default_app("application/x-javascript", desktop_file)
        ApplicationManager.set_default_app("application/x-perl", desktop_file)
        ApplicationManager.set_default_app("application/x-php", desktop_file)
        ApplicationManager.set_default_app("application/x-python", desktop_file)
        ApplicationManager.set_default_app("application/x-shellscript", desktop_file)
        ApplicationManager.set_default_app("application/xml", desktop_file)
        ApplicationManager.set_default_app("application/xml-dtd", desktop_file)

    def on_ui_otherdefaultapps_button_clicked(self, button):
        subprocess.Popen(["xfce4-mime-settings"])

    # Restore Defaults
    def on_restore(self, restore_type):
        self.restore_type = restore_type
        self.dialogs_window.show_all()
        self.dialogs_stack.set_visible_child_name("restore")

    def on_btn_restore_panel_clicked(self, button):
        self.on_restore("panel")

    def on_btn_restore_thunar_clicked(self, button):
        self.on_restore("thunar")

    def on_btn_restore_allxfce_clicked(self, button):
        self.on_restore("all-xfce")

    def on_dialog_restore_defaults_clicked(self, button):
        if not self.restore_type:
            return

        if self.restore_type == "panel":
            PanelManager.restore_default_settings()
        elif self.restore_type == "thunar":
            ThunarManager.restore_default_settings()
        elif self.restore_type == "all-xfce":
            subprocess.Popen(CWD + "/xfce/resetall.sh")

    def on_dialog_close_clicked(self, button):
        self.dialogs_window.hide()
