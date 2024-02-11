#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, threading, subprocess
import shutil

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Xfconf', '0')
from gi.repository import GLib, Gtk, GdkPixbuf, Xfconf

import locale
from locale import gettext as tr

# Translation Constants:
APPNAME = "pardus-xfce-tweaks"
TRANSLATIONS_PATH = "/usr/share/locale"
SYSTEM_LANGUAGE = os.environ.get("LANG")

# Translation functions:
locale.bindtextdomain(APPNAME, TRANSLATIONS_PATH)
locale.textdomain(APPNAME)
locale.setlocale(locale.LC_ALL, SYSTEM_LANGUAGE)


def getenv(str):
    env = os.environ.get(str)
    return env if env else ""
    
if "xfce" in getenv("SESSION").lower() or "xfce" in getenv("XDG_CURRENT_DESKTOP").lower():
    import xfce.WallpaperManager as WallpaperManager
    import xfce.ThemeManager as ThemeManager
    import xfce.ScaleManager as ScaleManager
    import xfce.KeyboardManager as KeyboardManager
    import xfce.PowerManager as PowerManager
    import xfce.ApplicationManager as ApplicationManager
    import xfce.FontManager as FontManager
    import xfce.DatetimeManager as DatetimeManager
    import xfce.LocaleManager as LocaleManager
    import xfce.PanelManager as PanelManager
    import xfce.ThunarManager as ThunarManager
else:
    print("This program requires XFCE desktop.")
    exit(0)

class MainWindow:
    def __init__(self, application):
        # Gtk Builder
        self.builder = Gtk.Builder()

        # Translate things on glade:
        self.builder.set_translation_domain(APPNAME)

        # Import UI file:
        self.builder.add_from_file(os.path.dirname(os.path.abspath(__file__)) + "/../ui/MainWindow.glade")
        self.builder.connect_signals(self)

        # Window
        self.window = self.builder.get_object("window")
        self.window.set_position(Gtk.WindowPosition.CENTER)
        self.window.set_application(application)
        self.window.connect("destroy", self.onDestroy)
        self.defineComponents()
        
        # Set application:
        self.application = application

        # Put Wallpapers on a Grid
        thread = threading.Thread(target=self.addWallpapers, args=(WallpaperManager.getWallpaperList(),))
        thread.daemon = True
        thread.start()

        # Set theme to system-default:
        self.getThemeDefaults()

        # Set scales to system-default:
        self.getScalingDefaults()

        # Keyboard
        self.getKeyboardDefaults()

        # Fonts
        self.getFontDefaults()

        # Languages
        self.getLocales()

        # Panel
        self.getPanelPreferences()

        # Power Management
        self.getPowerDefaults()

        # Startup Applications
        self.getStartupApplications()

        # Default Applications
        # self.getDefaultApplications()

        self.set_show_default_apps()

        # Show Screen:
        self.window.show_all()
    
    # Window methods:
    def onDestroy(self, action):
        self.window.get_application().quit()

    def on_ui_about_button_clicked(self, button):
        self.ui_about_dialog.run()
        self.ui_about_dialog.hide()

    def defineComponents(self):
        def UI(str):
            return self.builder.get_object(str)

        self.ui_about_dialog   = UI("ui_about_dialog")
        self.ui_about_dialog.set_program_name(tr("Pardus Xfce Tweaks"))
        if self.ui_about_dialog.get_titlebar() is None:
            about_headerbar = Gtk.HeaderBar.new()
            about_headerbar.set_show_close_button(True)
            about_headerbar.set_title(tr("About Pardus Xfce Tweaks"))
            about_headerbar.pack_start(Gtk.Image.new_from_icon_name("pardus-xfce-tweaks", Gtk.IconSize.LARGE_TOOLBAR))
            about_headerbar.show_all()
            self.ui_about_dialog.set_titlebar(about_headerbar)
        # Set version
        # If not getted from __version__ file then accept version in MainWindow.glade file
        try:
            version = open(os.path.dirname(os.path.abspath(__file__)) + "/__version__").readline()
            self.ui_about_dialog.set_version(version)
        except:
            pass

        # default apps appchoser
        self.cmb_default_video = UI("cmb_default_video")
        self.cmb_default_music = UI("cmb_default_music")
        self.cmb_default_image = UI("cmb_default_image")
        self.cmb_default_editor = UI("cmb_default_editor")

        self.nb_pages   = UI("nb_pages")
        self.lb_rows    = UI("lb_rows")

        # Wallpapers
        self.flow_wallpapers = UI("flow_wallpapers")

        # Theme
        self.rb_darkTheme   = UI("rb_darkTheme")
        self.rb_lightTheme  = UI("rb_lightTheme")

        # Display
        self.sli_cursor         = UI("sli_cursor")
        self.sli_scaling        = UI("sli_scaling")
        self.sli_desktopIcon    = UI("sli_desktopIcon")
        self.sli_panel          = UI("sli_panel")

        # Keyboard
        self.stk_trf            = UI("stk_trf")
        self.stk_trq            = UI("stk_trq")
        self.stk_en             = UI("stk_en")
        self.btn_trf_remove     = UI("btn_trf_remove")
        self.btn_trq_remove     = UI("btn_trq_remove")
        self.btn_en_remove      = UI("btn_en_remove")
        self.sw_lang_indicator  = UI("sw_lang_indicator")

        # Fonts
        self.font_system        = UI("font_system")
        self.font_monospace     = UI("font_monospace")

        # Languages
        self.dialog_languages_generate          = UI("dialog_languages_generate")
        self.dialog_languages_generate_failed   = UI("dialog_languages_generate_failed")
        self.dialog_languages_generate_success   = UI("dialog_languages_generate_success")
        self.revealer_languages                 = UI("revealer_languages")
        self.box_languages                      = UI("box_languages")
        self.btn_languages_lock                 = UI("btn_languages_lock")
        self.lb_langs_installed                 = UI("lb_langs_installed")
        self.lb_langs_not_installed             = UI("lb_langs_not_installed")

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
        self.stk_power_management         = UI("stk_power_management")
        self.cmb_laptop_screen_closed_bat = UI("cmb_laptop_screen_closed_bat")
        self.cmb_screen_off_after_bat     = UI("cmb_screen_off_after_bat")
        self.cmb_put_to_sleep_after_bat   = UI("cmb_put_to_sleep_after_bat")
        self.cmb_laptop_screen_closed     = UI("cmb_laptop_screen_closed")
        self.cmb_screen_off_after         = UI("cmb_screen_off_after")
        self.cmb_put_to_sleep_after       = UI("cmb_put_to_sleep_after")
        self.cmb_screen_off_after2        = UI("cmb_screen_off_after2")
        self.cmb_put_to_sleep_after2      = UI("cmb_put_to_sleep_after2")

        # Startup Applications
        self.lb_startup_applications        = UI("lb_startup_applications")
        self.revealer_startup_applications  = UI("revealer_startup_applications")
        self.dialog_applications            = UI("dialog_applications")
        self.appchooser_startup             = UI("appchooser_startup")

        # Default Applications
        # self.cmb_default_browser        = UI("cmb_default_browser")
        # self.cmb_default_filemanager    = UI("cmb_default_filemanager")
        # self.cmb_default_email          = UI("cmb_default_email")
        # self.cmb_default_terminal       = UI("cmb_default_terminal")

        self.lst_default_browser        = UI("lst_default_browser")
        self.lst_default_filemanager    = UI("lst_default_filemanager")
        self.lst_default_email          = UI("lst_default_email")
        self.lst_default_terminal       = UI("lst_default_terminal")


        self.dialog_restore_defaults      = UI("dialog_restore_defaults")

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

    def getThemeDefaults(self):
        theme = ThemeManager.getTheme()

        if theme == "pardus-xfce":
            self.rb_lightTheme.set_active(True)
        elif theme == "pardus-xfce-dark":
            self.rb_darkTheme.set_active(True)

    def getScalingDefaults(self):
        self.sli_panel.set_value(ScaleManager.getPanelSize())
        self.sli_desktopIcon.set_value(ScaleManager.getDesktopIconSize())
        
        currentScale = int((ScaleManager.getScale() / 0.25) - 4)
        self.sli_scaling.set_value(currentScale)
        self.sli_cursor.set_value((ScaleManager.getPointerSize()/16)-1)
    
    # Keyboard Settings:
    def getKeyboardDefaults(self):
        # We can choose the layout:
        KeyboardManager.initializeSettings()

        states = KeyboardManager.getKeyboardState()

        if states["tr-"] == True:
            self.stk_trq.set_visible_child_name("remove")
        else:
            self.stk_trq.set_visible_child_name("add")
        
        if states["tr-f"] == True:
            self.stk_trf.set_visible_child_name("remove")
        else:
            self.stk_trf.set_visible_child_name("add")
        
        if states["us-"] == True:
            self.stk_en.set_visible_child_name("remove")
        else:
            self.stk_en.set_visible_child_name("add")

        self.keyboardSelectionDisablingCheck()
        
        keyboardPlugin = KeyboardManager.getKeyboardPlugin()
        self.sw_lang_indicator.set_active(len(keyboardPlugin) > 0)
    
    def keyboardSelectionDisablingCheck(self):
        self.btn_trf_remove.set_sensitive(self.stk_trq.get_visible_child_name() == "remove" or self.stk_en.get_visible_child_name() == "remove")
        self.btn_trq_remove.set_sensitive(self.stk_trf.get_visible_child_name() == "remove" or self.stk_en.get_visible_child_name() == "remove")
        self.btn_en_remove.set_sensitive(self.stk_trq.get_visible_child_name() == "remove" or self.stk_trf.get_visible_child_name() == "remove")
    

    def getFontDefaults(self):
        system_font = FontManager.getSystemFont()
        monospace_font = FontManager.getMonospaceFont()

        if system_font != "":
            self.font_system.set_font(system_font)
        
        if monospace_font != "":
            self.font_monospace.set_font(monospace_font)
    
    def addLocaleToListBox(self, lang, codeset, isInstalled):
        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        box.set_margin_start(7)
        box.set_margin_end(1)

        if isInstalled:
            # Default Indicator
            default_img = Gtk.Image.new_from_icon_name("emblem-default-symbolic", Gtk.IconSize.BUTTON)
            default_img.set_tooltip_text(tr("Default System Language"))
            default_img.set_no_show_all(True)
            default_img.set_visible(lang == self.default_locale)
            default_img.set_margin_end(9)
            box.pack_end(default_img, False, False, 0)

            # # Remove button
            # btn = Gtk.Button.new_from_icon_name("user-trash-symbolic", Gtk.IconSize.BUTTON)
            # # btn.get_style_context().add_class("destructive-action")
            # btn.set_no_show_all(True)
            # btn.set_visible(lang != self.default_locale)
            # btn.connect("clicked", self.on_locale_remove)
            #
            # # btn.set_relief(Gtk.ReliefStyle.NONE)
            # btn.set_name(f"{lang} {codeset}")
            # box.pack_end(btn, False, False, 5)

            # Set as Default button
            btn_default = Gtk.Button.new_from_icon_name("emblem-ok-symbolic", Gtk.IconSize.BUTTON)
            btn_default.connect("clicked", self.on_locale_set_default)

            # btn_default.set_relief(Gtk.ReliefStyle.NONE)
            btn_default.set_name(f"{lang} {codeset}")
            btn_default.set_tooltip_text(tr("Set as Default"))
            btn_default.set_no_show_all(True)
            btn_default.set_visible(lang != self.default_locale)

            box.pack_end(btn_default, False, False, 0)
        else:
            # Add button
            btn = Gtk.Button.new_from_icon_name("list-add-symbolic", Gtk.IconSize.BUTTON)
            btn.connect("clicked", self.on_locale_add)
            
            btn.set_relief(Gtk.ReliefStyle.NONE)
            btn.set_name(f"{lang} {codeset}")
            box.pack_end(btn, False, False, 0)


        lbl_name = Gtk.Label.new(lang)
        lbl_name.set_margin_top(8)
        lbl_name.set_margin_bottom(8)
        box.add(lbl_name)

        if isInstalled:
            self.lb_langs_installed.add(box)
            self.lb_langs_installed.show_all()
        else:
            self.lb_langs_not_installed.add(box)
            self.lb_langs_not_installed.show_all()
    
    def getLocales(self):
        # Set Sorting function for listboxes
        def sortfunc(row1, row2):
            row1_label = row1.get_children()[0].get_children()[0].get_text()
            row2_label = row2.get_children()[0].get_children()[0].get_text()
            
            return locale.strcoll(row1_label, row2_label)
        
        self.lb_langs_installed.set_sort_func(sortfunc)
        self.lb_langs_not_installed.set_sort_func(sortfunc)

        # Get Available Locales
        availableLocales = LocaleManager.getAvailableLocales()
        installedLocales = LocaleManager.getInstalledLocales()
        self.default_locale = LocaleManager.getDefaultLocale()

        for lc in availableLocales:
            GLib.idle_add(self.addLocaleToListBox, lc[0], lc[1], True if lc in installedLocales else False)
    
    def getPanelPreferences(self):
        PanelManager.restoreActionsDefault()
        items = PanelManager.getActionsItems()
        self.cb_panel_action_lockscreen.set_active(items["lock-screen"])
        self.cb_panel_action_switchuser.set_active(items["switch-user"])
        self.cb_panel_action_suspend.set_active(items["suspend"])
        self.cb_panel_action_hibernate.set_active(items["hibernate"])
        self.cb_panel_action_shutdown.set_active(items["shutdown"])
        self.cb_panel_action_restart.set_active(items["restart"])
        self.cb_panel_action_logout.set_active(items["logout"])
        self.cb_panel_action_logoutdialog.set_active(items["logout-dialog"])
        self.cb_panel_action_hybridsleep.set_active(items["hybrid-sleep"])
        

    def addWallpapers(self, wallpaperList):
        for i in range(len(wallpaperList)):
            # Image
            bitmap = GdkPixbuf.Pixbuf.new_from_file(wallpaperList[i])
            bitmap = bitmap.scale_simple(240, 135, GdkPixbuf.InterpType.BILINEAR)

            img_wallpaper = Gtk.Image.new_from_pixbuf(bitmap)
            img_wallpaper.img_path = wallpaperList[i]

            tooltip = wallpaperList[i]
            try:
                tooltip = os.path.basename(tooltip)
                tooltip = os.path.splitext(tooltip)[0]
                if "pardus23-0_" in tooltip:
                    tooltip = tooltip.split("pardus23-0_")[1]
                    tooltip = tooltip.replace("-", " ")
                elif "pardus23-" in tooltip and "_" in tooltip:
                    tooltip = tooltip.split("_")[1]
                    tooltip = tooltip.replace("-", " ")
            except Exception as e:
                print("{}".format(e))
                pass
            img_wallpaper.set_tooltip_text(tooltip)

            GLib.idle_add(self.flow_wallpapers.insert, img_wallpaper, -1)
            GLib.idle_add(self.flow_wallpapers.show_all)
    
    def changeWindowTheme(self, isHdpi, isDark):
        if isHdpi:
            if isDark:
                GLib.idle_add(ThemeManager.setWindowTheme, "pardus-xfce-dark-default-hdpi")
            else:
                GLib.idle_add(ThemeManager.setWindowTheme, "pardus-xfce-default-hdpi")
        else:
            if isDark:
                GLib.idle_add(ThemeManager.setWindowTheme, "pardus-xfce-dark")
            else:
                GLib.idle_add(ThemeManager.setWindowTheme, "pardus-xfce")
    
    def getPowerDefaults(self):
        self.cmb_laptop_screen_closed_bat.set_active_id(str(PowerManager.getBatteryLaptopScreenClosed()))
        self.cmb_screen_off_after_bat.set_active_id(str(PowerManager.getBatteryScreenOff()))
        self.cmb_put_to_sleep_after_bat.set_active_id(str(PowerManager.getBatteryScreenSleep()))
        self.cmb_laptop_screen_closed.set_active_id(str(PowerManager.getACLaptopScreenClosed()))
        self.cmb_screen_off_after.set_active_id(str(PowerManager.getACScreenOff()))
        self.cmb_put_to_sleep_after.set_active_id(str(PowerManager.getACScreenSleep()))
        self.cmb_screen_off_after2.set_active_id(str(PowerManager.getACScreenOff()))
        self.cmb_put_to_sleep_after2.set_active_id(str(PowerManager.getACScreenSleep()))

        pageName = "laptop" if PowerManager.isLaptop() else "pc"
        self.stk_power_management.set_visible_child_name(pageName)
    

    def addStartupApplication(self, name, application_file, icon):
        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 7)
        box.props.margin = 7
        
        img_icon = Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.DND)
        box.add(img_icon)

        lbl_name = Gtk.Label.new(name)
        box.add(lbl_name)

        box.set_name(application_file)

        self.lb_startup_applications.add(box)
        self.lb_startup_applications.show_all()

    def getStartupApplications(self):
        startup_list = ApplicationManager.getStartupTupleList()
        
        for (exec, name, application_file, icon, categories) in startup_list:
            self.addStartupApplication(name, application_file, icon)
    
    def getDefaultApplications(self):
        browser_list = ApplicationManager.getApplicationListFromCategory("webbrowser")
        filemanager_list = ApplicationManager.getApplicationListFromCategory("filemanager")
        email_list = ApplicationManager.getApplicationListFromCategory("email")
        terminal_list = ApplicationManager.getApplicationListFromCategory("terminalemulator")

        # name, executable, icon
        for a in browser_list:
            self.lst_default_browser.append( [a["name"], a["executable"], a["icon"]] )
        
        for a in filemanager_list:
            self.lst_default_filemanager.append( [a["name"], a["executable"], a["icon"]] )

        for a in email_list:
            self.lst_default_email.append( [a["name"], a["executable"], a["icon"]] )

        for a in terminal_list:
            self.lst_default_terminal.append( [a["name"], a["executable"], a["icon"]] )
        
        
        # set default app
        # self.cmb_default_browser.set_active_id(     ApplicationManager.getDefaultXFCEApp("WebBrowser")["name"])
        # self.cmb_default_filemanager.set_active_id( ApplicationManager.getDefaultXFCEApp("FileManager")["name"])
        # self.cmb_default_email.set_active_id(       ApplicationManager.getDefaultXFCEApp("MailReader")["name"])
        # self.cmb_default_terminal.set_active_id(    ApplicationManager.getDefaultXFCEApp("TerminalEmulator")["name"])
        

        

    # SIGNALS
    def on_lb_rows_row_activated(self, rows, a):
        page = rows.get_selected_row().get_index()
        self.nb_pages.set_current_page(page)

    # - Wallpaper Select:
    def on_wallpaper_selected(self, flowbox, wallpaper):
        filename = str(wallpaper.get_children()[0].img_path)
        WallpaperManager.setWallpaper(filename)


    # - Theme Selection:
    def on_rb_lightTheme_clicked(self, rb):
        if rb.get_active():
            GLib.idle_add(ThemeManager.setTheme, "pardus-xfce")
            GLib.idle_add(ThemeManager.setIconTheme, "pardus-xfce")

            # Window Theme
            self.changeWindowTheme(ScaleManager.getScale() == 2.0, False)
    
    def on_rb_darkTheme_clicked(self, rb):
        if rb.get_active():
            GLib.idle_add(ThemeManager.setTheme, "pardus-xfce-dark")
            GLib.idle_add(ThemeManager.setIconTheme, "pardus-xfce-dark")

            # Window Theme
            self.changeWindowTheme(ScaleManager.getScale() == 2.0, True)
    
    
    # - Scale Changed:
    def on_sli_scaling_button_release(self, slider, b):
        value = int(slider.get_value()) * 0.25 + 1
        self.changeWindowTheme(value == 2.0, ThemeManager.getTheme() == "pardus-xfce-dark")
        ScaleManager.setScale(value)
    
    def on_sli_scaling_format_value(self, sli, value):
        return f"%{int(value * 25 + 100)}"
    
    def on_sli_panel_value_changed(self, sli):
        ScaleManager.setPanelSize(int(sli.get_value()))
    
    def on_sli_desktopIcon_value_changed(self, sli):
        ScaleManager.setDesktopIconSize(int(sli.get_value()))
    
    def on_sli_cursor_format_value(self, sli, value):
        return f"{int(value+1)*16}"
    
    def on_sli_cursor_value_changed(self, sli):
        ScaleManager.setPointerSize(int(sli.get_value()+1)*16)
    

    # - Keyboard Layout Changed:
    def on_btn_trf_add_clicked(self, button):
        KeyboardManager.setTurkishF(True)
        self.stk_trf.set_visible_child_name("remove")
        self.keyboardSelectionDisablingCheck()

    def on_btn_trf_remove_clicked(self, button):
        KeyboardManager.setTurkishF(False)
        self.stk_trf.set_visible_child_name("add")
        self.keyboardSelectionDisablingCheck()
    
    def on_btn_trq_add_clicked(self, button):
        KeyboardManager.setTurkishQ(True)
        self.stk_trq.set_visible_child_name("remove")
        self.keyboardSelectionDisablingCheck()

    def on_btn_trq_remove_clicked(self, button):
        KeyboardManager.setTurkishQ(False)
        self.stk_trq.set_visible_child_name("add")
        self.keyboardSelectionDisablingCheck()
    
    def on_btn_en_add_clicked(self, button):
        KeyboardManager.setEnglish(True)
        self.stk_en.set_visible_child_name("remove")
        self.keyboardSelectionDisablingCheck()

    def on_btn_en_remove_clicked(self, button):
        KeyboardManager.setEnglish(False)
        self.stk_en.set_visible_child_name("add")
        self.keyboardSelectionDisablingCheck()

    def on_sw_lang_indicator_state_set(self, switch, state):
        if state:
            KeyboardManager.createKeyboardPlugin()
        else:
            KeyboardManager.removeKeyboardPlugin()
    
    # Fonts
    def on_font_system_font_set(self, fontbutton):
        FontManager.setSystemFont(fontbutton.get_font())

    def on_font_monospace_font_set(self, fontbutton):
        FontManager.setMonospaceFont(fontbutton.get_font())
    
    # Language
    def on_locale_add(self, btn):
        lang, codeset = btn.get_name().split(" ")
        self.addLocaleToListBox(lang, codeset, True)
        
        parent_row = btn.get_parent().get_parent()
        parent_row.destroy()

        self.lb_langs_installed.invalidate_sort()
        self.lb_langs_not_installed.invalidate_sort()

        self.revealer_languages.set_reveal_child(True)

    def on_locale_remove(self, btn):
        if len(self.lb_langs_installed.get_children()) <= 1:
            return
        
        lang, codeset = btn.get_name().split(" ")
        self.addLocaleToListBox(lang, codeset, False)
        
        parent_row = btn.get_parent().get_parent()
        parent_row.destroy()

        self.lb_langs_installed.invalidate_sort()
        self.lb_langs_not_installed.invalidate_sort()

        self.revealer_languages.set_reveal_child(True)
    
    def on_locale_set_default(self, btn):
        self.default_locale = btn.get_name().split(" ")[0]

        # Show default icon
        default_btn = btn.get_parent().get_children()[1]
        default_btn.set_visible(False)

        # trash_btn = btn.get_parent().get_children()[2]
        # trash_btn.set_visible(False)

        default_img = btn.get_parent().get_children()[2]
        default_img.set_visible(True)

        self.revealer_languages.set_reveal_child(True)

        # Hide old default icon
        for rows in self.lb_langs_installed.get_children():
            box = rows.get_children()[0]

            label = box.get_children()[0]
            default_btn = box.get_children()[1]
            # trash_btn = box.get_children()[2]
            default_img = box.get_children()[2]

            if label.get_text() != self.default_locale:
                default_img.set_visible(False)
                default_btn.set_visible(True)
                # trash_btn.set_visible(True)
    
    def on_language_changes_saved(self, pid, status):
        self.dialog_languages_generate.hide()
        
        if status == 0:          
            self.revealer_languages.set_reveal_child(False)
            self.dialog_languages_generate_success.run()
            self.dialog_languages_generate_success.hide()
        else:
            self.dialog_languages_generate_failed.run()
            self.dialog_languages_generate_failed.hide()        
    
    def on_btn_languages_save_changes_clicked(self, btn):
        installed_languages = []

        self.lb_langs_installed.foreach(lambda x: installed_languages.append(x.get_children()[0].get_children()[-2].get_name()))

        LocaleManager.saveLocaleSettings("\|".join(installed_languages), self.default_locale, self.on_language_changes_saved)
        self.dialog_languages_generate.show_all()
    
    # Clock
    def on_btn_clock_time_only_clicked(self, btn):
        DatetimeManager.set("layout", "3")
        DatetimeManager.set("time_font", "Quicksand Medium, Bold 16")
        DatetimeManager.set("time_format", "%H:%M")

        DatetimeManager.set_panel_clock("digital-layout", "3")
        DatetimeManager.set_panel_clock("digital-time-font", "Quicksand\ Medium,\ Bold\ 16")
        DatetimeManager.set_panel_clock("digital-time-format", "%H:%M")


        DatetimeManager.saveFile()

    def on_btn_clock_date_time_clicked(self, btn):
        DatetimeManager.set("layout", "1")
        DatetimeManager.set("date_font", "Quicksand Medium, Bold 8")
        DatetimeManager.set("time_font", "Quicksand Medium, Bold 9")
        DatetimeManager.set("date_format", "%d.%m.%Y")
        DatetimeManager.set("time_format", "%H:%M")

        DatetimeManager.set_panel_clock("digital-layout", "1")
        DatetimeManager.set_panel_clock("digital-time-font", "Quicksand\ Medium,\ Bold\ 15")
        DatetimeManager.set_panel_clock("digital-time-format", "%H:%M")
        DatetimeManager.set_panel_clock("digital-date-font", "Quicksand\ Medium,\ Bold\ 10")
        DatetimeManager.set_panel_clock("digital-date-format", "%d.%m.%Y")

        DatetimeManager.saveFile()
    

    # Panel Preferences
    def on_panel_action_icon_clicked(self, btn):
        PanelManager.setActionsItem(btn.get_name(), "+" if btn.get_active() else "-")
    
    def on_btn_panel_actions_reset_clicked(self, btn):
        PanelManager.restoreActionsDefault()
        self.getPanelPreferences()

    # Power Management
    def on_cmb_laptop_screen_closed_bat_changed(self, combobox):
        tree_iter = combobox.get_active_iter()
        if tree_iter:
            model = combobox.get_model()
            value = int(model[tree_iter][0])  # 0:Switch Off Display, 1:Suspend, 2:Hibernate, 3:Lock Screen
            
            PowerManager.setBatteryLaptopScreenClosed(value)
    
    def on_cmb_screen_off_after_bat_changed(self, combobox):
        tree_iter = combobox.get_active_iter()
        if tree_iter:
            model = combobox.get_model()
            value = int(model[tree_iter][0])

            PowerManager.setBatteryScreenOff(value)
    
    def on_cmb_put_to_sleep_after_bat_changed(self, combobox):
        tree_iter = combobox.get_active_iter()
        if tree_iter:
            model = combobox.get_model()
            value = int(model[tree_iter][0])

            PowerManager.setBatteryScreenSleep(value)
    
    def on_cmb_laptop_screen_closed_changed(self, combobox):
        tree_iter = combobox.get_active_iter()
        if tree_iter:
            model = combobox.get_model()
            value = int(model[tree_iter][0])  # 0:Switch Off Display, 1:Suspend, 2:Hibernate, 3:Lock Screen

            PowerManager.setACLaptopScreenClosed(value)
    
    def on_cmb_screen_off_after_changed(self, combobox):
        tree_iter = combobox.get_active_iter()
        if tree_iter:
            model = combobox.get_model()
            value = int(model[tree_iter][0])

            PowerManager.setACScreenOff(value)
    
    def on_cmb_put_to_sleep_after_changed(self, combobox):
        tree_iter = combobox.get_active_iter()
        if tree_iter:
            model = combobox.get_model()
            value = int(model[tree_iter][0])

            PowerManager.setACScreenSleep(value)
    

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
            application_path = row.get_children()[0].get_name()
            if os.path.exists(application_path):
                os.remove(application_path)

            self.lb_startup_applications.remove(row)
    
    def on_btn_startup_add_application_clicked(self, button):
        self.lb_startup_applications.unselect_all()
        self.dialog_applications_selected_app = None

        res = self.dialog_applications.run()
        self.dialog_applications.hide()

        if res == Gtk.ResponseType.OK and self.dialog_applications_selected_app != None:
            app_info = self.dialog_applications_selected_app
            app_name = app_info.get_name()
            app_icon = app_info.get_icon().to_string() if app_info.get_icon() != None else "image-missing"
            app_path = app_info.get_filename()
            app_id = app_info.get_id()
            app_new_path = f"{ApplicationManager.STARTUP_PATH}/{app_id}"

            try:
                if not os.path.exists(app_new_path):
                    shutil.copy2(app_path, app_new_path)
                    self.addStartupApplication(app_name, app_new_path, app_icon)
            except:
                pass
    
    def on_appchooser_startup_application_selected(self, widget, appinfo):
        self.dialog_applications_selected_app = appinfo

    def on_appchooser_startup_application_activated(self, widget, appinfo):
        app_info = appinfo
        app_name = app_info.get_name()
        app_icon = app_info.get_icon().to_string() if app_info.get_icon() != None else "image-missing"
        app_path = app_info.get_filename()
        app_id = app_info.get_id()
        app_new_path = f"{ApplicationManager.STARTUP_PATH}/{app_id}"
        try:
            if not os.path.exists(app_new_path):
                shutil.copy2(app_path, app_new_path)
                self.addStartupApplication(app_name, app_new_path, app_icon)
        except:
            pass
        self.lb_startup_applications.unselect_all()
        self.dialog_applications_selected_app = None
        self.dialog_applications.hide()

    # Default Applications:
    def _get_cmb_executable(self, combobox):
        tree_iter = combobox.get_active_iter()
        if tree_iter:
            model = combobox.get_model()
            executable = model[tree_iter][1]
            return executable
        return None
    
    # def on_cmb_default_browser_changed(self, combobox):
    #     exe = self._get_cmb_executable(combobox)
    #     ApplicationManager.setDefaultXFCEApp("WebBrowser", exe)
    #
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

        ApplicationManager.setDefaultApp("video/mp4", desktop_file)
        ApplicationManager.setDefaultApp("video/quicktime", desktop_file)
        ApplicationManager.setDefaultApp("video/webm", desktop_file)
        ApplicationManager.setDefaultApp("video/ogg", desktop_file)
        ApplicationManager.setDefaultApp("video/msvideo", desktop_file)
        ApplicationManager.setDefaultApp("video/x-msvideo", desktop_file)
        ApplicationManager.setDefaultApp("video/flv", desktop_file)
    
    def on_cmb_default_music_changed(self, combobox):
        if combobox.get_active_iter() is None:
            return

        desktop_file = self._get_cmb_application(combobox)

        ApplicationManager.setDefaultApp("audio/mp4", desktop_file)
        ApplicationManager.setDefaultApp("audio/mpeg", desktop_file)
        ApplicationManager.setDefaultApp("audio/acc", desktop_file)
        ApplicationManager.setDefaultApp("audio/flac", desktop_file)
        ApplicationManager.setDefaultApp("audio/ogg", desktop_file)
        ApplicationManager.setDefaultApp("audio/x-mp3", desktop_file)
        ApplicationManager.setDefaultApp("audio/x-mpeg", desktop_file)
        ApplicationManager.setDefaultApp("audio/x-m4a", desktop_file)

    
    def on_cmb_default_image_changed(self, combobox):
        if combobox.get_active_iter() is None:
            return

        desktop_file = self._get_cmb_application(combobox)

        ApplicationManager.setDefaultApp("image/bmp", desktop_file)
        ApplicationManager.setDefaultApp("image/gif", desktop_file)
        ApplicationManager.setDefaultApp("image/jpeg", desktop_file)
        ApplicationManager.setDefaultApp("image/jpg", desktop_file)
        ApplicationManager.setDefaultApp("image/pjpeg", desktop_file)
        ApplicationManager.setDefaultApp("image/png", desktop_file)
        ApplicationManager.setDefaultApp("image/svg+xml", desktop_file)
        ApplicationManager.setDefaultApp("image/svg+xml-compressed", desktop_file)
        ApplicationManager.setDefaultApp("image/x-bmp", desktop_file)
        ApplicationManager.setDefaultApp("image/x-gray", desktop_file)
        ApplicationManager.setDefaultApp("image/x-icb", desktop_file)
        ApplicationManager.setDefaultApp("image/x-ico", desktop_file)
        ApplicationManager.setDefaultApp("image/x-pcx", desktop_file)
        ApplicationManager.setDefaultApp("image/x-png", desktop_file)
        ApplicationManager.setDefaultApp("image/x-portable-anymap", desktop_file)
        ApplicationManager.setDefaultApp("image/x-portable-bitmap", desktop_file)
        ApplicationManager.setDefaultApp("image/x-portable-graymap", desktop_file)
        ApplicationManager.setDefaultApp("image/x-portable-pixmap", desktop_file)
        ApplicationManager.setDefaultApp("image/x-xbitmap", desktop_file)
        ApplicationManager.setDefaultApp("image/x-xpixmap", desktop_file)
        ApplicationManager.setDefaultApp("image/vnd.wap.wbmp", desktop_file)
        ApplicationManager.setDefaultApp("image/webp", desktop_file)

    
    def on_cmb_default_editor_changed(self, combobox):
        if combobox.get_active_iter() is None:
            return

        desktop_file = self._get_cmb_application(combobox)

        ApplicationManager.setDefaultApp("text/plain", desktop_file)
        ApplicationManager.setDefaultApp("text/css", desktop_file)
        ApplicationManager.setDefaultApp("text/javascript", desktop_file)
        ApplicationManager.setDefaultApp("text/mathml", desktop_file)
        ApplicationManager.setDefaultApp("text/x-c++hdr", desktop_file)
        ApplicationManager.setDefaultApp("text/x-c++src", desktop_file)
        ApplicationManager.setDefaultApp("text/x-csrc", desktop_file)
        ApplicationManager.setDefaultApp("text/x-chdr", desktop_file)
        ApplicationManager.setDefaultApp("text/x-dtd", desktop_file)
        ApplicationManager.setDefaultApp("text/x-java", desktop_file)
        ApplicationManager.setDefaultApp("text/x-javascript", desktop_file)
        ApplicationManager.setDefaultApp("text/x-makefile", desktop_file)
        ApplicationManager.setDefaultApp("text/x-moc", desktop_file)
        ApplicationManager.setDefaultApp("text/x-pascal", desktop_file)
        ApplicationManager.setDefaultApp("text/x-patch", desktop_file)
        ApplicationManager.setDefaultApp("text/x-perl", desktop_file)
        ApplicationManager.setDefaultApp("text/x-php", desktop_file)
        ApplicationManager.setDefaultApp("text/x-python", desktop_file)
        ApplicationManager.setDefaultApp("text/x-python3", desktop_file)
        ApplicationManager.setDefaultApp("text/x-sql", desktop_file)
        ApplicationManager.setDefaultApp("text/x-tcl", desktop_file)
        ApplicationManager.setDefaultApp("text/x-tex", desktop_file)
        ApplicationManager.setDefaultApp("text/xml", desktop_file)
        ApplicationManager.setDefaultApp("application/javascript", desktop_file)
        ApplicationManager.setDefaultApp("application/x-cgi", desktop_file)
        ApplicationManager.setDefaultApp("application/x-javascript", desktop_file)
        ApplicationManager.setDefaultApp("application/x-perl", desktop_file)
        ApplicationManager.setDefaultApp("application/x-php", desktop_file)
        ApplicationManager.setDefaultApp("application/x-python", desktop_file)
        ApplicationManager.setDefaultApp("application/x-shellscript", desktop_file)
        ApplicationManager.setDefaultApp("application/xml", desktop_file)
        ApplicationManager.setDefaultApp("application/xml-dtd", desktop_file)

    def on_ui_otherdefaultapps_button_clicked(self, button):
        subprocess.Popen(["xfce4-mime-settings"])

    # Restore Defaults
    def on_btn_restore_panel_clicked(self, button):
        response = self.dialog_restore_defaults.run()
        self.dialog_restore_defaults.hide()
        if response == Gtk.ResponseType.YES:
            PanelManager.restoreDefaultSettings()
    
    def on_btn_restore_thunar_clicked(self, button):
        response = self.dialog_restore_defaults.run()
        self.dialog_restore_defaults.hide()
        if response == Gtk.ResponseType.YES:
            ThunarManager.restoreDefaultSettings()
    
    def on_btn_restore_allxfce_clicked(self, button):
        response = self.dialog_restore_defaults.run()
        self.dialog_restore_defaults.hide()
        if response == Gtk.ResponseType.YES:
            subprocess.Popen(os.path.dirname(os.path.abspath(__file__)) + "/xfce/resetall.sh")
