from PyQt5 import  QtGui, QtWidgets,QtCore
from PyQt5.QtCore import QTimer,QDateTime
from PyQt5.QtWidgets import QMessageBox,QFileDialog,QColorDialog
from PyQt5.QtGui import QImage, QPixmap,QIcon
import sys
import cv2
import UI
import test
import time
import numpy as np
user_config = r"user_config.txt"


class period_weather_predict(QtWidgets.QMainWindow, UI.Ui_MainWindow):
    def __init__(self, config):
        super(period_weather_predict, self).__init__()
        self.setWindowIcon(QIcon('./icon/logo.ico'))
        self.video_writer = cv2.VideoWriter()
        self.setupUi(self)  # 创建窗体对象
        self.config = config
        self.init(self.config)
        self.cap = cv2.VideoCapture()  # 摄像头
        self.cap2 = cv2.VideoCapture()  # 视频
        self.showtime()
        self.is_switching = False
        self.is_pause = True
        self.time_blue, self.time_green, self.time_red = self.config["time_bgr"]
        self.predict_blue, self.predict_green, self.predict_red = self.config["predict_bgr"]
        self.path = self.config['save_path']
        self.x = 0
        self.image_text = 0
        self.period_dict = {'Morning': '上午', 'Afternoon': '下午', 'Dawn': '黄昏', 'Dusk': '夜晚'}
        self.weather_dict = {'Cloudy': '阴天', 'Sunny': '晴天', 'Rainy': '雨天'}


    def init(self,config):
        # 定时器让其定时读取显示图片(设置刷新时间用的槽)
        self.camera_timer = QTimer()
        self.camera_timer.timeout.connect(self.show_camera_image)
        self.video_timer = QTimer()
        self.video_timer.timeout.connect(self.show_local_video)
        self.timer = QTimer()
        self.timer.timeout.connect(self.showtime)
        # 暂停视频
        self.button_pause.clicked.connect(self.video_pause)
        # 关闭摄像头
        self.button_reset.clicked.connect(self.reset)
        # 传入图片
        self.button_open_image.clicked.connect(self.open_image)
        # 传入视频
        self.button_open_video.clicked.connect(self.open_video)
        # 打开摄像头
        self.button_open_camera.clicked.connect(self.open_camera)
        # 设置结果颜色
        self.button_predict_color.clicked.connect(self.open_predict_color_choose)
        # 设置时间颜色
        self.button_time_color.clicked.connect(self.open_time_color_choose)
        # 更改保存路径
        self.button_change_path.clicked.connect(self.change_path)

        #使用保存的用户配置初始化
        # "{"pic_box": True/False, "time_box":True/False, "save_box": True/False}"
        # 将结果显示在图片上
        self.checkbox_pic.setChecked(self.config["pic_box"])
        self.checkbox_pic.clicked.connect(self.checkbox)
        # 将时间显示在图片上
        self.checkbox_time.setChecked(self.config["time_box"])
        self.checkbox_time.clicked.connect(self.checkbox2)
        # 图像是否翻转
        self.checkbox_flip.setChecked(self.config["flip_box"])
        self.checkbox_flip.clicked.connect(self.checkbox3)
        # 是否保存摄像头视频
        self.checkbox_video_write.setChecked(self.config["save_box"])
        self.checkbox_video_write.clicked.connect(self.video_write)
        # 切换背景至夜间模式
        self.checkbox_change_ui.setChecked(self.config["background_box"])
        self.checkbox_change_ui.clicked.connect(self.change_ui)

    '''加载图片并预测'''
    def open_image(self):
        if  self.cap2.isOpened():
            QMessageBox.critical(self, '错误', '请先关闭视频')
        elif   self.cap.isOpened():
            QMessageBox.critical(self, '错误', '请先关闭摄像头')
        else:
            local_image, _ = QFileDialog.getOpenFileName(self, '打开文件', '.', '图像文件(*.jpg *.png)')
            if  local_image=='':
                return None
            else:
                self.image_text = 1
                weather_period = test.image_predict(local_image)
                list_weather_period = list(weather_period)
                weather_period = str(weather_period)
                self.pre_weather.setText(self.weather_dict.get(list_weather_period[1]))
                self.pre_period.setText(self.period_dict.get(list_weather_period[0]))
                if list_weather_period[1] == 'Cloudy' and list_weather_period[0] != 'Dusk':
                    day_Cloudy = QPixmap("./icon/阴天.png")
                    day_Cloudy = day_Cloudy.scaled(45, 45)
                    self.label_8.setPixmap(day_Cloudy)
                if list_weather_period[1] == 'Cloudy' and list_weather_period[0] == 'Dusk':
                    night_Cloudy = QPixmap("./icon/阴天(夜).png")
                    night_Cloudy = night_Cloudy.scaled(45, 45)
                    self.label_8.setPixmap(night_Cloudy)
                if list_weather_period[1] == 'Sunny' and list_weather_period[0] != 'Dusk':
                    day_sun = QPixmap("./icon/晴天.png")
                    day_sun = day_sun.scaled(45, 45)
                    self.label_8.setPixmap(day_sun)
                if list_weather_period[1] == 'Sunny' and list_weather_period[0] == 'Dusk':
                    night_sun = QPixmap("./icon/夜晚.png")
                    night_sun = night_sun.scaled(40, 40)
                    self.label_8.setPixmap(night_sun)
                if list_weather_period[1] == 'Rainy':
                    rainy = QPixmap("./icon/下雨.png")
                    rainy = rainy.scaled(45, 45)
                    self.label_8.setPixmap(rainy)
                if list_weather_period[0] == 'Morning':
                    morning = QPixmap("./icon/上午.png")
                    morning = morning.scaled(45, 45)
                    self.label_12.setPixmap(morning)
                if list_weather_period[0] == 'Afternoon':
                    afternoon = QPixmap("./icon/下午.png")
                    afternoon = afternoon.scaled(45, 45)
                    self.label_12.setPixmap(afternoon)
                if list_weather_period[0] == 'Dawn' or list_weather_period[0] == 'Dusk':
                    night = QPixmap("./icon/夜晚(时间).png")
                    night = night.scaled(45, 45)
                    self.label_12.setPixmap(night)
                self.statusbar.showMessage('识别完成！    当前模式：图片     检测图片路径：' + local_image)
                local_image = cv2.imdecode(np.fromfile(local_image, dtype=np.uint8),-1)  # 巨坑
                local_image = cv2.resize(local_image, (640, 480))  # 把读到的帧的大小重新设置为 640x480
                if self.checkbox_flip.isChecked():
                    local_image = cv2.flip(local_image, 1)  # 水平翻转，因为摄像头拍的是镜像的。
                if self.checkbox_time.isChecked():
                    local_image = cv2.putText(local_image, str(self.timedisplay), (450, 20), cv2.FONT_HERSHEY_SIMPLEX,0.5, (self.time_red, self.time_green, self.time_blue), 1)
                if self.checkbox_pic.isChecked():
                    local_image = cv2.putText(local_image, weather_period, (0, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(self.predict_red, self.predict_green, self.predict_blue), 1)
                local_image = cv2.cvtColor(local_image, cv2.COLOR_BGR2RGB)
                width, height = local_image.shape[:2]  # 行:宽，列:高
                local_image = QtGui.QImage(local_image.data, height, width, QImage.Format_RGB888)
                self.label.setPixmap(QPixmap(local_image))
                self.label_11.setText("<html><head/><body><p><span style=\" font-size:16pt;\">当前模式：图片</span></p></body></html>")


    '''开启摄像头'''
    def open_camera(self):
        if  self.cap2.isOpened():
            QMessageBox.critical(self, '错误', '请先关闭视频')
        elif  self.cap.isOpened():
            return None
        else:
            # self.cap = cv2.VideoCapture()
            self.cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)  # 摄像头
            if  self.cap.isOpened():
                if  self.checkbox_video_write.isChecked():
                    w, h, save_path = self.set_video_name_and_path()
                    fps = 25
                    self.video_writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
                self.image_text = 0
                self.statusbar.showMessage('正在识别...    当前模式：摄像头')
                self.camera_timer.start(40)  # 每40毫秒读取一次，即刷新率为25帧
                self.show_camera_image()
            else:
                QMessageBox.critical(self, '错误', '未检测到摄像头')
                return None


    '''显示图像'''
    def show_camera_image(self):
        reg, camera_image = self.cap.read()  # 从视频流中读取图片
        camera_image = test.tf.convert_to_tensor(camera_image)
        weather_period = test.camera_predict(camera_image)
        list_weather_period = list(weather_period)
        weather_period = str(weather_period)
        self.pre_weather.setText(self.weather_dict.get(list_weather_period[1]))
        self.pre_period.setText(self.period_dict.get(list_weather_period[0]))
        if list_weather_period[1] == 'Cloudy' and list_weather_period[0] != 'Dusk':
            day_Cloudy = QPixmap("./icon/阴天.png")
            day_Cloudy = day_Cloudy.scaled(45, 45)
            self.label_8.setPixmap(day_Cloudy)
            self.label_4.setText('祝您一路顺风')
        if list_weather_period[1] == 'Cloudy' and list_weather_period[0] == 'Dusk':
            night_Cloudy = QPixmap("./icon/阴天(夜).png")
            night_Cloudy = night_Cloudy.scaled(45, 45)
            self.label_8.setPixmap(night_Cloudy)
            self.label_4.setText('夜间行驶，请尽量使用近光灯\n注意前方路况，控制车速')
        if list_weather_period[1] == 'Sunny' and list_weather_period[0] != 'Dusk':
            day_sun = QPixmap("./icon/晴天.png")
            day_sun = day_sun.scaled(45, 45)
            self.label_8.setPixmap(day_sun)
            self.label_4.setText('阳光刺眼，您可以放下遮阳板或带上墨镜')
        if list_weather_period[1] == 'Sunny' and list_weather_period[0] == 'Dusk':
            night_sun = QPixmap("./icon/夜晚.png")
            night_sun = night_sun.scaled(40, 40)
            self.label_8.setPixmap(night_sun)
            self.label_4.setText('夜间行驶，请尽量使用近光灯\n注意前方路况，控制车速')
        if list_weather_period[1] == 'Rainy':
            rainy = QPixmap("./icon/下雨.png")
            rainy = rainy.scaled(45, 45)
            self.label_8.setPixmap(rainy)
            self.label_4.setText('雨天行驶，路面湿滑\n请减慢车速，保持一定车距')
        if list_weather_period[0] == 'Morning':
            morning = QPixmap("./icon/上午.png")
            morning = morning.scaled(45, 45)
            self.label_12.setPixmap(morning)
        if list_weather_period[0] == 'Afternoon':
            afternoon = QPixmap("./icon/下午.png")
            afternoon = afternoon.scaled(45, 45)
            self.label_12.setPixmap(afternoon)
        if list_weather_period[0] == 'Dawn' or list_weather_period[0] == 'Dusk':
            night = QPixmap("./icon/夜晚(时间).png")
            night = night.scaled(45, 45)
            self.label_12.setPixmap(night)
        camera_image = test.np.array(camera_image)
        camera_image = cv2.resize(camera_image, (640, 480))  # 把读到的帧的大小重新设置为 640x480
        if self.checkbox_flip.isChecked():
            camera_image = cv2.flip(camera_image, 1)  # 水平翻转，因为摄像头拍的是镜像的。
        if self.checkbox_time.isChecked():
            camera_image = cv2.putText(camera_image, str(self.timedisplay), (450, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(self.time_red, self.time_green, self.time_blue), 1)
        if self.checkbox_pic.isChecked():
            camera_image = cv2.putText(camera_image, weather_period, (0, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(self.predict_red, self.predict_green, self.predict_blue), 1)
        width, height = camera_image.shape[:2]  # 行:宽，列:高
        if self.checkbox_video_write.isChecked():
            self.video_writer.write(camera_image)  #将摄像头图像写成视频
        camera_image = cv2.cvtColor(camera_image, cv2.COLOR_BGR2RGB)  # opencv读的通道是BGR,要转成RGB
        # 把读取到的视频数据变成QImage形式(图片数据、高、宽、RGB颜色空间，三个通道各有2**8=256种颜色)
        camera_image = QtGui.QImage(camera_image.data, height, width, QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(camera_image))  # 往显示视频的Label里显示QImage
        self.label_11.setText("<html><head/><body><p><span style=\" font-size:16pt;\">当前模式：摄像头</span></p></body></html>")


    '''输入视频'''
    def open_video(self):
        if  self.cap.isOpened():
            QMessageBox.critical(self, '错误', '请先关闭摄像头')
        else:
            local_video, _ = QFileDialog.getOpenFileName(self, '打开文件', '.', '图像文件(*.mp4 *.flv)')
            if local_video=='':
                return None
            else:
                self.local_video_path = local_video
                self.cap2 = cv2.VideoCapture(local_video)  # 视频
                rate = self.cap2.get(5)  # 帧速率
                FrameNumber = self.cap2.get(7)  # 视频文件的帧数
                self.duration = FrameNumber / rate  # 帧速率/视频总帧数 是时间，除以60之后单位是分钟
                self.y = 1000 / rate /10
                self.x = 0
                self.statusbar.showMessage('正在识别...    当前模式：视频      检测视频路径：' + self.local_video_path)
                self.image_text = 0
                self.is_pause = True
                if self.checkbox_change_ui.isChecked():
                    icon3 = QtGui.QIcon()
                    icon3.addPixmap(QtGui.QPixmap("./icon/暂停播放(1).png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                    self.button_pause.setIconSize(QtCore.QSize(30, 30))
                    self.button_pause.setIcon(icon3)
                else:
                    icon3 = QtGui.QIcon()
                    icon3.addPixmap(QtGui.QPixmap("./icon/暂停播放.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                    self.button_pause.setIconSize(QtCore.QSize(30, 30))
                    self.button_pause.setIcon(icon3)
                self.video_timer.start(40)  # 每40毫秒读取一次，即刷新率为25帧
                self.show_local_video()


    def show_local_video(self):
        reg, local_video = self.cap2.read()  # 从视频流中读取图片
        if not reg:
            self.camera_timer.stop()  # 停止读取
            self.cap.release()
            self.statusbar.showMessage('识别完成！    当前模式：视频      检测视频路径：' + self.local_video_path)
            return
        self.x += self.y / self.duration
        self.progressBar.setProperty("value",self.x)
        local_video = test.tf.convert_to_tensor(local_video)
        weather_period = test.vedio_predict(local_video)            #************************************************************************
        list_weather_period = list(weather_period)
        weather_period = str(weather_period)
        self.pre_weather.setText(self.weather_dict.get(list_weather_period[1]))
        self.pre_period.setText(self.period_dict.get(list_weather_period[0]))
        if list_weather_period[1] == 'Cloudy' and list_weather_period[0] != 'Dusk':
            day_Cloudy = QPixmap("./icon/阴天.png")
            day_Cloudy = day_Cloudy.scaled(45, 45)
            self.label_8.setPixmap(day_Cloudy)
        if list_weather_period[1] == 'Cloudy' and list_weather_period[0] == 'Dusk':
            night_Cloudy = QPixmap("./icon/阴天(夜).png")
            night_Cloudy = night_Cloudy.scaled(45, 45)
            self.label_8.setPixmap(night_Cloudy)
        if list_weather_period[1] == 'Sunny' and list_weather_period[0] != 'Dusk':
            day_sun = QPixmap("./icon/晴天.png")
            day_sun = day_sun.scaled(45, 45)
            self.label_8.setPixmap(day_sun)
        if list_weather_period[1] == 'Sunny' and list_weather_period[0] == 'Dusk':
            night_sun = QPixmap("./icon/夜晚.png")
            night_sun = night_sun.scaled(40, 40)
            self.label_8.setPixmap(night_sun)
        if list_weather_period[1] == 'Rainy':
            rainy = QPixmap("./icon/下雨.png")
            rainy = rainy.scaled(45, 45)
            self.label_8.setPixmap(rainy)
        if list_weather_period[0] == 'Morning':
            morning = QPixmap("./icon/上午.png")
            morning = morning.scaled(45, 45)
            self.label_12.setPixmap(morning)
        if list_weather_period[0] == 'Afternoon':
            afternoon = QPixmap("./icon/下午.png")
            afternoon = afternoon.scaled(45, 45)
            self.label_12.setPixmap(afternoon)
        if list_weather_period[0] == 'Dawn' or list_weather_period[0] == 'Dusk':
            night = QPixmap("./icon/夜晚(时间).png")
            night = night.scaled(45, 45)
            self.label_12.setPixmap(night)
        local_video = test.np.array(local_video)
        local_video = cv2.resize(local_video, (640, 480))  # 把读到的帧的大小重新设置为
        if  self.checkbox_flip.isChecked():
            local_video = cv2.flip(local_video, 1)  # 水平翻转，因为摄像头拍的是镜像的。
        if self.checkbox_time.isChecked():
            local_video = cv2.putText(local_video, str(self.timedisplay), (450, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(self.time_red, self.time_green, self.time_blue), 1)
        if self.checkbox_pic.isChecked():
            local_video = cv2.putText(local_video, weather_period, (0, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(self.predict_red, self.predict_green, self.predict_blue), 1)
        width, height = local_video.shape[:2]  # 行:宽，列:高
        local_video = cv2.cvtColor(local_video, cv2.COLOR_BGR2RGB)  # opencv读的通道是BGR,要转成RGB
        # 把读取到的视频数据变成QImage形式(图片数据、高、宽、RGB颜色空间，三个通道各有2**8=256种颜色)
        local_video = QtGui.QImage(local_video.data, height, width, QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(local_video))  # 往显示视频的Label里显示QImage
        self.label_11.setText("<html><head/><body><p><span style=\" font-size:16pt;\">当前模式：视频</span></p></body></html>")


    def reset(self):
            _translate = QtCore.QCoreApplication.translate
            self.camera_timer.stop()  # 停止读取
            self.cap.release()  # 释放摄像头
            self.video_timer.stop()  # 停止读取
            self.cap2.release()  # 释放视频
            self.video_writer.release()  #释放写视频
            self.label.clear()  # 清除label组件上的图片
            self.label_4.setText("<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">祝您一路顺风</span></p></body></html>")
            # self.label_4.setText('祝您一路顺风')
            self.label_8.clear()
            self.label_12.clear()
            self.progressBar.setProperty("value", 0)
            if self.checkbox_change_ui.isChecked():
                icon3 = QtGui.QIcon()
                icon3.addPixmap(QtGui.QPixmap("./icon/暂停播放(1).png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                self.button_pause.setIconSize(QtCore.QSize(30, 30))
                self.button_pause.setIcon(icon3)
            else:
                icon3 = QtGui.QIcon()
                icon3.addPixmap(QtGui.QPixmap("./icon/暂停播放.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                self.button_pause.setIconSize(QtCore.QSize(30, 30))
                self.button_pause.setIcon(icon3)
            self.is_pause = True
            #重置文本
            self.image_text = 0
            self.label_11.setText("<html><head/><body><p><span style=\" font-size:16pt;\">当前模式：</span></p></body></html>")
            self.statusbar.showMessage('')
            self.pre_weather.setText('')
            self.pre_period.setText('')
            self.x = 0


    def showtime(self):
        self.timer.start(40)
        self.updatetime()


    def updatetime(self):
        self.time = QDateTime.currentDateTime()  # 获取当前时间
        self.timedisplay = self.time.toString("yyyy-MM-dd hh:mm:ss")  # 格式化一下时间
        self.label_3.setText(self.timedisplay)


    def checkbox(self):
        if self.checkbox_pic.isChecked():
            self.config["pic_box"] = True
            f = open(r"user_config.txt", "w", encoding="utf-8")
            f.write(str(config))
            f.close()
        else:
            self.config["pic_box"] = False
            f = open(r"user_config.txt", "w", encoding="utf-8")
            f.write(str(config))
            f.close()
        return None


    def checkbox2(self):
        if self.checkbox_time.isChecked():
            self.config["time_box"] = True
            f = open(r"user_config.txt", "w", encoding="utf-8")
            f.write(str(config))
            f.close()
        else:
            self.config["time_box"] = False
            f = open(r"user_config.txt", "w", encoding="utf-8")
            f.write(str(config))
            f.close()
        return None


    def checkbox3(self):
        if self.checkbox_flip.isChecked():
            self.config["flip_box"] = True
            f = open(r"user_config.txt", "w", encoding="utf-8")
            f.write(str(config))
            f.close()
        else:
            self.config["flip_box"] = False
            f = open(r"user_config.txt", "w", encoding="utf-8")
            f.write(str(config))
            f.close()
        return None


    def set_video_name_and_path(self):
        # 获取当前系统时间，作为img和video的文件名
        now = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(time.time()))
        w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        # 视频检测结果存储位置

        save_path = self.path +'/' + now + '.mp4'
        return w, h, save_path


    def update_video_write(self):
        self.timer.start(1000)
        self.video_write()


    def video_write(self):
        if self.checkbox_video_write.isChecked():
            self.config["save_box"] = True
            f = open(r"user_config.txt", "w", encoding="utf-8")
            f.write(str(config))
            f.close()
        else:
            self.config["save_box"] = False
            f = open(r"user_config.txt", "w", encoding="utf-8")
            f.write(str(config))
            f.close()
        if self.checkbox_video_write.isChecked() and self.cap.isOpened():
            w, h, save_path = self.set_video_name_and_path()
            fps = 25
            self.video_writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
        else:
            return None


    def video_pause(self):
        if self.cap2.isOpened():
            if self.is_pause or self.is_switching:
                if self.checkbox_change_ui.isChecked():
                    icon3 = QtGui.QIcon()
                    icon3.addPixmap(QtGui.QPixmap("./icon/播放 (1).png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                    self.button_pause.setIconSize(QtCore.QSize(30, 30))
                    self.button_pause.setIcon(icon3)
                else:
                    icon3 = QtGui.QIcon()
                    icon3.addPixmap(QtGui.QPixmap("./icon/播放.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                    self.button_pause.setIconSize(QtCore.QSize(30, 30))
                    self.button_pause.setIcon(icon3)
                self.video_timer.stop()
                self.is_pause = False
            elif (not self.is_pause) and (not self.is_switching):
                if self.checkbox_change_ui.isChecked():
                    icon3 = QtGui.QIcon()
                    icon3.addPixmap(QtGui.QPixmap("./icon/暂停播放(1).png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                    self.button_pause.setIconSize(QtCore.QSize(30, 30))
                    self.button_pause.setIcon(icon3)
                else:
                    icon3 = QtGui.QIcon()
                    icon3.addPixmap(QtGui.QPixmap("./icon/暂停播放.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                    self.button_pause.setIconSize(QtCore.QSize(30, 30))
                    self.button_pause.setIcon(icon3)
                self.video_timer.start()
                self.is_pause = True
        else:return None


    def open_time_color_choose(self):
        qcolor = QColorDialog.getColor()
        if not qcolor.isValid():
            return None
        else:
            self.time_blue, self.time_green, self.time_red, _ = qcolor.getRgb()
            self.config["time_bgr"] = [self.time_blue, self.time_green, self.time_red]
            f = open(r"user_config.txt", "w", encoding="utf-8")
            f.write(str(config))
            f.close()
            return self.time_blue, self.time_green, self.time_red


    def open_predict_color_choose(self):
        qcolor = QColorDialog.getColor()
        if not qcolor.isValid():
            return None
        else:
            self.predict_blue, self.predict_green, self.predict_red, _ = qcolor.getRgb()
            self.config["predict_bgr"] = [self.predict_blue, self.predict_green, self.predict_red]
            f = open(r"user_config.txt", "w", encoding="utf-8")
            f.write(str(config))
            f.close()
            return self.predict_blue, self.predict_green, self.predict_red


    def change_path(self):
        self.path = QFileDialog.getExistingDirectory(self, '选择路径', 'C:/')
        self.config["save_path"] = self.path
        f = open(r"user_config.txt", "w", encoding="utf-8")
        f.write(str(config))
        f.close()
        return self.path


    def change_ui(self):
        if self.checkbox_change_ui.isChecked():
            self.config["background_box"] = True
            f = open(r"user_config.txt", "w", encoding="utf-8")
            f.write(str(config))
            f.close()
            self.centralwidget.setStyleSheet("background-color: rgb(048,048,048)")
            self.label_7.setStyleSheet("color: rgb(255, 255, 255)")
            self.label_8.setStyleSheet("background-color:rgb(125,125,125)")
            self.label_11.setStyleSheet("color: rgb(255, 255, 255)")
            self.checkbox_time.setStyleSheet("color: rgb(255, 255, 255); ")
            self.checkbox_video_write.setStyleSheet("color: rgb(255, 255, 255); ")
            self.checkbox_flip.setStyleSheet("color: rgb(255, 255, 255); ")
            self.checkbox_change_ui.setStyleSheet("color: rgb(255, 255, 255); ")
            self.checkbox_pic.setStyleSheet("color: rgb(255, 255, 255); ")
            self.label_12.setStyleSheet("background-color:rgb(125,125,125)")
            self.button_time_color.setStyleSheet("background-color:rgb(125,125,125);\n"
            "border-radius: 10px")
            self.button_predict_color.setStyleSheet("background-color:rgb(125,125,125);\n"
            "border-radius: 10px")
            self.button_change_path.setStyleSheet("background-color:rgb(125,125,125);\n"
            "border-radius: 10px")
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap("icon/文件夹 (1).png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.button_open_image.setIcon(icon)
            self.button_open_image.setIconSize(QtCore.QSize(30, 30))
            icon1 = QtGui.QIcon()
            icon1.addPixmap(QtGui.QPixmap("icon/视频播放 (1).png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.button_open_video.setIcon(icon1)
            self.button_open_video.setIconSize(QtCore.QSize(35, 35))
            icon2 = QtGui.QIcon()
            icon2.addPixmap(QtGui.QPixmap("icon/卡口视频摄像头,监控,桌面摄像头,网络摄像头 (3).png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.button_open_camera.setIcon(icon2)
            self.button_open_camera.setIconSize(QtCore.QSize(30, 30))
            self.pre_weather.setStyleSheet("background-color:rgb(125,125,125);\n"
                                           "color:rgb(255,255,255)")
            self.weather.setStyleSheet("background-color:rgb(125,125,125)")
            self.period.setStyleSheet("background-color:rgb(125,125,125)")
            self.pre_period.setStyleSheet("background-color:rgb(125,125,125);\n"
                                          "color:rgb(255,255,255)")
            self.label_4.setStyleSheet("background-color:rgb(125,125,125);\n"
                                       "color:rgb(255,255,255)")
            self.label_3.setStyleSheet("color:rgb(255,255,255)")
            if self.is_pause == False:
                icon3 = QtGui.QIcon()
                icon3.addPixmap(QtGui.QPixmap("./icon/播放 (1).png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                self.button_pause.setIcon(icon3)
                self.button_pause.setIconSize(QtCore.QSize(30, 30))
            else:
                icon3 = QtGui.QIcon()
                icon3.addPixmap(QtGui.QPixmap("icon/暂停播放(1).png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                self.button_pause.setIcon(icon3)
                self.button_pause.setIconSize(QtCore.QSize(30, 30))
            icon4 = QtGui.QIcon()
            icon4.addPixmap(QtGui.QPixmap("icon/停止 (1).png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.button_reset.setIcon(icon4)
            self.button_reset.setIconSize(QtCore.QSize(30, 30))
            _translate = QtCore.QCoreApplication.translate
            self.label_6.setText(_translate("MainWindow","<html><head/><body><p><span style=\" font-size:18pt; color:#ffffff;\">切换模式</span></p></body></html>"))
            if self.image_text == 1:
                self.label_11.setText(_translate("MainWindow","<html><head/><body><p><span style=\" font-size:16pt; color:#ffffff;\">当前模式：图片</span></p></body></html>"))
            elif self.cap2.isOpened():
                self.label_11.setText(_translate("MainWindow","<html><head/><body><p><span style=\" font-size:16pt; color:#ffffff;\">当前模式：视频</span></p></body></html>"))
            elif self.cap.isOpened():
                self.label_11.setText(_translate("MainWindow","<html><head/><body><p><span style=\" font-size:16pt; color:#ffffff;\">当前模式：摄像头</span></p></body></html>"))
            else:
                self.label_11.setText(_translate("MainWindow","<html><head/><body><p><span style=\" font-size:16pt; color:#ffffff;\">当前模式：</span></p></body></html>"))
            self.label_2.setText(_translate("MainWindow","<html><head/><body><p><span style=\" font-size:16pt; color:#ffffff;\">当前时间：</span></p></body></html>"))
            self.label_3.setText(_translate("MainWindow","<html><head/><body><p><span style=\" font-size:14pt; color:#ffffff;\"></span></p></body></html>"))
            self.label_9.setText(_translate("MainWindow","<html><head/><body><p><span style=\" font-size:18pt; color:#ffffff;\">设置</span></p></body></html>"))
            self.weather.setText(_translate("MainWindow","<html><head/><body><p align=\"center\"><span style=\" font-size:12pt; color:#ffffff;\">天气</span></p></body></html>"))
            self.period.setText(_translate("MainWindow","<html><head/><body><p align=\"center\"><span style=\" font-size:12pt; color:#ffffff;\">时间</span></p></body></html>"))
            self.label_4.setText(_translate("MainWindow","<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">祝您一路顺风</span></p></body></html>"))
            return None
        else:
            self.config["background_box"] = False
            f = open(r"user_config.txt", "w", encoding="utf-8")
            f.write(str(config))
            f.close()
            self.centralwidget.setStyleSheet("background-color: rgb(255,255,255)")
            self.label_7.setStyleSheet("")
            self.label_8.setStyleSheet("background-color:rgb(242,242,242)")
            self.label_3.setStyleSheet("color:rgb(101,101,101)")
            self.label_11.setStyleSheet("color:rgb(101,101,101)")
            self.label_4.setStyleSheet("background-color:rgb(242,242,242)")
            self.checkbox_time.setStyleSheet("")
            self.checkbox_video_write.setStyleSheet("")
            self.checkbox_flip.setStyleSheet("")
            self.checkbox_change_ui.setStyleSheet("")
            self.checkbox_pic.setStyleSheet("")
            self.label_12.setStyleSheet("background-color:rgb(242,242,242)")
            self.button_time_color.setStyleSheet("background-color:rgb(242,242,242);\n"
            "border-radius: 10px")
            self.button_predict_color.setStyleSheet("background-color:rgb(242,242,242);\n"
            "border-radius: 10px")
            self.button_change_path.setStyleSheet("background-color:rgb(242,242,242);\n"
            "border-radius: 10px")
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap("icon/文件夹.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.button_open_image.setIcon(icon)
            self.button_open_image.setIconSize(QtCore.QSize(30, 30))
            icon1 = QtGui.QIcon()
            icon1.addPixmap(QtGui.QPixmap("icon/视频播放.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.button_open_video.setIcon(icon1)
            self.button_open_video.setIconSize(QtCore.QSize(35, 35))
            icon2 = QtGui.QIcon()
            icon2.addPixmap(QtGui.QPixmap("icon/卡口视频摄像头,监控,桌面摄像头,网络摄像头 (2).png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.button_open_camera.setIcon(icon2)
            self.button_open_camera.setIconSize(QtCore.QSize(30, 30))
            self.pre_weather.setStyleSheet("background-color:rgb(242,242,242)")
            self.weather.setStyleSheet("background-color:rgb(242,242,242)")
            self.period.setStyleSheet("background-color:rgb(242,242,242)")
            self.pre_period.setStyleSheet("background-color:rgb(242,242,242)")
            self.pre_period.setStyleSheet("background-color:rgb(242,242,242)")
            if self.is_pause == False:
                icon3 = QtGui.QIcon()
                icon3.addPixmap(QtGui.QPixmap("icon/播放.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                self.button_pause.setIcon(icon3)
                self.button_pause.setIconSize(QtCore.QSize(30, 30))
            else:
                icon3 = QtGui.QIcon()
                icon3.addPixmap(QtGui.QPixmap("icon/暂停播放.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                self.button_pause.setIcon(icon3)
                self.button_pause.setIconSize(QtCore.QSize(30, 30))
            icon4 = QtGui.QIcon()
            icon4.addPixmap(QtGui.QPixmap("icon/停止.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.button_reset.setIcon(icon4)
            self.button_reset.setIconSize(QtCore.QSize(30, 30))
            _translate = QtCore.QCoreApplication.translate
            self.label_6.setText(_translate("MainWindow","<html><head/><body><p><span style=\" font-size:18pt; color:#000000;\">切换模式</span></p></body></html>"))
            if self.image_text == 1:
                self.label_11.setText(_translate("MainWindow","<html><head/><body><p><span style=\" font-size:16pt; color:#656565;\">当前模式：图片</span></p></body></html>"))
            elif self.cap2.isOpened():
                self.label_11.setText(_translate("MainWindow","<html><head/><body><p><span style=\" font-size:16pt; color:#656565;\">当前模式：视频</span></p></body></html>"))
            elif self.cap.isOpened():
                self.label_11.setText(_translate("MainWindow","<html><head/><body><p><span style=\" font-size:16pt; color:#656565;\">当前模式：摄像头</span></p></body></html>"))
            else:
                self.label_11.setText(_translate("MainWindow","<html><head/><body><p><span style=\" font-size:16pt; color:#656565;\">当前模式：</span></p></body></html>"))
            self.label_2.setText(_translate("MainWindow","<html><head/><body><p><span style=\" font-size:16pt; color:#656565;\">当前时间：</span></p></body></html>"))
            self.label_3.setText(_translate("MainWindow","<html><head/><body><p><span style=\" font-size:14pt; color:#656565;\"></span></p></body></html>"))
            self.label_9.setText(_translate("MainWindow","<html><head/><body><p><span style=\" font-size:18pt; color:#000000;\">设置</span></p></body></html>"))
            self.weather.setText(_translate("MainWindow","<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">天气</span></p></body></html>"))
            self.period.setText(_translate("MainWindow","<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">时间</span></p></body></html>"))
            self.label_4.setText(_translate("MainWindow","<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">祝您一路顺风</span></p></body></html>"))
            return None


if __name__ == '__main__':
    # 读取保存的用户配置
    f = open(user_config, "r", encoding="utf-8")
    config = eval(f.readlines()[0])
    f.close()
    app = QtWidgets.QApplication(sys.argv)
    ui = period_weather_predict(config)
    ui.show()
    ui.change_ui()
    sys.exit(app.exec_())