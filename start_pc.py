from PyQt6 import QtWidgets,QtCore, QtGui, sip, QtWebEngineWidgets
from PyQt6.QtGui import QPixmap, QIcon, QMouseEvent
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from windows_toasts import WindowsToaster, Toast, ToastDisplayImage, ToastImage, ToastImagePosition
from mutagen.mp3 import MP3
import sys, psutil, json, os, random,webbrowser,requests
from typing import Literal,Self
from datetime import datetime,timedelta,date
from PIL import Image, ImageQt

path = os.getcwd() + "\\init_file\\"
__stderr__ = open(f"{path}start_log.txt", "a")
sys.stderr = __stderr__
page_type = Literal["todo", "dic", "learn", "class", "set","addiction","exe"]
data_type = Literal["Todo", "Class", "music", "learn", "set", "window", "page", "color", "style","exe", "date","bookmark"]
align = Qt.AlignmentFlag
types = Qt.WindowType
MessageBox = QtWidgets.QMessageBox
FileDialog = QtWidgets.QFileDialog
Attribute = Qt.WidgetAttribute


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
            widget.show()

    def delete(self, widget: QtWidgets.QLabel | QtWidgets.QPushButton):
        del self.widget[self.widget.index(widget)]


def destroy():
    main_window.destroy(True, True)
    sip.delete(main_window)


def destroyed():
    data.set.update({"PlayMode":Music.mode,"dark": V_state.get(),"ClockVolume": Page.ClockVolume,"ClockRate": Page.ClockRate,"MusicVolume": Page.MusicVolume,"MusicRate": Page.MusicRate,"BackgroundBlur": Page.BackgroundBlur})
    data.write_all()
    Music.stop_list()
    m = list(Page.page.keys())[0:]
    for i in m:
        Page.destroy_page(i)
    sys.exit()


def weather():
    url = data.set["WeatherUrl"]
    try:
        data_str = requests.get(url)
        data_json:dict = data_str.json()
        location = data_json["records"]["location"]
        key = list(filter(lambda x:x["locationName"]==data.set["location"],location))
        if len(key)>0:
            Position.setText(data.set["location"])
            key = key[0]["weatherElement"]
            for time in range(0,3):
                dic = weather_dict[time]
                min_temperature8 = key[2]["time"][time]["parameter"]["parameterName"]
                max_temperature8 = key[4]["time"][time]["parameter"]["parameterName"]
                dic[0].setText(key[0]["time"][time]["parameter"]["parameterName"])
                dic[1].setText(f"{min_temperature8}~{max_temperature8}℃")
                dic[2].setText(f"{key[1]['time'][time]['parameter']['parameterName']}%")
        else:
            Position.setText("Error")
    except:
        inter.notifier("Error",["請開啟 wi-fi並確認網址無誤","網址如下："+url])

def clock():
    
    def make_ring(name: str):
        nonlocal messages
        prompts = str(date[name]["prompt"]).split("\n")
        if prompts==[""]:
            messages+=[name]
        else:
            prompts = list(map(lambda prompt:"  "+prompt,prompts[:3]))
            messages+=[name+":",*prompts]

    def make_message(name:str):
        nonlocal messages
        prompts = str(ans[name]["prompt"]).split("\n")
        if prompts==[""]:
            messages+=[name]
        else:
            prompts = list(map(lambda prompt:"  "+prompt,prompts[:3]))
            messages+=[name+":",*prompts]
    
    def make_time_dicts(name:str):
        data = ans[name]
        if data["date"] == "Next":
            return V_time.get() == data["time"] and data["type"]<2
        else:
            return f"{data['date']} {data['time']}" == ds and data["type"]<2
    
    ans = data.Todo
    date = data.date
    di = datetime.now()
    ds = di.strftime("%Y-%m-%d %H:%M:%S")
    V_date.set(di.strftime("%a  %b  %d    %Y"))
    V_time.set(di.strftime("%H:%M:%S"))
    time_dicts = list(filter(lambda name:make_time_dicts(name), ans.keys()))
    event_dicts = list(filter(lambda name:ds in date[name]["rings"], date.keys()))
    if di.hour%8==di.minute==di.second==0:
        weather()
    if len(time_dicts)>0 or len(event_dicts)>0:
        if Music.media.isPlaying():
            if Music.playlist:
                Music.stop_list()
            else:
                Music.stop()
        Music.play(data.set["ClockMusic"])
        if len(event_dicts)+len(time_dicts)==1:
            if event_dicts:
                inter.notifier(event_dicts[0], date[event_dicts[0]]["prompt"].split("\n")[:3])
            else:
                inter.notifier(time_dicts[0], ans[time_dicts[0]]["prompt"].split("\n")[:3])
        else:
            messages = []
            list(map(lambda name:make_ring(name),event_dicts))
            list(map(lambda name:make_message(name),time_dicts))
            inter.notifier("Multiple Task",messages)
    elif V_play.get() == -1 and not Music.media.isPlaying():
        V_play.set(0)


class Label(QtWidgets.QLabel):
    def __init__(self, master, geometry, text:str|None=None, image: QPixmap|None=None,style: str|None=None):
        super().__init__(master)
        if text!=None:
            self.setText(text)
        elif image!=None:
            self.setPixmap(image)
        if style != None:
            self.setStyleSheet(style)
        if geometry == "adjust":
            self.adjustSize()
        else:
            self.setGeometry(*geometry)


class Button(QtWidgets.QPushButton):
    def __init__(self, master, geometry=[], left_command=None, text:str|None=None, image: QIcon|None=None, style:str|None=None,):
        """
        ::geometry: x, y, w, h
        """
        super().__init__(master)
        if text!=None:
            self.setText(text)
        elif image!=None:
            self.setIconSize(QtCore.QSize(*geometry[2:]))
            self.setIcon(image)
        self.setStyleSheet(style if style != None else button_style)
        self.LeftCommand=left_command
        self.RightCommand=None
        self.setGeometry(*geometry)
    def mousePressEvent(self,a0:QMouseEvent):
        if self.LeftCommand != None and (a0.button() is Qt.MouseButton.LeftButton or self.RightCommand is None):
            self.LeftCommand()
        elif not self.RightCommand is None and a0.button() is Qt.MouseButton.RightButton:
            self.RightCommand()
        if not sip.isdeleted(self):
            clicked_label.add(self.parentWidget(),a0.pos()+self.pos(),self)
        a0.accept()


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
    def update_items(self,values:list[str]):
        self.clear()
        self.addItems(values)


class Combo(Combobox):
    def __init__(self,master,font_family,font_size: int,item_font_size: int,bold=False,bg="transparent",geometry=[],):
        super().__init__(master,f"QComboBox{{background-color:{bg};color:#fc8289;}}",[],geometry,[font_family,font_size,bold,item_font_size])
        self.ItemView = QtWidgets.QListWidget()
        self.ItemView.setStyleSheet(f"background-color:{color};color:#fc8289;font-family:{font_family};font-size:{item_font_size}pt;")
        self.setView(self.ItemView)
        self.setModel(self.ItemView.model())
        self.update_items(list(data.music.keys()))
        self.setCurrentText(list(data.music.keys())[0])
        if len(geometry) == 4:
            self.setGeometry(*geometry)
        if Music.playlist in list(data.music.keys()):
            self.setCurrentText(Music.playlist)


class Entry(QtWidgets.QLineEdit):
    def __init__(self, parent: QtWidgets.QWidget | None, style="", geometry=[0, 0, 0, 0], text=""):
        super().__init__(text, parent)
        self.setStyleSheet(style)
        self.setGeometry(*geometry)


class CalendarWidget(QtWidgets.QCalendarWidget):
    def __init__(self,master,geometry,connect,style,visible=True,grid_visible=False):
        super().__init__(master)
        self.setGeometry(*geometry)
        self.setVerticalHeaderFormat(self.VerticalHeaderFormat.NoVerticalHeader)
        self.setHorizontalHeaderFormat(self.HorizontalHeaderFormat.NoHorizontalHeader)
        self.clicked.connect(connect)
        self.setStyleSheet(style)
        self.setVisible(visible)
        self.setGridVisible(grid_visible)


def progressbar(parent: QtWidgets.QWidget | None, min=0,max=1,stylesheet="",y=0,):
    pb = QtWidgets.QProgressBar(parent)
    pb.setRange(min,max)
    pb.setStyleSheet(stylesheet)
    pb.setGeometry(0,y,180,3)
    pb.show()
    return pb


class TodoData(object):
    __slots__ = ["date", "time", "prompt", "type","win"]
    def __init__(self, date: str, time: str, prompt: str, type:Literal[0,1,2,3]):
        if date == "Next":
            dn = datetime.now()
            self.date = [dn.year,dn.month,dn.day]
        else:
            self.date = list(map(int, date.split("-")))
        self.time = list(map(int, time.split(":")))
        self.prompt = prompt
        self.type:Literal[0,1,2,3] = type
        self.win=None
    def get_date(self) -> str:
        return "{0[0]:02d}-{0[1]:02d}-{0[2]:02d}".format(self.date)
    def get_time(self) -> str:
        return "{0[0]:02d}:{0[1]:02d}:{0[2]:02d}".format(self.time)
    def hover(self,x:int,y:int) -> None:
        l=Label(Page.page["todo"],[0,0,300,300],self.prompt,style=f"color:{color_bg};background:{color};")
        l.adjustSize()
        l.show()
        l.setGeometry(x-l.width(),y-l.height(),l.width(),l.height())
        self.win = l


class Choose(QtWidgets.QCheckBox):
    el = ["每日循環", "一次", "已解決", "停用"]
    
    def __init__(self, mas:QtWidgets.QWidget, text: str, todo_data: TodoData, y:int, visible=True,wid_todo:QtWidgets.QScrollArea|None=None):
        super().__init__(text,mas)
        self.mas = wid_todo
        self.setStyleSheet(f"QCheckBox {{background:#dd7aff;color:{color};font-family:Arial;font-size:20pt;border-radius:10px;}}QCheckBox:disabled {{background:{'#d48649'if todo_data.type == 0 else'#088fb7'};color:{color2};border-radius:10px;}}")
        self.move(0,y)
        self.num_list = list(map(str, range(0, 60)))
        self.Data = todo_data
        self.No_Change = True
        self.win_count = False
        self.Time = todo_data.date+todo_data.time
        self.adjustSize()
        self.b1=Button(mas,[self.width(), y+8, 70, 20],lambda: self.scream_choose(),text=self.Data.get_time(),style=f"background:transparent;color:#dd7aff;font-family:Arial;font-size:12pt;text-align:right;",)
        self.b2=Button(mas,[self.b1.x()+self.b1.width(), y+5, 11, 19],lambda:self.prompt_show(),"*",style="color:#7bc3c4;font-family:Arial;font-size:20pt;font-weight:bold;background:transparent;",)
        self.setVisible(visible)
        self.b1.setVisible(visible)
        self.b2.setVisible(visible and len(todo_data.prompt)>0)
        if visible:
            self.setChecked(todo_data.type != 1)
            self.setDisabled(todo_data.type in [0,3])
            self.clicked.connect(lambda: self.Check())
    
    def prompt_show(self):
        if self.Data.win is None or sip.isdeleted(self.Data.win):
            p0 = self.mas
            p1 = self.b2
            self.Data.hover(p0.x()+p1.x(),p0.y()+p1.y())
        else:
            sip.delete(self.Data.win)

    def Check(self):
        data.Todo[self.text()]["type"] = int(self.isChecked()) + 1
        data.write("Todo")
        if calendar.selectedDate().toString("yyyy-MM-dd") == self.Data.get_date():
            show_todo()

    def scream_choose(self, Type: Literal["change", "add"] = "change"):
        
        def Clock():
            if "todo" in Page.page and not sip.isdeleted(self) and not sip.isdeleted(b0):
                b0.setText(Events.clock(self.datetime))
            else:
                del_func_1000(f"Choose Clock:{id(self)}")
            
        def clock_top_window():
            t0 = WID(None, f"background-color:{colors['normal-bg']};", 0, 0, 300, 50)
            t0.setWindowFlag(types.SubWindow,True)
            t0.setWindowOpacity(0.5)
            t0.clockTopWin(b0.text(), self.Time, self.text())
        
        def rel():
            p = Page.cal.selectedDate()
            c = calendar.selectedDate()
            if 0<=(p.toPyDate()-c.toPyDate()).days <7:
                show_todo()
            cancel()
            Page.destroy_page("todo")
            Page.todo(p)

        def button_choose():
            e = self.el.index(e4.currentText())
            if Type == "change" and e1.text() != self.text():
                del data.Todo[self.text()]
            data.Todo[e1.text()] = {"date": t1.date().toString("yyyy-MM-dd") if e != 0 else "Next","time": t1.time().toString("hh:mm:ss"),"prompt": e3.toPlainText(),"type": e,}
            data.write("Todo")
            rel()

        def delete():
            del data.Todo[self.text()]
            data.write("Todo")
            rel()

        def cancel():
            self.No_Change = True
            del_func_1000(f"Choose Clock:{id(self)}")
            sip.delete(ma)
            sip.delete(t1c)
        
        def calendar_show():
            t=data.page["todo"]
            t1c.setGeometry(t[0],t[1]+90,260,200)
            if t1c.isVisible():
                t1.setDate(t1c.selectedDate())
            t1c.setVisible(not t1c.isVisible())
        
        def calendar_selected():
            t1.setDate(t1c.selectedDate())
            t1c.setVisible(False)

        if self.No_Change:
            self.datetime = datetime(*self.Time)
            self.No_Change = False
            color_bg_0 = f"rgba({color_alpha[0]},{color_alpha[1]},{color_alpha[2]},0.8)"
            page_todo = data.page["todo"]
            ma = WID(None,f"background:{color_bg_0};",*page_todo,300,250)
            ma.setWindowFlags(types.SubWindow)
            ma.setWindowTitle(Type if Type == "add" else f"{Type}:{self.text()}")
            e1 = Entry(ma,f"font-family:Arial;font-size:17pt;background:transparent;color:{color2};",[0, 0, 300, 30],self.text(),)
            t1 = QtWidgets.QDateTimeEdit(ma)
            t1.setStyleSheet(f"font-family:Arial;font-size:16pt;color:{color2};background:{color};")
            t1.setCalendarPopup(False)
            t1.setDisplayFormat("yyyy/MM/dd hh:mm:ss")
            t1.setGeometry(0, 30, 240, 30)
            t1.show()
            t1c = CalendarWidget(None,[page_todo[0],page_todo[1]+90,260,200],calendar_selected,calendar_style1,False)
            t1c.setWindowFlag(types.FramelessWindowHint,True)
            Button(ma,[240,30,20,30],calendar_show,text="d").show()
            Button(ma,[260,30,20,30],lambda:inter.time_show(t1),text="t").show()
            e4 = Combobox(
                ma,
                f"background:{color};color:{color2};font-family:Arial;font-size:17pt;",
                self.el,
                [0, 60, 400, 30],
            )
            e4.show()
            e3 = TextEdit(ma, 0, 90, 300, 90)
            e3.show()
            t1.setDateTime(datetime(*self.Time))
            t1c.setSelectedDate(t1.date())
            e3.insertPlainText(self.Data.prompt)
            e4.setCurrentIndex(self.Data.type)
            if Type == "change":
                Button(ma,[0, 180, 40, 30],button_choose,text="ok",).show()
                Button(ma, [40, 180, 60, 30], delete, text="delete").show()
                Button(ma, [100, 180, 50, 30], cancel, text="cancel").show()
            else:
                Button(ma,[0, 180, 40, 30],button_choose,text="add",).show()
                Button(ma, [40, 180, 50, 30], cancel, text="cancel").show()
            b0 = Button(ma,[200,180,50, 30],clock_top_window,text="1 00:00:00",style=f"background:transparent;color:#dd7aff;font-family:Arial;font-size:12pt;",)
            b0.adjustSize()
            Clock()
            add_func_1000(f"Choose Clock:{id(self)}", Clock)
            ma.show()


class Events():
    __slots__ = ["text","start_date","start_time","start_dt", "end_date", "end_time","end_dt", "prompt","rings"]
    def __init__(self, text: str, start_date:str, start_time:str, end_date:str, end_time:str, prompt:str,rings:list[str]):
        self.text=text
        self.start_date = start_date
        self.start_time = start_time
        self.end_date = end_date
        self.end_time = end_time
        self.start_dt = datetime.strptime(start_date+" "+start_time,"%Y-%m-%d %H:%M:%S")
        self.end_dt = datetime.strptime(end_date+" "+end_time,"%Y-%m-%d %H:%M:%S")
        self.prompt = prompt
        self.rings = rings
    @staticmethod
    def get_in_datetime(start_date:str,date:date, end_date:str):
        start_dt = datetime.strptime(start_date,"%Y-%m-%d").date()
        end_dt = datetime.strptime(end_date,"%Y-%m-%d").date()
        return start_dt<=date<=end_dt
    @staticmethod
    def clock(date:datetime):
        date1 = date-datetime.now()
        seconds = date1.seconds+1
        t = f"{seconds//3600:02d}:{(seconds%3600)//60:02d}:{(seconds)%60:02d}"
        if date1.days==0:
            return t
        else:
            return f"{date1.days} "+t


class ShowEvents(Button):
    styles = """
        QPushButton {
            background:#ff8bc3;
            color:%s;
            font-family:Arial;
            font-size:20pt;
            border-radius:10px;
        }
    """
    style_disabled="""
        QPushButton {
            background:#ffca75;
            font-family:Arial;
            font-size:20pt;
            color:%s;
            border-radius:10px;
        }"""
    def __init__(self, master, y, date:date, event:Events,show:bool=True):
        super().__init__(master, [0,y,200,30],lambda:self.scream_choose(),event.text,style=self.styles%(color))
        self.adjustSize()
        self.events = event
        self.No_Change = True
        self.setVisible(show)
        if event.end_dt<datetime.now():
            self.setStyleSheet(self.style_disabled%color2)
            self.LeftCommand=None
            self.mouseDoubleClickEvent = self.delete
        if event.end_date == date.strftime("%Y-%m-%d") and show:
            label=Label(master, [self.width(),y+8,100,30],event.end_time+"結束",style=f"background:transparent;color:#b588ff;font-family:Arial;font-size:12pt;text-align:right;")
            label.adjustSize()
            label.show()
        elif event.start_date == date.strftime("%Y-%m-%d") and show:
            label=Label(master, [self.width(),y+8,100,30],event.start_time+"開始",style=f"background:transparent;color:#b588ff;font-family:Arial;font-size:12pt;text-align:right;")
            label.adjustSize()
            label.show()
    def delete(self,a0: QMouseEvent|None=None):
        del data.date[self.text()]
        data.write("date")
        p = Page.cal.selectedDate()
        c = calendar.selectedDate()
        if c.addDays(1-c.dayOfWeek()) == p.addDays(1-p.dayOfWeek()):
            show_todo()
        Page.destroy_page("todo")
        Page.todo(p)
        if not a0 is None: 
            a0.accept()
    def scream_choose(self, Type: Literal["change", "add"] = "change"):

        def Clock():
            if "todo" in Page.page and not sip.isdeleted(self) and not sip.isdeleted(b0):
                b0.setText(Events.clock(self.datetime))
            else:
                del_func_1000(f"Choose Clock:{id(self)}")

        def clock_top_window():
            t0 = WID(None, f"background-color:{colors['normal-bg']};", 0, 0, 300, 50)
            t0.setWindowFlag(types.SubWindow,True)
            t0.setWindowOpacity(0.5)
            t0.clockTopWin(b0.text(), self.Time, self.text())

        def reload_page():
            p = Page.cal.selectedDate()
            if calendar.selectedDate() in map(lambda x:p.addDays(x-p.dayOfWeek()+1),[0,1,2,3,4,5,6]):
                show_todo()
            cancel()
            Page.destroy_page("todo")
            Page.todo(p)

        def button_choose():
            if t1.dateTime() < t2.dateTime():
                if Type == "change" and e1.text() != self.text():
                    del data.date[self.text()]
                data.date[e1.text()] = {
                    "start_date":t1.date().toString("yyyy-MM-dd"),
                    "start_time":t1.time().toString("hh:mm:ss"),
                    "end_date": t2.date().toString("yyyy-MM-dd"),
                    "end_time":t2.time().toString("hh:mm:ss"),
                    "rings": e4.toPlainText().split("\n"),
                    "prompt":e3.toPlainText()
                }
                data.write("date")
                reload_page()

        def delete():
            cancel()
            self.delete()

        def cancel():
            self.No_Change = True
            del_func_1000(f"Choose Clock:{id(self)}")
            sip.delete(ma)
            sip.delete(t1c)
            sip.delete(t2c)

        def calendar_show():
            t=data.page["todo"]
            t1c.setGeometry(t[0],t[1]+90,260,200)
            if t1c.isVisible():
                t1.setDate(t1c.selectedDate())
            t1c.setVisible(not t1c.isVisible())

        def calendar_selected():
            t1.setDate(t1c.selectedDate())
            t1c.setVisible(False)

        def calendar_show2():
            t=data.page["todo"]
            t2c.setGeometry(t[0],t[1]+120,260,200)
            if t2c.isVisible():
                t2.setDate(t2c.selectedDate())
            t2c.setVisible(not t2c.isVisible())

        def calendar_selected2():
            t2.setDate(t2c.selectedDate())
            t2c.setVisible(False)

        if self.No_Change:
            event = self.events
            self.datetime = event.start_dt if event.start_dt>datetime.now() else event.end_dt
            self.No_Change = False
            color_bg_0 = f"rgba({color_alpha[0]},{color_alpha[1]},{color_alpha[2]},0.8)"
            page_todo = data.page["todo"]
            ma = WID(None,f"background:{color_bg_0};",*page_todo,300,280)
            ma.setWindowFlags(types.SubWindow)
            ma.setWindowTitle(Type if Type == "add" else f"{Type}:{event.text}")
            e1 = Entry(ma,f"font-family:Arial;font-size:17pt;background:transparent;color:{color2};",[0, 0, 300, 30],self.text(),)
            t1 = QtWidgets.QDateTimeEdit(ma)
            t1.setStyleSheet(f"font-family:Arial;font-size:16pt;color:{color2};background:{color};")
            t1.setCalendarPopup(False)
            t1.setDisplayFormat("yyyy/MM/dd hh:mm:ss")
            t1.setGeometry(0, 30, 240, 30)
            t1.show()
            t1c = CalendarWidget(None,[page_todo[0],page_todo[1]+90,260,200],calendar_selected, calendar_style1,False)
            t1c.setWindowFlag(types.FramelessWindowHint,True)
            Button(ma,[240,30,20,30],calendar_show,"d").show()
            Button(ma,[260,30,20,30],lambda:inter.time_show(t1),"t").show()
            t2 = QtWidgets.QDateTimeEdit(ma)
            t2.setStyleSheet(f"font-family:Arial;font-size:16pt;color:{color2};background:{color};")
            t2.setCalendarPopup(False)
            t2.setDisplayFormat("yyyy/MM/dd hh:mm:ss")
            t2.setGeometry(0, 60, 240, 30)
            t2.show()
            t2c = CalendarWidget(None,[page_todo[0],page_todo[1]+120,260,200],calendar_selected2, calendar_style1,False)
            t2c.setWindowFlag(types.FramelessWindowHint,True)
            Button(ma,[240,60,20,30],calendar_show2,"d").show()
            Button(ma,[260,60,20,30],lambda:inter.time_show(t2),"t").show()
            e3 = TextEdit(ma, 0, 90, 300, 90)
            e3.show()
            e4 = TextEdit(ma, 0, 180, 300, 30)
            e4.show()
            t1.setDateTime(event.start_dt)
            t2.setDateTime(event.end_dt)
            t1c.setSelectedDate(t1.date())
            t2c.setSelectedDate(t2.date())
            e3.insertPlainText(event.prompt)
            e4.insertPlainText("\n".join(event.rings))
            if Type == "change":
                Button(ma,[0, 210, 40, 30],button_choose,text="ok",).show()
                Button(ma, [40, 210, 60, 30], delete, text="delete").show()
                Button(ma, [100, 210, 50, 30], cancel, text="cancel").show()
            else:
                Button(ma,[0, 210, 40, 30],button_choose,text="add",).show()
                Button(ma, [40, 210, 50, 30], cancel, text="cancel").show()
            b0 = Button(ma,[200,210,50, 30],clock_top_window,text="1 00:00:00",style=f"background:transparent;color:#dd7aff;font-family:Arial;font-size:12pt;",)
            b0.adjustSize()
            Clock()
            add_func_1000(f"Choose Clock:{id(self)}", Clock)
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
    
    def clockDestroy(self):
        del_func_1000(f"TopWin clockCount:{id(self)}")
        sip.delete(self)

    def clockTopWin(self, target, time, title):
        
        def mousePressEvent(a0: QMouseEvent):
            clicked_label.add(self,a0.pos())
            if a0.button() == Qt.MouseButton.LeftButton:
                self.moveFlag = True
                self.movePosition = a0.globalPosition().toPoint() - self.pos()
                self.raise_()
                a0.accept()

        def mouseMoveEvent(a0: QMouseEvent):
            if self.moveFlag:
                self.move(a0.globalPosition().toPoint() - self.movePosition)
                a0.accept()

        def mouseReleaseEvent(a0: QMouseEvent):
            self.moveFlag = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            a0.accept()
        
        def changeBackgroundColor():
            color = QtWidgets.QColorDialog.getColor(QtGui.QColor(221,122,255),title="background color")
            color_rgb = color.getRgb()
            self.setStyleSheet(f"background-color:rgb({color_rgb[0]},{color_rgb[1]},{color_rgb[2]});")
        def changeForegroundColor():
            color = QtWidgets.QColorDialog.getColor(QtGui.QColor(221,122,255),title="foreground color")
            color_rgb = color.getRgb()
            style = f"background:transparent;color:rgb({color_rgb[0]},{color_rgb[1]},{color_rgb[2]});font-family:Arial;font-size:"
            l0.setStyleSheet(style+"13pt;")
            l1.setStyleSheet(style+"20pt;")
            fg.setStyleSheet(style+"8pt;")
            bg.setStyleSheet(style+"8pt;")
            x.setStyleSheet(style+"8pt;")
        
        self.left_time = Valuable(target)
        self.moveFlag = False
        self.Time = time
        self.datetime = datetime(*time)
        self.title = title
        self.setWindowFlag(types.FramelessWindowHint,True)
        self.setWindowFlag(types.WindowStaysOnTopHint,True)
        self.mouseMoveEvent = mouseMoveEvent
        self.mousePressEvent = mousePressEvent
        self.mouseReleaseEvent = mouseReleaseEvent
        self.setFixedSize(175, 60)
        self.show()
        style = "background:transparent;color:#dd7aff;font-family:Arial;font-size:"
        l0=Label(self,[0, 0, 175, 30],text=title,style=style+"13pt;",)
        l0.show()
        l1 = Label(self,[0, 30, 175, 30],text="100 00:00:00",style=style+"20pt;",)
        l1.setAlignment(align.AlignCenter)
        self.left_time.add(l1)
        fg=Button(self,[135, 0, 15, 15],changeForegroundColor,text="fg",style=style+"8pt;",)
        fg.show()
        bg=Button(self,[150, 0, 15, 15],changeBackgroundColor,text="bg",style=style+"8pt;",)
        bg.show()
        x=Button(self,[165, 0, 10, 10],lambda: self.clockDestroy(),text="x",style=style+"8pt;",)
        x.show()
        self.clockCount()
        add_func_1000(f"TopWin clockCount:{id(self)}", self.clockCount)

    def clockCount(self):
        if self.title in data.Todo:
            self.left_time.set(Events.clock(self.datetime))
        else:
            self.clockDestroy()


class WID_Todo(QtWidgets.QScrollArea):
    def __init__(self, parent: QtWidgets.QWidget | None = ...,wid=None,styleSheet:str="",geometry=[0,0,0,0]):
        super().__init__(parent)
        self.wid = wid
        self.setWidget(wid)
        self.setStyleSheet(styleSheet)
        self.setGeometry(*geometry)
        self.setWidgetResizable(True)


class NoTitleWidget(WID):
    def __init__(self, parent, text:Literal["page","todo","song"], *geometry):
        super().__init__(parent,"",*data.window[text],*geometry[:2])
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
        data.window[self.text] = [self.pos().x(), self.pos().y()]
        data.write("window")
        a0.accept()


class TopWin(WID):
    def __init__(self, parent: QtWidgets.QWidget | None, text:page_type, color="transparent", x=0,y=0):
        super().__init__(parent, f"background-color:{color};", *data.page[text], x,y)
        self.setAttribute(Attribute.WA_StyledBackground,True)
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

    def mouseReleaseEvent(self, a0: QMouseEvent):
        if self.moveFlag:
            self.moveFlag = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            data.page[self.text] = [self.x(), self.y()]
            data.write("page")
        a0.accept()

class MusicPlayer:
    __slots__ = ["media","audio","song","timer","playlist","slider","clear","states","play_num","button_dict","mode","play_already","show_duration","music_slider","clock_slider"]
    State = Literal["stop", "play", "pause"]

    def __init__(self):
        self.mode: Literal["all_once", "all_infinite", "one_infinite"] = data.set["PlayMode"]
        self.media = QMediaPlayer()
        self.play_already=0
        self.audio = QAudioOutput()
        self.song = Valuable("")
        self.show_duration = Valuable("")
        self.playlist = ""
        self.media.setAudioOutput(self.audio)
        self.states: MusicPlayer.State = "stop"
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self.update_slide())
        self.button_dict: dict[Literal["1", "music"], Button] = {}
        self.slider:list[Slider] = []
        self.music_slider:dict[Literal["addiction","set"], Slider] = {}
        self.clock_slider:dict[Literal["addiction","set"], Slider] = {}

    def add_music_slider(self,key:Literal["addiction","set"],music_slider:Slider,clock_slider:Slider):
        self.music_slider.update({key:music_slider})
        self.clock_slider.update({key:clock_slider})
    def music_slider_change(self,key:Literal["addiction","set"]):
        volume = self.music_slider[key].value()
        Page.MusicVolume = volume
        if key == "addiction" and "set" in self.music_slider:
            self.music_slider["set"].setValue(volume)
        elif "addiction" in self.music_slider:
            self.music_slider["addiction"].setValue(volume)
        if V_play.get() == 1:
            Music.audio.setVolume(volume / 100)
    def clock_slider_change(self,key:Literal["addiction","set"]):
        volume = self.clock_slider[key].value()
        Page.ClockVolume = volume
        if key == "addiction" and "set" in self.clock_slider:
            self.clock_slider["set"].setValue(volume)
        elif "addiction" in self.clock_slider:
            self.clock_slider["addiction"].setValue(volume)
        if V_play.get() == -1:
            Music.audio.setVolume(volume / 100)

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
        url = QUrl.fromLocalFile(song)
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
        play_list = data.music[self.playlist]
        self.play_num = play_list["Number"]
        self.media.setPlaybackRate(Page.MusicRate)
        self.audio.setVolume(Page.MusicVolume / 100)
        if self.mode != "one_infinite":
            self.play_num -= 1
        self.play_list(play_list["Position"])
        add_func_500(f"MusicPlayer play_list{id(self)}",self.play_list)
        self.timer.start(int(1000//Page.MusicRate))

    def play_list(self,pos=0):
        """
        MusicPlayer play_list{id(self)}
        """
        if V_play.get() == 1 and self.states == "play" and not self.media.isPlaying():
            li = list(data.music[self.playlist]["list"])
            if self.mode == "all_once" and self.play_num == len(li) - 1:
                self.stop_list()
            else:
                if self.mode != "one_infinite":
                    self.play_num = (self.play_num + 1 if self.play_num < len(li) - 1 else 0)
                    data.music[self.playlist]["Number"] = self.play_num
                    data.write("music")
                listbox.setCurrentRow(self.play_num)
                song = f"{data.set['MusicDir']}\\{li[self.play_num]}.mp3"
                self.song.set(li[self.play_num])
                self.reset_slide(MP3(song).info.length)
                self.media.setSource(QUrl.fromLocalFile(song))
                self.media.setPosition(pos)
                self.media.play()
            self.play_already+=int(self.play_already < 2)

    def pause_list(self):
        del_func_500(f"MusicPlayer play_list{id(self)}")
        self.timer.stop()
        self.change_button()
        self.states = "pause"
        self.media.pause()

    def unpause_list(self):
        add_func_500(f"MusicPlayer play_list{id(self)}",self.play_list)
        self.timer.start(int(1000//Page.MusicRate))
        self.change_button("暫停")
        self.states = "play"
        self.media.play()

    def stop_list(self):
        if self.states != "stop":
            data.music[self.playlist]["Position"] = self.media.position()
            data.write("music")
            V_play.set(0)
            self.states = "stop"
            self.play_already=2
            del_func_500(f"MusicPlayer play_list{id(self)}")
            self.timer.stop()
            self.reset_slide()
            self.change_button()
            self.song.set("")
            self.playlist=""
            self.media.stop()

    def stop(self):
        V_play.set(0)
        self.timer.stop()
        self.song.set("")
        self.reset_slide()
        self.change_button()
        self.media.stop()

    @property
    def music_list(self):
        return sorted(map(lambda x: x[:-4],filter(lambda x: x[-4:] == ".mp3", os.listdir(data.set["MusicDir"])),))


class Json_Data(object):
    __slots__ = ["Todo", "Class", "music", "learn", "set", "window", "page", "color", "style","exe", "date","bookmark"]
    
    def __init__(self):
        self.Todo:dict[str,dict]=self.get("Todo")
        self.Class:dict[str,int|list] = self.get("Class")
        self.music:dict[str,int|list] = self.get("music")
        self.learn:dict[str,str] = self.get("learn")
        self.set:dict = self.get("set")
        self.window:dict[str,list] = self.get("window")
        self.page:dict[str,list] = self.get("page")
        self.color:list[dict] = self.get("color")
        self.style:list[dict] = self.get("style")
        self.exe:list[dict] = self.get("exe")
        self.date:dict[str,dict] = self.get("date")
        self.bookmark:dict[str,str] = self.get("bookmark")
    def write(self,key:data_type):
        with open(f"{path}json\\{key}.json", "w", encoding="UTF-8") as r:
            json.dump(self.__getattribute__(key), r)
    def get(self,key:data_type) -> dict|list:
        with open(f"{path}json\\{key}.json",encoding="UTF-8") as r:
            d = json.load(r)
        return d
    def write_all(self):
        for i in self.__slots__:
            self.write(i)

class Interaction:
    __slots__ = ["time","timer","ctime","count","win_bool","show"]

    def __init__(self):
        self.show = Valuable("00:00:00")
        self.time = 0
        self.count = False
        self.win_bool = False

    def filename(self, types: Literal["*.mp3", "*.txt", "dir"],path: str):
        """::types (str): 類型"""
        if types == "dir":
            return FileDialog.getExistingDirectory(main_window, directory=path)
        else:
            return FileDialog.getOpenFileName(main_window, directory=path, filter=types)[0]

    def AskStr(self, prompt: str):
        return QtWidgets.QInputDialog.getText(main_window, "today's homework!!!", prompt)

    def notifier(self,title:str,message:list[str]):
        
        def active(a0):
            Music.stop()
        
        toaster = WindowsToaster(data.set["title"])
        toast = Toast(on_activated=active, on_dismissed=active)
        toast_image = ToastImage(r"./init_file/music.ico")
        toast.AddImage(ToastDisplayImage(toast_image,data.set["title"],ToastImagePosition.AppLogo))
        toast.text_fields=[title]+message
        toaster.show_toast(toast)

    @staticmethod
    def split(list1: list):
        d = {}
        di = list(filter(lambda x: len(x) == 2, map(lambda x: x.split(":", 1), list1)))
        d = {x: y for (x, y) in di}
        return d

    def set_win(self):

        def destroy_win():
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
            Button(win, [0, 150, 60, 30], destroy_win, text="確認", style=style).show()
            win.show()

    def start(self):
        self.count = True
        self.ctime = 30
        self.timer = QTimer()
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
                Music.play(data.set["ClockMusic"])
                V_play.set(1)
                Music.reset_slide(30)
            if self.ctime >= 0:
                self.ctime -= 1
            if self.ctime == -1:
                Music.reset_slide()
                Music.stop()
        if not (self.time > 0 and self.count) and self.ctime < 0:
            self.timer.stop()

    def time_show(self,obj:QtWidgets.QDateTimeEdit):
        
        def hour():
            if int(label_hour.text()[:-1])<12:
                label_hour.setText(f"{slide_hr.value()+12}時")
            else:
                label_hour.setText(f"{slide_hr.value()}時")
        
        def count_hour():
            text = int(int(label_hour.text()[:-1])>11)
            label_hour.setText(f"{slide_hr.value()+(12*text)}時")
        
        def count_minute():
            label_min.setText(str(slide_min0.value()*5+slide_min1.value())+"分")
        
        def count_second():
            label_sec.setText(str(slide_sec0.value()*5+slide_sec1.value())+"秒")
        
        def destroy():
            obj.setTime(datetime.strptime(f"{('0'+label_hour.text())[-3:-1]}:{('0'+label_min.text())[-3:-1]}:{('0'+label_sec.text())[-3:-1]}","%H:%M:%S").time())
            sip.delete(win_time)
            obj.destroyed.disconnect()
        
        def delete():
            if not sip.isdeleted(win_time):
                sip.delete(win_time)
                obj.destroyed.disconnect()
        
        win_time = WID(None,f"background-color:{color};", data.page["todo"][0]+300,data.page["todo"][1], 180, 110)
        win_time.setWindowFlag(types.SubWindow,True)
        Button(win_time,[165,0,15,15],destroy,"x").show()
        style=f"background-color:transparent;color:{color2};font-family:Arial;font-size:"
        hr = obj.time().hour()
        min = obj.time().minute()
        sec = obj.time().second()
        label_hour = Button(win_time,[0,0,50,30],hour,f"{hr}時",style=style+"9pt;")
        label_hour.show()
        slide_hr = Slider(win_time,50,0,110,20)
        slide_hr.setting([0,11],hr%12,count_hour)
        slide_hr.show()
        label_min = Label(win_time,[0,30,30,20],f"{min}分",style=style+"10pt;")
        label_min.show()
        slide_min0 = Slider(win_time,30,30,150,20)
        slide_min0.setting([0,11],min//5,count_minute)
        slide_min0.show()
        slide_min1 = Slider(win_time,30,50,150,20)
        slide_min1.setting([0,4],min%5,count_minute)
        slide_min1.show()
        label_sec = Label(win_time,[0,70,30,20],f"{sec}秒",style=style+"10pt;")
        label_sec.show()
        slide_sec0 = Slider(win_time,30,70,150,20)
        slide_sec0.setting([0,11],sec//5,count_second,)
        slide_sec0.show()
        slide_sec1 = Slider(win_time,30,90,150,20)
        slide_sec1.setting([0,4],sec%5,count_second,)
        slide_sec1.show()
        win_time.show()
        obj.destroyed.connect(delete)


class Page_Organize:
    __slots__ = ["page", "test_num", "test_number", "ClockVolume","MusicVolume","ClockRate","MusicRate","BackgroundBlur","mini_dict","todo_dict","cal"]

    class But(QtWidgets.QPushButton):
        refresh_func = None
        def __init__(self, master, x,y,w,h, command=None,text="",image: str = None,num=0):
            super().__init__(master)
            b = Button(master,[x,y+h,w,15],lambda:self.win(text,command,image,str(w),str(h),num),text=text,style=f"color:{color2};background:transparent;text-align:left;")
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
        def win(self,text:str,exec:str,icon:str,w:str,h:str,num:int):
            def submit():
                width = int(entry_x.text())
                height = int(entry_y.text())
                if "" not in [entry_text.text(),entry_exec.text(),entry_icon.text()] and 0 not in [width,height]:
                    if len(list(filter(lambda x:text==x["text"],data.exe)))==1:
                        data.exe.pop(num)
                    data.exe.insert(entry_num.currentIndex(),{"text":entry_text.text(),"exec": entry_exec.text(),"icon": entry_icon.text(),"width":width,"height":height})
                    data.write("exe")
                    window.destroy(True,True)
                    sip.delete(window)
                    self.refresh_func()
            def delete():
                o=list(filter(lambda x:text==x["text"],data.exe))
                if len(o)==1:
                    data.exe.pop(data.exe.index(o[0]))
                    data.write("exe")
                    Page.addiction()
                window.destroy(True,True)
                sip.delete(window)
                self.refresh_func()

            def set_exec():
                file = inter.filename("Exec(*.exe)",path)
                entry_exec.setText(file[0])

            def set_icon():
                file = inter.filename("Icon(*.ico);;Png(*.png);;Jpeg(*.jpeg,*.jpg);;All(*.*)",path)
                entry_icon.setText(file[0])

            window = WID(None,"",300,300,200,150)
            window.setWindowFlag(types.SubWindow,True)
            window.setWindowTitle(text)
            entry_text = Entry(window,"",[0,0,200,30],text)
            entry_text.show()
            entry_exec = Entry(window,"",[0,30,150,30],exec)
            entry_exec.show()
            Button(window,[150,30,50,30],set_exec,text="exe").show()
            entry_icon = Entry(window,"",[0,60,150,30],icon)
            entry_icon.show()
            Button(window,[150,60,50,30],set_icon,text="icon").show()
            entry_num = Combobox(window,"",map(str,range(len(data.exe))),[0,90,100,30])
            entry_num.setCurrentIndex(num)
            entry_num.show()
            entry_x = Entry(window,"",[100,90,50,30],w)
            entry_x.show()
            entry_y = Entry(window,"",[150,90,50,30],h)
            entry_y.show()
            Button(window,[0,120,50,30],submit,text="submit").show()
            Button(window,[50,120,50,30],delete,text="delete").show()
            Button(window,[100,120,50,30],lambda:window.deleteLater(),text="cancel").show()
            window.show()
        @staticmethod
        def add():
            def submit():
                width = int(entry_x.text())
                height = int(entry_y.text())
                if "" not in [entry_text.text(),entry_exec.text(),entry_icon.text()] and 0 not in [width,height]:
                    data.exe.insert(entry_num.currentIndex(),{"text":entry_text.text(),"exec": entry_exec.text(),"icon": entry_icon.text(),"width":width,"height":height})
                    data.write("exe")
                    sip.delete(window)
                    Page.destroy_page("addiction")
                    Page_Organize.But.refresh_func()

            def set_exec():
                file = inter.filename("Exec(*.exe)",path)
                entry_exec.setText(file[0])

            def set_icon():
                file = inter.filename("Icon(*.ico);;Png(*.png);;Jpeg(*.jpeg,*.jpg);;All(*.*)",path)
                entry_icon.setText(file[0])

            window = WID(None,"",300,300,200,150)
            window.setWindowFlag(types.SubWindow,True)
            window.setWindowTitle("add")
            entry_text = Entry(window,"",[0,0,200,30])
            entry_text.show()
            entry_exec = Entry(window,"",[0,30,150,30])
            entry_exec.show()
            Button(window,[150,30,50,30],set_exec,text="exec").show()
            entry_icon = Entry(window,"",[0,60,150,30])
            entry_icon.show()
            Button(window,[150,60,50,30],set_icon,text="icon").show()
            entry_num = Combobox(window,"",map(str,range(len(data.exe)+1)),[0,90,100,30])
            entry_num.show()
            entry_x = Entry(window,"",[100,90,50,30],"0")
            entry_x.show()
            entry_y = Entry(window,"",[150,90,50,30],"0")
            entry_y.show()
            Button(window,[0,120,50,30],submit,text="submit").show()
            Button(window,[50,120,50,30],lambda:window.deleteLater(),text="cancel").show()
            window.show()

    def __init__(self):
        self.page: dict[page_type, TopWin] = {}
        self.test_num = -1
        self.test_number = 0
        s = data.set
        self.ClockVolume = s["ClockVolume"]
        self.MusicVolume = s["MusicVolume"]
        self.ClockRate = s["ClockRate"]
        self.MusicRate = s["MusicRate"]
        self.BackgroundBlur = s["BackgroundBlur"]
        self.mini_dict:dict[Literal["time","date","combo","mode","timer","wid_exe","scr_exe"],Label|Button|Combo|WID]={}
        self.cal = None

    def add_win(self,page: page_type,parent: QtWidgets.QMainWindow | None = None,color="transparent",x=0,y=0,) -> TopWin:
        if page in self.page:
            self.destroy_page(page)
        self.page[page] = TopWin(parent, page, color, x, y)
        return self.page[page]

    def destroy_page(self, page: page_type):
        if page in self.page:
            if not sip.isdeleted(top_win := self.page.pop(page)):
                sip.delete(top_win)
            if page == "addiction":
                del_func_1000(f"Page_Organize addiction after:{id(self)}")
                V_time.delete(self.mini_dict["time"])
                V_date.delete(self.mini_dict["date"])
                inter.show.delete(self.mini_dict["timer"])
                Music.slider.pop()
                Music.show_duration.widget.pop()
                self.mini_dict={}
            if page in ["addiction","set"]:
                Music.music_slider.pop(page)
                Music.clock_slider.pop(page)

    def todo(self,select_date:date|None=None):
        def clicked():
            today = cal.selectedDate().toPyDate()
            today = today - timedelta(today.weekday())
            todo = data.Todo
            event = data.date
            list(map(lambda x:(sip.delete(x[0]),sip.delete(x[1])),self.todo_dict))
            self.todo_dict = []
            for dates in map(lambda x:today+timedelta(x),[0,1,2,3,4,5,6]):
                position_y = 25
                if dates.weekday()<5:
                    y = 100*dates.weekday()
                    x=0
                else:
                    y = 100*(dates.weekday()-2)
                    x = 340
                wi = WID(win,"background:transparent;",0,0,1,1)
                si = WID_Todo(win,wi,style,[x,y,340,100])
                self.todo_dict+=[[wi,si]]
                Label(wi,[10,5,100,20],dates.strftime("%m/%d  %a"),style=f"color:{color2};font-family:Arial;font-size:14pt;background:transparent;border:none;").show()
                if dates.strftime("%Y/%m/%d  %a")==datetime.now().strftime("%Y/%m/%d  %a"):
                    Label(wi,[110,4,100,21],text="Today",style=f"color:#6ae680;font-family:Arial Rounded MT Bold;font-weight:bold;font-size:13pt;background:transparent;").show()
                for event_key in sorted(filter(lambda x:Events.get_in_datetime(event[x]["start_date"],dates,event[x]["end_date"]),event)):
                    event_ = Events(event_key,**event[event_key])
                    label_event = ShowEvents(wi, position_y, dates, event_)
                    label_event.show()
                    position_y+=label_event.height()
                for todo_list in sorted(filter(lambda x:todo[x]["date"]==dates.strftime("%Y-%m-%d"),todo),key=lambda x:todo[x]["time"]):
                    gn = todo[todo_list]
                    ch = Choose(wi, todo_list, TodoData(**gn),position_y,wid_todo=si)
                    ch.show()
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
        def add_todo():
            chose = Choose(win,"",TodoData(cal.selectedDate().toString("yyyy-MM-dd"),"00:00:00","",1),0,False)
            chose.scream_choose("add")
        def add_event():
            day = cal.selectedDate().toPyDate()
            date = day.strftime("%Y-%m-%d")
            chose = ShowEvents(win,0,day,Events("",date,"00:00:00",date,"00:00:00","",[]),False)
            chose.scream_choose("add")

        win = self.add_win("todo", main_window, f"rgba({color_alpha[0]},{color_alpha[1]},{color_alpha[2]},0.15)", 680, 510)
        ge = data.Todo
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
        w = WID(win,"background:transparent;",0,0,1,1)
        t=WID_Todo(win,w,style,[340,200,340,100])
        position_y = 0
        for fa in filter(lambda x:ge[x]["date"]=="Next",ge):
            gn = ge[fa]
            ch = Choose(w, fa, TodoData(**gn),position_y,wid_todo=t)
            ch.show()
            if len(gn["prompt"]) > 0:
                Label(w,[ch.b1.x()+ch.b1.width(), position_y+5, 11, 19],text="*",style="color:#7bc3c4;font-family:細明體-ExtB;font-size:14pt;font-weight:bold;background:transparent;",).show()
            position_y+=30
        w.adjustSize()
        w.setMinimumSize(w.width(),w.height())
        t.show()
        cal = CalendarWidget(win,[340,0,200,200],clicked,calendar_style0,grid_visible=True)
        cal.setHorizontalHeaderFormat(cal.HorizontalHeaderFormat.SingleLetterDayNames)
        forma = cal.headerTextFormat()
        forma.setBackground(QtGui.QColor(color_alpha[0],color_alpha[1],color_alpha[2],30))
        forma.setFontPointSize(8)
        cal.setSelectedDate(select_date or datetime.now().date())
        cal.setHeaderTextFormat(forma)
        cal.setFirstDayOfWeek(Qt.DayOfWeek.Monday)
        cal.show()
        self.cal = cal
        style0=f"background:rgba({color_alpha[0]},{color_alpha[1]},{color_alpha[2]},0.56);"
        Label(win,[540,125,25,25],image=QPixmap(f"{path}icon\\加入.png"),style=style0)
        Button(win,[540,150,50,25],add_todo,"todo",style=style0+f"color:{color_bg};",).show()
        Button(win,[590,150,50,25],add_event,"event",style=style0+f"color:{color_bg};",).show()
        Button(win,[540,175,25,25],last,image=QIcon(f"{path}home\\last.png"),style=style0,).show()
        Button(win,[565,175,25,25],next,image=QIcon(f"{path}home\\next.png"),style=style0,).show()
        clicked()
        Button(win,[655, 0, 25, 20],lambda: self.destroy_page("todo"),text="x").show()
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

            LReadDict = inter.split(list(write1.Open().split("\n")))
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

        def double_click():
            MessageBox.information(main_window, "字典：查詢成功！", write1.toPlainText().split("\n",int(write2.currentItem().text())+1)[-2])

        win = self.add_win("dic", main_window, x=600, y=300)
        style = f"background-color:{color};color:#fc8289;font-family:Arial;font-size:16pt;font-weight:bold;"
        write2 = QtWidgets.QListWidget(win)
        write2.setStyleSheet(widget["PlainTextEdit"])
        write2.setGeometry(400, 100, 200, 200)
        write1 = WriteIt(win, write2, 0, 0, 400, 300)
        write1.setLineWrapMode(write1.LineWrapMode.NoWrap)
        write2.clicked.connect(lambda: write1.moved())
        write2.itemDoubleClicked.connect(double_click)
        entry = Entry(win, style, [400, 70, 200, 30])
        entry.textChanged.connect(lambda: connect())
        style1 = f"""QPushButton {{background-color:{color};color:#d48649;font-family:Arial;font-size:16pt;font-weight:bold;}}QPushButton:activate {{background-color:{color};color:#d48649}}"""
        but2 = Button(win, [400, 40, 100, 30], lambda: write1.clean(), text="clear", style=style1)
        but3 = Button(win,[500, 40, 100, 30],lambda: write1.save_file(),text="save",style=style1,)
        but4 = Button(win, [400, 10, 100, 30], lambda: word_card(), text="單字卡", style=style1)
        l0 = Label(win, [500, 10, 100, 30], text="第1行", style=style)
        write1.put.add(l0)
        for fa in [write1, write2, entry, but2, but3, but4]:
            fa.show()
        Button(win,[580, 0, 20, 15],lambda: self.destroy_page("dic"),text="x").show()
        win.show()
        write1.clean()

    def learn(self):
        def add_func():
            if (j := inter.AskStr("加入\n標題: "))[1]and j[0] not in data.learn and j[0] != "Class":
                data.learn[j[0]] = {}
                data.write("learn")
                lrn_but.update_items(list(data.learn.keys()) + ["Class"])

        def rename_func():
            if (j := inter.AskStr("重新命名\n新標題:"))[1] and lrn_but.currentText() in data.learn:
                data.learn[j[0]] = data.learn.pop(lrn_but.currentText())
                data.write("learn")
                lrn_but.update_items(list(data.learn.keys()) + ["Class"])

        def delete_func():
            c = lrn_but.currentText()
            if c in data.learn and MessageBox.question(main_window, "today's homework!!!", f"你確定要刪除這個字典嗎?\n{c}"):
                del data.learn[c]
                data.write("learn")
                lrn_but.removeItem(lrn_but.currentIndex())

        def search_func():
            if (m := inter.AskStr("您想查詢:"))[1] and lrn_but.currentText() in (sh := data.learn):
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
            if (m := inter.filename("*.txt",path)) and (s := inter.AskStr("開啟\n新的標題:"))[1] and s not in data.learn and s != "Class":
                with open(m, encoding="UTF-8") as w:
                    data.learn[s[0]] = inter.split(w.read().split("\n"))
                    data.write("learn")
                lrn_but.update_items(list(data.learn.keys()) + ["Class"])

        def trans_func():
            if lrn_but.currentText() in data.learn and len(s1 := lrn_t1.toPlainText()) == len(s2 := lrn_t2.toPlainText()):
                with open(path + lrn_but.currentText() + ".txt", "w", encoding="UTF-8") as w:
                    w.write("\n".join(map(lambda x, y: x + ":" + y, s1, s2)))

        def ADD():
            if (m := inter.AskStr("加入\n標題:"))[1] and m not in data.Class:
                data.Class[m[0]] = []
                data.write("Class")
                lrn_but2.update_items(list(data.Class.keys()))

        def DELETE():
            c = lrn_but2.currentText()
            if c in data.Class and MessageBox.question(main_window, "today's homework!!!", f"你確定要刪除這個字典嗎?\nClass-{c}"):
                del data.Class[c]
                data.write("Class")
                lrn_but2.removeItem(lrn_but2.currentIndex())

        def Class():
            t2 = ""
            so = data.Class[lrn_but2.currentText()]
            if type(so) == list:
                t2 = "\n".join(so)
            else:
                t2 = str(so)
            lrn_t2.setPlainText(t2)

        def save():
            n = lrn_t2.toPlainText().split("\n")
            c = lrn_but2.currentText()
            if c in ["日數", "節數"]:
                try:
                    data.Class[c] = int(n[0])
                except:
                    MessageBox.warning(main_window, "today's homework!!!","第一行應為整數！")
            else:
                data.Class[c] = n
            data.write("Class")

        def lear():
            so = dict(data.learn[lrn_but.currentText()])
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
                data.learn[lrn_but.currentText()] = {x: y for (x, y) in list(zip(s1, s2))}
                data.write("learn")

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
        lrn_but = Combobox(win,f"QComboBox {{background-color:rgba(255, 255, 255, 0.58);color:#fc8289;}}QComboBox:activate {{background-color:rgba(255, 255, 255, 0.58);color:#fc8289;}}",list(data.learn.keys()) + ["Class"],[0, 0, 200, 30],)
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
        lrn_but2 = Combobox(button_frame,f"""QComboBox {{background-color:rgba(255, 255, 255, 0.58);color:#fc8289;}}QComboBox:activate {{background-color:rgba(255, 255, 255, 0.58);color:#fc8289;}}""",list(data.Class.keys()),[100, 0, 200, 30],)
        lrn_but2.activated.connect(Class)
        lrn_but2.show()
        Button(button_frame, [100, 30, 50, 30], save, text="save", style=style).show()
        Button(button_frame, [150, 30, 40, 30], ADD, text="Add", style=style).show()
        Button(button_frame,[190, 30, 70, 30],DELETE,text="Delete",style=style,).show()
        Button(win,[580, 0, 20, 20],lambda: self.destroy_page("learn"),text="x").show()
        win.show()

    def classes(self):
        i1 = data.Class
        length = i1["節數"]
        width = i1["日數"]
        win = self.add_win("class", main_window, x=width * 90, y=length * 30)
        c=f"rgba({color_alpha[0]},{color_alpha[1]},{color_alpha[2]},0.56)"
        for fa in range(width):
            i3 = list(i1.keys())[2:][fa]
            Label(win,[fa * 90, 0, 90, 30],text=f"  {i3}  ",style=f"background-color:{c};color:#fc8289;font-family:Arial;font-size:16pt;font-weight:bold;",).show()
            list(map(lambda fi:Label(win,[fa * 90, (fi + 1) * 30, 90, 30],text=i1[i3][fi],style=f"background-color:{c};color:{color2};font-family:Arial;font-size:16pt;font-weight:bold;",).show(),range(length)))
        Button(win,[width * 90 - 20, 0, 20, 20],lambda: self.destroy_page("class"),text="x").show()
        win.show()

    def set(self):
        def dark():
            V_state.set(dark_scale.value())

        def set_m():
            m_label.setText(f"Music Volume {m_scale.value()}%")
            Music.music_slider_change("set")

        def set_c():
            c_label.setText(f"Clock Volume {c_scale.value()}%")
            Music.clock_slider_change("set")
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
            f = "\\" if "\\" in data.set["ClockMusic"] else "/"
            if file := inter.filename("*.mp3",f.join(data.set["ClockMusic"].split(f)[:-1])):
                data.set["ClockMusic"] = file
                data.write("set")
                t0.setText(file)

        def set_DictTxt():
            f = "\\" if "\\" in data.set["DictTxt"] else "/"
            if file := inter.filename("*.txt",f.join(data.set["DictTxt"].split(f)[:-1])):
                data.set["DictTxt"] = file
                data.write("set")
                t1.setText(file)

        def set_MusicDir():
            f = "\\" if "\\" in data.set["MusicDir"] else "/"
            if file := inter.filename("*.mp3",f.join(data.set["MusicDir"].split(f)[:-1])):
                Music.stop_list()
                data.set["MusicDir"] = file
                data.write("set")
                t2.setText(file)

        def set_Background_file():
            f = "\\" if "\\" in data.set["Background"] else "/"
            file = inter.filename("JPEG (*.jpg *.jpeg *jpe *.jfif);;PNG (*png);;All (*.*)",f.join(data.set["Background"].split(f)[:-1]))
            if len(file) > 0:
                data.set["Background"] = file
                data.write("set")
                t3.setText(file)
                background_blur_show(file)

        def set_Background_dir():
            f = "\\" if "\\" in data.set["Background"] else "/"
            file = inter.filename("dir",f.join(data.set["Background"].split(f)[:-1]))
            if len(file) > 0:
                data.set["Background"] = file
                data.write("set")
                t3.setText(file)
                background_blur_show(file+"/"+random.choice(os.listdir(file)))
        def set_background_blur():
            self.BackgroundBlur=bg_blur_scale.value()/10
            bg_blur_label.setText(f"BG Blur {self.BackgroundBlur}")
            op.setBlurRadius(self.BackgroundBlur)

        win = self.add_win("set", main_window, f"rgba({color_alpha[0]}, {color_alpha[1]}, {color_alpha[2]}, 0.7)", x=320, y=330)
        wid = QtWidgets.QWidget(win)
        wid.setStyleSheet("background:transparent;")
        wid.setMinimumSize(320,420)
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
        s = data.set
        style_label=f"background:transparent;color:{color2};font-family:Arial;font-size:12pt;"
        style_button=f"QPushButton {{background:{color};color:{color_bg};border-radius:5px;font-family:Arial;font-size:12pt;border:1px solid {color_bg};}} QPushButton:hover {{color:{color_bg};background:transparent;}}"
        style_entry=f"background:rgba(209, 142, 109, 0.4);color:#dd7aff;font-family:Arial;font-size:12pt;"
        dark_label = Label(wid,[70, 0, 70, 20],text="Dark",style=style_label)
        dark_label.setAlignment(align.AlignRight)
        dark_label.show()
        dark_scale = Slider(wid, 140, 0, 60, 30)
        dark_scale.setting([0,1],int(data.set["dark"]),dark)
        m_label = Label(wid,[0, 30, 140, 20],text=f"Music Volume {self.MusicVolume}%",style=style_label)
        m_scale = Slider(wid, 140, 30, 160, 30)
        m_scale.setting([0,100],self.MusicVolume,set_m)
        c_label = Label(wid,[0, 60, 140, 20],text=f"Clock Volume {self.ClockVolume}%",style=style_label)
        c_scale = Slider(wid, 140, 60, 160, 30)
        c_scale.setting([0, 100],self.ClockVolume,set_c)
        Music.add_music_slider("set",m_scale,c_scale)
        m_rate_label = Label(wid,[0, 90, 140, 20],text=f"Music Rate {self.MusicRate}",style=style_label)
        m_rate_scale = Slider(wid, 140, 90, 160, 30)
        m_rate_scale.setting([50, 200],int(self.MusicRate*100),set_music_rate)
        c_rate_label = Label(wid,[0, 120, 140, 20],text=f"Clock Rate {self.ClockRate}",style=style_label)
        c_rate_scale = Slider(wid, 140, 120, 160, 30)
        c_rate_scale.setting([50, 200],int(self.ClockRate*100),set_clock_rate)
        bg_blur_label = Label(wid,[0, 150, 140, 20],text=f"BG Blur {self.BackgroundBlur}",style=style_label)
        bg_blur_scale = Slider(wid, 140, 150, 160, 30)
        bg_blur_scale.setting([0,1000],int(self.BackgroundBlur*10),set_background_blur)
        Button(wid,[0, 180, 100, 30],set_ClockMusic,text="Clock Music",style=style_button).show()
        t0 = Entry(wid,style_entry,[0,210,300,30],s["ClockMusic"])
        Button(wid,[0, 240, 100, 30],set_DictTxt,text="Dictionary file",style=style_button).show()
        t1 = Entry(wid,style_entry,[0,270,300,30],s["DictTxt"])
        Button(wid,[0, 300, 100, 30],set_MusicDir,text="Music Dir",style=style_button).show()
        t2 = Entry(wid,style_entry,[0,330,300,30],s["MusicDir"])
        Label(wid,[0, 360, 100, 30],text="Background",style=style_label).show()
        Button(wid,[100, 360, 40, 30],set_Background_file,text="file",style=style_button).show()
        Button(
            wid, [140, 360, 40, 30], set_Background_dir, text="dir", style=style_button
        ).show()
        t3 = Entry(wid,style_entry,[0,390,300,30],s["Background"])
        list(map(lambda i:i.show(),[m_label, c_label,m_rate_label,c_rate_label, m_scale, c_scale,m_rate_scale,c_rate_scale,bg_blur_label,bg_blur_scale, t0, t1, t2, t3]))
        Button(win,[300, 0, 20, 15],lambda: self.destroy_page("set"),text="x").show()
        win.show()

    def addiction(self):

        def play_command():
            com(comb)
            music_play()

        def move():
            if win.pos().x()==m.width()-30:
                win.move(m.width()-230,(m.height()-y)//2)
            else:
                win.move(m.width()-30,(m.height()-y)//2)

        def click(a0:QMouseEvent):
            clicked_label.add(win,a0.pos())
            a0.accept()

        def after():
            """Page_Organize addiction after:{id(self)}"""
            label_memory.setText(f"{psutil.virtual_memory().percent:05.2f}%")
            scale_memory.setValue(int(psutil.virtual_memory().percent*100))
            cpu = sum(psutil.cpu_percent(interval=0.5,percpu=True))/psutil.cpu_count(False)
            label_cpu.setText(f"{cpu:05.2f}%")
            scale_cpu.setValue(int(cpu*100))
            if len(psutil.disk_partitions()) != len(label_dict):
                self.destroy_page("addiction")
                Page.addiction()
            else:
                for i,a, in label_dict.items():
                    usage = psutil.disk_usage(i).percent
                    a[0].setText(f"{usage:05.2f}%")
                    a[1].setValue(int(usage*100))

        def count():
            if inter.count:
                inter.count = False
                inter.ctime = -1
                inter.timer.stop()
                button_count.setIcon(QIcon(f"{path}icon\\播放.png"))
            else:
                inter.start()
                button_count.setIcon(QIcon(f"{path}\\icon\\暫停.png"))

        def refresh(a0=None):
            if "wid_exe" in self.mini_dict and "scr_exe" in self.mini_dict:
                sip.delete(self.mini_dict["wid_exe"])
                sip.delete(self.mini_dict["scr_exe"])
            exec_list=data.exe
            wid_exe = WID(win,"background:#00000000;",30,0,200,200)
            width=0
            height=0
            num=0
            for i in exec_list:
                but=self.But(wid_exe,width,height,i["width"],i["height"],i["exec"],i["text"],i["icon"],num)
                max_x = max(but.width(),but.b.width())
                if max_x+width>=180:
                    height+=but.b.height()+but.height()
                    width=0
                else:
                    width+=max_x-10
                num+=1
            scr_exe=WID_Todo(win,wid_exe,"background:#00000000;border:none;",[30,255+win_battery.height(),200,300])
            scr_exe.show()
            self.mini_dict.update(wid_exe=wid_exe,scr_exe=scr_exe)

        def set_m():
            m_label.setText(f"Music Volume {m_scale.value()}%")
            Music.music_slider_change("addiction")

        def set_c():
            c_label.setText(f"Clock Volume {c_scale.value()}%")
            Music.clock_slider_change("addiction")

        win = self.add_win("addiction",x=230,y=100)
        win.setAttribute(Attribute.WA_TranslucentBackground, True)
        win.mouseMoveEvent = lambda a0:a0.accept()
        win.mousePressEvent = click
        win.setGeometry(m.width()-200,0,230,m.height())
        win.setWindowOpacity(0.7)
        win.setWindowFlags(types.FramelessWindowHint|types.WindowStaysOnTopHint|types.SubWindow)
        win_all_label = Label(win, [30, 0, 200, m.height()], "", style=f"background-color:{color};border:none;border-top-left-radius:15px;border-bottom-left-radius:15px;")
        time = Label(win,[30, 0, 200, 30],text=V_time.get(),style="background-color:#00000000;color:#FFAEC9;font-family:Arial Rounded MT Bold;font-size:28pt;font-weight:bold;",)
        time.setAlignment(align.AlignCenter)
        V_time.add(time)
        date = Label(win,[30, 30, 200, 30],text=V_date.get(),style="background-color:#00000000;color:#FFAEC9;font-family:Arial;font-size:14pt;font-weight:bold;",)
        date.setAlignment(align.AlignCenter)
        V_date.add(date)
        comb = Combo(win, "Arial", 14, 8, True, geometry=[30, 60, 200, 30])
        comb.activated.connect(lambda:com(comb))
        comb.show()
        slider_mini = Slider(win, 30, 90, 200, 10)
        slider_mini.setStyleSheet(widget["Slider-1"])
        slider_mini.actionTriggered.connect(lambda:Music.slider_change(slider_mini))
        slider_mini.setRange(0,int(slider.maximum()))
        slider_mini.show()
        Music.add_slider(slider_mini)
        l = Label(win,[30,100,70,15],text="00:00/00:00",style=f"color:{color_bg};")
        Music.show_duration.add(l)
        Button(win,[30,115, 15, 15],last,image=QIcon(f"{path}home\\last.png"),style="background:transparent;").show()
        play = Button(win, [45, 110, 25, 25], play_command, image=QIcon(f"{path}icon\\播放.png"),style="background:transparent;")
        Music.set_button("1", play)
        play.show()
        Button(win,[70, 110, 25, 25],lambda: Music.stop_list(),image=QIcon(f"{path}icon\\停止.png"),style="background:transparent;",).show()
        Button(win,[95, 115, 15, 15],next_music,image=QIcon(f"{path}home\\next.png"),style="background:transparent;").show()
        mode = Button(win,[160, 110, 25, 25],image=QIcon(f"{path}home\\{Music.mode}.png"),style="background:transparent;",)
        mode.LeftCommand=lambda:set_play_mode(mode)
        mode.show()
        scale_style = f"""
        QSlider::groove:horizontal {{
            height: 20px;border-radius: 10px;background: {color};
        }}
        QSlider::handle:horizontal{{
            background: {colors['normal-bg']};width: 20px;height: 20px;margin: 0px 0;border-radius: 10px;
        }}
        QSlider::sub-page:horizontal{{
            border-radius: 10px;background:#d48649;
        }}
        QSlider {{
            background: transparent;border-radius: 10px;
        }}"""
        m_scale = Slider(win, 40, 135, 180, 30)
        m_label = Label(m_scale,[10, 0, 170, 30],text=f"Music Volume {self.MusicVolume}%",style=f"background:transparent;color:{color2};font-family:Arial;font-size:12pt;")
        m_label.setAttribute(Attribute.WA_TransparentForMouseEvents,True)
        m_scale.setStyleSheet(scale_style)
        m_scale.setting([0,100],self.MusicVolume,set_m)
        c_scale = Slider(win, 40, 165, 180, 30)
        c_label = Label(c_scale,[10, 0, 170, 30],text=f"Clock Volume {self.ClockVolume}%",style=f"background:transparent;color:{color2};font-family:Arial;font-size:12pt;")
        c_label.setAttribute(Attribute.WA_TransparentForMouseEvents,True)
        c_scale.setting([0, 100],self.ClockVolume,set_c)
        c_scale.setStyleSheet(scale_style)
        Music.add_music_slider("addiction" ,m_scale,c_scale)
        m_label.show()
        m_scale.show()
        c_label.show()
        c_scale.show()
        Timer_Win = WID(win,"background:#00000000;",30,195,200,60)
        Timer_l1 = Label(Timer_Win, [0, 0, 200, 35], text=inter.show.get(), style=f"background-color:rgba({color_alpha[0]}, {color_alpha[1]}, {color_alpha[2]}, 0.78);font-family:Arial;font-size:26pt;font-weight:bold;color:#d48649")
        Timer_l1.setAlignment(align.AlignRight)
        inter.show.add(Timer_l1)
        button_count = Button(Timer_Win,[60, 35, 25, 25],count,image=QIcon(f"{path}icon\\播放.png"),style="background:transparent;",)
        button_count.show()
        Button(Timer_Win,[95, 35, 25, 25],lambda: inter.set_win(),image=QIcon(f"{path}icon\\編輯.png"),style="background:transparent;",).show()
        Timer_Win.show()
        win_battery = WID(win,"background:#00000000;",30,255,200,120)
        co = ",".join(map(str, color_alpha))
        s = "color:%s;background:rgba("+co+",0.5);font-family:Arial;font-size:17pt;"
        progress_style = "QProgressBar {background: rgba("+co+",0.5);border: none;} QProgressBar::chunk {background: %s;}"
        Label(win_battery,[0,0,60,27],text="RAM",style=s%color_bg).show()
        label_memory = Label(win_battery,[60, 0, 120, 27],text="",style=s%color_bg,)
        label_memory.setAlignment(align.AlignRight)
        label_memory.show()
        scale_memory = progressbar(win_battery,0,10000,progress_style % color_bg,27)
        Label(win_battery,[0,30,60,27],text="CPU",style=s % "#ff6cd1").show()
        label_cpu = Label(win_battery,[60, 30, 120, 27],text="",style=s % "#ff6cd1",)
        label_cpu.setAlignment(align.AlignRight)
        label_cpu.show()
        scale_cpu = progressbar(win_battery,0,10000,progress_style % "#ff6cd1",57)
        label_dict:dict[str,list[Label|QtWidgets.QProgressBar]] = {}
        h=60
        for i in psutil.disk_partitions():
            Label(win_battery, [0, h, 60, 27], text=f"{i.device}", style=s % "#6ae680").show()
            l = Label(win_battery,[60,h,120,27],text="",style=s % "#6ae680",)
            l.setAlignment(align.AlignRight)
            l.show()
            ps = progressbar(win_battery,0,10000,progress_style % "#6ae680",h+27)
            label_dict[i.device] = [l,ps]
            h+=30
        after()
        add_func_1000(f"Page_Organize addiction after:{id(self)}",after)
        win_battery.adjustSize()
        win_battery.show()
        Button(win,[200,195+win_battery.height(),30,20],lambda:self.But.add(),text="add").show()
        Page_Organize.But.refresh_func=refresh
        refresh()
        y=215+win_battery.height()+300
        win.setGeometry(m.width()-230,(m.height()-y)//2,230,y)
        win_all_label.setGeometry(30,0,200,y)
        win_all_label.show()
        Label(win, [0, win.height()//2-50, 30, 100], "", style=f"background-color:{color_bg};border:none;border-top-left-radius:15px;border-bottom-left-radius:15px;").show()
        Button(win,[0,win.height()//2-40,30,30],move,text=" ").show()
        Button(win, [0,win.height()//2+10,30,30], lambda:self.destroy_page("addiction"), text="x").show()
        self.mini_dict.update(time=time,date=date,combo=comb,mode=mode,timer=Timer_l1)
        win.show()

    def exe(self):
        global WebWidget,web_url

        def load_url():
            web_url.setUrl(url_input.text())
            WebWidget.load(web_url)
            check()
        def last_url():
            WebWidget.back()
            web_url.setUrl(WebWidget.url().url())
            check()
        def next_url():
            WebWidget.forward()
            web_url.setUrl(WebWidget.url().url())
            check()
        def maximum_web():
            nonlocal x,y
            rect = QtCore.QRect(0,0,m.width(),m.height())
            if win.geometry() != rect:
                win.move(0,0)
                resize(m.width(),m.height())
                l.setGeometry(0,-15,m.width(),90)
            else:
                win.move(*data.page["exe"])
                resize(x,y)
        def destroy_web():
            global web_url
            web_url = QUrl(WebWidget.url().url())
            win.setVisible(False)
        def resize(x:int,y:int):
            win.resize(x,y)
            l.setGeometry(0,0,x,75)
            destroy_button.move(x-40,0)
            max_button.move(x-75,0)
            url_input.resize(x-30,30)
            WebWidget.resize(x,y-60)
            load_button.move(x-30,30)
        def resize_it():
            nonlocal x,y
            pos = inter.AskStr(f"大小多少？ (寬x高)\n目前: {win.width()}x{win.height()}")
            if pos[1]:
                x,y, = list(map(int,pos[0].split("x")))
                resize(x,y)
        def url_refresh():
            global web_url
            web_url = WebWidget.url()
            url_input.setText(web_url.url())
            check()
        def bookmark_add():
            name=inter.AskStr("bookmark name: ")
            if not name[0] in data.bookmark and name[1]:
                data.bookmark.update({name[0]:WebWidget.url().url()})
                print(list(data.bookmark.keys()))
                bookmark.update_items(["無"]+list(data.bookmark.keys()))
                data.write("bookmark")
                check()
        def bookmark_delete():
            data.bookmark.pop(bookmark.currentText())
            data.write("bookmark")
            check()
        def bookmark_rename():
            name=inter.AskStr("bookmark name: ")
            if not name in data.bookmark:
                data.bookmark.update({name:data.bookmark.pop(bookmark.text())})
                bookmark.update_items(["無",*list(data.bookmark.keys())])
                data.write("bookmark")
                check()
        def bookmark_get():
            if bookmark.currentText() in data.bookmark:
                web_url.setUrl(data.bookmark[bookmark.currentText()])
                WebWidget.load(web_url)
                check()
        def check():
            boolean = web_url.url() in data.bookmark.values()
            if boolean:
                b = list(filter(lambda x:data.bookmark[x]==web_url.url(),data.bookmark))
                bookmark.setCurrentText(b[0])
            else:
                bookmark.setCurrentText("無")
            rename.setVisible(boolean)
            delete.setVisible(boolean)
            add.setVisible(not boolean)
        def browser():
            webbrowser.open(url_input.text())

        x=600
        y=400
        win = self.add_win("exe",x=x,y=y)
        win.setWindowFlags(types.FramelessWindowHint|types.SubWindow)
        win.setAttribute(Attribute.WA_TranslucentBackground,True)
        l=Label(win,[0,0,600,75],"",style=f"background-color:rgba({color_alpha[0]},{color_alpha[1]},{color_alpha[2]},0.56);border-radius:15px;")
        l.show()
        destroy_button=Button(win,[560,0,30,30],destroy_web,"x")
        destroy_button.show()
        max_button=Button(win,[525,0,30,30],maximum_web,"▭")
        max_button.show()
        text_style=f"background-color:rgba({color_alpha[0]},{color_alpha[1]},{color_alpha[2]},0.56);color:#fc8289;font-family:Arial;font-weight:bold;font-size:"
        url_input = Entry(win,text_style+"15pt;",[0,30,570,30],web_url.url())
        url_input.show()
        load_button=Button(win,[570,30,30,30],load_url,"GO!",style=text_style+"13pt;")
        load_button.show()
        WebWidget=QtWebEngineWidgets.QWebEngineView(win)
        WebWidget.resize(600, 340)
        WebWidget.move(0,60)
        WebWidget.load(web_url)
        WebWidget.setVisible(True)
        WebWidget.urlChanged.connect(url_refresh)
        Button(win,[20,0,30,30],last_url,image=QIcon(f"{path}home\\last.png"),style="background:transparent;").show()
        Button(win,[55,0,30,30],lambda:WebWidget.reload(),image=QIcon(f"{path}home\\refresh.png"),style="background:transparent;").show()
        Button(win,[90,0,30,30],next_url,image=QIcon(f"{path}home\\next.png"),style="background:transparent;").show()
        Button(win,[125,0,50,30],browser,"browse","background:transparent;color:#fc8289;").show()
        Button(win,[175,0,50,30],resize_it,"resize","background:transparent;color:#fc8289;").show()
        bookmark = Combobox(win,"QComboBox{background-color:transparent;color:#fc8289;}",["無",*list(data.bookmark.keys())],[230,0,90,30])
        bookmark.currentTextChanged.connect(bookmark_get)
        bookmark.show()
        add = Button(win,[320,0,40,30],bookmark_add,"add",style="background:transparent;color:#fc8289;")
        rename = Button(win,[320,0,60,30],bookmark_rename,"rename",style="background:transparent;color:#fc8289;")
        delete = Button(win,[380,0,60,30],bookmark_delete,"delete",style="background:transparent;color:#fc8289;")
        check()
        win.setVisible(False)


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
    def mousePressEvent(self, e: QMouseEvent | None) -> None:
        super().mousePressEvent(e)
        clicked_label.add(self,e.pos())
        self.parentWidget().raise_()
        e.accept()


class TEXT(QtWidgets.QTextEdit):
    def __init__(self, parent: QtWidgets.QWidget, geometry: list[int, int, int, int]):
        super().__init__(parent)
        self.setGeometry(*geometry)
        self.setStyleSheet(f"background-color:{color};color:#fc8289;font-family:Arial;font-size:17pt;font-weight:bold;")
    def mousePressEvent(self, e: QMouseEvent | None):
        super().mousePressEvent(e)
        clicked_label.add(self,e.pos())
        self.parentWidget().raise_()
        e.accept()

    def setting(self, obj:Self):
        def on_roll():
            self.rol.setValue(self.sc.value())
        def on_scroll():
            self.sc.setValue(self.rol.value())

        self.obj = obj
        self.sc = obj.verticalScrollBar()
        self.rol = self.verticalScrollBar()
        self.sc.valueChanged.connect(on_roll)
        self.rol.valueChanged.connect(on_scroll)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)


class WriteIt(WST):
    def __init__(self, master, write2: QtWidgets.QListWidget, *geometry):
        super().__init__(master, *geometry)
        self.WST = write2
        self.put = Valuable("")
        self.currentLine = Valuable(0)
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
        with open(data.set["DictTxt"], "w+", encoding="UTF-8") as o:
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
        self.currentLine = self.textCursor().blockNumber()
        self.put.set(f"第{self.currentLine}行")

    def Open(self, mode="r"):
        with open(data.set["DictTxt"], mode, encoding="UTF-8") as o:
            m = o.read()
        return m


def background_blur_show(file):
    img0 = Image.open(file)
    q_image0 = ImageQt.toqimage(img0)
    i_tan = img0.width/img0.height
    m_tan = m.width()/m.height()
    i=QPixmap(img0.width, img0.height).fromImage(q_image0)
    if i_tan>m_tan:
        w = int(i.width()/m_tan)
        i = i.copy((i.width()-w)//2,0,w,i.height()).scaled(m.width(),m.height())
    else:
        i = i.scaled(m.width(),int(m.width()*img0.height/img0.width))
    bg.setPixmap(i)
    l0.setPixmap(i.copy(0, 0, 250, m.height()))


def double_clicked():
    clicked_label.add(Song_Win,Song_Win.mapFromGlobal(QtGui.QCursor.pos()))
    if combo.currentText() in data.music and listbox.currentItem()!=None and Music.play_already == 2:
        Music.stop()
        data.music[combo.currentText()]["Number"] = listbox.currentRow()
        data.write("music")
        Music.play_list_start()


def show_todo():
    
    def event_sorted(x):
        if dates[x]["start_date"]==Date.toString("yyyy-MM-dd"):
            return datetime.strptime(dates[x]["start_date"]+" "+dates[x]["start_time"],"%Y-%m-%d %H:%M:%S")
        else:
            return x
    
    todo_ = data.Todo
    text = ""
    Date=calendar.selectedDate()
    todo = list(filter(lambda x: todo_[x]["date"] == Date.toString("yyyy-MM-dd") and todo_[x]["type"] in [1,3],todo_,))
    dates = data.date
    event = sorted(filter(lambda x:Events.get_in_datetime(dates[x]["start_date"],Date.toPyDate(),dates[x]["end_date"]),dates),key=event_sorted)
    if len(event)> 0:
        text = "\n".join(event)
    if len(todo) > 0:
        text += "\n".join(map(lambda x:f'{todo_[x]["time"]} {x}',sorted(todo,key=lambda x:todo_[x]["time"])))
    elif len(event)==0:
        text = "無"
    text_home.setPlainText(text)


def music_play():
    if Music.states == "stop":
        if len(listbox.selectedIndexes()) == 1:
            data.music[combo.currentText()]["Number"] = listbox.selectedIndexes()[0].row()
            data.write("music")
        Music.play_list_start()
    elif Music.states == "play":
        Music.pause_list()
    else:
        Music.unpause_list()


def add_music():
    if combo.currentText() in data.music and (c := QtWidgets.QInputDialog.getItem(main_window, "add", "您要加入什麼音樂?", Music.music_list, 0))[1]:
        if listbox.currentItem():
            n = listbox.currentRow()
            data.music[combo.currentText()]["list"][n : n + 1] = [listbox.currentItem().text(),c[0],]
        elif listbox.count()==0:
            n=0
            data.music[combo.currentText()]["list"][0] = c[0]
        data.write("music")
        listbox.insertItem(n + 1, c[0])


def edit_func(text: str):
    listbox.clear()
    li = data.music[text]
    listbox.addItems(li["list"])
    if len(li["list"]) > li["Number"]:
        listbox.setCurrentRow(li["Number"])


def add_list():
    if (m := inter.AskStr("新增播放清單 名稱為："))[1] and m not in data.music:
        data.music[m[0]] = {"Number": 0, "Position":0, "list": []}
        data.write("music")
        combo.update_items(list(data.music.keys()))


def delete_list():
    if combo.currentText() in data.music and MessageBox.question(main_window, "today's homework!!!", f"你確定要刪除這個播放清單嗎?\n{combo.currentText()}")< 50000:
        del data.music[combo.currentText()]
        data.write("music")
        key = data.music.keys()
        combo.update_items(list(key))


def edit():
    def add_func():
        if combobox.currentText() in Music.music_list:
            data.music[combo.currentText()]["list"][i] = combobox.currentText()
            data.write("music")
        ma.deleteLater()
        edit_func(combo.currentText())
    
    def del_func():
        del data.music[combo.currentText()]["list"][i]
        data.write("music")
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
        r = r - 2 if r > 0 else len(data.music[combo.currentText()]["list"])-2
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
        self.timer = QTimer()
        self.timer.timeout.connect(lambda:self.exec_animation())
        self.timer.start(50)
    def add(self,parent:QtWidgets.QWidget,a0:QtCore.QPoint,mousePressTarget:None|Button=None):
        def Wid_func(a1:QMouseEvent):
            clicked_label.add(parent,label.pos()+a1.pos())
            if a1.button() == Qt.MouseButton.LeftButton:
                parent.moveFlag = True
                parent.movePosition = a1.globalPosition().toPoint() - parent.pos()
                parent.raise_()
            a1.accept()
        
        def Text_func(a1: QMouseEvent):
            clicked_label.add(parent,a1.pos()+label.pos())
            a1.accept()
        
        def Button_func(a1:QMouseEvent):
            if mousePressTarget.LeftCommand != None:
                mousePressTarget.LeftCommand()
            if not sip.isdeleted(mousePressTarget):
                self.add(parent,label.pos()+a1.pos(),mousePressTarget)
            a1.accept()
        
        label = Label(parent,[a0.x(),a0.y(),0,0],image=p.scaled(0,0),style="background:transparent;")
        if not mousePressTarget is None:
            label.mousePressEvent = Button_func
        elif type(parent) ==QtWidgets.QWidget:
            label.mousePressEvent = Wid_func
        else:
            label.mousePressEvent = Text_func
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


def add_func_500(key: str, func):
    global func_500
    func_500.update({key:func})

def add_func_1000(key:str, func):
    global func_1000
    func_1000.update({key:func})

def del_func_500(key):
    global func_500
    if key in func_500:
        del func_500[key]

def del_func_1000(key):
    global func_1000
    if key in func_1000:
        del func_1000[key]

def connect_500():
    list(map(lambda x: x(), list(func_500.values())))

def connect_1000():
    list(map(lambda x: x(), list(func_1000.values())))

def main_window_clicked(a0: QMouseEvent):
    clicked_label.add(main_window,a0.pos())
    a0.accept()

def music_list_show():
    listbox.setVisible(not listbox.isVisible())

modes=["all_once","all_infinite","one_infinite"]
data = Json_Data()
inter = Interaction()
app = QtWidgets.QApplication(sys.argv)
data_set = data.set
app.setApplicationName(data_set["title"])
app.setWindowIcon(QIcon(r".\init_file\music.ico"))
Page = Page_Organize()
func_500 = {}
func_1000 = {}
timer_1000 = QTimer()
timer_1000.timeout.connect(connect_1000)
timer_1000.start(1000)
timer_500 = QTimer()
timer_500.timeout.connect(connect_500)
timer_500.start(500)
clicked_label = ClickedLabel()
Music = MusicPlayer()
V_date = Valuable("")
V_time = Valuable("")
V_play = Valuable()
V_state = Valuable(bool(data_set["dark"]))
p = QPixmap(f"{path}clicked.png")
widget = data.style[int(V_state.get())]
colors = data.color[int(V_state.get())]
color_alpha = list(colors["none"])
color = f"rgb({', '.join(map(str,color_alpha))})"
color_alpha2 = list(colors["normal"])
color2 = f"rgb({','.join(map(str,color_alpha2))})"
color_bg = colors["bg"]
m = app.screens()[0].size()
main_window = QtWidgets.QWidget()
main_window.destroyed.connect(destroyed)
main_window.mousePressEvent = main_window_clicked
main_window.setWindowTitle(data_set["title"])
main_window.setWindowFlags(types.FramelessWindowHint|types.WindowStaysOnBottomHint|types.MaximizeUsingFullscreenGeometryHint)
WebWidget = None
web_url = QUrl("https://www.google.com/")
if data_set["cursor"]!="":
    pixmap = QPixmap(data_set["cursor"])
    pixmap = pixmap.scaled(30, 30)
    cursor = QtGui.QCursor(pixmap,0,0)
    main_window.setCursor(cursor)
bg_path = data_set["Background"]
if os.path.isdir(bg_path) and len(list_bg := os.listdir(bg_path))>0:
    bg_path +="/"+random.choice(list_bg)
bg = Label(main_window, [0, 0, m.width(), m.height()])
bg.show()
l0 = Label(bg, [0, 0, 260, m.height()],style=f"background:rgba({', '.join(map(str,color_alpha))},0.6);")
op = QtWidgets.QGraphicsBlurEffect()
op.setBlurRadius(Page.BackgroundBlur)
op.setBlurHints(op.BlurHint.QualityHint)
l0.setGraphicsEffect(op)
l0.setAttribute(Qt.WidgetAttribute.WA_TintedBackground, True)
l0.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
l0.show()
background_blur_show(bg_path)
style0 = "font-family:Arial;color:#FFAEC9;background-color: transparent;"
WLtime = Label(main_window, [0, 0, 250, 40], style=style0 + "font-size:42pt;", text="")
WLtime.setAlignment(align.AlignCenter)
V_time.add(WLtime)
WLdate = Label(main_window,[0, 43, 250, 20],text=" ",style=style0 + "text-decoration:underline; font-size:15pt;",)
WLdate.setAlignment(align.AlignCenter)
V_date.add(WLdate)
g1 = NoTitleWidget(main_window,"page",320,50)
Label(g1,[2,15,6,20],style=f"background:{color2};",text=" ")
Label(g1,[0,0,320,50],style=f"background:rgba({', '.join(map(str,color_alpha))}, 0.6);border-radius:25px;")
button_style=f"QPushButton {{background:{color};color:{color_bg};border-radius:5px;border:1px solid {color_bg};}} QPushButton:hover {{color:{color_bg};background:rgba({color_alpha[0]}, {color_alpha[1]}, {color_alpha[2]}, 0.4);}}"
Button(g1,[10, 0, 50, 50],lambda: Page.todo(),image=QIcon(f"{path}icon\\todo.png"),style="background:transparent;").show()
Button(g1,[60, 0, 50, 50],lambda: Page.dic(),image=QIcon(f"{path}icon\\dict.png"),style="background:transparent;").show()
Button(g1,[110, 0, 50, 50],lambda: Page.learn(),image=QIcon(f"{path}icon\\learn.png"),style="background:transparent;").show()
Button(g1,[160, 0, 50, 50],lambda: Page.classes(),image=QIcon(f"{path}icon\\class.png"),style="background:transparent;").show()
Button(g1,[210, 0, 50, 50],lambda: Page.page["exe"].setVisible(True),image=QIcon(f"{path}icon\\exec.png"),style="background:transparent;").show()
Button(g1,[260, 10, 30, 30],lambda: Page.set(),image=QIcon(f"{path}icon\\set.png"),style=style0,).show()
Button(g1,[290, 10, 30, 30],lambda: Page.addiction(),text="⿻",style="font-family:Arial;color:#d48649;background-color: transparent;font-size:29px;",).show()
Page.exe()
Button(main_window, [m.width() - 42, 0, 20, 20], main_window.showMinimized, text="-").show()
Button(main_window, [m.width() - 20, 0, 20, 20], destroy, text="x").show()
WeatherWin = WID(main_window,f"background:rgba({color_alpha[0]},{color_alpha[1]},{color_alpha[2]},0.8);",0,70,250,180)
WeatherWin.setAttribute(Attribute.WA_StyledBackground,True)
Button(WeatherWin,[160,0,30,30],weather,image=QIcon(f"{path}home\\point.png"),style="background:#00000000;").show()
style_label = f"background:#00000000;color:{color2};font-family:Fira Code Retina;font-size:"
Position = Label(WeatherWin,[190,0,60,30],"",style=style_label+"20px;")
Position.show()
weather_dict:list[list[Label]] = []
pop_image = QPixmap(f"{path}home\\pop.png")
for i in range(0,3):
    y = 10+i*50
    Weather = Label(WeatherWin,[0,y+3,160,20],"",style=style_label+"17px;")
    Weather.show()
    Label(WeatherWin,[0,y+20,20,20],image=pop_image,style="background:#00000000;").show()
    Pop = Label(WeatherWin,[20,y+20,90,20],"",style=style_label+"20px;")
    Pop.show()
    Temperature = Label(WeatherWin,[140,y+20,130,20],"",style=style_label+"20px;")
    Temperature.show()
    weather_dict.append([Weather,Temperature,Pop])
WeatherWin.show()
Todo_Win = NoTitleWidget(main_window, "todo", 250, 290)
Todo_Win.setStyleSheet("background:transparent;")
calendar_style0=f"""
    QCalendarWidget QWidget {{
        background:#ffa040;
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
        color:#ffffff;
        background:#ffa040;
    }}
"""
calendar_style1 = f"""
    QCalendarWidget QWidget {{
        background:{color};
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
calendar = CalendarWidget(Todo_Win,[0, 0, 250, 200],show_todo,calendar_style0)
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
text_home.setLineWrapMode(text_home.LineWrapMode.NoWrap)
text_home.setReadOnly(True)
show_todo()
Song_Win = NoTitleWidget(main_window, "song", 250, 330)
Button(Song_Win,[0,0,30,30],music_list_show,image=QIcon(f"{path}icon\\music.png"),style="background:transparent;").show()
combo = Combo(Song_Win, "Arial", 15, 8, True,geometry=[30, 0, 100, 30])
combo.textActivated.connect(lambda:com(combo))
Button(Song_Win,[150, 0, 25, 25],edit,image=QIcon(f"{path}icon\\編輯.png"),style="background:transparent;",).show()
Button(Song_Win,[175, 0, 25, 25],add_music,image=QIcon(f"{path}icon\\加入.png"),style="background:transparent;",).show()
Button(Song_Win,[200, 0, 25, 25],delete_list,text="刪除\n清單",style="background:transparent;color:#AA5F39;font-family:Arial;font-size:8pt;").show()
Button(Song_Win,[225, 0, 25, 25],add_list,text="加入\n清單",style="background:transparent;color:#AA5F39;font-family:Arial;font-size:8pt;").show()
song_home = Label(Song_Win, [40, 30, 250, 30], text=Music.song.get(), style=style0 + "font-size:12pt;")
Music.song.add(song_home)
l = Label(Song_Win,[0,65,70,25],text="00:00/00:00",style="color:#ffffff;font-family:Arial;font-size:10pt;")
Music.show_duration.add(l)
Button(Song_Win,[70, 65, 15, 15],last,image=QIcon(f"{path}home\\last.png"),style="background:transparent;").show()
button_play = Button(Song_Win,[100, 60, 25, 25],music_play,image=QIcon(f"{path}icon\\播放.png"),style="background:transparent;",)
button_play.show()
Music.set_button("music", button_play)
background = f"rgba({color_alpha[0]}, {color_alpha[1]}, {color_alpha[2]},0.46)"
Button(Song_Win,[125, 60, 25, 25],lambda: Music.stop_list(),image=QIcon(f"{path}icon\\停止.png"),style="background:transparent;",).show()
Button(Song_Win,[165, 65, 15, 15],next_music,image=QIcon(f"{path}home\\next.png"),style="background-color:transparent;").show()
mode = Button(Song_Win,[225, 60, 25, 25],image=QIcon(f"{path}home\\{Music.mode}.png"),style="background-color:transparent;",)
mode.LeftCommand=lambda:set_play_mode(mode)
mode.show()
slider = Slider(Song_Win, 5, 85, 240, 20)
slider.actionTriggered.connect(lambda:Music.slider_change(slider))
Music.add_slider(slider)
listbox = QtWidgets.QListWidget(Song_Win)
listbox.setGeometry(0, 105, 250, 200)
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
for i in [g1,Todo_Win,text_home,Song_Win,combo,slider,]:
    i.show()
weather()
clock()
add_func_1000("clock",clock)
main_window.showMaximized()
sys.exit(app.exec())
