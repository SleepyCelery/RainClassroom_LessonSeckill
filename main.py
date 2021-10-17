from gevent import monkey

monkey.patch_all()
import config
import window
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem
from PyQt5.QtCore import QThread
import sys
from selenium import webdriver
import time
import build_requests

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def tprint(string):
    ui.Info.appendPlainText('[{}] {}'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), string))
    print('[{}] {}'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), string))
    app.processEvents()


class RefreshThread(QThread):
    def __init__(self):
        QThread.__init__(self)

    def run(self):
        while True:
            app.processEvents()


class LoginThread(QThread):
    def __init__(self):
        QThread.__init__(self)

    def run(self):
        browser = ui.Browser.currentText()
        try:
            if browser == 'Google Chrome':
                driver = webdriver.Chrome('./chromedriver.exe')
            elif browser == 'Microsoft Edge':
                driver = webdriver.Edge('./msedgedriver.exe')
            else:
                tprint('登录时出现未知错误！')
        except Exception as e:
            tprint('在打开浏览器时出现错误：{}'.format(e))
            return
        driver.get(config.login_url)
        locatorapp = (By.ID, 'app')
        try:
            WebDriverWait(driver, 60, 1).until(EC.presence_of_element_located(locatorapp))
            tprint('检测到登录成功，正在获取cookie...')
            dictCookies = driver.get_cookies()
            # print(dictCookies)
            cookie = ''
            for i in dictCookies:
                if i['domain'] == 'changjiang.yuketang.cn':
                    cookie += '{}={};'.format(i['name'], i['value'])
            ui.CookieEdit.setText(cookie)
            tprint('获取cookie成功！')
            ui.LoginButton.setEnabled(True)
            ui.StartButton.setEnabled(True)
            driver.quit()
        except Exception as e:
            tprint('发生了一个错误，错误信息：{}'.format(e))


class Seckill(QThread):
    def __init__(self, session: build_requests.VideoSession, coroutine=False):
        QThread.__init__(self)
        self.session = session
        self.coroutine = coroutine

    def run(self):
        try:
            self.session.send_heartbeats(coroutine=self.coroutine)
        except Exception as e:
            print(e)


def login_ykt():
    global classinfo
    ui.LoginButton.setEnabled(False)
    tprint('请在60秒内在接下来弹出的页面登录雨课堂...')
    login_thread = LoginThread()
    login_thread.start()
    while not login_thread.wait():
        app.processEvents()
    classinfo = build_requests.get_classinfo_dict(cookie=ui.CookieEdit.text())
    tprint("课程表获取完成！")
    for i in classinfo:
        ui.ClassName.insertItem(0, i['course_name'] + "_" + i['teacher_name'])


def StartSeckill():
    global classinfo
    ui.StartButton.setEnabled(False)
    if ui.CookieEdit.text() == "":
        tprint("请先登录并选课后再启动刷课！")
        ui.StartButton.setEnabled(True)
        return
    if ui.ClassName.currentText() != "":
        course_name, teacher_name = ui.ClassName.currentText().split('_')
        for i in classinfo:
            if i['course_name'] == course_name and i['teacher_name'] == teacher_name:
                classroom_id = i['classroom_id']
                break
        if not ui.ifAllVideos.isChecked():
            try:
                sku_id = build_requests.get_sku_id(ui.CookieEdit.text(), classroom_id)
                video_ids = build_requests.get_unfinished_video_id(ui.CookieEdit.text(), sku_id, str(classroom_id))
                tprint('检测到{}有{}节课尚未完成！'.format(ui.ClassName.currentText(), len(video_ids)))
                if len(video_ids) == 0:
                    return
                tprint("正在构造请求...")
                session = build_requests.VideoSession(ui.CookieEdit.text(), classroom_id, video_ids[0]['id'])
                tprint("请求构造完成!")
                tprint('正在刷视频ID为{}的课程...'.format(video_ids[0]['id']))
                if ui.ifCoroutine.isChecked():
                    tprint('协程并发已启动!')
                    coroutine_seckill = Seckill(session, coroutine=True)
                    coroutine_seckill.start()
                    while not coroutine_seckill.wait():
                        app.processEvents()
                    ui.StartButton.setEnabled(True)
                    tprint('视频ID为{}的课程已完成！'.format(coroutine_seckill.session.video_id))
                else:
                    tprint('协程并发未启动，请求即将发送，在执行期间请勿关闭软件，请稍后...')
                    seckill = Seckill(session, coroutine=False)
                    seckill.start()
                    while not seckill.wait():
                        app.processEvents()
                    ui.StartButton.setEnabled(True)
                    tprint('已提交刷课请求！')
                    tprint('视频ID为{}的课程已完成！'.format(seckill.session.video_id))
            except Exception as e:
                tprint("出现错误：{}".format(e))
                ui.StartButton.setEnabled(True)

        else:
            try:
                sku_id = build_requests.get_sku_id(ui.CookieEdit.text(), classroom_id)
                video_ids = build_requests.get_all_video_id(ui.CookieEdit.text(), sku_id, str(classroom_id))
                tprint('检测到{}一共有{}节课！'.format(ui.ClassName.currentText(), len(video_ids)))
                if len(video_ids) == 0:
                    return
                sessions = []
                tprint("正在批量添加会话，期间程序将会卡顿，请勿关闭程序...")
                if ui.ifCoroutine.isChecked():
                    tprint('协程并发已启动!')
                else:
                    tprint('协程并发未启动，请求时间将会较长!')
                for i in video_ids:
                    session = Seckill(build_requests.VideoSession(ui.CookieEdit.text(), classroom_id, i['id']),
                                      coroutine=ui.ifCoroutine.isChecked())
                    sessions.append(session)
                tprint("批量添加会话完成！")
                if QMessageBox.question(window, '提示', '即将一次性刷完课程所有视频，是否继续？',
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes) == QMessageBox.Yes:
                    for i in sessions:
                        i.start()
                        tprint("视频ID为{}的课程已启动刷课！".format(i.session.video_id))
                        while not i.wait():
                            app.processEvents()
                        tprint('视频ID为{}的课程已完成！等待10秒后开始刷下一节课...'.format(i.session.video_id))
                        time.sleep(10)
                        app.processEvents()
                    tprint('所有视频均已刷完！')
                    ui.StartButton.setEnabled(True)

                else:
                    tprint("已取消批量刷课！")
                    ui.StartButton.setEnabled(True)
            except Exception as e:
                tprint("出现错误：{}".format(e))
                ui.StartButton.setEnabled(True)
    else:
        tprint('请先选课后再启动刷课！')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = window.Ui_MainWindow()
    window = QMainWindow()
    ui.setupUi(window)
    window.show()

    refresh_thread = RefreshThread()
    refresh_thread.start()

    ui.LoginButton.clicked.connect(login_ykt)
    ui.StartButton.clicked.connect(StartSeckill)
    ui.StartButton.setEnabled(False)

    sys.exit(app.exec_())
