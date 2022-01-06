import os, threading, subprocess

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gio, Gtk, GdkPixbuf

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

        # Power Management
        self.getPowerDefaults()

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

        # Keyboard:
        self.stk_trf            = getUI("stk_trf")
        self.stk_trq            = getUI("stk_trq")
        self.stk_en             = getUI("stk_en")
        self.btn_trf_remove     = getUI("btn_trf_remove")
        self.btn_trq_remove     = getUI("btn_trq_remove")
        self.btn_en_remove      = getUI("btn_en_remove")
        self.sw_lang_indicator  = getUI("sw_lang_indicator")

        # Power Management
        self.cmb_laptop_screen_closed_bat = getUI("cmb_laptop_screen_closed_bat")
        self.cmb_screen_off_after_bat     = getUI("cmb_screen_off_after_bat")
        self.cmb_put_to_sleep_after_bat   = getUI("cmb_put_to_sleep_after_bat")
        self.cmb_laptop_screen_closed     = getUI("cmb_laptop_screen_closed")
        self.cmb_screen_off_after         = getUI("cmb_screen_off_after")
        self.cmb_put_to_sleep_after       = getUI("cmb_put_to_sleep_after")
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
        
