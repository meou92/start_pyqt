# TODO: 在todo頁面加上整日的行程
# 如下:
# 名稱 時間(若為全天(資料無時間)則不用)
# 按下可改時間

from PyQt6 import QtWidgets,QtCore, QtGui, sip
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from mutagen.mp3 import MP3
import sys, psutil, json, os, random,webbrowser
from typing import overload, Literal
from datetime import datetime,timedelta
from PIL import Image, ImageFilter, ImageQt

path = os.getcwd() + "\\init_file\\"
__stderr__ = open(f"{path}start_log.txt", "a")
sys.stderr = __stderr__
page_type = Literal["todo", "dic", "learn", "class", "set","addiction"]
align = Qt.AlignmentFlag
types = Qt.WindowType
MessageBox = QtWidgets.QMessageBox


class Timers:
    __slots__ = ["timer_1000", "timer_500", "func_1000", "func_500"]

    def __init__(self):
        self.timer_1000 = QtCore.QTimer()
        self.timer_1000.timeout.connect(lambda: self.connect_1000())
        self.timer_1000.start(1000)
        self.timer_500 = QtCore.QTimer()
        self.timer_500.timeout.connect(lambda: self.connect_500())
        self.timer_500.start(500)
        self.func_500 = []
        self.func_1000 = []

    def add_func_500(self, func):
        self.func_500.append(func)

    def add_func_1000(self, func):
        self.func_1000.append(func)

    def del_func_500(self, func):
        if func in self.func_500:
            del self.func_500[self.func_500.index(func)]

    def del_func_1000(self, func):
        if func in self.func_1000:
            del self.func_1000[self.func_1000.index(func)]


    def connect_500(self):
        list(map(lambda x: x(), self.func_500))

    def connect_1000(self):
        list(map(lambda x: x(), self.func_1000))

    def stop_500(self):
        self.timer_500.stop()

    def stop_1000(self):
        self.timer_1000.stop()


class Valuable:
    __slots__ = ["value", "widget", "type"]

    def __init__(self, value: str | int = 0):
        self.value = value
        self.widget:list[QtWidgets.QLabel | QtWidgets.QPushButton] = []
        self.type = value.__class__

    def set(self, value, change=True):
        try:
            self.value = self.type(value)
        except:
            self.value = self.type(0)
        if change and len(self.widget) > 0:
            list(map(lambda x:x.setText(self.value), self.widget))

    def get(self):
        return self.value

    def add(self, widget: QtWidgets.QLabel | QtWidgets.QPushButton):
        if widget not in self.widget:
            self.widget.append(widget)

    def delete(self, widget: QtWidgets.QLabel | QtWidgets.QPushButton):
        del self.widget[self.widget.index(widget)]


def destroy():
    h = Data.load()
    h["set"]["PlayMode"] = Music.mode
    h["set"]["dark"] = V_state.get()
    h["set"]["ClockVolume"] = Page.ClockVolume
    h["set"]["ClockRate"] = Page.ClockRate
    h["set"]["MusicVolume"] = Page.MusicVolume
    h["set"]["MusicRate"] = Page.MusicRate
    Data.write(h)
    Timer.stop_1000()
    Timer.stop_500()
    m = list(Page.page.keys())[0:]
    for i in m:
        Page.destroy(i)
    main_window.destroy(True, True)
    sip.delete(main_window)
    sys.exit()


def clock():
    def time_dict(x):
        if ans[x]["date"] == "Next":
            return V_time.get() == ans[x]["time"] and ans[x]["type"]<2
        else:
            return f"{ans[x]['date']} {ans[x]['time']}" == ds and ans[x]["type"]<2

    ans = Data.get("Todo")
    di = datetime.now()
    ds = di.strftime("%Y-%m-%d %H:%M:%S")
    V_date.set(di.strftime("%a  %b  %d    %Y"))
    V_time.set(di.strftime("%H:%M:%S"))
    if time_dict := list(filter(time_dict, ans)):
        todo = time_dict[0]
        ti = ans[todo]["prompt"].split("\n")
        if Music.media.isPlaying():
            if Music.playlist:
                Music.stop_list()
            else:
                Music.stop()
        Music.play(Data.get("set")["ClockMusic"])
        MessageBox.information(main_window, "today's homework!!!", f"--{todo}--\n" + "\n".join(ti[:3] if len(ti) > 4 else ti))
    elif V_play.get() == -1 and not Music.media.isPlaying():
        V_play.set(0)


class Label(QtWidgets.QLabel):
    @overload
    def __init__(self, master, geometry: str | list, *, text: str, style: str): ...

    @overload
    def __init__(self, master, geometry: list, *, image: QPixmap, style: str): ...
    def __init__(self, master, geometry="adjust", **arg):
        super().__init__(master)
        if "text" in arg:
            self.setText(arg["text"])
        elif "image" in arg:
            self.setPixmap(arg["image"])
        if "style" in arg:
            self.setStyleSheet(arg["style"])
        if geometry == "adjust":
            self.adjustSize()
        else:
            self.setGeometry(*geometry)


class Button(QtWidgets.QPushButton):
    @overload
    def __init__(self, master, geometry=[], command=None, *, text="", style=""): ...
    @overload
    def __init__(
        self, master, geometry=[], command=None, *, image: QIcon = None, style=""
    ): ...
    def __init__(self, master, geometry=[], command=None, **arg):
        """
        ::geometry: x, y, w, h
        """
        super().__init__(master)
        if "text" in arg:
            self.setText(arg["text"])
        if "image" in arg:
            self.setIconSize(QtCore.QSize(*geometry[2:]))
            self.setIcon(arg["image"])
        if "style" in arg:
            self.setStyleSheet(arg["style"])
        else:
            self.setStyleSheet(button_style)
        self.command=command
        self.setGeometry(*geometry)
    def mousePressEvent(self,a0:QtGui.QMouseEvent):
        if self.command != None:
            self.command()
        a0.accept()
        if not sip.isdeleted(self):
            clicked_label.add(self.parentWidget(),a0.pos()+self.pos())


class Combobox(QtWidgets.QComboBox):
    def __init__(self, master, style="", values=[], geometry=[], font=["Arial", 17, False, 15]):
        super().__init__(master)
        self.setStyleSheet(style)
        self.setGeometry(*geometry)
        _font = self.font()
        _font.setFamily(font[0])
        _font.setPointSize(font[1])
        _font.setBold(font[2])
        self.setFont(_font)
        self.ItemView = QtWidgets.QListWidget()
        self.ItemView.setStyleSheet(f"background:rgba(255, 255, 255, 0.24);color:#fc8289;font-family:{font[0]};font-size:{font[3]}pt;")
        self.setView(self.ItemView)
        self.setModel(self.ItemView.model())
        self.addItems(values)


class Combo(QtWidgets.QComboBox):
    def __init__(self,master,font_family,font_size: int,item_font_size: int,bold=False,bg="transparent",geometry=[],):
        super().__init__(master)
        self.setStyleSheet(f"QComboBox {{background-color:{bg};color:#fc8289;}}QComboBox:activate {{background-color:{bg};color:#fc8289;}}")
        font = self.font()
        font.setFamily(font_family)
        font.setPointSize(font_size)
        font.setBold(bold)
        self.setFont(font)
        self.ItemView = QtWidgets.QListWidget()
        self.ItemView.setStyleSheet(f"background-color:{color};color:#fc8289;font-family:{font_family};font-size:{item_font_size}pt;")
        self.setView(self.ItemView)
        self.setModel(self.ItemView.model())
        self.addItems(list(Data.get("music").keys()))
        if len(geometry) == 4:
            self.setGeometry(*geometry)
        if Music.playlist in list(Data.get("music").keys()):
            self.setCurrentText(Music.playlist)


class Entry(QtWidgets.QLineEdit):
    def __init__(self, parent: QtWidgets.QWidget | None, style="", geometry=[0, 0, 0, 0], text=""):
        super().__init__(text, parent)
        self.setStyleSheet(style)
        self.setGeometry(*geometry)


def progressbar(parent: QtWidgets.QWidget | None, min=0,max=1,stylesheet="",y=0):
    pb = QtWidgets.QProgressBar(parent)
    pb.setRange(min,max)
    pb.setStyleSheet(stylesheet)
    pb.setGeometry(0,y,180,3)
    pb.show()
    return pb


class Choose(QtWidgets.QCheckBox):
    el = ["每日循環", "一次", "已解決", "停用"]
    def __init__(self, mas, text: str, else_list: dict):
        super().__init__(mas, text=text)
        self.setStyleSheet(f"QCheckBox {{background:#dd7aff;color:{color};font-family:Arial;font-size:20pt;border-radius:10px;}}QCheckBox:disabled {{background:{'#d48649'if else_list['type'] == 0 else'#088fb7'};color:{color2};border-radius:10px;}}")
        self.num_list = list(map(str, range(0, 60)))
        self.left_time = Valuable("")
        self.Else = else_list
        self.No_Change = True
        self.win_count = False
        self.tag = "tag1"
        t = else_list["type"]
        if t == 0:
            self.setChecked(True)
            self.tag = "tag2"
            dn = datetime.now()
            t = else_list["time"].split(":")
            self.Time = [dn.year,dn.month,dn.day,int(t[0]),int(t[1]),int(t[2]),]
            self.setDisabled(True)
        else:
            self.Time = list(map(int, else_list["date"].split("-"))) + list(map(int, else_list["time"].split(":")))
            if t != 1:
                self.setChecked(True)
                if t == 3:
                    self.setDisabled(True)
        self.clicked.connect(lambda: self.Check())

    def button(self, y):
        b1 = Button(self.parentWidget(),[self.width(), y, 70, 20],lambda: self.scream_choose(),text=self.Else["time"],style=f"background:transparent;color:#dd7aff;font-family:Arial;font-size:12pt;text-align:right;",)
        b1.show()
        return b1

    def Clock(self):
        if "todo" in Page.page:
            date0 = datetime.now()
            times = [(datetime(*self.Time) - date0).days,self.Time[3] - date0.hour,self.Time[4] - date0.minute,self.Time[5] - date0.second,]
            if times[3] < 0:
                times[2] -= 1
                times[3] += 60
            if times[2] < 0:
                times[1] -= 1
                times[2] += 60
            if times[1] < 0:
                times[1] += 24
            if self.Else["type"] == 0:
                self.left_time.set(f"{times[1]:02d}:{times[2]:02d}:{times[3]:02d}",not sip.isdeleted(self),)
            else:
                self.left_time.set(f"{times[0]} {times[1]:02d}:{times[2]:02d}:{times[3]:02d}",not sip.isdeleted(self),)
        else:
            Timer.del_func_1000(self.Clock)

    def clock_top_window(self):
        t0 = WID(None, f"background-color:{colors['normal-bg']};", 0, 0, 300, 50)
        t0.setWindowFlag(types.SubWindow,True)
        t0.setWindowOpacity(0.48)
        t0.clockTopWin(self.left_time.get(), self.Time, self.text())

    def Check(self):
        h = Data.load()
        h["Todo"][self.text()]["type"] = int(self.isChecked()) + 1
        Data.write(h)
        if calendar.selectedDate().toString("yyyy-MM-dd") == self.Else["date"]:
            show_todo()

    def scream_choose(self, Type: Literal["change", "add"] = "change"):
        def rel():
            p = Page.cal.selectedDate()
            if calendar.selectedDate() in map(lambda x:p.addDays(x-p.dayOfWeek()+1),[0,1,2,3,4,5,6]):
                show_todo()
            self.left_time.widget = []
            Timer.del_func_1000(self.Clock)
            sip.delete(ma)
            Page.destroy("todo")
            Page.todo()
            Page.cal.setSelectedDate(p)

        def button_choose():
            e = self.el.index(e4.currentText())
            h = Data.load()
            if Type == "change" and e1.text() != self.text():
                del h["Todo"][self.text()]
            h["Todo"][e1.text()] = {"date": t1.date().toString("yyyy-MM-dd") if e != 0 else "Next","time": t1.time().toString("hh:mm:ss"),"prompt": e3.toPlainText(),"type": e,}
            Data.write(h)
            rel()
            des()

        def delete():
            global win_count
            h = Data.load()
            del h["Todo"][self.text()]
            Data.write(h)
            rel()

        def cancel():
            self.No_Change = True
            self.left_time.widget = []
            Timer.del_func_1000(self.Clock)
            sip.delete(ma)

        def des():
            self.left_time.widget = []
            Timer.del_func_1000(self.Clock)
            self.No_Change = True

        if self.No_Change:
            self.No_Change = False
            color_bg_0 = f"rgba({color_alpha[0]},{color_alpha[1]},{color_alpha[2]},0.8)"
            ma = WID(None,f"background:{color_bg_0};",0,0,300,250)
            ma.setWindowFlags(types.SubWindow)
            ma.setWindowTitle(Type if Type == "add" else f"{Type}:{self.text()}")
            ma.destroyed.connect(des)
            e1 = Entry(ma,f"font-family:Arial;font-size:17pt;background:transparent;color:{color2};",[0, 0, 300, 30],self.text(),)
            t1 = QtWidgets.QDateTimeEdit(ma)
            t1.setStyleSheet(f"font-family:Arial;font-size:16pt;color:{color2};background:transparent;")
            t1.setCalendarPopup(True)
            t1c = QtWidgets.QCalendarWidget()
            t1c.setVerticalHeaderFormat(t1c.VerticalHeaderFormat.NoVerticalHeader)
            t1c.setHorizontalHeaderFormat(t1c.HorizontalHeaderFormat.NoHorizontalHeader)
            t1c.setStyleSheet(
                """
                QCalendarWidget QWidget {{
                    background:transparent;
                    width:300px;
                    height:300px;
                }}
                QCalendarWidget QAbstractItemView {{
                    font-family:Arial;font-size:8pt;
                    color:#d48649;
                    background-color:#ffc496;
                    selection-background-color:#d48649;
                    selection-color:#ffffff;
                }}
                QCalendarWidget QToolButton {{
                    font-family:Arial;font-size:8pt;
                    color:#d48549;background:transparent;
                }}
            """
            )
            t1.setCalendarWidget(t1c)
            t1.setDisplayFormat("yyyy/MM/dd hh:mm:ss")
            t1.setGeometry(0, 30, 300, 30)
            t1.show()
            e4 = Combobox(
                ma,
                f"background:{color};color:{color2};font-family:Arial;font-size:17pt;",
                self.el,
                [0, 60, 400, 30],
            )
            e4.show()
            e3 = TextEdit(ma, 0, 90, 300, 90)
            e3.show()
            Else = self.Else
            if Else["type"] != 0:
                t1.setDateTime(datetime(*list(map(int, Else["date"].split("-") + Else["time"].split(":")))))
            else:
                d=datetime.now().date()
                t1.setDateTime(datetime(d.year,d.month,d.day,*list(map(int, Else["time"].split(":")))),)
            e3.insertPlainText(Else["prompt"])
            e4.setCurrentIndex(Else["type"])
            if Type == "change":
                Button(ma,[0, 180, 40, 30],button_choose,text="ok",).show()
                Button(ma, [40, 180, 70, 30], delete, text="delete").show()
                Button(ma, [110, 180, 80, 30], cancel, text="cancel").show()
            else:
                Button(ma,[0, 180, 40, 30],button_choose,text="add",).show()
                Button(ma, [40, 180, 70, 30], cancel, text="cancel").show()
            b0 = Button(ma,[200,180,50, 30],lambda: self.clock_top_window(),text="1 00:00:00",style=f"background:transparent;color:#dd7aff;font-family:Arial;font-size:12pt;",)
            self.left_time.add(b0)
            b0.adjustSize()
            b0.show()
            self.Clock()
            Timer.add_func_1000(self.Clock)
            ma.show()


class Slider(QtWidgets.QSlider):
    def __init__(self,master: QtWidgets.QWidget,*geometry,):
        super().__init__(master)
        self.setOrientation(Qt.Orientation.Horizontal)
        self.setStyleSheet(widget["Slider-0"])
        self.setGeometry(*geometry)
    def setting(self,range=[0,100],value=0,func=None):
        self.setRange(*range)
        self.setValue(value)
        if func:
            self.valueChanged.connect(func)


class WID(QtWidgets.QWidget):
    def __init__(self, parent, style="", *geometry):
        super().__init__(parent)
        self.setGeometry(*geometry[:4])
        self.setStyleSheet(style)


class WID_Todo(QtWidgets.QScrollArea):
    def __init__(self, parent: QtWidgets.QWidget | None = ...,wid=None,styleSheet:str="",geometry=[0,0,0,0]):
        super().__init__(parent)
        self.wid = wid
        self.setWidget(wid)
        self.setStyleSheet(styleSheet)
        self.setGeometry(*geometry)
        self.setWidgetResizable(True)


class NoTitleWidget(WID):
    def __init__(self, parent, text:Literal["page","todo","song","timer","battery"], *geometry):
        super().__init__(parent,"",*Data.get("window")[text],*geometry[:2])
        self.text = text
        self.moveFlag = False
    def mousePressEvent(self, a0):
        clicked_label.add(self,a0.pos())
        if a0.button() == Qt.MouseButton.LeftButton:
            self.moveFlag = True
            self.movePosition = a0.globalPosition().toPoint() - self.pos()
            self.raise_()
            a0.accept()

    def mouseMoveEvent(self, a0):
        if self.moveFlag:
            self.move(a0.globalPosition().toPoint() - self.movePosition)
            a0.accept()

    def mouseReleaseEvent(self, a0):
        self.moveFlag = False
        o = Data.load()
        o["window"][self.text] = [self.pos().x(), self.pos().y()]
        Data.write(o)
        a0.accept()


class TopWin(WID):
    def __init__(self, parent: QtWidgets.QWidget | None, text:page_type, color="transparent", x=0,y=0):
        super().__init__(parent, f"background-color:{color};", *Data.get("page")[text], x,y)
        self.text = text
        self.moveFlag = False
    def mousePressEvent(self, a0):
        clicked_label.add(self,a0.pos())
        if a0.button() == Qt.MouseButton.LeftButton:
            self.moveFlag = True
            self.movePosition = a0.globalPosition().toPoint() - self.pos()
            self.raise_()
            a0.accept()

    def mouseMoveEvent(self, a0):
        if self.moveFlag:
            self.move(a0.globalPosition().toPoint() - self.movePosition)
            a0.accept()

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent):
        self.moveFlag = False
        self.setCursor(Qt.CursorShape.ArrowCursor)
        o = Data.load()
        o["page"][self.text] = [self.pos().x(), self.pos().y()]
        Data.write(o)
        a0.accept()

    def clockDestroy(self):
        Timer.del_func_1000(self.clockCount)
        sip.delete(self)

    def clockTopWin(self, target, time, title):
        self.left_time = Valuable(target)
        self.Time = time
        self.title = title
        self.setWindowFlag(types.FramelessWindowHint,True)
        self.setWindowFlag(types.WindowStaysOnTopHint,True)
        self.setFixedSize(175, 60)
        self.show()
        l0 = Label(self,[0, 0, 175, 30],text=title,style="background:transparent;color:#dd7aff;font-family:Arial;font-size:13pt;",)
        l0.show()
        l1 = Label(self,[0, 30, 175, 30],text="100 00:00:00",style="background:transparent;color:#dd7aff;font-family:Arial;font-size:20pt;",)
        l1.setAlignment(align.AlignCenter)
        self.left_time.add(l1)
        l1.show()
        Button(self,[165, 0, 10, 10],lambda: self.clockDestroy(),text="x",style="background:transparent;color:#AA5F39;font-family:Arial;font-size:8pt;",).show()
        self.clockCount()
        Timer.add_func_1000(self.clockCount)

    def clockCount(self):
        if self.title in Data.get("Todo"):
            date0 = datetime.now()
            times = [(date0 - datetime(*self.Time)).days,self.Time[3] - date0.hour,self.Time[4] - date0.minute,self.Time[5] - date0.second,]
            if times[3] < 0:
                times[2] -= 1
                times[3] += 60
            if times[2] < 0:
                times[1] -= 1
                times[2] += 60
            if times[1] < 0:
                times[1] += 24
            self.left_time.set(f"{times[0] or ''} {times[1]:02d}:{times[2]:02d}:{times[3]:02d}")
        else:
            self.clockDestroy()


class MusicPlayer:
    __slots__ = ["media","audio","song","timer","playlist","slider","clear","states","play_num","button_dict","mode","play_already","show_duration"]
    State = Literal["stop", "play", "pause"]

    def __init__(self, slider=None):
        self.mode: Literal["all_once", "all_infinite", "one_infinite"] = Data.get("set")["PlayMode"]
        self.media = QMediaPlayer()
        self.play_already=0
        self.audio = QAudioOutput()
        self.song = Valuable("")
        self.show_duration = Valuable("")
        self.playlist = ""
        self.media.setAudioOutput(self.audio)
        self.states: MusicPlayer.State = "stop"
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(lambda: self.update_slide())
        self.button_dict: dict[Literal["1", "music"], Button] = {}
        if type(slider) == QtWidgets.QSlider:
            self.slider = [slider]
        else:
            self.slider = []

    def add_slider(self, slider):
        if type(slider) == Slider:
            self.slider.append(slider)

    def update_slide(self):
        pos = round(self.media.position()/1000)
        self.show_duration.set(f"{pos//60:02d}:{pos%60:02d}/{self.slider[0].maximum()//60:02d}:{self.slider[0].maximum()%60:02d}")
        for i in self.slider:
            i.setValue(pos)

    def reset_slide(self, max: int = 0):
        max = int(max)
        self.show_duration.set(f"00:00/{max//60:02d}:{max%60:02d}")
        for i in self.slider:
            i.setValue(0)
            i.setRange(0, max)

    def slider_change(self,slider:Slider):
        self.media.setPosition(slider.value()*1000)
        self.show_duration.set(f"{slider.value()//60:02d}:{slider.value()%60:02d}/{slider.maximum()//60:02d}:{slider.maximum()%60:02d}")
        for i in filter(lambda x:x != slider,self.slider):
            i.setValue(slider.value())

    def change_button(self, text="播放"):
        icon = QIcon(f"{path}icon\\{text}.png")
        button_play.setIcon(icon)
        if "addiction" in Page.page:
            self.button_dict["1"].setIcon(icon)
        elif "1" in self.button_dict:
            del self.button_dict["1"]

    def set_button(self, state: Literal["1", "music"], button: Button):
        self.button_dict.update({state: button})
        button.setIcon(QIcon(f"{path}icon\\{'暫停'if V_play.get()==1 else '播放'}.png"))

    def play(self, song: str):
        V_play.set(-1)
        url = QtCore.QUrl.fromLocalFile(song)
        self.media.setSource(url)
        self.media.play()
        self.audio.setVolume(Page.ClockVolume / 100)
        self.media.setPlaybackRate(Page.ClockRate)
        self.reset_slide(MP3(song).info.length)
        self.timer.start(int(1000//Page.ClockRate))
        self.song.set(song.split("\\" if "\\" in song else "/")[-1][:-4])

    def play_list_start(self):
        self.change_button("暫停")
        V_play.set(1)
        self.states = "play"
        self.playlist=combo.currentText()
        self.play_num = Data.get("music")[self.playlist]["Number"]
        self.media.setPlaybackRate(Page.MusicRate)
        self.audio.setVolume(Page.MusicVolume / 100)
        if self.mode != "one_infinite":
            self.play_num -= 1
        self.play_list()
        Timer.add_func_500(self.play_list)
        self.timer.start(int(1000//Page.MusicRate))

    def play_list(self):
        if V_play.get() == 1 and self.states == "play" and not self.media.isPlaying():
            h = Data.load()
            li = list(h["music"][self.playlist]["list"])
            if self.mode == "all_once" and self.play_num == len(li) - 1:
                self.stop_list()
            else:
                if self.mode != "one_infinite":
                    self.play_num = (self.play_num + 1 if self.play_num < len(li) - 1 else 0)
                    h["music"][self.playlist]["Number"] = self.play_num
                    Data.write(h)
                listbox.setCurrentRow(self.play_num)
                song = f"{h['set']['MusicDir']}\\{li[self.play_num]}.mp3"
                self.song.set(li[self.play_num])
                self.reset_slide(MP3(song).info.length)
                self.media.setSource(QtCore.QUrl.fromLocalFile(song))
                self.media.setPosition(0)
                self.media.play()
            self.play_already+=int(self.play_already < 2)

    def pause_list(self):
        Timer.del_func_500(self.play_list)
        self.timer.stop()
        self.change_button()
        self.states = "pause"
        self.media.pause()

    def unpause_list(self):
        Timer.add_func_500(self.play_list)
        self.timer.start(int(1000//Page.MusicRate))
        self.change_button("暫停")
        self.states = "play"
        self.media.play()

    def stop_list(self):
        if self.states != "stop":
            V_play.set(0)
            self.states = "stop"
            self.play_already=2
            Timer.del_func_500(self.play_list)
            self.timer.stop()
            self.reset_slide()
            self.change_button()
            self.song.set("")
            self.playlist=""
            self.media.stop()

    def stop(self):
        V_play.set(0)
        self.timer.stop()
        self.media.stop()

    @property
    def music_list(self):
        return sorted(map(lambda x: x[:-4],filter(lambda x: x[-4:] == ".mp3", os.listdir(Data.get("set")["MusicDir"])),))


class Interaction:
    __slots__ = ["path","tem_dic","time","timer","ctime","count","win","win_bool","ListBox","NoEdit","show",]

    def __init__(self, path):
        self.path = path
        self.show = Valuable("00:00:00")
        self.time = 0
        with open(path, encoding="UTF-8") as r:
            self.tem_dic = dict(json.load(r))
        self.count = False
        self.win_bool = False

    def filename(self, types: Literal["*.mp3", "*.txt", "dir"],path: str):
        """::types (str): 類型"""
        if types == "dir":
            return QtWidgets.QFileDialog.getExistingDirectory(main_window, directory=path)
        else:
            return QtWidgets.QFileDialog.getOpenFileName(main_window, directory=path, filter=types)[0]

    def AskStr(self, prompt: str):
        return QtWidgets.QInputDialog.getText(main_window, "today's homework!!!", prompt)

    def load(self):
        return self.tem_dic

    def write(self, obj: dict):
        with open(self.path, "w", encoding="UTF-8") as r:
            self.tem_dic = obj
            json.dump(obj, r)

    def get(self,key: Literal["Todo", "Class", "music", "learn", "set", "window", "page", "color", "style","exe"],):
        if key in self.tem_dic and type(self.tem_dic[key])==dict:
            return dict(self.tem_dic[key])
        elif key in self.tem_dic and type(self.tem_dic[key])==list:
            return list(self.tem_dic[key])

    @staticmethod
    def split(list1: list):
        d = {}
        di = list(filter(lambda x: len(x) == 2, map(lambda x: x.split(":", 1), list1)))
        d = {x: y for (x, y) in di}
        return d

    def set_win(self):

        def destroy():
            hour, minute, second = list(map(lambda x: int(x.currentText()), [e0, e1, e2]))
            self.show.set(f"{hour:02d}:{minute:02d}:{second:02d}")
            self.time = hour * 3600 + minute * 60 + second
            win.deleteLater()

        if not self.count:
            win = WID(None, f"background-color:{color};", 400, 400, 200, 180)
            win.setWindowFlag(types.SubWindow,True)
            win.setWindowTitle("count down")
            li = list(map(str, range(0, 100)))
            style = f"font-family:Arial;font-size:15pt;background-color:{color};color:{color2};"
            s = self.show.get().split(":")
            Label(win, [0, 0, 70, 50], text="hour", style=style).show()
            e0 = Combobox(win, style, li, [70, 0, 100, 50])
            e0.setCurrentIndex(int(s[0]))
            e0.show()
            Label(win, [0, 50, 70, 50], text="minute", style=style).show()
            e1 = Combobox(win, style, li[:60], [70, 50, 100, 50])
            e1.setCurrentIndex(int(s[1]))
            e1.show()
            Label(win, [0, 100, 70, 50], text="second", style=style).show()
            e2 = Combobox(win, style, li[:60], [70, 100, 100, 50])
            e2.setCurrentIndex(int(s[2]))
            e2.show()
            Button(win, [0, 150, 60, 30], destroy, text="確認", style=style).show()
            win.show()

    def start(self):
        self.count = True
        self.ctime = 30
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(lambda: self.counting())
        self.timer.start(1000)
        self.counting()

    def counting(self):
        if self.time > 0 and self.count:
            h,i,s, = self.show.get().split(":")
            if s == "00":
                if i == "00" and h != "00":
                    self.show.set(f"{int(h)-1:02d}:59:59")
                else:
                    self.show.set(f"{h}:{int(i)-1:02d}:59")
            else:
                self.show.set(f"{h}:{i}:{int(s)-1:02d}")
            self.time -= 1
        elif self.time == 0:
            if self.ctime == 30:
                self.count = False
                Music.stop()
                Music.play(Data.get("set")["ClockMusic"])
                V_play.set(1)
                Music.reset_slide(30)
            if self.ctime >= 0:
                self.ctime -= 1
            if self.ctime == -1:
                Music.reset_slide()
                Music.stop()
        if not (self.time > 0 and self.count) and self.ctime < 0:
            self.timer.stop()


class Page_Organize:
    __slots__ = ["page", "test_num", "test_number", "listbox","ClockVolume","MusicVolume","ClockRate","MusicRate","mini_dict","todo_dict","cal","after"]

    class But(QtWidgets.QPushButton):
        def __init__(self, master, x,y,w,h, command=None,text="",image: str = None,num=0):
            super().__init__(master)
            b = Button(master,[x,y+h,w,15],lambda:self.win(text,command,image,[w,h],num),text=text,style=f"color:{color2};background:transparent;text-align:left;")
            b.adjustSize()
            b.show()
            self.b=b
            self.setIcon(QIcon(image))
            self.setIconSize(QtCore.QSize(w,h))
            self.setGeometry(x,y,w,h)
            self.setStyleSheet("background:transparent;")
            if type(command)==str and command[:4] == "http":
                self.clicked.connect(lambda:webbrowser.open(command))
            elif type(command) == str:
                self.clicked.connect(lambda:os.popen(command))
            self.show()
        @staticmethod
        def win(text,exec,icon:str,geometry,num):
            def submit():
                h = Data.load()
                width = int(entry_x.text())
                height = int(entry_y.text())
                if "" not in [entry_text.text(),entry_exec.text(),entry_icon.text()] and 0 not in [width,height]:
                    if len(list(filter(lambda x:text==x["text"],h["exe"])))==1:
                        h["exe"].pop(num)
                    h["exe"].insert(entry_num.currentIndex(),{"text":entry_text.text(),"exec": entry_exec.text(),"icon": entry_icon.text(),"width":width,"height":height})
                    Data.write(h)
                    window.destroy(True,True)
                    sip.delete(window)
                    Page.addiction()
            def delete():
                o=list(filter(lambda x:text==x["text"],h["exe"]))
                if len(o)==1:
                    h = Data.load()
                    h["exe"].pop(h["exe"].index(o[0]))
                    Data.write(h)
                    Page.addiction()
                window.destroy(True,True)
                sip.delete(window)

            def set_exec():
                file = QtWidgets.QFileDialog.getOpenFileName(main_window, directory=path,filter="Exec(*.exe)")
                entry_exec.setText(file[0])

            def set_icon():
                file = QtWidgets.QFileDialog.getOpenFileName(main_window, directory=path,filter="Icon(*.ico);;Png(*.png);;Jpeg(*.jpeg,*.jpg);;All(*.*)")
                entry_icon.setText(file[0])

            window = WID(None,"",300,300,200,150)
            window.setWindowFlag(types.SubWindow,True)
            window.setWindowTitle(text)
            entry_text = Entry(window,"",[0,0,200,30],text)
            entry_text.show()
            entry_exec = Entry(window,"",[0,30,150,30],exec)
            entry_exec.show()
            Button(window,[150,30,50,30],set_exec,text="set").show()
            entry_icon = Entry(window,"",[0,60,150,30],icon)
            entry_icon.show()
            Button(window,[150,60,50,30],set_icon,text="set").show()
            entry_num = Combobox(window,"",map(str,range(len(Data.get("exe")))),[0,90,100,30])
            entry_num.setCurrentIndex(num)
            entry_num.show()
            entry_x = Entry(window,"",[100,90,50,30],str(geometry[0]))
            entry_x.show()
            entry_y = Entry(window,"",[150,90,50,30],str(geometry[1]))
            entry_y.show()
            Button(window,[0,120,50,30],submit,text="submit").show()
            Button(window,[50,120,50,30],delete,text="delete").show()
            Button(window,[100,120,50,30],lambda:window.deleteLater(),text="cancel").show()
            window.show()
        @staticmethod
        def add():
            def submit():
                h = Data.load()
                width = int(entry_x.text())
                height = int(entry_y.text())
                if "" not in [entry_text.text(),entry_exec.text(),entry_icon.text()] and 0 not in [width,height]:
                    h["exe"].insert(entry_num.currentIndex(),{"text":entry_text.text(),"exec": entry_exec.text(),"icon": entry_icon.text(),"width":width,"height":height})
                    Data.write(h)
                    window.deleteLater()
                    Page.addiction()

            def set_exec():
                file = QtWidgets.QFileDialog.getOpenFileName(main_window, directory=path,filter="Exec(*.exe)")
                entry_exec.setText(file[0])

            def set_icon():
                file = QtWidgets.QFileDialog.getOpenFileName(main_window, directory=path,filter="Icon(*.ico);;Png(*.png);;Jpeg(*.jpeg,*.jpg);;All(*.*)")
                entry_icon.setText(file[0])

            window = WID(None,"",300,300,200,150)
            window.setWindowFlag(types.SubWindow,True)
            window.setWindowTitle("add")
            entry_text = Entry(window,"",[0,0,200,30])
            entry_text.show()
            entry_exec = Entry(window,"",[0,30,150,30])
            entry_exec.show()
            Button(window,[150,30,50,30],set_exec,text="set").show()
            entry_icon = Entry(window,"",[0,60,150,30])
            entry_icon.show()
            Button(window,[150,60,50,30],set_icon,text="set").show()
            entry_num = Combobox(window,"",map(str,range(len(Data.get("exe")))),[0,90,100,30])
            entry_num.show()
            entry_x = Entry(window,"",[100,90,50,30],"0")
            entry_x.show()
            entry_y = Entry(window,"",[150,90,50,30],"0")
            entry_y.show()
            Button(window,[0,120,50,30],submit,text="submit").show()
            Button(window,[50,120,50,30],lambda:window.deleteLater(),text="cancel").show()
            window.show()

    def __init__(self):
        self.test_num = -1
        self.test_number = 0
        self.page: dict[page_type, TopWin] = {}
        s = Data.get("set")
        self.ClockVolume = s["ClockVolume"]
        self.MusicVolume = s["MusicVolume"]
        self.ClockRate = s["ClockRate"]
        self.MusicRate = s["MusicRate"]
        self.mini_dict={}
        self.cal = None

    def add_win(self,page: page_type,parent: QtWidgets.QMainWindow | None = None,color="transparent",x=0,y=0,):
        if page in self.page:
            if page == "addiction":
                V_time.delete(self.mini_dict["time"])
                V_date.delete(self.mini_dict["date"])
                sip.delete(self.mini_dict["win"])
                Timer.func_1000.pop(self.after)
            self.destroy(page)
        self.page[page] = TopWin(parent, page, color, x, y)
        self.page[page].setAttribute(Qt.WidgetAttribute.WA_StyledBackground,True)
        return self.page[page]

    def destroy(self, page: page_type):
        if page in self.page:
            sip.delete(self.page.pop(page))

    def todo(self):
        def clicked():
            def lambda_click():
                if len(m:=list(filter(lambda x:x[0].underMouse(),self.todo_dict)))>0:
                    chose = Choose(win,"",{"date": (today+timedelta(self.todo_dict.index(m[0]))).strftime("%Y-%m-%d"),"time": "00:00:00","prompt": "","type": 1,},)
                    chose.setVisible(False)
                    chose.scream_choose("add")

            today = cal.selectedDate().toPyDate()
            today = today - timedelta(today.weekday())
            ge = Data.get("Todo")
            list(map(lambda x:(sip.delete(x[0]),sip.delete(x[1])),self.todo_dict))
            self.todo_dict = []
            for fa in map(lambda x:today+timedelta(x),[0,1,2,3,4,5,6]):
                position_y = 25
                if fa.weekday()<5:
                    y = 100*fa.weekday()
                    x=0
                else:
                    y = 100*(fa.weekday()-2)
                    x = 340
                wi = WID(win,"background:transparent;",0,0,1,1)
                si = WID_Todo(win,wi,style,[x,y,340,100])
                self.todo_dict+=[[wi,si]]
                Button(wi,[10,5,100,20],lambda_click,text=fa.strftime("%m/%d  %a"),style=f"color:{color2};font-family:Arial;font-size:14pt;background:transparent;border:none;").show()
                if fa.strftime("%Y/%m/%d  %a")==datetime.now().strftime("%Y/%m/%d  %a"):
                    Label(wi,[110,4,100,21],text="Today",style=f"color:#6ae680;font-family:Arial Rounded MT Bold;font-weight:bold;font-size:13pt;background:transparent;").show()
                for fi in sorted(filter(lambda x:ge[x]["date"]==fa.strftime("%Y-%m-%d"),ge),key=lambda x:ge[x]["time"]):
                    gn = ge[fi]
                    ch = Choose(wi, fi, gn)
                    ch.move(0, position_y)
                    ch.adjustSize()
                    ch.show()
                    b1 = ch.button(position_y + 8)
                    if len(gn["prompt"]) > 0:
                        l1 = Label(wi,[b1.x()+b1.width(), position_y, 30, 30],text="*",style="color:#7bc3c4;font-family:細明體-ExtB;font-size:14pt;font-weight:bold;background:transparent;",)
                        l1.adjustSize()
                        l1.show()
                    position_y+=ch.height()
                wi.adjustSize()
                wi.setMinimumSize(wi.width(),wi.height())
                si.show()
        def last():
            cal.setSelectedDate(cal.selectedDate().toPyDate()-timedelta(7))
            clicked()
        def next():
            cal.setSelectedDate(cal.selectedDate().toPyDate()+timedelta(7))
            clicked()

        win = self.add_win("todo", main_window, f"rgba({color_alpha[0]},{color_alpha[1]},{color_alpha[2]},0.15)", 680, 510)
        ge = Data.get("Todo")
        self.todo_dict:list[list[WID]] = []
        style = f"""
            QScrollArea {{background: rgba({color_alpha[0]},{color_alpha[1]},{color_alpha[2]},0.56);border-radius:20px;border: 2px dotted rgba({color_alpha2[0]}, {color_alpha2[1]}, {color_alpha2[2]}, 0.89);}}
            QScrollBar:vertical {{{widget["ScrollBar"]["vertical"]}}}
            QScrollBar:vertical:hover {{{widget["ScrollBar"]["vertical"]}}}
            QScrollBar::handle:vertical {{{widget["ScrollBar"]["handle"]}}}
            QScrollBar::add-page:vertical {{width: 10px;background: transparent;}}
            QScrollBar::sub-page:vertical {{width: 10px;background: transparent;}}
            QScrollBar::sub-line:vertical {{height: 12px;width: 10px;background: transparent;subcontrol-position: top;}}
            QScrollBar::add-line:vertical {{height: 12px;width: 10px;background: transparent;subcontrol-position: bottom;}}
            QScrollBar:horizontal {{{widget["ScrollBar"]["vertical"]}}}
            QScrollBar:horizontal:hover {{{widget["ScrollBar"]["vertical"]}}}
            QScrollBar::handle:horizontal {{{widget["ScrollBar"]["handle"]}}}
            QScrollBar::add-page:horizontal {{width: 10px;background: transparent;}}
            QScrollBar::sub-page:horizontal {{width: 10px;background: transparent;}}
            QScrollBar::sub-line:horizontal {{height: 12px;width: 10px;background: transparent;subcontrol-position: left;}}
            QScrollBar::add-line:horizontal {{height: 12px;width: 10px;background: transparent;subcontrol-position: right;}}
        """
        w = QtWidgets.QWidget(win)
        w.setStyleSheet("background:transparent;")
        position_y = 0
        for fa in filter(lambda x:ge[x]["date"]=="Next",ge):
            gn = ge[fa]
            ch = Choose(w, fa, gn)
            ch.move(0, position_y)
            ch.adjustSize()
            ch.show()
            b1 = ch.button(position_y+8)
            if len(gn["prompt"]) > 0:
                l1 = Label(w,[b1.x()+b1.width(), position_y+5, 11, 19],text="*",style="color:#7bc3c4;font-family:細明體-ExtB;font-size:14pt;font-weight:bold;background:transparent;",)
                l1.show()
            position_y+=30
        w.adjustSize()
        w.setMinimumSize(w.width(),w.height())
        WID_Todo(win,w,style,[340,200,340,100]).show()
        cal = QtWidgets.QCalendarWidget(win)
        cal.setGeometry(340,0,200,200)
        cal.setVerticalHeaderFormat(cal.VerticalHeaderFormat.NoVerticalHeader)
        cal.setHorizontalHeaderFormat(cal.HorizontalHeaderFormat.SingleLetterDayNames)
        forma = cal.headerTextFormat()
        forma.setBackground(QtGui.QColor(color_alpha[0],color_alpha[1],color_alpha[2],30))
        forma.setFontPointSize(8)
        cal.setHeaderTextFormat(forma)
        cal.setFirstDayOfWeek(Qt.DayOfWeek.Monday)
        cal.setGridVisible(True)
        cal.setStyleSheet(
            f"""
            QCalendarWidget QWidget {{
                background:transparent;
            }}
            QCalendarWidget QAbstractItemView {{
                color:{color2};
                background-color:{color};
                selection-background-color:{color2};
                selection-color:{color};
            }}
            QCalendarWidget QToolButton {{
                font-family:Arial;
                font-weight:bold;
                color:#ffffff;background:transparent;
            }}
        """
        )
        cal.selectionChanged.connect(clicked)
        cal.show()
        self.cal = cal
        Button(win,[540,175,25,25],last,image=QIcon(f"{path}home\\last.png"),style=f"background:rgba({color_alpha[0]},{color_alpha[1]},{color_alpha[2]},0.56);",).show()
        Button(win,[565,175,25,25],next,image=QIcon(f"{path}home\\next.png"),style=f"background:rgba({color_alpha[0]},{color_alpha[1]},{color_alpha[2]},0.56);",).show()
        clicked()
        Button(win,[655, 0, 25, 20],lambda: self.destroy("todo"),text="x").show()
        win.show()

    def dic(self):
        def word_card():
            def next_question():
                text = ""
                self.test_num += 1
                if self.test_num > 0:
                    text += f"{self.test_num-1}. {(LA:=list(LReadDict.keys())[self.test_number])}\n{LReadDict[LA]}\n--{['加油!!','你對了。'][entry.text() in LReadDict[LA]]}\n\n"
                self.test_number = random.randint(0, len(LReadDict) - 1)
                text += f"{self.test_num}. {list(LReadDict.keys())[self.test_number]}"
                write1.clear()
                write1.insertPlainText(text)
                write1.ensureCursorVisible()

            def reload_it():
                sip.delete(WL_but1)
                sip.delete(WL_but2)
                for fa in [but2, but3, but4, l0]:
                    fa.setVisible(True)
                entry.textChanged.connect(lambda: connect())
                write1.setReadOnly(False)
                write1.clean()

            LReadDict = Data.split(list(write1.Open().split("\n")))
            entry.textChanged.disconnect()
            for fa in [but2, but3, but4, l0]:
                fa.setVisible(False)
            write1.setReadOnly(True)
            write2.clear()
            next_question()
            WL_but1 = Button(win,[400, 40, 200, 30],lambda: next_question(),text="next",style=style1,)
            WL_but1.show()
            WL_but2 = Button(
                win, [400, 10, 200, 30], lambda: reload_it(), text="exit", style=style1
            )
            WL_but2.show()

        def connect():
            write1.clean()
            if entry.text() != "":
                write1.get = entry.text()
                str1 = write1.Open().split("\n")
                write1.list1 = list(map(lambda x: str(str1.index(x)),filter(lambda y: write1.get in y, str1),))
                write1.WST.clear()
                write1.WST.addItems(write1.list1)

        win = self.add_win("dic", main_window, x=600, y=300)
        style = f"background-color:{color};color:#fc8289;font-family:Arial;font-size:16pt;font-weight:bold;"
        write2 = QtWidgets.QListWidget(win)
        write2.setStyleSheet(widget["PlainTextEdit"])
        write2.setGeometry(400, 100, 200, 200)
        write1 = WriteIt(win, write2, 0, 0, 400, 300)
        write2.clicked.connect(lambda: write1.moved())
        entry = Entry(win, style, [400, 70, 200, 30])
        entry.textChanged.connect(lambda: connect())
        style1 = f"""QPushButton {{background-color:{color};color:#d48649;font-family:Arial;font-size:16pt;font-weight:bold;}}QPushButton:activate {{background-color:{color};color:#d48649}}"""
        but2 = Button(win, [400, 40, 100, 30], lambda: write1.clear(), text="clear", style=style1)
        but3 = Button(win,[500, 40, 100, 30],lambda: write1.save_file(),text="save",style=style1,)
        but4 = Button(win, [400, 10, 100, 30], lambda: word_card(), text="單字卡", style=style1)
        l0 = Label(win, [500, 10, 100, 30], text="第1行", style=style)
        write1.put.add(l0)
        for fa in [write1, write2, entry, but2, but3, but4, l0]:
            fa.show()
        Button(win,[580, 0, 20, 15],lambda: self.destroy("dic"),text="x").show()
        win.show()
        write1.clean()

    def learn(self):
        def add_func():
            h = Data.load()
            if (j := Data.AskStr("加入\n標題: "))[1]and j[0] not in h["learn"]and j[0] != "Class":
                h["learn"][j[0]] = {}
                Data.write(h)
                lrn_but.clear()
                lrn_but.addItems(list(h.get("learn").keys()) + ["Class"])

        def rename_func():
            if (j := Data.AskStr("重新命名\n新標題:"))[1] and lrn_but.currentText() in (h := Data.load())["learn"]:
                h["learn"][j[0]] = h["learn"].pop(lrn_but.currentText())
                Data.write(h)
                lrn_but.clear()
                lrn_but.addItems(list(h.get("learn").keys()) + ["Class"])

        def delete_func():
            h = Data.load()
            c = lrn_but.currentText()
            if c in h["learn"] and MessageBox.question(main_window, "today's homework!!!", f"你確定要刪除這個字典嗎?\n{c}"):
                del h["learn"][c]
                Data.write(h)
                lrn_but.removeItem(lrn_but.currentIndex())

        def search_func():
            if (m := Data.AskStr("您想查詢:"))[1] and lrn_but.currentText() in (sh := Data.get("learn")):
                sh = sh[lrn_but.currentText()]
                t = m + "\n"
                if m in sh:
                    t += sh[m]
                elif m in (si := {x: y for (x, y) in si.items()}):
                    t += si[m]
                else:
                    t += "不在這字典中"
                MessageBox.information(main_window, "today's homework!!!", t)

        def open_func():
            h = Data.load()
            if (m := Data.filename("*.txt",path)) and (s := Data.AskStr("開啟\n新的標題:"))[1] and s not in Data.get("learn") and s != "Class":
                with open(m, encoding="UTF-8") as w:
                    h["learn"][s[0]] = Data.split(w.read().split("\n"))
                    Data.write(h)
                lrn_but.clear()
                lrn_but.addItems(list(h.get("learn").keys()) + ["Class"])

        def trans_func():
            if lrn_but.currentText() in Data.get("learn") and len(s1 := lrn_t1.toPlainText()) == len(s2 := lrn_t2.toPlainText()):
                with open(path + lrn_but.currentText() + ".txt", "w", encoding="UTF-8") as w:
                    w.write("\n".join(map(lambda x, y: x + ":" + y, s1, s2)))

        def ADD():
            h = Data.load()
            if (m := Data.AskStr("加入\n標題:"))[1] and m not in h["Class"]:
                h["Class"][m[0]] = []
                Data.write(h)
                lrn_but2.clear()
                lrn_but2.addItems(list(h.get("Class").keys()))

        def DELETE():
            h = Data.load()
            c = lrn_but2.currentText()
            if c in h["Class"] and MessageBox.question(main_window, "today's homework!!!", f"你確定要刪除這個字典嗎?\nClass-{c}"):
                del h["Class"][c]
                Data.write(h)
                lrn_but2.removeItem(lrn_but2.currentIndex())

        def Class():
            t2 = ""
            so = Data.get("Class")[lrn_but2.currentText()]
            if type(so) == list:
                t2 = "\n".join(so)
            else:
                t2 = str(so)
            lrn_t2.setPlainText(t2)

        def save():
            h = Data.load()
            n = lrn_t2.toPlainText().split("\n")
            c = lrn_but2.currentText()
            if c in ["日數", "節數"]:
                try:
                    h["Class"][c] = int(n[0])
                except:
                    MessageBox.warning(main_window, "today's homework!!!","第一行應為整數！")
            else:
                h["Class"][c] = n
            Data.write(h)

        def lear():
            so = dict(Data.get("learn")[lrn_but.currentText()])
            lrn_t1.setPlainText("\n".join(so.keys()))
            lrn_t2.setPlainText("\n".join(so.values()))

        def enter():
            if lrn_but.currentText() == "Class":
                lrn_t1.setVisible(False)
                button_frame.setVisible(True)
                lrn_t2.clear()
            else:
                lrn_t1.setVisible(True)
                button_frame.setVisible(False)
                lear()

        def save_func():
            if len(s1 := lrn_t1.toPlainText().split("\n")) != len(s2 := lrn_t2.toPlainText().split("\n")):
                MessageBox.warning(main_window, "today's homework!!!", "單字與中文翻譯數量不一致")
            elif len(set(s1)) != len(s2):
                MessageBox.warning(main_window, "today's homework!!!", "有重複的單字")
            else:
                h = Data.load()
                h["learn"][lrn_but.currentText()] = {x: y for (x, y) in list(zip(s1, s2))}
                Data.write(h)

        win = self.add_win("learn", main_window, x=600, y=460)
        t = f"rgba({', '.join(map(str,color_alpha+[0.56]))})"
        style = f"background:{t};color:#fc8289;font-family:Arial;font-size:15pt;font-weight:bold;"
        lrn_t1 = TEXT(win, [0, 30, 300, 400])
        lrn_t1.setStyleSheet(f"background:{t};color:#fc8289;font-family:Arial;font-size:15pt;")
        lrn_t2 = TEXT(win, [300, 30, 300, 400])
        lrn_t2.setStyleSheet(f"background:{t};color:#fc8289;font-family:微軟正黑體;font-size:13pt;font-weight:bold;")
        lrn_t2.setLineWrapMode(lrn_t2.LineWrapMode.NoWrap)
        lrn_t1.setLineWrapMode(lrn_t1.LineWrapMode.NoWrap)
        lrn_t1.setting(lrn_t2)
        lrn_t2.show()
        lrn_t1.show()
        lrn_but = Combobox(win,f"QComboBox {{background-color:rgba(255, 255, 255, 0.58);color:#fc8289;}}QComboBox:activate {{background-color:rgba(255, 255, 255, 0.58);color:#fc8289;}}",list(Data.get("learn").keys()) + ["Class"],[0, 0, 200, 30],)
        lrn_but.activated.connect(enter)
        lrn_but.show()
        Button(win, [200, 0, 40, 30], add_func, text="add", style=style).show()
        Button(win, [0, 430, 45, 30], save_func, text="save", style=style).show()
        Button(win, [45, 430, 70, 30], search_func, text="search", style=style).show()
        Button(win, [115, 430, 50, 30], trans_func, text="trans", style=style).show()
        Button(win, [165, 430, 50, 30], open_func, text="open", style=style).show()
        Button(win, [215, 430, 70, 30], rename_func, text="rename", style=style).show()
        Button(win, [285, 430, 65, 30], delete_func, text="delete", style=style).show()
        button_frame = QtWidgets.QFrame(win)
        button_frame.setGeometry(0, 30, 300, 400)
        button_frame.setStyleSheet(style)
        button_frame.setVisible(False)
        lrn_but2 = Combobox(button_frame,f"""QComboBox {{background-color:rgba(255, 255, 255, 0.58);color:#fc8289;}}QComboBox:activate {{background-color:rgba(255, 255, 255, 0.58);color:#fc8289;}}""",list(Data.get("Class").keys()),[100, 0, 200, 30],)
        lrn_but2.activated.connect(Class)
        lrn_but2.show()
        Button(button_frame, [100, 30, 50, 30], save, text="save", style=style).show()
        Button(button_frame, [150, 30, 40, 30], ADD, text="Add", style=style).show()
        Button(button_frame,[190, 30, 70, 30],DELETE,text="Delete",style=style,).show()
        Button(win,[580, 0, 20, 20],lambda: self.destroy("learn"),text="x").show()
        win.show()

    def classes(self):
        i1 = Data.get("Class")
        length = i1["節數"]
        width = i1["日數"]
        win = self.add_win("class", main_window, x=width * 90, y=length * 30)
        c=f"rgba({color_alpha[0]},{color_alpha[1]},{color_alpha[2]},0.56)"
        for fa in range(width):
            i3 = list(i1.keys())[2:][fa]
            Label(win,[fa * 90, 0, 90, 30],text=f"  {i3}  ",style=f"background-color:{c};color:#fc8289;font-family:Arial;font-size:16pt;font-weight:bold;",).show()
            for fi in range(length):
                Label(win,[fa * 90, (fi + 1) * 30, 90, 30],text=i1[i3][fi],style=f"background-color:{c};color:{color2};font-family:Arial;font-size:16pt;font-weight:bold;",).show()
        Button(win,[width * 90 - 20, 0, 20, 20],lambda: self.destroy("class"),text="x").show()
        win.show()

    def set(self):
        def dark():
            V_state.set(dark_scale.value())

        def set_m():
            volume = m_scale.value()
            self.MusicVolume = volume
            m_label.setText(f"Music Volume {volume}%")
            if V_play.get() == 1:
                Music.audio.setVolume(volume / 100)

        def set_c():
            volume = c_scale.value()
            self.ClockVolume = volume
            c_label.setText(f"Clock Volume {volume}%")
            if V_play.get() == -1:
                Music.audio.setVolume(volume / 100)
        def set_music_rate():
            rate = m_rate_scale.value()/100
            self.MusicRate = rate
            m_rate_label.setText(f"Music Rate: {rate}")
            if V_play.get() == 1:
                Music.timer.stop()
                Music.timer.start(int(1000//rate))
                Music.update_slide()
                Music.media.setPlaybackRate(rate)

        def set_clock_rate():
            rate = c_rate_scale.value()/100
            self.ClockRate = rate
            c_rate_label.setText(f"Clock Rate: {rate}")
            if V_play.get() == -1:
                Music.timer.stop()
                Music.timer.start(int(1000//rate))
                Music.update_slide()
                Music.media.setPlaybackRate(rate)

        def set_ClockMusic():
            h = Data.load()
            f = "\\" if "\\" in h["set"]["ClockMusic"] else "/"
            if file := Data.filename("*.mp3",f.join(h["set"]["ClockMusic"].split(f)[:-1])):
                h["set"]["ClockMusic"] = file
                Data.write(h)
                t0.setText(file)

        def set_DictTxt():
            h = Data.load()
            f = "\\" if "\\" in h["set"]["DictTxt"] else "/"
            if file := Data.filename("*.txt",f.join(h["set"]["DictTxt"].split(f)[:-1])):
                h["set"]["DictTxt"] = file
                Data.write(h)
                t1.setText(file)

        def set_MusicDir():
            h = Data.load()
            f = "\\" if "\\" in h["set"]["MusicDir"] else "/"
            if file := Data.filename("*.mp3",f.join(h["set"]["MusicDir"].split(f)[:-1])):
                Music.stop_list()
                h["set"]["MusicDir"] = file
                Data.write(h)
                t2.setText(file)

        def set_Background_file():
            h = Data.load()
            f = "\\" if "\\" in h["set"]["Background"] else "/"
            file = Data.filename("JPEG(*.jpg, *.jpeg, *jpe, *.jfif);;PNG(*png)",f.join(h["set"]["Background"].split(f)[:-1]))
            if len(file) > 0:
                h["set"]["Background"] = file
                Data.write(h)
                t3.setText(file)
                img0 = Image.open(file)
                q_image0 = ImageQt.toqimage(img0)
                q_image1 = ImageQt.toqimage(img0.filter(ImageFilter.GaussianBlur(20)))
                i = QPixmap(img0.width, img0.height).fromImage(q_image0)
                i0 = QPixmap(img0.width, img0.height).fromImage(q_image1).scaled(m.width(), m.height() * (i.width() // i.height())).copy(0, 0, 250, m.height())
                bg.setPixmap(i.scaled(m.width(), m.height() * (i.width() // i.height())))
                l0.setPixmap(i0)

        def set_Background_dir():
            h = Data.load()
            f = "\\" if "\\" in h["set"]["Background"] else "/"
            file = Data.filename("dir",f.join(h["set"]["Background"].split(f)[:-1]))
            if len(file) > 0:
                h["set"]["Background"] = file
                Data.write(h)
                t3.setText(file)
                list_bg = os.listdir(file)
                img0 = Image.open(file+"/"+list_bg[random.randint(0,len(list_bg)-1)])
                q_image0 = ImageQt.toqimage(img0)
                q_image1 = ImageQt.toqimage(img0.filter(ImageFilter.GaussianBlur(20)))
                i = QPixmap(img0.width, img0.height).fromImage(q_image0)
                i0 = QPixmap(img0.width, img0.height).fromImage(q_image1).scaled(m.width(), m.height() * (i.width() // i.height())).copy(0, 0, 250, m.height())
                bg.setPixmap(i.scaled(m.width(), m.height() * (i.width() // i.height())))
                l0.setPixmap(i0)

        win = self.add_win("set", main_window, f"rgba({color_alpha[0]}, {color_alpha[1]}, {color_alpha[2]}, 0.7)", x=320, y=330)
        wid = QtWidgets.QWidget(win)
        wid.setStyleSheet("background:transparent;")
        wid.setMinimumSize(320,390)
        WID_Todo(win,wid,f"""
            QScrollArea {{background:transparent;}}
            QScrollBar:vertical {{{widget["ScrollBar"]["vertical"]}}}
            QScrollBar:vertical:hover {{{widget["ScrollBar"]["vertical"]}}}
            QScrollBar::handle:vertical {{{widget["ScrollBar"]["handle"]}}}
            QScrollBar::add-page:vertical {{width: 10px;background: transparent;}}
            QScrollBar::sub-page:vertical {{width: 10px;background: transparent;}}
            QScrollBar::sub-line:vertical {{height: 12px;width: 10px;background: transparent;subcontrol-position: top;}}
            QScrollBar::add-line:vertical {{height: 12px;width: 10px;background: transparent;subcontrol-position: bottom;}}
        """,[0,0,340,330]).show()
        s = Data.get("set")
        dark_label = Label(wid,[70, 0, 70, 20],text="Dark",style=f"background:transparent;color:#dd7aff;font-family:Arial;font-size:12pt;",)
        dark_label.setAlignment(align.AlignRight)
        dark_label.show()
        dark_scale = Slider(wid, 140, 0, 60, 30)
        dark_scale.setting([0,1],int(Data.get("set")["dark"]),dark)
        m_label = Label(wid,[0, 30, 140, 20],text=f"Music Volume {self.MusicVolume}%",style=f"background:transparent;color:#dd7aff;font-family:Arial;font-size:12pt;",)
        m_scale = Slider(wid, 140, 30, 160, 30)
        c_label = Label(wid,[0, 60, 140, 20],text=f"Clock Volume {self.ClockVolume}%",style=f"background:transparent;color:#dd7aff;font-family:Arial;font-size:12pt;",)
        c_scale = Slider(wid, 140, 60, 160, 30)
        m_rate_label = Label(wid,[0, 90, 140, 20],text=f"Music Rate {self.MusicRate}",style=f"background:transparent;color:#dd7aff;font-family:Arial;font-size:12pt;",)
        m_rate_scale = Slider(wid, 140, 90, 160, 30)
        c_rate_label = Label(wid,[0, 120, 140, 20],text=f"Clock Rate {self.ClockRate}",style=f"background:transparent;color:#dd7aff;font-family:Arial;font-size:12pt;",)
        c_rate_scale = Slider(wid, 140, 120, 160, 30)
        m_scale.setting([0,100],self.MusicVolume,set_m)
        c_scale.setting([0, 100],self.ClockVolume,set_c)
        m_rate_scale.setting([50, 200],int(self.MusicRate*100),set_music_rate)
        c_rate_scale.setting([50, 200],int(self.ClockRate*100),set_clock_rate)
        Button(wid,[0, 150, 100, 30],set_ClockMusic,text="Clock Music",style=f"background:transparent;color:#dd7aff;font-family:Arial;font-size:12pt;",).show()
        t0 = Entry(wid,f"background:rgba(209, 142, 109, 0.4);color:#dd7aff;font-family:Arial;font-size:12pt;",[0,180,300,30],s["ClockMusic"])
        Button(wid,[0, 210, 100, 30],set_DictTxt,text="Dictionary file",style=f"background:transparent;color:#dd7aff;font-family:Arial;font-size:12pt;",).show()
        t1 = Entry(wid,f"background:rgba(209, 142, 109, 0.4);color:#dd7aff;font-family:Arial;font-size:12pt;",[0,240,300,30],s["DictTxt"])
        Button(wid,[0, 270, 100, 30],set_MusicDir,text="Music Dir",style=f"background:transparent;color:#dd7aff;font-family:Arial;font-size:12pt;",).show()
        t2 = Entry(wid,f"background:rgba(209, 142, 109, 0.4);color:#dd7aff;font-family:Arial;font-size:12pt;",[0,300,300,30],s["MusicDir"])
        Label(wid,[0, 330, 100, 30],text="Background",style=f"background:transparent;color:#dd7aff;font-family:Arial;font-size:12pt;",).show()
        Button(wid,[100, 330, 40, 30],set_Background_file,text="file").show()
        Button(wid,[140, 330, 40, 30],set_Background_dir,text="dir").show()
        t3 = Entry(wid,f"background:rgba(209, 142, 109, 0.4);color:#dd7aff;font-family:Arial;font-size:12pt;",[0,360,300,30],s["Background"])
        for i in [m_label, c_label,m_rate_label,c_rate_label, m_scale, c_scale,m_rate_scale,c_rate_scale, t0, t1, t2, t3]:
            i.show()
        Button(win,[300, 0, 20, 15],lambda: self.destroy("set"),text="x").show()
        win.show()

    def addiction(self):
        def des():
            Timer.del_func_1000(after)
            V_time.delete(time)
            V_date.delete(date)
            Data.show.delete(Timer_l1)
            Music.slider.pop()
            Music.show_duration.widget.pop()
            self.mini_dict={}
            self.destroy("addiction")
            sip.delete(win_all)

        def play_command():
            com(comb)
            music_play()

        def move():
            if win.pos().x()==m.width()-30:
                win.move(m.width()-230,int(m.height()//2-50))
                win_all.move(m.width()-200,(m.height()-y)//2)
            else:
                win.move(m.width() - 30,int(m.height()//2-50))
                win_all.move(m.width(),(m.height()-y)//2)
        
        def click(a0:QtGui.QMouseEvent):
            clicked_label.add(win_all,a0.pos())
            a0.accept()

        def mouse(a0):
            a0.accept()

        def after():
            label_battery.setText(f"{psutil.sensors_battery().percent}%")
            scale_battery.setValue(psutil.sensors_battery().percent)
            label_memory.setText(f"{psutil.virtual_memory().percent:05.2f}%")
            scale_memory.setValue(int(psutil.virtual_memory().percent*100))
            cpu = sum(psutil.cpu_percent(interval=0.5,percpu=True))/psutil.cpu_count(False)
            label_cpu.setText(f"{cpu:05.2f}%")
            scale_cpu.setValue(int(cpu*100))
            for i in label_dict:
                try:
                    label_dict[i][0].setText(f"{psutil.disk_usage(i).percent:05.2f}%")
                    label_dict[i][1].setValue(int(psutil.disk_usage(i).percent*100))
                except:
                    ...
            if len(psutil.disk_partitions()) != len(label_dict):
                des()
                Page.addiction()

        def count():
            if Data.count:
                Data.count = False
                Data.ctime = -1
                Data.timer.stop()
                button_count.setIcon(QIcon(f"{path}icon\\播放.png"))
            else:
                Data.start()
                button_count.setIcon(QIcon(f"{path}\\icon\\暫停.png"))

        win = self.add_win("addiction",x=30,y=100)
        win.setStyleSheet(f"background:{color_bg};border:none;border-radius:50%;")
        win.mouseMoveEvent = mouse
        win.setGeometry(m.width()-30,int(m.height()//2-50),30,100)
        win.setWindowOpacity(0.7)
        win.setWindowFlags(types.FramelessWindowHint|types.WindowStaysOnTopHint|types.Sheet|types.Tool|types.SubWindow)
        win_all = WID(None,f"background:{color};",m.width(),0,200,m.height())
        win_all.setWindowOpacity(0.7)
        win_all.mouseMoveEvent = mouse
        win_all.mousePressEvent = click
        win_all.setWindowFlags(types.FramelessWindowHint|types.WindowStaysOnTopHint|types.Sheet|types.Tool|types.SubWindow)
        win_all.show()
        if Data.get("set")["cursor"]!="":
            win.setCursor(cursor)
            win_all.setCursor(cursor)
        Button(win,[0,10,30,30],move,text=" ").show()
        Button(win, [0,65,30,30], des, text="x").show()
        time = Label(win_all,[0, 0, 200, 30],text=V_time.get(),style="background-color:#00000000;color:#FFAEC9;font-family:Arial Rounded MT Bold;font-size:22pt;font-weight:bold;",)
        time.setAlignment(align.AlignCenter)
        V_time.add(time)
        date = Label(win_all,[0, 30, 200, 30],text=V_date.get(),style="background-color:#00000000;color:#FFAEC9;font-family:Arial;font-size:12pt;font-weight:bold;",)
        date.setAlignment(align.AlignCenter)
        V_date.add(date)
        comb = Combo(win_all, "Arial", 14, 8, True, geometry=[0, 60, 200, 30])
        comb.activated.connect(lambda:com(comb))
        slider_mini = Slider(win_all, 0, 90, 200, 10)
        slider_mini.setStyleSheet(widget["Slider-1"])
        slider_mini.actionTriggered.connect(lambda:Music.slider_change(slider_mini))
        slider_mini.setRange(0,int(slider.maximum()))
        slider_mini.show()
        Music.add_slider(slider_mini)
        l = Label(win_all,[0,100,70,15],text="00:00/00:00",style=f"color:{color_bg};")
        Music.show_duration.add(l)
        l.show()
        Button(win_all,[0,115, 15, 15],last,image=QIcon(f"{path}home\\last.png"),style="background:transparent;").show()
        play = Button(win_all, [15, 110, 25, 25], play_command, image=QIcon(f"{path}icon\\播放.png"),style="background:transparent;")
        Music.set_button("1", play)
        Button(win_all,[40, 110, 25, 25],lambda: Music.stop_list(),image=QIcon(f"{path}icon\\停止.png"),style="background:transparent;",).show()
        Button(win_all,[65, 115, 15, 15],next_music,image=QIcon(f"{path}home\\next.png"),style="background:transparent;").show()
        mode = Button(win_all,[130, 110, 25, 25],image=QIcon(f"{path}home\\{Music.mode}.png"),style="background:transparent;",)
        mode.command=lambda:set_play_mode(mode)
        Timer_Win = WID(win_all,"background:#00000000;",0,135,200,60)
        Timer_l1 = Label(Timer_Win, [0, 0, 200, 35], text=Data.show.get(), style=f"background-color:rgba({color_alpha[0]}, {color_alpha[1]}, {color_alpha[2]}, 0.78);font-family:Arial;font-size:26pt;font-weight:bold;color:#d48649")
        Timer_l1.setAlignment(align.AlignRight)
        Data.show.add(Timer_l1)
        Timer_l1.show()
        button_count = Button(Timer_Win,[70, 35, 25, 25],count,image=QIcon(f"{path}icon\\播放.png"),style="background:transparent;",)
        button_count.show()
        Button(Timer_Win,[105, 35, 25, 25],lambda: Data.set_win(),image=QIcon(f"{path}icon\\編輯.png"),style="background:transparent;",).show()
        Timer_Win.show()
        win_battery = WID(win_all,"background:#00000000;",0,195,200,120)
        co = ",".join(map(str, color_alpha))
        s = "color:%s;background:rgba("+co+",0.5);font-family:Arial;font-size:17pt;"
        progress_style = "QProgressBar {background: rgba("+co+",0.5);border: none;} QProgressBar::chunk {background: %s;}"
        Label(win_battery,[0,0,80,27],text="Battery",style=s%color2).show()
        label_battery = Label(win_battery,[80, 0, 100, 27],text="",style=s%color2)
        label_battery.setAlignment(align.AlignRight)
        label_battery.show()
        scale_battery = progressbar(win_battery,0,100,progress_style % color2,27)
        Label(win_battery,[0,30,60,27],text="RAM",style=s%color_bg).show()
        label_memory = Label(win_battery,[60, 30, 120, 27],text="",style=s%color_bg,)
        label_memory.setAlignment(align.AlignRight)
        label_memory.show()
        scale_memory = progressbar(win_battery,0,10000,progress_style % color_bg,57)
        Label(win_battery,[0,60,60,27],text="CPU",style=s % "#ff6cd1").show()
        label_cpu = Label(win_battery,[60, 60, 120, 27],text="",style=s % "#ff6cd1",)
        label_cpu.setAlignment(align.AlignRight)
        label_cpu.show()
        scale_cpu = progressbar(win_battery,0,10000,progress_style % "#ff6cd1",87)
        label_dict:dict[str,list[Label,QtWidgets.QProgressBar]] = {}
        h=90
        for i in psutil.disk_partitions():
            Label(win_battery, [0, h, 60, 27], text=f"{i.device}  ", style=s % "#6ae680").show()
            l = Label(win_battery,[60,h,120,27],text="",style=s % "#6ae680",)
            l.setAlignment(align.AlignRight)
            l.show()
            ps = progressbar(win_battery,0,10000,progress_style % "#6ae680",h+27)
            label_dict[i.device] = [l,ps]
            h+=30
        after()
        self.after = len(Timer.func_1000)
        Timer.add_func_1000(after)
        win_battery.adjustSize()
        win_battery.show()
        exec_list:list = Data.get("exe")
        win_exec = WID(win_all,"background:#00000000;",0,0,200,200)
        width=0
        height=0
        num=0
        for i in exec_list:
            but=self.But(win_exec,width,height,i["width"],i["height"],i["exec"],i["text"],i["icon"],num)
            max_x = max(but.width(),but.b.width())
            if max_x+width>=180:
                height+=but.b.height()+but.height()
                width=0
            else:
                width+=max_x-10
            num+=1
        WID_Todo(win_all,win_exec,"background:#00000000;border:none;",[0,215+win_battery.height(),200,300]).show()
        Button(win_all,[170,195+win_battery.height(),30,20],lambda:self.But.add(),text="add").show()
        y=215+win_battery.height()+300
        win_all.setGeometry(m.width(),(m.height()-y)//2,200,y)
        self.mini_dict = {"time":time,"date":date,"combo":comb, "mode":mode,"win":win_all}
        for i in [time,date,comb,play,mode]:
            i.show()
        win.show()


class TextEdit(QtWidgets.QTextEdit):
    def __init__(self, master, *geometry):
        super().__init__(master)
        self.setGeometry(*geometry)
        self.setStyleSheet(
            f"""
            QTextEdit{{{widget["PlainTextEdit"]}}}
            QScrollBar:vertical {{{widget["ScrollBar"]["vertical"]}}}
            QScrollBar:vertical:hover {{{widget["ScrollBar"]["vertical"]}}}
            QScrollBar::handle:vertical {{{widget["ScrollBar"]["handle"]}}}
            QScrollBar::add-page:vertical {{width: 10px;background: transparent;}}
            QScrollBar::sub-page:vertical {{width: 10px;background: transparent;}}
            QScrollBar::sub-line:vertical {{height: 12px;width: 10px;background: transparent;subcontrol-position: top;}}
            QScrollBar::add-line:vertical {{height: 12px;width: 10px;background: transparent;subcontrol-position: bottom;}}
        """
        )
        self.show()


class WST(TextEdit):
    def mousePressEvent(self, e: QtGui.QMouseEvent | None) -> None:
        super().mousePressEvent(e)
        clicked_label.add(self,e.pos())
        self.parentWidget().raise_()
        e.accept()


class TEXT(QtWidgets.QTextEdit):
    def __init__(self, parent: QtWidgets.QWidget, geometry: list[int, int, int, int]):
        super().__init__(parent)
        self.setGeometry(*geometry)
        self.setStyleSheet(f"background-color:{color};color:#fc8289;font-family:Arial;font-size:17pt;font-weight:bold;")
    def mousePressEvent(self, e: QtGui.QMouseEvent | None):
        super().mousePressEvent(e)
        clicked_label.add(self,e.pos())
        self.parentWidget().raise_()
        e.accept()

    def setting(self, obj):
        def on_roll():
            self.rol.setValue(self.sc.value())
        def on_scroll():
            self.sc.setValue(self.rol.value())

        if type(obj) is TEXT:
            self.obj = obj
            self.sc = obj.verticalScrollBar()
            self.rol = self.verticalScrollBar()
            obj.rol.valueChanged.connect(on_roll)
            self.rol.valueChanged.connect(on_scroll)
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)


class WriteIt(WST):
    def __init__(self, master, write2: QtWidgets.QListWidget, *geometry):
        super().__init__(master, *geometry)
        self.WST = write2
        self.put = Valuable("")
        self.cursorPositionChanged.connect(lambda: self.show_line())
        self.setStyleSheet(
            f"""
            QTextEdit{{{widget["PlainTextEdit"]}}}
            QScrollBar:vertical {{{widget["ScrollBar"]["vertical"]}}}
            QScrollBar:vertical:hover {{{widget["ScrollBar"]["vertical"]}}}
            QScrollBar::handle:vertical {{{widget["ScrollBar"]["handle"]}}}
            QScrollBar::add-page:vertical {{width: 10px;background: rgba(255, 164, 164, 0.76);}}
            QScrollBar::sub-page:vertical {{width: 10px;background: rgba(255, 164, 164, 0.76);}}
            QScrollBar::sub-line:vertical {{height: 12px;width: 10px;background: transparent;subcontrol-position: top;}}
            QScrollBar::add-line:vertical {{height: 12px;width: 10px;background: transparent;subcontrol-position: bottom;}}
        """
        )

    def save_file(self):
        with open(Data.get("set")["DictTxt"], "w+", encoding="UTF-8") as o:
            o.write(self.toPlainText())

    def clean(self):
        self.clear()
        if len(self.toPlainText()) > 1:
            self.save_file()
        self.WST.clear()
        self.setPlainText(self.Open())

    def moved(self):
        if len(self.WST.selectedItems()) > 0:
            m = int(self.WST.selectedItems()[0].text())
            var = len("\n".join(self.Open().split("\n")[:m])) * 1.89
            self.verticalScrollBar().setValue(int(var))

    def show_line(self):
        self.put.set(f"第{self.textCursor().blockNumber()}行")

    def Open(self, mode="r"):
        with open(Data.get("set")["DictTxt"], mode, encoding="UTF-8") as o:
            m = o.read()
        return m


def double_clicked():
    clicked_label.add(Song_Win,Song_Win.mapFromGlobal(QtGui.QCursor.pos()))
    d = Data.load()
    if combo.currentText() in d["music"] and listbox.currentItem()!=None and Music.play_already == 2:
        Music.stop()
        d["music"][combo.currentText()]["Number"] = listbox.currentRow()
        Data.write(d)
        Music.play_list_start()


def show_todo():
    todo = Data.get("Todo")
    text = ""
    li = list(filter(lambda x: todo[x]["date"] == calendar.selectedDate().toString("yyyy-MM-dd") and todo[x]["type"] in [1,3],todo,))
    if len(li) > 0:
        text = "\n".join(map(lambda x:f'{todo[x]["time"]} {x}',sorted(li,key=lambda x:todo[x]["time"])))
    else:
        text = "無"
    text_home.setPlainText(text)


def music_play():
    if Music.states == "stop":
        if len(listbox.selectedIndexes()) == 1:
            h = Data.load()
            h["music"][combo.currentText()]["Number"] = listbox.selectedIndexes()[0].row()
            Data.write(h)
        Music.play_list_start()
    elif Music.states == "play":
        Music.pause_list()
    else:
        Music.unpause_list()


def add_music():
    if combo.currentText() in Data.get("music") and (c := QtWidgets.QInputDialog.getItem(main_window, "add", "您要加入什麼音樂?", Music.music_list, 0))[1]:
        h = Data.load()
        if listbox.currentItem():
            n = listbox.currentRow()
            h["music"][combo.currentText()]["list"][n : n + 1] = [listbox.currentItem().text(),c[0],]
        elif listbox.count()==0:
            n=0
            h["music"][combo.currentText()]["list"][0] = c[0]
        Data.write(h)
        listbox.insertItem(n + 1, c[0])


def edit_func(text: str):
    listbox.clear()
    li = Data.get("music")[text]
    listbox.addItems(li["list"])
    if len(li["list"]) > li["Number"]:
        listbox.setCurrentRow(li["Number"])


def add_list():
    h = Data.load()
    if (m := Data.AskStr("新增播放清單 名稱為："))[1] and m not in h["music"]:
        h["music"][m[0]] = {"Number": 0, "list": []}
        Data.write(h)
        combo.clear()
        combo.addItems(list(h.get("music").keys()))


def delete_list():
    h = Data.load()
    if combo.currentText() in h["music"]and MessageBox.question(main_window, "today's homework!!!", f"你確定要刪除這個播放清單嗎?\n{combo.currentText()}")< 50000:
        del h["music"][combo.currentText()]
        Data.write(h)
        key = h.get("music").keys()
        combo.clear()
        combo.addItems(list(key))


def edit():
    def add_func():
        h = Data.load()
        if combobox.currentText() in Music.music_list:
            h["music"][combo.currentText()]["list"][i] = combobox.currentText()
        Data.write(h)
        ma.deleteLater()
        edit_func(combo.currentText())
    
    def del_func():
        h = Data.load()
        del h["music"][combo.currentText()]["list"][i]
        Data.write(h)
        ma.deleteLater()
        edit_func(combo.currentText())
    
    i = 0
    if listbox.currentItem():
        i = listbox.currentRow()
        ma = WID(None,"",m.width()//2,m.height()//2,200,60)
        ma.setWindowTitle("edit")
        Label(ma,[0,0,200,60],style=f"background:{color2};").show()
        combobox = Combobox(ma,"",Music.music_list,[0,0,200,30])
        combobox.setCurrentText(listbox.currentItem().text())
        combobox.show()
        Button(ma,[0,30,40,30],add_func,text="check").show()
        Button(ma,[40,30,40,30],del_func,text="delete").show()
        ma.show()


def set_play_mode(_mode:Button):
    Music.mode = modes[(modes.index(Music.mode)+1)%3]
    icon=QIcon(f"{path}home\\{Music.mode}.png")
    _mode.setIcon(icon)
    if "addiction" in Page.page:
        if _mode is mode:
            Page.mini_dict["mode"].setIcon(icon)
        else:
            mode.setIcon(icon)


def last():
    if combo.currentText() == Music.playlist:
        r = listbox.currentRow() if Music.states =="stop" and listbox.currentItem() else Music.play_num
        r = r - 2 if r > 0 else len(Data.get("music")[combo.currentText()]["list"])-2
        if Music.play_already == 2:
            Music.play_num = r if Music.mode != "one_infinite" else r+1
            Music.media.stop()
            Music.play_list()
        else:
            Music.stop_list()
            if listbox.count() > r+1:
                listbox.setCurrentRow(r+1)
            elif listbox.count() > 0:
                listbox.setCurrentRow(0)


def next_music():
    if combo.currentText() == Music.playlist:
        r = listbox.currentRow() if Music.states =="stop" and listbox.currentItem() else Music.play_num
        if Music.play_already == 2:
            Music.media.stop()
            Music.play_num = r  if Music.mode != "one_infinite" else r+1
            Music.play_list()
        else:
            Music.stop_list()
            if listbox.count() > r+1:
                listbox.setCurrentRow(r+1)
            elif listbox.count() > 0:
                listbox.setCurrentRow(0)


class ClickedLabel():
    __slots__ = ["lists","timer"]
    def __init__(self):
        self.lists:list[list] = []
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(lambda:self.exec_animation())
        self.timer.start(50)
    def add(self,parent:QtWidgets.QWidget,a0:QtCore.QPoint):
        label = Label(parent,[a0.x(),a0.y(),0,0],image=p.scaled(0,0),style="background:transparent;")
        opacity = QtWidgets.QGraphicsOpacityEffect()
        opacity.setOpacity(1.0)
        label.setGraphicsEffect(opacity)
        label.show()
        self.lists.append([label,opacity,a0,0])
    def anima(self,label:Label,opacity:QtWidgets.QGraphicsOpacityEffect,a0:QtCore.QPoint,num:int, number:int):
        num+=10
        self.lists[number][3] = num
        if num < 40:
            n=int(num/2)
            label.setGeometry(a0.x()-n,a0.y()-n,num,num)
            label.setPixmap(p.scaled(num,num))
        elif num ==40:
            opacity.setOpacity(0.5)
        else:
            sip.delete(label)
            self.lists.pop(number)
    def exec_animation(self):
        list(map(lambda x:self.lists.pop(self.lists.index(x)),filter(lambda x:sip.isdeleted(x[0]),self.lists)))
        list(map(lambda x:self.anima(*x,self.lists.index(x)),self.lists))


def com(_combo:Combo):
    edit_func(_combo.currentText())
    if "addiction" in Page.page:
        if _combo is combo:
            Page.mini_dict["combo"].setCurrentText(combo.currentText())
        else:
            combo.setCurrentText(_combo.currentText())


modes=["all_once","all_infinite","one_infinite"]
app = QtWidgets.QApplication(sys.argv)
app.setWindowIcon(QIcon(r".\init_file\music.ico"))
Data = Interaction(path + "homework.json")
Page = Page_Organize()
Timer = Timers()
clicked_label = ClickedLabel()
Music = MusicPlayer()
V_date = Valuable("")
V_time = Valuable("")
V_play = Valuable()
V_state = Valuable(bool(Data.get("set")["dark"]))
p = QPixmap(f"{path}clicked.png")
widget = Data.get("style")[int(V_state.get())]
colors = Data.get("color")[int(V_state.get())]
color_alpha = list(colors["none"])
color = f"rgb({', '.join(map(str,color_alpha))})"
color_alpha2 = list(colors["normal"])
color2 = f"rgb({','.join(map(str,color_alpha2))})"
color_bg = colors["bg"]
m = app.screens()[0].size()
main_window = QtWidgets.QMainWindow()
main_window.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
main_window.setWindowTitle("Start")
main_window.setWindowFlags(types.FramelessWindowHint|types.WindowStaysOnBottomHint|types.MaximizeUsingFullscreenGeometryHint)
main_window.showMaximized()
main_window.mousePressEvent = lambda a0:clicked_label.add(main_window,a0.pos())
if Data.get("set")["cursor"]!="":
    pixmap = QPixmap(Data.get("set")["cursor"])
    pixmap = pixmap.scaled(30, 30)
    cursor = QtGui.QCursor(pixmap,0,0)
    main_window.setCursor(cursor)
background_path:str = Data.get("set")["Background"]
bg_path = background_path
if os.path.isdir(background_path) and len(list_bg := os.listdir(background_path))>0:
    bg_path +="/"+list_bg[random.randint(0,len(list_bg)-1)]
img0 = Image.open(bg_path)
q_image0 = ImageQt.toqimage(img0)
q_image1 = ImageQt.toqimage(img0.filter(ImageFilter.GaussianBlur(20)))
i = QPixmap(img0.width, img0.height).fromImage(q_image0)
i0 = QPixmap(img0.width, img0.height).fromImage(q_image1).scaled(m.width(), m.height() * (i.width() // i.height())).copy(0, 0, 250, m.height())
bg = Label(main_window, [0, 0, m.width(), m.height()], image=i.scaled(m.width(), m.height() * (i.width() // i.height())))
bg.show()
l0 = Label(main_window, [0, 0, 250, m.height()], image=i0)
style0 = "font-family:Arial;color:#FFAEC9;background-color: transparent;"
WLtime = Label(main_window, [0, 0, 250, 40], style=style0 + "font-size:42pt;", text="")
V_time.add(WLtime)
WLtime.setAlignment(align.AlignCenter)
WLdate = Label(main_window,[0, 43, 250, 20],text=" ",style=style0 + "text-decoration:underline; font-size:15pt;",)
V_date.add(WLdate)
WLdate.setAlignment(align.AlignCenter)
g1 = NoTitleWidget(main_window,"page",270,50)
Label(g1,[2,15,6,20],style=f"background:{color2};",text=" ")
Label(g1,[0,0,270,50],style=f"background:rgba({', '.join(map(str,color_alpha))}, 0.6);border-radius:25px;")
button_style=f"QPushButton {{background:{color};color:{color_bg};border-radius:5px;border:1px solid {color_bg};}} QPushButton:hover {{color:{color_bg};background:rgba({color_alpha[0]}, {color_alpha[1]}, {color_alpha[2]}, 0.4);}}"
Button(g1,[10, 0, 50, 50],lambda: Page.todo(),image=QIcon(f"{path}icon\\todo.png"),style="background:transparent;").show()
Button(g1,[60, 0, 50, 50],lambda: Page.dic(),image=QIcon(f"{path}icon\\dict.png"),style="background:transparent;").show()
Button(g1,[110, 0, 50, 50],lambda: Page.learn(),image=QIcon(f"{path}icon\\learn.png"),style="background:transparent;").show()
Button(g1,[160, 0, 50, 50],lambda: Page.classes(),image=QIcon(f"{path}icon\\class.png"),style="background:transparent;border-radius:25px;").show()
Button(g1,[210, 10, 30, 30],lambda: Page.set(),image=QIcon(f"{path}icon\\set.png"),style=style0,).show()
Button(g1,[240, 10, 30, 30],lambda: Page.addiction(),text="⿻",style="font-family:Arial;color:#d48649;background-color: transparent;font-size:29px;",).show()
Button(main_window, [m.width() - 42, 0, 20, 20], main_window.showMinimized, text="-").show()
Button(main_window, [m.width() - 20, 0, 20, 20], destroy, text="x").show()
Todo_Win = NoTitleWidget(main_window, "todo", 250, 290)
Todo_Win.setStyleSheet("background:transparent;")
calendar = QtWidgets.QCalendarWidget(Todo_Win)
calendar.setVerticalHeaderFormat(calendar.VerticalHeaderFormat.NoVerticalHeader)
calendar.setHorizontalHeaderFormat(calendar.HorizontalHeaderFormat.NoHorizontalHeader)
calendar.clicked.connect(show_todo)
calendar.setGeometry(0, 0, 250, 200)
calendar.setStyleSheet(
    f"""
    QCalendarWidget QWidget {{
        background:transparent;
    }}
    QCalendarWidget QAbstractItemView {{
        color:{color2};
        background-color:{color};
        selection-background-color:{color2};
        selection-color:{color};
    }}
    QCalendarWidget QToolButton {{
        font-family:Arial Rounded MT Bold;
        font-weight:bold;
        color:#ffffff;background:transparent;
    }}
"""
)
op0 = QtWidgets.QGraphicsOpacityEffect()
op0.setOpacity(0.53)
calendar.setGraphicsEffect(op0)
text_home = WST(Todo_Win, 0, 200, 250, 90)
text_home.setStyleSheet(
    f"""
    QTextEdit{{{widget["PlainTextEdit"]}}}
    QScrollBar:vertical {{{widget["ScrollBar"]["vertical"]}}}
    QScrollBar:vertical:hover {{{widget["ScrollBar"]["vertical"]}}}
    QScrollBar::handle:vertical {{{widget["ScrollBar"]["handle"]}}}
    QScrollBar::add-page:vertical {{width: 10px;background: transparent;}}
    QScrollBar::sub-page:vertical {{width: 10px;background: transparent;}}
    QScrollBar::sub-line:vertical {{height: 12px;width: 10px;background: transparent;subcontrol-position: top;}}
    QScrollBar::add-line:vertical {{height: 12px;width: 10px;background: transparent;subcontrol-position: bottom;}}
"""
)
text_home.setReadOnly(True)
show_todo()
Song_Win = NoTitleWidget(main_window, "song", 250, 330)
combo = Combo(Song_Win, "Arial", 15, 8, False, geometry=[0, 0, 100, 30])
combo.textActivated.connect(lambda:com(combo))
song_home = Label(Song_Win, [10, 30, 250, 30], text=Music.song.get(), style=style0 + "font-size:12pt;")
Music.song.add(song_home)
Button(Song_Win,[70, 65, 15, 15],last,image=QIcon(f"{path}home\\last.png"),style="background:transparent;").show()
button_play = Button(Song_Win,[100, 60, 25, 25],music_play,image=QIcon(f"{path}icon\\播放.png"),style="background:transparent;",)
button_play.show()
Music.set_button("music", button_play)
background = f"rgba({color_alpha[0]}, {color_alpha[1]}, {color_alpha[2]},0.46)"
Button(Song_Win,[125, 60, 25, 25],lambda: Music.stop_list(),image=QIcon(f"{path}icon\\停止.png"),style="background:transparent;",).show()
Button(Song_Win,[165, 65, 15, 15],next_music,image=QIcon(f"{path}home\\next.png"),style="background-color:transparent;").show()
mode = Button(Song_Win,[225, 60, 25, 25],image=QIcon(f"{path}home\\{Music.mode}.png"),style="background-color:transparent;",)
mode.command=lambda:set_play_mode(mode)
mode.show()
slider = Slider(Song_Win, 5, 85, 240, 20)
slider.actionTriggered.connect(lambda:Music.slider_change(slider))
Music.add_slider(slider)
l = Label(Song_Win,[0,105,70,25],text="00:00/00:00",style="color:#ffffff;")
Music.show_duration.add(l)
l.show()
Button(Song_Win,[150, 105, 25, 25],edit,image=QIcon(f"{path}icon\\編輯.png"),style="background:transparent;",).show()
Button(Song_Win,[175, 105, 25, 25],add_music,image=QIcon(f"{path}icon\\加入.png"),style="background:transparent;",).show()
Button(Song_Win,[200, 105, 25, 25],delete_list,text="刪除\n清單",style="background:transparent;color:#AA5F39;font-family:Arial;font-size:8pt;").show()
Button(Song_Win,[225, 105, 25, 25],add_list,text="加入\n清單",style="background:transparent;color:#AA5F39;font-family:Arial;font-size:8pt;").show()
listbox = QtWidgets.QListWidget(Song_Win)
listbox.setGeometry(0, 130, 250, 200)
listbox.setSelectionMode(listbox.SelectionMode.SingleSelection)
listbox.setStyleSheet(f"""
    QListWidget {{background:{background};color:#d66b70;font-family:Arial;font-size:15pt;font-weight:bold;}}
    QScrollBar:vertical {{{widget["ScrollBar"]["vertical"]}}}
    QScrollBar:vertical:hover {{{widget["ScrollBar"]["vertical"]}}}
    QScrollBar::handle:vertical {{{widget["ScrollBar"]["handle"]}}}
    QScrollBar::add-page:vertical {{width: 10px;background: transparent;}}
    QScrollBar::sub-page:vertical {{width: 10px;background: transparent;}}
    QScrollBar::sub-line:vertical {{height: 12px;width: 10px;background: transparent;subcontrol-position: top;}}
    QScrollBar::add-line:vertical {{height: 12px;width: 10px;background: transparent;subcontrol-position: bottom;}}
    QScrollBar:horizontal {{{widget["ScrollBar"]["vertical"]}}}
    QScrollBar:horizontal:hover {{{widget["ScrollBar"]["vertical"]}}}
    QScrollBar::handle:horizontal {{{widget["ScrollBar"]["handle"]}}}
    QScrollBar::add-page:horizontal {{width: 10px;background: transparent;}}
    QScrollBar::sub-page:horizontal {{width: 10px;background: transparent;}}
    QScrollBar::sub-line:horizontal {{height: 12px;width: 10px;background: transparent;subcontrol-position: left;}}
    QScrollBar::add-line:horizontal {{height: 12px;width: 10px;background: transparent;subcontrol-position: right;}}
""")
listbox.itemDoubleClicked.connect(double_clicked)
com(combo)
listbox.show()
for i in [bg,l0,WLtime,WLdate,g1,Todo_Win,text_home,Song_Win,combo,song_home,slider,calendar,]:
    i.show()
clock()
Timer.add_func_500(clock)
sys.exit(app.exec())
