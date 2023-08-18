# Malody to Phigros Chart Converter v1.4.0
# Produced by IambicCave
# -*- coding: UTF-8 -*-

import json
import csv
import zipfile
from os import path, chdir, remove, getcwd, mkdir
from sys import exit, argv
from random import random as rand
from webbrowser import open as open_url

from PyQt5.QtGui import *  # useful?
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox

import untitled as wd
import ico

Path = path.split(path.abspath(argv[0]))[0]
path.realpath(argv[0])
chdir(Path)  # change working directory
Path = str(Path).replace("\\", "/")
FILECHT = []  # absolute path
FILEPIC = []  # absolute path
FILEMUS = []  # absolute path
FILEMCZ = []  # [[absolute_path_of_mcz, filename1, filename2, ...], [...], ...]
decode = "utf-8"

# basic info from malody
mld_j = {}
name = "NameNotFound"
bpm = []
mainbpm = [0, 0]  # [bpm value, total time (float)]
offset = 0
note_number = 0
special_note = 0
malodyid = 0
column_number = 0
charter = ""
composer = ""
level = ""
background = ""
backgrounddir = ""
song = ""
songdir = ""
# options for phigros
line_y = -350.0
line_speed = 13.0
speed_change_with_bpm = True
speed_change_with_effect = True
line_alpha = 255
line_x = 0.0
line_rotate = 0.0
illustrator = ""

note_flip = False
note_luck = False
# [mld, music, pic, _, 4K, 5K, 6K, 7K, 8K, 9K]
lock = [False, False, False, False, False, False, False, False, False, False]

# some formats
questionnaire = "https://wj.qq.com/s2/12839820/287c/"
zipflag = "[mcz]"
tmp_folder = "temp"
export_folder = "export"
information = []
E0 = "缺失“template.json”文件"
E1 = "未选择Malody谱面文件"
E2 = "未选择音乐文件"
E3 = "未选择图片文件"
End = "已生成压缩包：%s"


class ClassBPM:
    def __init__(self):
        self.data = 120
        self.time = [0, 0, 1]


def column_builder(clm, div):
    ret = []
    for i in range(clm):
        ret.append(round(float((1 - clm) * div / 2 + i * div), 2))
    return ret


column_pos = [0, 0, 0, 0,
              column_builder(4, 260),
              column_builder(5, 250),
              column_builder(6, 220),
              column_builder(7, 180),
              column_builder(8, 160),
              column_builder(9, 140)]


def mine(a, x, y):  # minus 768^-1 beat
    if x == 0:
        return [a - 1, 767, 768]
    return [a, round(x * 768 / y) - 1, 768]


def list_to_str(x):  # to print the "information"
    ret = ""
    for i in range(len(x)):
        if type(x[i]) == list:
            for j in range(len(x[i])):
                ret = ret + x[i][j] + '\n'
        else:
            ret = ret + x[i] + '\n'
    return ret


def time_to_float(x):
    return round(x[0] + x[1] / x[2], 8)


def format_speed(speed, time):  # return recognizable speedEvents
    time[0] += time[1] // time[2]
    time[1] = time[1] % time[2]
    end_time = [0, 1, 768]
    start_time = [0, 0, 1]
    if time[0] != 0 or time[1] != 0:
        end_time = [time[0], time[1], time[2]]
        start_time = mine(time[0], time[1], time[2])
    new_speed = {"end": speed,
                 "endTime": end_time,
                 "linkgroup": 0,
                 "start": speed,
                 "startTime": start_time}
    return new_speed


def load_file(x, inzip):  # x: absolute path of a file; or extracted file
    if x.endswith(".mc"):
        if x in FILECHT:
            return
        with open(x, "r", encoding=decode) as mld_file:
            mld_jt = json.load(mld_file)
        if mld_jt.get("meta").get("mode") != 0:
            return
        if inzip:
            ui.mld_chart_box.addItem(zipflag + x.split("/")[-1])
        else:
            ui.mld_chart_box.addItem(x.split("/")[-1])
            FILECHT.append(x)
    if x.endswith(".ogg") or x.endswith(".mp3"):
        if x in FILEMUS:
            return
        if inzip:
            ui.music_box.addItem(zipflag + x.split("/")[-1])
        else:
            ui.music_box.addItem(x.split("/")[-1])
            FILEMUS.append(x)
    if x.endswith(".jpg") or x.endswith(".png"):
        if x in FILEPIC:
            return
        if inzip:
            ui.picture_box.addItem(zipflag + x.split("/")[-1])
        else:
            ui.picture_box.addItem(x.split("/")[-1])
            FILEPIC.append(x)


def open_file():
    global lock
    lock[0] = lock[1] = lock[2] = True
    selects, _ = QFileDialog.getOpenFileNames(None, "选取文件", getcwd(), "所有谱面文件 (*.mc;*.png;*.jpg;*.mp3;*ogg;*.mcz)")
    for i in range(len(selects)):
        if selects[i].endswith(".mcz"):
            if selects[i] in FILEMCZ:
                continue
            mczfile = zipfile.ZipFile(selects[i])
            mczfile.extractall(tmp_folder)
            tmplist = [selects[i]]
            for j in range(len(mczfile.namelist())):
                tmplist.append(mczfile.namelist()[j])
                load_file(Path + '/' + tmp_folder + '/' + mczfile.namelist()[j], True)
                remove(tmp_folder + '/' + mczfile.namelist()[j])
            FILEMCZ.append(tmplist)
        else:
            load_file(selects[i], False)
    ui.mld_chart_box.setCurrentIndex(-1)
    ui.music_box.setCurrentIndex(-1)
    ui.picture_box.setCurrentIndex(-1)
    lock[0] = lock[1] = lock[2] = False


def open_folder():
    pass


def open_feedback():
    open_url(questionnaire)


def pick_malody_chart():
    global information, mld_j, column_number, note_number, special_note, charter, level, \
        name, composer, bpm, mainbpm, speed_change_with_bpm, offset, illustrator, lock
    if lock[0]:
        return
    # read Malody chart file
    inzip = False
    mczfile = ""
    mld_filedir = ""
    mld_filename = ui.mld_chart_box.currentText()  # file name (in zip)
    if mld_filename.find(zipflag) == 0:
        flag = 0  # target's index in FILEMCZ
        inzip = True
        mld_filename = mld_filename[len(zipflag):]
        for i in range(len(FILEMCZ)):
            for j in range(1, len(FILEMCZ[i])):
                if mld_filename == FILEMCZ[i][j]:
                    flag = i
        print("flag", flag)
        mczfile = zipfile.ZipFile(FILEMCZ[flag])
        mczfile.extractall(tmp_folder)
        mld_filedir = Path + '/' + tmp_folder + '/' + mld_filename
        print("inzip, ", end='')
    else:
        for i in range(len(FILECHT)):
            if FILECHT[i].split('/')[-1] == mld_filename:
                mld_filedir = FILECHT[i]
                print("outzip, ", end='')
    print("mld_filedir: ", mld_filedir)
    with open(mld_filedir, "r", encoding=decode) as mld_file:
        mld_j = json.load(mld_file)
    # get basic information from Malody chart file & fill the information box
    information.clear()
    column_number = mld_j.get("meta").get("mode_ext").get("column")
    information.append("轨道个数:\t" + str(column_number))
    note_number = len(mld_j.get("note")) - 1
    information.append("音符总数:\t" + str(note_number))
    for i in range(note_number + 1):
        flag = mld_j.get("note")[i].get("sound")
        if flag is not None:
            special_note = i
    charter = mld_j.get("meta").get("creator")
    information.append("谱师:\t" + charter)
    level = mld_j.get("meta").get("version")
    ui.level.setText(level)
    information.append("等级提示:\t" + level)
    illustrator = ""
    ui.illustrator.setText(illustrator)
    information.append("曲绘作者:\t" + illustrator)
    name = mld_j.get("meta").get("song").get("title")
    information.append("谱面名称:\t" + name)
    composer = mld_j.get("meta").get("song").get("artist")
    information.append("曲师:\t" + composer)
    endtime = mld_j.get("note")[note_number - 1].get("endbeat")
    if endtime is None:
        endtime = mld_j.get("note")[note_number - 1].get("beat")
    bpm_num = len(mld_j.get("time"))
    information.append([])
    for i in range(bpm_num):
        bpm.append(ClassBPM())
        bpm[i].data = mld_j.get("time")[i].get("bpm")
        for j in range(3):
            bpm[i].time[j] = mld_j.get("time")[i].get("beat")[j]
        during = 0
        if i == bpm_num - 1:
            during = time_to_float(endtime) - time_to_float(mld_j.get("time")[i].get("beat"))
        else:
            during = time_to_float(mld_j.get("time")[i + 1].get("beat")) - time_to_float(
                mld_j.get("time")[i].get("beat"))
        if during > mainbpm[1]:
            mainbpm = [bpm[i].data, during]
    if bpm_num <= 3:
        for i in range(bpm_num):
            information[len(information) - 1].append("BPM:\t" + str(round(bpm[i].data, 3)) + " (开始时间" + str(
                bpm[i].time[0]) + ":" + str(bpm[i].time[1]) + "/" + str(bpm[i].time[2]) + ")")
    else:
        information[len(information) - 1].append("(主)BPM:\t" + str(mainbpm[0]) + " (总BPM数" + str(bpm_num) + ")")
    offset = mld_j.get("note")[special_note].get("offset")
    if offset is None:
        offset = 0
    offset = -offset
    # The offset between Phigros and Malody is just the opposite
    information.append("偏移值:\t" + str(offset))
    information.append("基础流速:\t" + str(line_speed))
    information.append("线高度:\t" + str(line_y))
    information.append([])
    if note_luck:
        information[11].append("LUCK:\tON")
    else:
        information[11].append("LUCK:\tOFF")
    if note_flip:
        information[11].append("FLIP:\tON")
    else:
        information[11].append("FLIP:\tOFF")
    if speed_change_with_effect and speed_change_with_bpm:
        information[11].append("CONST:\tOFF")
    else:  # separate control may have problem!
        information[11].append("CONST:\tON")
    information.append("")
    information.append("线透明度:\t" + str(line_alpha))
    information.append("横向偏移:\t" + str(line_x))
    information.append("旋转角度:\t" + str(line_rotate))
    ui.information_browser.setText(list_to_str(information))
    flag = True  # whether music need to choose
    for i in range(ui.music_box.count()):
        if ui.music_box.itemText(i) == mld_j.get("note")[special_note].get("sound") or \
                (inzip and ui.music_box.itemText(i)[len(zipflag):] == mld_j.get("note")[special_note].get("sound")):
            ui.music_box.setCurrentIndex(i)
            ui.music_label.setText("选择音乐文件（已对应谱面）")
            flag = False
    if flag:
        ui.music_box.setCurrentIndex(-1)
        ui.music_label.setText("选择音乐文件")
    flag = True  # whether picture need to choose
    for i in range(ui.picture_box.count()):
        if ui.picture_box.itemText(i) == mld_j.get("meta").get("background") or \
                (inzip and ui.picture_box.itemText(i)[len(zipflag):] == mld_j.get("meta").get("background")):
            ui.picture_box.setCurrentIndex(i)
            ui.picture_label.setText("选择图片文件（已对应谱面）")
            flag = False
    if flag:
        ui.picture_box.setCurrentIndex(-1)
        ui.picture_label.setText("选择图片文件")

    if inzip:
        for i in range(len(mczfile.namelist())):
            remove(tmp_folder + '/' + mczfile.namelist()[i])


def pick_music_file():
    global song
    if not lock[1]:
        song = ui.music_box.currentText()
        ui.music_label.setText("选择音乐文件")


def pick_picture_file():
    global background
    if not lock[2]:
        background = ui.picture_box.currentText()
        ui.picture_label.setText("选择图片文件")


def level_changing():
    global information, level
    level = ui.level.text()
    if len(information) >= 4:
        information[3] = "等级提示:\t" + level
        ui.information_browser.setText(list_to_str(information))


def illustrator_changing():
    global information, illustrator
    illustrator = ui.illustrator.text()
    if len(information) >= 5:
        information[4] = "曲绘作者:\t" + illustrator
        ui.information_browser.setText(list_to_str(information))


def LUCK_changing():
    global information, note_luck, note_flip
    if note_flip:
        ui.FLIP.setChecked(False)
        note_flip = False
    if not information:
        note_luck = 1 - note_luck
        return
    if note_luck:
        note_luck = False
        information[11][0] = "LUCK:\tOFF"
    else:
        note_luck = True
        information[11][0] = "LUCK:\tON"
        information[11][1] = "FLIP:\tOFF"
    ui.information_browser.setText(list_to_str(information))


def FLIP_changing():
    global information, note_luck, note_flip
    if note_luck:
        ui.LUCK.setChecked(False)
        note_luck = False
    if not information:
        note_flip = 1 - note_flip
        return
    if note_flip:
        note_flip = False
        information[11][1] = "FLIP:\tOFF"
    else:
        note_flip = True
        information[11][1] = "FLIP:\tON"
        information[11][0] = "LUCK:\tOFF"
    ui.information_browser.setText(list_to_str(information))


def CONST_changing():
    global information, speed_change_with_bpm, speed_change_with_effect
    if not information:
        speed_change_with_bpm = 1 - speed_change_with_bpm
        speed_change_with_effect = 1 - speed_change_with_effect
        return
    if speed_change_with_bpm and speed_change_with_effect:
        speed_change_with_bpm = speed_change_with_effect = False
        information[11][2] = "CONST:\tON"
    else:
        speed_change_with_bpm = speed_change_with_effect = True
        information[11][2] = "CONST:\tOFF"
    ui.information_browser.setText(list_to_str(information))


def speed_changing():
    global information, line_speed
    line_speed = round(float(ui.general_speed.text()), 2)
    if len(information) >= 4:
        information[9] = "基础流速:\t" + str(line_speed)
        ui.information_browser.setText(list_to_str(information))


def line_y_changing():
    global information, line_y
    line_y = round(float(ui.y_movement.text()), 2)
    if len(information) >= 4:
        information[10] = "线高度:\t" + str(line_y)
        ui.information_browser.setText(list_to_str(information))


def line_alpha_changing():
    global information, line_alpha
    line_alpha = ui.alpha.value()
    if len(information) >= 4:
        information[13] = "线透明度:\t" + str(line_alpha)
        ui.information_browser.setText(list_to_str(information))


def line_x_changing():
    global information, line_x
    line_x = round(float(ui.x_movement.text()), 2)
    if len(information) >= 4:
        information[14] = "横向偏移:\t" + str(line_x)
        ui.information_browser.setText(list_to_str(information))


def line_rotate_changing():
    global information, line_rotate
    line_rotate = round(float(ui.rotate.text()), 2)
    if len(information) >= 4:
        information[15] = "旋转角度:\t" + str(line_rotate)
        ui.information_browser.setText(list_to_str(information))


# region Tracks Modify UI
# 4K UI
def dist_4K_changing():
    global column_pos, lock
    column_pos[4] = column_builder(4, ui.dist_4K.value())
    lock[4] = True
    ui.dist_4K_label.setText("轨道间隔")
    ui._4K1.setValue(column_pos[4][0])
    ui._4K1_sl.setValue(int(column_pos[4][0]))
    ui._4K2.setValue(column_pos[4][1])
    ui._4K2_sl.setValue(int(column_pos[4][1]))
    ui._4K3.setValue(column_pos[4][2])
    ui._4K3_sl.setValue(int(column_pos[4][2]))
    ui._4K4.setValue(column_pos[4][3])
    ui._4K4_sl.setValue(int(column_pos[4][3]))
    lock[4] = False


def _4K1_changing():
    global column_pos
    if not lock[4]:
        ui.dist_4K_label.setText("轨道间隔（失效）")
        column_pos[4][0] = ui._4K1.value()
        ui._4K1_sl.setValue(int(ui._4K1.value()))


def _4K2_changing():
    global column_pos
    if not lock[4]:
        ui.dist_4K_label.setText("轨道间隔（失效）")
        column_pos[4][1] = ui._4K2.value()
        ui._4K2_sl.setValue(int(ui._4K2.value()))


def _4K3_changing():
    global column_pos
    if not lock[4]:
        ui.dist_4K_label.setText("轨道间隔（失效）")
        column_pos[4][2] = ui._4K3.value()
        ui._4K3_sl.setValue(int(ui._4K3.value()))


def _4K4_changing():
    global column_pos
    if not lock[4]:
        ui.dist_4K_label.setText("轨道间隔（失效）")
        column_pos[4][3] = ui._4K4.value()
        ui._4K4_sl.setValue(int(ui._4K4.value()))


def _4K1_sl_changing():
    global column_pos
    if not lock[4]:
        ui.dist_4K_label.setText("轨道间隔（失效）")
        column_pos[4][0] = float(ui._4K1_sl.value())
        ui._4K1.setValue(float(ui._4K1_sl.value()))


def _4K2_sl_changing():
    global column_pos
    if not lock[4]:
        ui.dist_4K_label.setText("轨道间隔（失效）")
        column_pos[4][1] = float(ui._4K2_sl.value())
        ui._4K2.setValue(float(ui._4K2_sl.value()))


def _4K3_sl_changing():
    global column_pos
    if not lock[4]:
        ui.dist_4K_label.setText("轨道间隔（失效）")
        column_pos[4][2] = float(ui._4K3_sl.value())
        ui._4K3.setValue(float(ui._4K3_sl.value()))


def _4K4_sl_changing():
    global column_pos
    if not lock[4]:
        ui.dist_4K_label.setText("轨道间隔（失效）")
        column_pos[4][3] = float(ui._4K4_sl.value())
        ui._4K4.setValue(float(ui._4K4_sl.value()))


# 5K UI
def dist_5K_changing():
    global column_pos, lock
    column_pos[5] = column_builder(5, ui.dist_5K.value())
    lock[5] = True
    ui.dist_5K_label.setText("轨道间隔")
    ui._5K1.setValue(column_pos[5][0])
    ui._5K1_sl.setValue(int(column_pos[5][0]))
    ui._5K2.setValue(column_pos[5][1])
    ui._5K2_sl.setValue(int(column_pos[5][1]))
    ui._5K3.setValue(column_pos[5][2])
    ui._5K3_sl.setValue(int(column_pos[5][2]))
    ui._5K4.setValue(column_pos[5][3])
    ui._5K4_sl.setValue(int(column_pos[5][3]))
    ui._5K5.setValue(column_pos[5][4])
    ui._5K5_sl.setValue(int(column_pos[5][4]))
    lock[5] = False


def _5K1_changing():
    global column_pos
    if not lock[5]:
        ui.dist_5K_label.setText("轨道间隔（失效）")
        column_pos[5][0] = ui._5K1.value()
        ui._5K1_sl.setValue(int(ui._5K1.value()))


def _5K2_changing():
    global column_pos
    if not lock[5]:
        ui.dist_5K_label.setText("轨道间隔（失效）")
        column_pos[5][1] = ui._5K2.value()
        ui._5K2_sl.setValue(int(ui._5K2.value()))


def _5K3_changing():
    global column_pos
    if not lock[5]:
        ui.dist_5K_label.setText("轨道间隔（失效）")
        column_pos[5][2] = ui._5K3.value()
        ui._5K3_sl.setValue(int(ui._5K3.value()))


def _5K4_changing():
    global column_pos
    if not lock[5]:
        ui.dist_5K_label.setText("轨道间隔（失效）")
        column_pos[5][3] = ui._5K4.value()
        ui._5K4_sl.setValue(int(ui._5K4.value()))


def _5K5_changing():
    global column_pos
    if not lock[5]:
        ui.dist_5K_label.setText("轨道间隔（失效）")
        column_pos[5][4] = ui._5K5.value()
        ui._5K5_sl.setValue(int(ui._5K5.value()))


def _5K1_sl_changing():
    global column_pos
    if not lock[5]:
        ui.dist_5K_label.setText("轨道间隔（失效）")
        column_pos[5][0] = float(ui._5K1_sl.value())
        ui._5K1.setValue(float(ui._5K1_sl.value()))


def _5K2_sl_changing():
    global column_pos
    if not lock[5]:
        ui.dist_5K_label.setText("轨道间隔（失效）")
        column_pos[5][1] = float(ui._5K2_sl.value())
        ui._5K2.setValue(float(ui._5K2_sl.value()))


def _5K3_sl_changing():
    global column_pos
    if not lock[5]:
        ui.dist_5K_label.setText("轨道间隔（失效）")
        column_pos[5][2] = float(ui._5K3_sl.value())
        ui._5K3.setValue(float(ui._5K3_sl.value()))


def _5K4_sl_changing():
    global column_pos
    if not lock[5]:
        ui.dist_5K_label.setText("轨道间隔（失效）")
        column_pos[5][3] = float(ui._5K4_sl.value())
        ui._5K4.setValue(float(ui._5K4_sl.value()))


def _5K5_sl_changing():
    global column_pos
    if not lock[5]:
        ui.dist_5K_label.setText("轨道间隔（失效）")
        column_pos[5][4] = float(ui._5K5_sl.value())
        ui._5K5.setValue(float(ui._5K5_sl.value()))


# 6K UI
def dist_6K_changing():
    global column_pos, lock
    column_pos[6] = column_builder(6, ui.dist_6K.value())
    lock[6] = True
    ui.dist_6K_label.setText("轨道间隔")
    ui._6K1.setValue(column_pos[6][0])
    ui._6K1_sl.setValue(int(column_pos[6][0]))
    ui._6K2.setValue(column_pos[6][1])
    ui._6K2_sl.setValue(int(column_pos[6][1]))
    ui._6K3.setValue(column_pos[6][2])
    ui._6K3_sl.setValue(int(column_pos[6][2]))
    ui._6K4.setValue(column_pos[6][3])
    ui._6K4_sl.setValue(int(column_pos[6][3]))
    ui._6K5.setValue(column_pos[6][4])
    ui._6K5_sl.setValue(int(column_pos[6][4]))
    ui._6K6.setValue(column_pos[6][5])
    ui._6K6_sl.setValue(int(column_pos[6][5]))
    lock[6] = False


def _6K1_changing():
    global column_pos
    if not lock[6]:
        ui.dist_6K_label.setText("轨道间隔（失效）")
        column_pos[6][0] = ui._6K1.value()
        ui._6K1_sl.setValue(int(ui._6K1.value()))


def _6K2_changing():
    global column_pos
    if not lock[6]:
        ui.dist_6K_label.setText("轨道间隔（失效）")
        column_pos[6][1] = ui._6K2.value()
        ui._6K2_sl.setValue(int(ui._6K2.value()))


def _6K3_changing():
    global column_pos
    if not lock[6]:
        ui.dist_6K_label.setText("轨道间隔（失效）")
        column_pos[6][2] = ui._6K3.value()
        ui._6K3_sl.setValue(int(ui._6K3.value()))


def _6K4_changing():
    global column_pos
    if not lock[6]:
        ui.dist_6K_label.setText("轨道间隔（失效）")
        column_pos[6][3] = ui._6K4.value()
        ui._6K4_sl.setValue(int(ui._6K4.value()))


def _6K5_changing():
    global column_pos
    if not lock[6]:
        ui.dist_6K_label.setText("轨道间隔（失效）")
        column_pos[6][4] = ui._6K5.value()
        ui._6K5_sl.setValue(int(ui._6K5.value()))


def _6K6_changing():
    global column_pos
    if not lock[6]:
        ui.dist_6K_label.setText("轨道间隔（失效）")
        column_pos[6][5] = ui._6K6.value()
        ui._6K6_sl.setValue(int(ui._6K6.value()))


def _6K1_sl_changing():
    global column_pos
    if not lock[6]:
        ui.dist_6K_label.setText("轨道间隔（失效）")
        column_pos[6][0] = float(ui._6K1_sl.value())
        ui._6K1.setValue(float(ui._6K1_sl.value()))


def _6K2_sl_changing():
    global column_pos
    if not lock[6]:
        ui.dist_6K_label.setText("轨道间隔（失效）")
        column_pos[6][1] = float(ui._6K2_sl.value())
        ui._6K2.setValue(float(ui._6K2_sl.value()))


def _6K3_sl_changing():
    global column_pos
    if not lock[6]:
        ui.dist_6K_label.setText("轨道间隔（失效）")
        column_pos[6][2] = float(ui._6K3_sl.value())
        ui._6K3.setValue(float(ui._6K3_sl.value()))


def _6K4_sl_changing():
    global column_pos
    if not lock[6]:
        ui.dist_6K_label.setText("轨道间隔（失效）")
        column_pos[6][3] = float(ui._6K4_sl.value())
        ui._6K4.setValue(float(ui._6K4_sl.value()))


def _6K5_sl_changing():
    global column_pos
    if not lock[6]:
        ui.dist_6K_label.setText("轨道间隔（失效）")
        column_pos[6][4] = float(ui._6K5_sl.value())
        ui._6K5.setValue(float(ui._6K5_sl.value()))


def _6K6_sl_changing():
    global column_pos
    if not lock[6]:
        ui.dist_6K_label.setText("轨道间隔（失效）")
        column_pos[6][5] = float(ui._6K6_sl.value())
        ui._6K6.setValue(float(ui._6K6_sl.value()))


# 7K UI
def dist_7K_changing():
    global column_pos, lock
    column_pos[7] = column_builder(7, ui.dist_7K.value())
    lock[7] = True
    ui.dist_7K_label.setText("轨道间隔")
    ui._7K1.setValue(column_pos[7][0])
    ui._7K1_sl.setValue(int(column_pos[7][0]))
    ui._7K2.setValue(column_pos[7][1])
    ui._7K2_sl.setValue(int(column_pos[7][1]))
    ui._7K3.setValue(column_pos[7][2])
    ui._7K3_sl.setValue(int(column_pos[7][2]))
    ui._7K4.setValue(column_pos[7][3])
    ui._7K4_sl.setValue(int(column_pos[7][3]))
    ui._7K5.setValue(column_pos[7][4])
    ui._7K5_sl.setValue(int(column_pos[7][4]))
    ui._7K6.setValue(column_pos[7][5])
    ui._7K6_sl.setValue(int(column_pos[7][5]))
    ui._7K7.setValue(column_pos[7][6])
    ui._7K7_sl.setValue(int(column_pos[7][6]))
    lock[7] = False


def _7K1_changing():
    global column_pos
    if not lock[7]:
        ui.dist_7K_label.setText("轨道间隔（失效）")
        column_pos[7][0] = ui._7K1.value()
        ui._7K1_sl.setValue(int(ui._7K1.value()))


def _7K2_changing():
    global column_pos
    if not lock[7]:
        ui.dist_7K_label.setText("轨道间隔（失效）")
        column_pos[7][1] = ui._7K2.value()
        ui._7K2_sl.setValue(int(ui._7K2.value()))


def _7K3_changing():
    global column_pos
    if not lock[7]:
        ui.dist_7K_label.setText("轨道间隔（失效）")
        column_pos[7][2] = ui._7K3.value()
        ui._7K3_sl.setValue(int(ui._7K3.value()))


def _7K4_changing():
    global column_pos
    if not lock[7]:
        ui.dist_7K_label.setText("轨道间隔（失效）")
        column_pos[7][3] = ui._7K4.value()
        ui._7K4_sl.setValue(int(ui._7K4.value()))


def _7K5_changing():
    global column_pos
    if not lock[7]:
        ui.dist_7K_label.setText("轨道间隔（失效）")
        column_pos[7][4] = ui._7K5.value()
        ui._7K5_sl.setValue(int(ui._7K5.value()))


def _7K6_changing():
    global column_pos
    if not lock[7]:
        ui.dist_7K_label.setText("轨道间隔（失效）")
        column_pos[7][5] = ui._7K6.value()
        ui._7K6_sl.setValue(int(ui._7K6.value()))


def _7K7_changing():
    global column_pos
    if not lock[7]:
        ui.dist_7K_label.setText("轨道间隔（失效）")
        column_pos[7][6] = ui._7K7.value()
        ui._7K7_sl.setValue(int(ui._7K7.value()))


def _7K1_sl_changing():
    global column_pos
    if not lock[7]:
        ui.dist_7K_label.setText("轨道间隔（失效）")
        column_pos[7][0] = float(ui._7K1_sl.value())
        ui._7K1.setValue(float(ui._7K1_sl.value()))


def _7K2_sl_changing():
    global column_pos
    if not lock[7]:
        ui.dist_7K_label.setText("轨道间隔（失效）")
        column_pos[7][1] = float(ui._7K2_sl.value())
        ui._7K2.setValue(float(ui._7K2_sl.value()))


def _7K3_sl_changing():
    global column_pos
    if not lock[7]:
        ui.dist_7K_label.setText("轨道间隔（失效）")
        column_pos[7][2] = float(ui._7K3_sl.value())
        ui._7K3.setValue(float(ui._7K3_sl.value()))


def _7K4_sl_changing():
    global column_pos
    if not lock[7]:
        ui.dist_7K_label.setText("轨道间隔（失效）")
        column_pos[7][3] = float(ui._7K4_sl.value())
        ui._7K4.setValue(float(ui._7K4_sl.value()))


def _7K5_sl_changing():
    global column_pos
    if not lock[7]:
        ui.dist_7K_label.setText("轨道间隔（失效）")
        column_pos[7][4] = float(ui._7K5_sl.value())
        ui._7K5.setValue(float(ui._7K5_sl.value()))


def _7K6_sl_changing():
    global column_pos
    if not lock[7]:
        ui.dist_7K_label.setText("轨道间隔（失效）")
        column_pos[7][5] = float(ui._7K6_sl.value())
        ui._7K6.setValue(float(ui._7K6_sl.value()))


def _7K7_sl_changing():
    global column_pos
    if not lock[7]:
        ui.dist_7K_label.setText("轨道间隔（失效）")
        column_pos[7][6] = float(ui._7K7_sl.value())
        ui._7K7.setValue(float(ui._7K7_sl.value()))


# 8K UI
def dist_8K_changing():
    global column_pos, lock
    column_pos[8] = column_builder(8, ui.dist_8K.value())
    lock[8] = True
    ui.dist_8K_label.setText("轨道间隔")
    ui._8K1.setValue(column_pos[8][0])
    ui._8K1_sl.setValue(int(column_pos[8][0]))
    ui._8K2.setValue(column_pos[8][1])
    ui._8K2_sl.setValue(int(column_pos[8][1]))
    ui._8K3.setValue(column_pos[8][2])
    ui._8K3_sl.setValue(int(column_pos[8][2]))
    ui._8K4.setValue(column_pos[8][3])
    ui._8K4_sl.setValue(int(column_pos[8][3]))
    ui._8K5.setValue(column_pos[8][4])
    ui._8K5_sl.setValue(int(column_pos[8][4]))
    ui._8K6.setValue(column_pos[8][5])
    ui._8K6_sl.setValue(int(column_pos[8][5]))
    ui._8K7.setValue(column_pos[8][6])
    ui._8K7_sl.setValue(int(column_pos[8][6]))
    ui._8K8.setValue(column_pos[8][7])
    ui._8K8_sl.setValue(int(column_pos[8][7]))
    lock[8] = False


def _8K1_changing():
    global column_pos
    if not lock[8]:
        ui.dist_8K_label.setText("轨道间隔（失效）")
        column_pos[8][0] = ui._8K1.value()
        ui._8K1_sl.setValue(int(ui._8K1.value()))


def _8K2_changing():
    global column_pos
    if not lock[8]:
        ui.dist_8K_label.setText("轨道间隔（失效）")
        column_pos[8][1] = ui._8K1.value()
        ui._8K1_sl.setValue(int(ui._8K1.value()))


def _8K3_changing():
    global column_pos
    if not lock[8]:
        ui.dist_8K_label.setText("轨道间隔（失效）")
        column_pos[8][2] = ui._8K1.value()
        ui._8K1_sl.setValue(int(ui._8K1.value()))


def _8K4_changing():
    global column_pos
    if not lock[8]:
        ui.dist_8K_label.setText("轨道间隔（失效）")
        column_pos[8][3] = ui._8K1.value()
        ui._8K1_sl.setValue(int(ui._8K1.value()))


def _8K5_changing():
    global column_pos
    if not lock[8]:
        ui.dist_8K_label.setText("轨道间隔（失效）")
        column_pos[8][4] = ui._8K1.value()
        ui._8K1_sl.setValue(int(ui._8K1.value()))


def _8K6_changing():
    global column_pos
    if not lock[8]:
        ui.dist_8K_label.setText("轨道间隔（失效）")
        column_pos[8][5] = ui._8K1.value()
        ui._8K1_sl.setValue(int(ui._8K1.value()))


def _8K7_changing():
    global column_pos
    if not lock[8]:
        ui.dist_8K_label.setText("轨道间隔（失效）")
        column_pos[8][6] = ui._8K1.value()
        ui._8K1_sl.setValue(int(ui._8K1.value()))


def _8K8_changing():
    global column_pos
    if not lock[8]:
        ui.dist_8K_label.setText("轨道间隔（失效）")
        column_pos[8][7] = ui._8K1.value()
        ui._8K1_sl.setValue(int(ui._8K1.value()))


def _8K1_sl_changing():
    global column_pos
    if not lock[8]:
        ui.dist_8K_label.setText("轨道间隔（失效）")
        column_pos[8][0] = float(ui._8K1_sl.value())
        ui._8K1.setValue(float(ui._8K1_sl.value()))


def _8K2_sl_changing():
    global column_pos
    if not lock[8]:
        ui.dist_8K_label.setText("轨道间隔（失效）")
        column_pos[8][1] = float(ui._8K2_sl.value())
        ui._8K2.setValue(float(ui._8K2_sl.value()))


def _8K3_sl_changing():
    global column_pos
    if not lock[8]:
        ui.dist_8K_label.setText("轨道间隔（失效）")
        column_pos[8][2] = float(ui._8K3_sl.value())
        ui._8K3.setValue(float(ui._8K3_sl.value()))


def _8K4_sl_changing():
    global column_pos
    if not lock[8]:
        ui.dist_8K_label.setText("轨道间隔（失效）")
        column_pos[8][3] = float(ui._8K4_sl.value())
        ui._8K4.setValue(float(ui._8K4_sl.value()))


def _8K5_sl_changing():
    global column_pos
    if not lock[8]:
        ui.dist_8K_label.setText("轨道间隔（失效）")
        column_pos[8][4] = float(ui._8K5_sl.value())
        ui._8K5.setValue(float(ui._8K5_sl.value()))


def _8K6_sl_changing():
    global column_pos
    if not lock[8]:
        ui.dist_8K_label.setText("轨道间隔（失效）")
        column_pos[8][5] = float(ui._8K6_sl.value())
        ui._8K6.setValue(float(ui._8K6_sl.value()))


def _8K7_sl_changing():
    global column_pos
    if not lock[8]:
        ui.dist_8K_label.setText("轨道间隔（失效）")
        column_pos[8][6] = float(ui._8K7_sl.value())
        ui._8K7.setValue(float(ui._8K7_sl.value()))


def _8K8_sl_changing():
    global column_pos
    if not lock[8]:
        ui.dist_8K_label.setText("轨道间隔（失效）")
        column_pos[8][7] = float(ui._8K8_sl.value())
        ui._8K8.setValue(float(ui._8K8_sl.value()))


# 9K UI
def dist_9K_changing():
    global column_pos, lock
    column_pos[9] = column_builder(9, ui.dist_9K.value())
    lock[9] = True
    ui.dist_9K_label.setText("轨道间隔")
    ui._9K1.setValue(column_pos[9][0])
    ui._9K1_sl.setValue(int(column_pos[9][0]))
    ui._9K2.setValue(column_pos[9][1])
    ui._9K2_sl.setValue(int(column_pos[9][1]))
    ui._9K3.setValue(column_pos[9][2])
    ui._9K3_sl.setValue(int(column_pos[9][2]))
    ui._9K4.setValue(column_pos[9][3])
    ui._9K4_sl.setValue(int(column_pos[9][3]))
    ui._9K5.setValue(column_pos[9][4])
    ui._9K5_sl.setValue(int(column_pos[9][4]))
    ui._9K6.setValue(column_pos[9][5])
    ui._9K6_sl.setValue(int(column_pos[9][5]))
    ui._9K7.setValue(column_pos[9][6])
    ui._9K7_sl.setValue(int(column_pos[9][6]))
    ui._9K8.setValue(column_pos[9][7])
    ui._9K8_sl.setValue(int(column_pos[9][7]))
    ui._9K9.setValue(column_pos[9][8])
    ui._9K9_sl.setValue(int(column_pos[9][8]))
    lock[9] = False


def _9K1_changing():
    global column_pos
    if not lock[9]:
        ui.dist_9K_label.setText("轨道间隔（失效）")
        column_pos[9][0] = ui._9K1.value()
        ui._9K1_sl.setValue(int(ui._9K1.value()))


def _9K2_changing():
    global column_pos
    if not lock[9]:
        ui.dist_9K_label.setText("轨道间隔（失效）")
        column_pos[9][1] = ui._9K2.value()
        ui._9K2_sl.setValue(int(ui._9K2.value()))


def _9K3_changing():
    global column_pos
    if not lock[9]:
        ui.dist_9K_label.setText("轨道间隔（失效）")
        column_pos[9][2] = ui._9K3.value()
        ui._9K3_sl.setValue(int(ui._9K3.value()))


def _9K4_changing():
    global column_pos
    if not lock[9]:
        ui.dist_9K_label.setText("轨道间隔（失效）")
        column_pos[9][3] = ui._9K4.value()
        ui._9K4_sl.setValue(int(ui._9K4.value()))


def _9K5_changing():
    global column_pos
    if not lock[9]:
        ui.dist_9K_label.setText("轨道间隔（失效）")
        column_pos[9][4] = ui._9K5.value()
        ui._9K5_sl.setValue(int(ui._9K5.value()))


def _9K6_changing():
    global column_pos
    if not lock[9]:
        ui.dist_9K_label.setText("轨道间隔（失效）")
        column_pos[9][5] = ui._9K6.value()
        ui._9K6_sl.setValue(int(ui._9K6.value()))


def _9K7_changing():
    global column_pos
    if not lock[9]:
        ui.dist_9K_label.setText("轨道间隔（失效）")
        column_pos[9][6] = ui._9K7.value()
        ui._9K7_sl.setValue(int(ui._9K7.value()))


def _9K8_changing():
    global column_pos
    if not lock[9]:
        ui.dist_9K_label.setText("轨道间隔（失效）")
        column_pos[9][7] = ui._9K8.value()
        ui._9K8_sl.setValue(int(ui._9K8.value()))


def _9K9_changing():
    global column_pos
    if not lock[9]:
        ui.dist_9K_label.setText("轨道间隔（失效）")
        column_pos[9][8] = ui._9K9.value()
        ui._9K9_sl.setValue(int(ui._9K9.value()))


def _9K1_sl_changing():
    global column_pos
    if not lock[9]:
        ui.dist_9K_label.setText("轨道间隔（失效）")
        column_pos[9][0] = float(ui._9K1_sl.value())
        ui._9K1.setValue(float(ui._9K1_sl.value()))


def _9K2_sl_changing():
    global column_pos
    if not lock[9]:
        ui.dist_9K_label.setText("轨道间隔（失效）")
        column_pos[9][1] = float(ui._9K2_sl.value())
        ui._9K2.setValue(float(ui._9K2_sl.value()))


def _9K3_sl_changing():
    global column_pos
    if not lock[9]:
        ui.dist_9K_label.setText("轨道间隔（失效）")
        column_pos[9][2] = float(ui._9K3_sl.value())
        ui._9K3.setValue(float(ui._9K3_sl.value()))


def _9K4_sl_changing():
    global column_pos
    if not lock[9]:
        ui.dist_9K_label.setText("轨道间隔（失效）")
        column_pos[9][3] = float(ui._9K4_sl.value())
        ui._9K4.setValue(float(ui._9K4_sl.value()))


def _9K5_sl_changing():
    global column_pos
    if not lock[9]:
        ui.dist_9K_label.setText("轨道间隔（失效）")
        column_pos[9][4] = float(ui._9K5_sl.value())
        ui._9K5.setValue(float(ui._9K5_sl.value()))


def _9K6_sl_changing():
    global column_pos
    if not lock[9]:
        ui.dist_9K_label.setText("轨道间隔（失效）")
        column_pos[9][5] = float(ui._9K6_sl.value())
        ui._9K6.setValue(float(ui._9K6_sl.value()))


def _9K7_sl_changing():
    global column_pos
    if not lock[9]:
        ui.dist_9K_label.setText("轨道间隔（失效）")
        column_pos[9][6] = float(ui._9K7_sl.value())
        ui._9K7.setValue(float(ui._9K7_sl.value()))


def _9K8_sl_changing():
    global column_pos
    if not lock[9]:
        ui.dist_9K_label.setText("轨道间隔（失效）")
        column_pos[9][7] = float(ui._9K8_sl.value())
        ui._9K8.setValue(float(ui._9K8_sl.value()))


def _9K9_sl_changing():
    global column_pos
    if not lock[9]:
        ui.dist_9K_label.setText("轨道间隔（失效）")
        column_pos[9][8] = float(ui._9K9_sl.value())
        ui._9K9.setValue(float(ui._9K9_sl.value()))


# endregion

def generating():
    ui.warning_label.setText("")
    with open("template.json", "r", encoding=decode) as tpl_file:
        pgr_j = json.load(tpl_file)
    if ui.mld_chart_box.currentText() == "":
        QMessageBox.critical(None, "错误", E1, QMessageBox.Ok)
        return
    if ui.music_box.currentText() == "":
        QMessageBox.critical(None, "错误", E2, QMessageBox.Ok)
        return
    if ui.picture_box.currentText() == "":
        QMessageBox.critical(None, "错误", E3, QMessageBox.Ok)
        return
    # modify arguments
    pgr_j.get("META")["background"] = background
    pgr_j.get("META")["charter"] = charter
    pgr_j.get("META")["composer"] = composer
    pgr_j.get("META")["id"] = malodyid
    pgr_j.get("META")["level"] = level
    pgr_j.get("META")["name"] = name
    pgr_j.get("META")["offset"] = offset
    pgr_j.get("META")["song"] = song
    pgr_j.get("BPMList")[0]["bpm"] = bpm[0].data
    pgr_j.get("BPMList")[0]["startTime"][0] = bpm[0].time[0]
    pgr_j.get("BPMList")[0]["startTime"][1] = bpm[0].time[1]
    pgr_j.get("BPMList")[0]["startTime"][2] = bpm[0].time[2]
    line_event = pgr_j.get("judgeLineList")[0].get("eventLayers")[0]
    line_event.get("alphaEvents")[0]["end"] = line_event.get("alphaEvents")[0]["start"] = line_alpha
    line_event.get("moveXEvents")[0]["end"] = line_event.get("moveXEvents")[0]["start"] = line_x
    line_event.get("moveYEvents")[0]["end"] = line_event.get("moveYEvents")[0]["start"] = line_y
    line_event.get("rotateEvents")[0]["end"] = line_event.get("rotateEvents")[0]["start"] = line_rotate
    line_event.get("speedEvents").append(
        {"end": line_speed,
         "endTime": [0, 1, 1],
         "linkgroup": 0,
         "start": line_speed,
         "startTime": [0, 0, 1]})
    for i in range(1, len(mld_j.get("time"))):
        this_bpm = {'bpm': bpm[i].data, "startTime": [bpm[i].time[0], bpm[i].time[1], bpm[i].time[2]]}
        pgr_j.get("BPMList").append(this_bpm)
    # use double pointer to modify speed according to both bpm and scroll
    if len(mld_j.get("effect")) == 0 or time_to_float(mld_j.get("effect")[0].get("beat")) != 0.0:
        mld_j.get("effect").insert(0, {'beat': [0, 0, 1], "scroll": 1.0})
    t_bpm = []
    v_bpm = []
    t_scroll = []
    v_scroll = []
    for i in range(len(mld_j.get("time"))):
        t_bpm.append(mld_j.get("time")[i].get("beat"))
        v_bpm.append(mld_j.get("time")[i].get("bpm"))
    for i in range(len(mld_j.get("effect"))):
        if mld_j.get("effect")[i].get("scroll") is not None:
            t_scroll.append(mld_j.get("effect")[i].get("beat"))
            v_scroll.append(mld_j.get("effect")[i].get("scroll"))
    lim1 = 1
    lim2 = 0
    if speed_change_with_bpm:
        lim1 = len(t_bpm)
    if speed_change_with_effect:
        lim2 = len(t_scroll)
    cur2 = 0
    speed_list = pgr_j.get("judgeLineList")[0].get("eventLayers")[0].get("speedEvents")
    for cur1 in range(1, lim1):
        while cur2 < lim2 and time_to_float(t_bpm[cur1]) > time_to_float(t_scroll[cur2]):
            if len(speed_list) != 0 and time_to_float(t_bpm[cur1 - 1]) == time_to_float(t_scroll[cur2]):
                speed_list.pop()
            new_speed = line_speed / mainbpm[0] * v_bpm[cur1 - 1] * v_scroll[cur2]
            new_time = t_scroll[cur2]
            speed_list.append(format_speed(new_speed, new_time))
            cur2 += 1
        new_speed = line_speed / mainbpm[0] * v_bpm[cur1] * v_scroll[cur2 - 1]
        new_time = t_bpm[cur1]
        speed_list.append(format_speed(new_speed, new_time))
    while cur2 < lim2:
        if len(speed_list) != 0 and time_to_float(t_bpm[lim1 - 1]) == time_to_float(t_scroll[cur2]):
            speed_list.pop()
        new_speed = line_speed / mainbpm[0] * v_bpm[lim1 - 1] * v_scroll[cur2]
        new_time = t_scroll[cur2]
        speed_list.append(format_speed(new_speed, new_time))
        cur2 += 1
    # print(speed_change_with_bpm)
    # print(speed_change_with_effect)
    # print(lim1)
    # print(t_bpm)
    # print(v_bpm)
    # print(lim2)
    # print(t_scroll)
    # print(v_scroll)
    # for i in range(len(speed_list)):
    #     print(speed_list[i].get("startTime"), speed_list[i].get("start"))
    # print(mainbpm[0])
    # enforce setting the first speed time to end at 0:1/1, so that the ichzh simulator can recognize successfully
    speed_list[0].get("endTime")[2] = 1
    mapping = []
    for i in range(column_number):
        mapping.append(column_pos[column_number][i])
    if note_luck:
        for i in range(100):
            col1 = int(rand() * column_number)
            col2 = int(rand() * column_number)
            tmp = mapping[col1]
            mapping[col1] = mapping[col2]
            mapping[col2] = tmp
    if note_flip:
        for i in range(int(column_number / 2)):
            col1 = i
            col2 = column_number - 1 - i
            tmp = mapping[col1]
            mapping[col1] = mapping[col2]
            mapping[col2] = tmp
    for i in range(note_number + 1):
        if i == special_note:
            continue
        ftime = mld_j.get("note")[i].get("beat")
        ftime_ = mld_j.get("note")[i].get("endbeat")
        note_type = 2
        if ftime_ is None:
            ftime_ = mld_j.get("note")[i].get("beat")
            note_type = 1
        position = mapping[mld_j.get("note")[i].get("column")]
        this_note = {"above": 1,
                     "alpha": 255,
                     "endTime": [ftime_[0], ftime_[1], ftime_[2]],
                     "isFake": 0,
                     "positionX": position,
                     "size": 1.0,
                     "speed": 1.0,
                     "startTime": [ftime[0], ftime[1], ftime[2]],
                     "type": note_type,
                     "visibleTime": 999999.0,
                     "yOffset": 0.0}
        pgr_j.get("judgeLineList")[0].get("notes").append(this_note)
    pgr_j.get("judgeLineList")[0]["numOfNotes"] = note_number
    pgr_filename = name + " (From Malody).json"  # !!!!!!!!
    with open(pgr_filename, "w", encoding=decode) as pgr_file:
        json.dump(pgr_j, pgr_file, indent=4, ensure_ascii=False)
    with open('info.csv', 'w', encoding=decode, newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Chart", "Music", "Image", "Name", "Artist", "Level", "Illustrator", "Charter"])
        writer.writerow([pgr_filename, song, background, name, composer, level, illustrator, charter])
    zip_files = [pgr_filename, "info.csv", song, background]
    zip_filename = pgr_filename[:-5] + '.zip'
    with zipfile.ZipFile(zip_filename, mode='w', compression=zipfile.ZIP_DEFLATED) as z:
        for i in zip_files:
            parent_path, thisname = path.split(i)
            z.write(i, arcname=thisname)
    z.close()
    remove(pgr_filename)
    remove("info.csv")
    ui.warning_label.setText(End % zip_filename)


def init():
    MainWindow.setWindowIcon(QIcon(":/icon2.ico"))
    try:
        open("template.json", "r", encoding=decode)
    except:
        QMessageBox.critical(None, "错误", E0, QMessageBox.Ok)
        exit()
    ui.dist_4K.setValue(260.0)
    ui.dist_5K.setValue(250.0)
    ui.dist_6K.setValue(220.0)
    ui.dist_7K.setValue(180.0)
    ui.dist_8K.setValue(160.0)
    ui.dist_9K.setValue(140.0)
    dist_4K_changing()
    dist_5K_changing()
    dist_6K_changing()
    dist_7K_changing()
    dist_8K_changing()
    dist_9K_changing()


if __name__ == '__main__':
    app = QApplication(argv)
    MainWindow = QMainWindow()
    ui = wd.Ui_MainWindow()
    ui.setupUi(MainWindow)
    init()
    MainWindow.show()

    ui.open_file.triggered.connect(open_file)
    ui.open_folder.triggered.connect(open_folder)
    ui.feedback.triggered.connect(open_feedback)
    ui.mld_chart_box.currentIndexChanged.connect(pick_malody_chart)
    ui.music_box.currentIndexChanged.connect(pick_music_file)
    ui.picture_box.currentIndexChanged.connect(pick_picture_file)
    ui.level.textChanged.connect(level_changing)
    ui.illustrator.textChanged.connect(illustrator_changing)
    ui.general_speed.valueChanged.connect(speed_changing)
    ui.y_movement.valueChanged.connect(line_y_changing)
    ui.LUCK.clicked.connect(LUCK_changing)
    ui.FLIP.clicked.connect(FLIP_changing)
    ui.CONST.clicked.connect(CONST_changing)
    ui.alpha.valueChanged.connect(line_alpha_changing)
    ui.x_movement.valueChanged.connect(line_x_changing)
    ui.rotate.valueChanged.connect(line_rotate_changing)

    ui.dist_4K.valueChanged.connect(dist_4K_changing)
    ui._4K1.valueChanged.connect(_4K1_changing)
    ui._4K2.valueChanged.connect(_4K2_changing)
    ui._4K3.valueChanged.connect(_4K3_changing)
    ui._4K4.valueChanged.connect(_4K4_changing)
    ui._4K1_sl.valueChanged.connect(_4K1_sl_changing)
    ui._4K2_sl.valueChanged.connect(_4K2_sl_changing)
    ui._4K3_sl.valueChanged.connect(_4K3_sl_changing)
    ui._4K4_sl.valueChanged.connect(_4K4_sl_changing)

    ui.dist_5K.valueChanged.connect(dist_5K_changing)
    ui._5K1.valueChanged.connect(_5K1_changing)
    ui._5K2.valueChanged.connect(_5K2_changing)
    ui._5K3.valueChanged.connect(_5K3_changing)
    ui._5K4.valueChanged.connect(_5K4_changing)
    ui._5K5.valueChanged.connect(_5K5_changing)
    ui._5K1_sl.valueChanged.connect(_5K1_sl_changing)
    ui._5K2_sl.valueChanged.connect(_5K2_sl_changing)
    ui._5K3_sl.valueChanged.connect(_5K3_sl_changing)
    ui._5K4_sl.valueChanged.connect(_5K4_sl_changing)
    ui._5K5_sl.valueChanged.connect(_5K5_sl_changing)

    ui.dist_6K.valueChanged.connect(dist_6K_changing)
    ui._6K1.valueChanged.connect(_6K1_changing)
    ui._6K2.valueChanged.connect(_6K2_changing)
    ui._6K3.valueChanged.connect(_6K3_changing)
    ui._6K4.valueChanged.connect(_6K4_changing)
    ui._6K5.valueChanged.connect(_6K5_changing)
    ui._6K6.valueChanged.connect(_6K6_changing)
    ui._6K1_sl.valueChanged.connect(_6K1_sl_changing)
    ui._6K2_sl.valueChanged.connect(_6K2_sl_changing)
    ui._6K3_sl.valueChanged.connect(_6K3_sl_changing)
    ui._6K4_sl.valueChanged.connect(_6K4_sl_changing)
    ui._6K5_sl.valueChanged.connect(_6K5_sl_changing)
    ui._6K6_sl.valueChanged.connect(_6K6_sl_changing)

    ui.dist_7K.valueChanged.connect(dist_7K_changing)
    ui._7K1.valueChanged.connect(_7K1_changing)
    ui._7K2.valueChanged.connect(_7K2_changing)
    ui._7K3.valueChanged.connect(_7K3_changing)
    ui._7K4.valueChanged.connect(_7K4_changing)
    ui._7K5.valueChanged.connect(_7K5_changing)
    ui._7K6.valueChanged.connect(_7K6_changing)
    ui._7K7.valueChanged.connect(_7K7_changing)
    ui._7K1_sl.valueChanged.connect(_7K1_sl_changing)
    ui._7K2_sl.valueChanged.connect(_7K2_sl_changing)
    ui._7K3_sl.valueChanged.connect(_7K3_sl_changing)
    ui._7K4_sl.valueChanged.connect(_7K4_sl_changing)
    ui._7K5_sl.valueChanged.connect(_7K5_sl_changing)
    ui._7K6_sl.valueChanged.connect(_7K6_sl_changing)
    ui._7K7_sl.valueChanged.connect(_7K7_sl_changing)

    ui.dist_8K.valueChanged.connect(dist_8K_changing)
    ui._8K1.valueChanged.connect(_8K1_changing)
    ui._8K2.valueChanged.connect(_8K2_changing)
    ui._8K3.valueChanged.connect(_8K3_changing)
    ui._8K4.valueChanged.connect(_8K4_changing)
    ui._8K5.valueChanged.connect(_8K5_changing)
    ui._8K6.valueChanged.connect(_8K6_changing)
    ui._8K7.valueChanged.connect(_8K7_changing)
    ui._8K8.valueChanged.connect(_8K8_changing)
    ui._8K1_sl.valueChanged.connect(_8K1_sl_changing)
    ui._8K2_sl.valueChanged.connect(_8K2_sl_changing)
    ui._8K3_sl.valueChanged.connect(_8K3_sl_changing)
    ui._8K4_sl.valueChanged.connect(_8K4_sl_changing)
    ui._8K5_sl.valueChanged.connect(_8K5_sl_changing)
    ui._8K6_sl.valueChanged.connect(_8K6_sl_changing)
    ui._8K7_sl.valueChanged.connect(_8K7_sl_changing)
    ui._8K8_sl.valueChanged.connect(_8K8_sl_changing)

    ui.dist_9K.valueChanged.connect(dist_9K_changing)
    ui._9K1.valueChanged.connect(_9K1_changing)
    ui._9K2.valueChanged.connect(_9K2_changing)
    ui._9K3.valueChanged.connect(_9K3_changing)
    ui._9K4.valueChanged.connect(_9K4_changing)
    ui._9K5.valueChanged.connect(_9K5_changing)
    ui._9K6.valueChanged.connect(_9K6_changing)
    ui._9K7.valueChanged.connect(_9K7_changing)
    ui._9K8.valueChanged.connect(_9K8_changing)
    ui._9K9.valueChanged.connect(_9K9_changing)
    ui._9K1_sl.valueChanged.connect(_9K1_sl_changing)
    ui._9K2_sl.valueChanged.connect(_9K2_sl_changing)
    ui._9K3_sl.valueChanged.connect(_9K3_sl_changing)
    ui._9K4_sl.valueChanged.connect(_9K4_sl_changing)
    ui._9K5_sl.valueChanged.connect(_9K5_sl_changing)
    ui._9K6_sl.valueChanged.connect(_9K6_sl_changing)
    ui._9K7_sl.valueChanged.connect(_9K7_sl_changing)
    ui._9K8_sl.valueChanged.connect(_9K8_sl_changing)
    ui._9K9_sl.valueChanged.connect(_9K9_sl_changing)

    ui.generate_button.clicked.connect(generating)

    exit(app.exec_())
