#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Cocoa Log Checker GUI

"""
import json
import sys  # process関係
import traceback
from datetime import date, datetime, timedelta
from pprint import pformat, pprint

import matplotlib
import numpy as np
import pandas as pd
from matplotlib import pylab as plt
from openpyxl.comments import Comment

import PySimpleGUI as sg

import cocoa
import cocoaChart as ccht
import cocoaConfig as cc
import cocoaExcel as cex

__author__ = "hyuasa"
__version__ = "0.0.2"
__date__ = "Aug 25 2022"


def select_cocoa_log_filename(logger, window):
    """Select cocoa log via file dialog

    Args:
        logger (logging): ロガー
        window (Window): GUI window instance

    Returns:
        None

    """
    dialoglayout = [
        [sg.Text("ファイル"), sg.InputText(), sg.FileBrowse(key="-FILENAME-")],
        [sg.Open(), sg.Cancel()],
    ]

    dialogwindow = sg.Window("ファイル選択", dialoglayout)
    dialogevent, dialogvalues = dialogwindow.read()
    dialogwindow.close()
    cc.COCOA_LOG = dialogvalues['-FILENAME-']
    window['-STATUS-'].update(f'選択されたCOCOAログ: {cc.COCOA_LOG}')

    return


def refresh_window(logger, window):
    """refresh Table
       
       read data,
       if valid, close old window, if not valid, say so.
       create new window.
       because, PySimpleGUI table header can not update via table.update()

    Args:
        logger (logging): ロガー
        window (Window): GUI window instance

    Returns:
        None

    """
    merge_df = cocoa.update_dataframe(logger)
    if merge_df is not None:
        headings, data = build_table_data(logger, merge_df)
        # pprint(headings)
        # pprint(data)
        #window['-TABLE-'].update(values=data)
        #window['-STATUS-'].update(f'新しいCOCOAログを分析しました: {cc.COCOA_LOG}')
        window.close()  # close old window
        window = create_window(logger, headings, data, f'REFRESH Data: {cc.COCOA_LOG}')
        handle_events(logger, window, merge_df)

    else:
        window['-STATUS-'].update(f'正しいCOCOAログではありません: {cc.COCOA_LOG}')
    return


def build_table_data(logger, merge_df):
    """build table data

    Args:
        logger (logging): ロガー
        merge_df (DataFrame): pandas data

    Returns:
        (list) : table headings
        (list) : table values

    """
    pd.options.display.float_format = '{:,.1f}'.format
    values = merge_df.values.tolist()
    indexes = merge_df.index.tolist()
    headings = []
    cols = merge_df.columns.tolist()
    for col in cols:
        if col[2] == 'contact':
            headings.append('接触回数')
        elif col[2] == 'cocoa_score':
            headings.append('COCOAスコア')
        else:
            headings.append(col[2])
    # pprint(headings)        
    # pprint(values)

    days = []
    dows = []

    for index in indexes:
        days.append(index[0])
        dows.append(index[1])

    i = 0
    data = []

    for line in values:
        atoms = []
        for atom in line:
            atoms.append('{:,.1f}'.format(atom))
        # print(atoms)
        line = atoms
        line.insert(0, dows[i])
        line.insert(0, days[i])
        data.append(line)
        i += 1

    return headings, data


def create_window(logger, headings, data, status_message):
    """create new window

    Args:
        logger (logging): ロガー
        headings (list): tableカラムタイトル
        data (list): tableデータ 
        status_message (str): ステータスメッセージ

    Returns:
        (Window) : PySimpleGUI Window インスタンス

    """
    sg.theme(cc.SG_THEME)
    sg.set_options(font=(cc.FONT_FAMILY, 10)) 
    layout = [
        [sg.MenuBar([['ファイル', ['COCOAログファイルを開く', '閉じる']]], key='-MENU-')],

        [sg.Button(button_text='ファイル選択', key='-BUTTON_FILE-'),
         sg.Button(button_text='ログ情報', key='-BUTTON_LOGINFO-'),
         sg.Button(button_text='グラフ表示', key='-BUTTON_GRAPH-'),
         sg.Button(button_text='Excel保管', key='-BUTTON_EXCEL-'),
         sg.Button(button_text='終了', key='-BUTTON_END-')],

        [sg.Table(
         headings=headings,
         values=data,
         auto_size_columns=False,
         justification='right',
         key='-TABLE-',
         alternating_row_color=cc.SG_ALT_ROW_COLOR,
         header_text_color=cc.SG_HEADER_TEXT_COLOR,
         num_rows=min(25, len(data)),
         col_widths=list(map(lambda x:len(x)+5, headings)))
         ],

        [sg.StatusBar(status_message, size=(100), key='-STATUS-')]
    ]

    window = sg.Window('COCOA Exposure History',  layout)
    return window 


def handle_events(logger, window, merge_df):
    """ Handling GUI events

    Args:
        logger (logging): ロガー
        window (Window) : PySimpleGUI Window インスタンス
        merge_df (DataFrame): COCOAログDataFrame

    Returns:
        None

    """
    while True:
        event, value = window.read()
        #pprint(event)
        #pprint(value)
        if event == sg.WINDOW_CLOSED or event == '-BUTTON_END-' or value['-MENU-'] == '閉じる':
            break

        if event == '-BUTTON_GRAPH-':
            window['-STATUS-'].update(f'COCOAチャートをOpenします')
            if merge_df is not None:
                ccht.draw_cocoa_charts(logger, merge_df)
                window['-STATUS-'].update(f'COCOAチャートをCloseしました')
            else:
                window['-STATUS-'].update(f'正しいCOCOAログではありません')

        if event == '-BUTTON_EXCEL-':
            if merge_df is not None:
                bookname = cex.create_cocoa_excel(logger, merge_df)
                window['-STATUS-'].update(f'Excelファイルが作成されました: {bookname}')
            else:
                window['-STATUS-'].update(f'正しいCOCOAログではありません')

        if event == '-BUTTON_LOGINFO-':
            log_detail = 'COCOAログ情報\n'+'\n'.join(cc.COCOA_LOG_INFORMATION)
            value = sg.popup_ok_cancel(log_detail)
            # pprint(value)
            continue

        if event == '-BUTTON_FILE-' or value['-MENU-'] == 'COCOAログファイルを開く':
            select_cocoa_log_filename(logger, window)
            refresh_window(logger, window)


    # print('window closed')
    window.close()


def main(logger, merge_df):
    """GUI main

    Args:
        logger (logging): ロガー
        merge_df (DataFrame): pandas data

    Returns:
        None

    """
    status_message = 'Status is Here. . . '
    if cc.NEED_VALID_COCOA_LOG:
        headings = []
        data = []
        status_message = f'正しいCOCOAログが必要です。ファイル選択ボタンで指定してください: tried to open : {cc.COCOA_LOG}'
    else:
        headings, data = build_table_data(logger, merge_df)
   
    window = create_window(logger, headings, data, status_message)
    handle_events(logger, window, merge_df)
 
