import os, threading, subprocess
import shutil

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gtk, GdkPixbuf

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

        # Power Management
        self.getPowerDefaults()

        # Startup Applications
        self.getStartupApplications()

        # Default Applications
        self.getDefaultApplications()

        # Show Screen:
        self.window.show_all()
    
    # Window methods:
    def onDestroy(self, action):
        self.window.get_application().quit()

    def defineComponents(self):
        def getUI(str):
            return self.builder.get_object(str)
        
        self.nb_pages = getUI("nb_pages")
        self.lb_rows = getUI("lb_rows")

        # Wallpapers
        self.flow_wallpapers = getUI("flow_wallpapers")

        # Theme
        self.rb_darkTheme = getUI("rb_darkTheme")
        self.rb_lightTheme = getUI("rb_lightTheme")

        # Display
        self.sli_scaling = getUI("sli_scaling")
        self.sli_desktopIcon = getUI("sli_desktopIcon")
        self.sli_panel = getUI("sli_panel")

        # Keyboard
        self.stk_trf            = getUI("stk_trf")
        self.stk_trq            = getUI("stk_trq")
        self.stk_en             = getUI("stk_en")
        self.btn_trf_remove     = getUI("btn_trf_remove")
        self.btn_trq_remove     = getUI("btn_trq_remove")
        self.btn_en_remove      = getUI("btn_en_remove")
        self.sw_lang_indicator  = getUI("sw_lang_indicator")

        # Fonts
        self.font_system        = getUI("font_system")
        self.font_monospace     = getUI("font_monospace")

        # Languages
        self.lb_langs_installed         = getUI("lb_langs_installed")
        self.lb_langs_not_installed     = getUI("lb_langs_not_installed")

        # Power Management
        self.stk_power_management         = getUI("stk_power_management")
        self.cmb_laptop_screen_closed_bat = getUI("cmb_laptop_screen_closed_bat")
        self.cmb_screen_off_after_bat     = getUI("cmb_screen_off_after_bat")
        self.cmb_put_to_sleep_after_bat   = getUI("cmb_put_to_sleep_after_bat")
        self.cmb_laptop_screen_closed     = getUI("cmb_laptop_screen_closed")
        self.cmb_screen_off_after         = getUI("cmb_screen_off_after")
        self.cmb_put_to_sleep_after       = getUI("cmb_put_to_sleep_after")
        self.cmb_screen_off_after2        = getUI("cmb_screen_off_after2")
        self.cmb_put_to_sleep_after2      = getUI("cmb_put_to_sleep_after2")

        # Startup Applications
        self.lb_startup_applications        = getUI("lb_startup_applications")
        self.revealer_startup_applications  = getUI("revealer_startup_applications")
        self.dialog_applications            = getUI("dialog_applications")
        self.appchooser_startup             = getUI("appchooser_startup")

        # Default Applications
        self.cmb_default_browser        = getUI("cmb_default_browser")
        self.cmb_default_filemanager    = getUI("cmb_default_filemanager")
        self.cmb_default_email          = getUI("cmb_default_email")
        self.cmb_default_terminal       = getUI("cmb_default_terminal")

        self.lst_default_browser        = getUI("lst_default_browser")
        self.lst_default_filemanager    = getUI("lst_default_filemanager")
        self.lst_default_email          = getUI("lst_default_email")
        self.lst_default_terminal       = getUI("lst_default_terminal")


        self.dialog_restore_defaults      = getUI("dialog_restore_defaults")
    
    def addSliderMarks(self):        
        self.sli_scaling.add_mark(0, Gtk.PositionType.BOTTOM, "%100")
        self.sli_scaling.add_mark(1, Gtk.PositionType.BOTTOM, "%125")
        self.sli_scaling.add_mark(2, Gtk.PositionType.BOTTOM, "%150")
        self.sli_scaling.add_mark(3, Gtk.PositionType.BOTTOM, "%175")
        self.sli_scaling.add_mark(4, Gtk.PositionType.BOTTOM, "%200")

    def getThemeDefaults(self):
        theme = ThemeManager.getTheme()

        if theme == "pardus":
            self.rb_lightTheme.set_active(True)
        elif theme == "pardus-dark":
            self.rb_darkTheme.set_active(True)

    def getScalingDefaults(self):
        self.sli_panel.set_value(ScaleManager.getPanelSize())
        self.sli_desktopIcon.set_value(ScaleManager.getDesktopIconSize())
        
        currentScale = int((ScaleManager.getScale() / 0.25) - 4)
        self.sli_scaling.set_value(currentScale)
    
    # Keyboard Settings:
    def getKeyboardDefaults(self):
        # We can choose the layout:
        KeyboardManager.initializeSettings()

        states = KeyboardManager.getKeyboardState()

        if states[0] == True:
            self.stk_trq.set_visible_child_name("remove")
        else:
            self.stk_trq.set_visible_child_name("add")
        
        if states[1] == True:
            self.stk_trf.set_visible_child_name("remove")
        else:
            self.stk_trf.set_visible_child_name("add")
        
        if states[2] == True:
            self.stk_en.set_visible_child_name("remove")
        else:
            self.stk_en.set_visible_child_name("add")

        self.keyboardSelectionDisablingCheck()
        
        keyboardPlugin = KeyboardManager.getKeyboardPlugin()
        self.sw_lang_indicator.set_active(len(keyboardPlugin) > 0)
    
    def keyboardSelectionDisablingCheck(self):
        # print(f"trq:{self.stk_trq.get_visible_child_name()}, trf:{self.stk_trf.get_visible_child_name()}, en:{self.stk_en.get_visible_child_name()}")
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
            # Remove button
            btn = Gtk.Button.new_from_icon_name("user-trash-symbolic", Gtk.IconSize.BUTTON)
            btn.get_style_context().add_class("destructive-action")
            btn.connect("clicked", self.on_locale_remove)

            btn.set_relief(Gtk.ReliefStyle.NONE)
            btn.set_name(f"{lang} {codeset}")
            box.pack_end(btn, False, False, 0)

            # Set as Default button
            btn_default = Gtk.Button.new_from_icon_name("view-reveal-symbolic", Gtk.IconSize.BUTTON)
            btn_default.connect("clicked", self.on_locale_set_default)

            btn_default.set_relief(Gtk.ReliefStyle.NONE)
            btn_default.set_name(f"{lang} {codeset}")
            btn_default.set_tooltip_text(tr("Set as Default"))

            box.pack_end(btn_default, False, False, 0)     
        else:
            # Add button
            btn = Gtk.Button.new_from_icon_name("list-add-symbolic", Gtk.IconSize.BUTTON)
            btn.connect("clicked", self.on_locale_add)
            
            btn.set_relief(Gtk.ReliefStyle.NONE)
            btn.set_name(f"{lang} {codeset}")
            box.pack_end(btn, False, False, 0)


        lbl_name = Gtk.Label.new(lang)
        box.add(lbl_name)        

        if isInstalled:
            self.lb_langs_installed.add(box)
            self.lb_langs_installed.show_all()
        else:
            self.lb_langs_not_installed.add(box)
            self.lb_langs_not_installed.show_all()
    
    def getLocales(self):
        availableLocales = LocaleManager.getAvailableLocales()
        installedLocales = LocaleManager.getInstalledLocales()

        for lc in availableLocales:
            self.addLocaleToListBox(lc[0], lc[1], True if lc in installedLocales else False)


    def addWallpapers(self, wallpaperList):
        for i in range(len(wallpaperList)):
            # Image
            bitmap = GdkPixbuf.Pixbuf.new_from_file(wallpaperList[i])
            bitmap = bitmap.scale_simple(240, 135, GdkPixbuf.InterpType.BILINEAR)

            img_wallpaper = Gtk.Image.new_from_pixbuf(bitmap)
            img_wallpaper.img_path = wallpaperList[i]

            GLib.idle_add(self.flow_wallpapers.insert, img_wallpaper, -1)
            GLib.idle_add(self.flow_wallpapers.show_all)
    
    def changeWindowTheme(self, isHdpi, isDark):
        if isHdpi:
            if isDark:
                GLib.idle_add(ThemeManager.setWindowTheme, "pardus-dark-default-hdpi")
            else:
                GLib.idle_add(ThemeManager.setWindowTheme, "pardus-default-hdpi")
        else:
            if isDark:
                GLib.idle_add(ThemeManager.setWindowTheme, "pardus-dark-default")
            else:
                GLib.idle_add(ThemeManager.setWindowTheme, "pardus-default")
    
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
        self.cmb_default_browser.set_active_id(     ApplicationManager.getDefaultXFCEApp("WebBrowser")["name"])
        self.cmb_default_filemanager.set_active_id( ApplicationManager.getDefaultXFCEApp("FileManager")["name"])
        self.cmb_default_email.set_active_id(       ApplicationManager.getDefaultXFCEApp("MailReader")["name"])
        self.cmb_default_terminal.set_active_id(    ApplicationManager.getDefaultXFCEApp("TerminalEmulator")["name"])
        

        

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
            GLib.idle_add(ThemeManager.setTheme, "pardus")
            GLib.idle_add(ThemeManager.setIconTheme, "pardus")

            # Window Theme
            self.changeWindowTheme(ScaleManager.getScale() == 2.0, False)
    
    def on_rb_darkTheme_clicked(self, rb):
        if rb.get_active():
            GLib.idle_add(ThemeManager.setTheme, "pardus-dark")
            GLib.idle_add(ThemeManager.setIconTheme, "pardus-dark")

            # Window Theme
            self.changeWindowTheme(ScaleManager.getScale() == 2.0, True)
    
    
    # - Scale Changed:
    def on_sli_scaling_button_release(self, slider, b):
        value = int(slider.get_value()) * 0.25 + 1
        self.changeWindowTheme(value == 2.0, ThemeManager.getTheme() == "pardus-dark")
        ScaleManager.setScale(value)
    
    def on_sli_scaling_format_value(self, sli, value):
        return f"%{int(value * 25 + 100)}"
    
    def on_sli_panel_value_changed(self, sli):
        ScaleManager.setPanelSize(int(sli.get_value()))
    
    def on_sli_desktopIcon_value_changed(self, sli):
        ScaleManager.setDesktopIconSize(int(sli.get_value()))
    

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
        LocaleManager.installLocale(btn.get_name())

    def on_locale_remove(self, btn):
        LocaleManager.removeLocale(btn.get_name())
    
    def on_locale_set_default(self, btn):
        LocaleManager.setDefaultLocale(btn.get_name())
    
    # Clock
    def on_btn_clock_time_only_clicked(self, btn):
        DatetimeManager.set("layout", "3")

        DatetimeManager.saveFile()

    def on_btn_clock_date_only_clicked(self, btn):
        DatetimeManager.set("layout", "2")

        DatetimeManager.saveFile()
    

    # - Power Management
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
            subprocess.run(f"rm {application_path}", shell="True")

            self.lb_startup_applications.remove(row)
    
    def on_btn_startup_add_application_clicked(self, button):
        self.lb_startup_applications.unselect_all()
        self.dialog_applications_selected_app = None

        res = self.dialog_applications.run()
        self.dialog_applications.hide()

        if res == Gtk.ResponseType.OK and self.dialog_applications_selected_app != None:
            app_info = self.dialog_applications_selected_app
            app_name = app_info.get_name()
            app_icon = app_info.get_icon().to_string() if app_info.get_icon() != None else ""
            app_path = app_info.get_filename()
            app_id = app_info.get_id()
            app_new_path = f"{ApplicationManager.STARTUP_PATH}/{app_id}"

            try:
                if not os.path.exists(app_new_path):
                    shutil.copy(app_path, app_new_path)
                    self.addStartupApplication(app_name, app_new_path, app_icon)
            except:
                pass
    
    def on_appchooser_startup_application_selected(self, widget, appinfo):
        self.dialog_applications_selected_app = appinfo
    

    # Default Applications:
    def _get_cmb_executable(self, combobox):
        tree_iter = combobox.get_active_iter()
        if tree_iter:
            model = combobox.get_model()
            executable = model[tree_iter][1]
            return executable
        return None
    
    def on_cmb_default_browser_changed(self, combobox):
        exe = self._get_cmb_executable(combobox)
        ApplicationManager.setDefaultXFCEApp("WebBrowser", exe)

    def on_cmb_default_filemanager_changed(self, combobox):
        exe = self._get_cmb_executable(combobox)
        ApplicationManager.setDefaultXFCEApp("FileManager", exe)

    def on_cmb_default_email_changed(self, combobox):
        exe = self._get_cmb_executable(combobox)
        ApplicationManager.setDefaultXFCEApp("MailReader", exe)
            
    def on_cmb_default_terminal_changed(self, combobox):
        exe = self._get_cmb_executable(combobox)
        ApplicationManager.setDefaultXFCEApp("TerminalEmulator", exe)

    
    def _get_cmb_application(self, combobox):
        tree_iter = combobox.get_active_iter()
        if tree_iter:
            model = combobox.get_model()
            desktop_file = model[tree_iter][0].get_filename().split("/")[-1]
            return desktop_file
        return None
    
    def on_cmb_default_video_changed(self, combobox):
        desktop_file = self._get_cmb_application(combobox)

        ApplicationManager.setDefaultApp("video/mp4", desktop_file)
        ApplicationManager.setDefaultApp("video/quicktime", desktop_file)
        ApplicationManager.setDefaultApp("video/webm", desktop_file)
        ApplicationManager.setDefaultApp("video/ogg", desktop_file)
    
    def on_cmb_default_music_changed(self, combobox):
        desktop_file = self._get_cmb_application(combobox)

        ApplicationManager.setDefaultApp("audio/mp4", desktop_file)
        ApplicationManager.setDefaultApp("audio/mpeg", desktop_file)
        ApplicationManager.setDefaultApp("audio/acc", desktop_file)
        ApplicationManager.setDefaultApp("audio/flac", desktop_file)
    
    def on_cmb_default_image_changed(self, combobox):
        desktop_file = self._get_cmb_application(combobox)

        ApplicationManager.setDefaultApp("image/jpeg", desktop_file)
        ApplicationManager.setDefaultApp("image/webp", desktop_file)
        ApplicationManager.setDefaultApp("image/png", desktop_file)
        ApplicationManager.setDefaultApp("image/gif", desktop_file)
        ApplicationManager.setDefaultApp("image/bmp", desktop_file)
    
    def on_cmb_default_editor_changed(self, combobox):
        desktop_file = self._get_cmb_application(combobox)

        ApplicationManager.setDefaultApp("text/plain", desktop_file)


    

    # Restore Defaults
    def on_btn_restore_panel_clicked(self, button):
        response = self.dialog_restore_defaults.run()
        self.dialog_restore_defaults.hide()
        if response == Gtk.ResponseType.YES:
            subprocess.run("""xfce4-panel --quit; pkill xfconfd; rm -rf ~/.config/xfce4/panel ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml;
                            cp -R /etc/xdg/pardus/xfce4/panel/* ~/.config/xfce4/panel/; cp /etc/xdg/pardus/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml;
                            (xfce4-panel &);""", shell=True)
    
    def on_btn_restore_thunar_clicked(self, button):
        response = self.dialog_restore_defaults.run()
        self.dialog_restore_defaults.hide()
        if response == Gtk.ResponseType.YES:
            subprocess.run("rm -rf ~/.config/Thunar/*; cp -R /etc/xdg/pardus/Thunar/* ~/.config/Thunar/", shell=True)
    
    def on_btn_restore_allxfce_clicked(self, button):
        response = self.dialog_restore_defaults.run()
        self.dialog_restore_defaults.hide()
        if response == Gtk.ResponseType.YES:
            subprocess.run("""xfce4-panel --quit; pkill xfconfd;
                            rm -rf ~/.config/xfce4/panel/*; rm ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml;
                            cp -R /etc/xdg/pardus/xfce4/panel/* ~/.config/xfce4/panel/; cp /etc/xdg/pardus/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml;
                            rm -rf ~/.config/Thunar/*; cp -R /etc/xdg/pardus/Thunar/* ~/.config/Thunar/;
                            (xfce4-panel &);""", shell=True)
        
