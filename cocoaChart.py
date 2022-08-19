#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Cocoa Chart Builder

"""
import cocoaConfig as cc
import pandas as pd
import matplotlib.pyplot as plt
from pprint import pformat, pprint
from datetime import date, datetime, timedelta
import warnings
import traceback
import sys  # process関係
from os import TMP_MAX
import json
__author__ = "hyuasa"
__version__ = "0.0.1"
__date__ = "Aug 16 2022"




# constant for Bar Chart
COLOR_WASURENAGUSA = '#89c3eb'
COLOR_KANZOUIRO = '#f8b862'
COLOR_RURIKON = '#19448e'
COLOR_KUROKAWACHA = '#583822'
COLOR_DEFAULT = '#95949a'
R_ANGLE = 60       # X axsix Rotete Angle
TPX = 0.28         # Title Position X coordinate
TPY = 0.85         # Title Position Y coordinate
L_ALPHA = 0.8      # Scale line Transparency
L_WIDTH = 0.4      # Scale Line Width
L_STYLE = 'dashed'  # Scale Line Style
F_MIN = 4          # X axis Font size
F_NORMAL = 10      # Normal Font size


def setup_bar_chart(axes, x_data, y_data, title='チャートタイトル',  y_label='', bar_color=COLOR_DEFAULT, title_color=COLOR_DEFAULT):
    """draw chats

    Args:
        logger (logging): ロガー
        axes (AxesSubplot) : プロットエリア
        x_data (list) : x軸データ
        y_data (list) : y軸データ
        title (str) : チャートタイトル
        y_label (str) : y軸ラベル
        bar_color (matplotlib color str) : 棒グラフの色
        title_color (matplotlib color str) : タイトル文字の色

    Retuens:
        None

    """
    # print(type(axes))
    axes.bar(x_data, y_data, color=bar_color)
    axes.set_title(title, fontname=cc.FONT_FAMILY,
                   y=TPY, x=TPX, color=title_color)
    axes.set_xticklabels(x_data, fontsize=F_MIN, rotation=R_ANGLE, ha='right')
    axes.set_ylabel(y_label, fontsize=F_NORMAL, fontname=cc.FONT_FAMILY)
    axes.grid(which="major", axis="y", color=COLOR_WASURENAGUSA, alpha=L_ALPHA,
              linestyle=L_STYLE, linewidth=L_WIDTH)
    return


def draw_cocoa_charts(logger, df):
    """draw chats

    Args:
        logger (logging): ロガー
        df (DataFrame): グラフを書くDataの入ったDataFrame

    Returns:
        None

    """
    warnings.simplefilter('ignore', UserWarning)

    # data for x axis and contact event count for y axis
    contacts_dict = (df[('count', 'contact_event', 'contact')].to_dict())
    x_axis = []
    days = list(contacts_dict.keys())
    for day in days:
        x_axis.append(day[0])
    a1_y_axis = list(contacts_dict.values())
    # data exposure duraion for y axis
    duration_dict = (
        df[('exposure_minutes', 'duration', '接触時間計(分)')].to_dict())
    a2_y_axis = list(duration_dict.values())
    # data cocoa score for y axis
    cocoa_score_dict = (df[('sum', 'cocoa_score', 'cocoa_score')].to_dict())
    a3_y_axis = list(cocoa_score_dict.values())
    # data calculated score for y axis
    calclate_score_dict = (df[('calc_score_sum', 'score', '算出スコア計')].to_dict())
    a4_y_axis = list(calclate_score_dict.values())

    # create Figure and axes.
    fig, axes = plt.subplots(2, 2, figsize=(10.0, 6.0))   # 2行2列 1000x600ピクセル
    fig.suptitle('COCOA接触履歴 - スコア1350ポイント以上で濃厚接触アラート', fontname=cc.FONT_FAMILY)
    fig.canvas.set_window_title('COCOA Exposure History')

    # axes[0,0] cocoa contact event counts
    setup_bar_chart(axes[0, 0], x_axis, a1_y_axis,
                    bar_color=COLOR_WASURENAGUSA, title_color=COLOR_RURIKON,
                    title='COCOA 接触回数', y_label=' 回数')
    # axes[0,1] cocoa exposure duration
    setup_bar_chart(axes[0, 1], x_axis, a2_y_axis,
                    bar_color=COLOR_WASURENAGUSA, title_color=COLOR_RURIKON,
                    title='COCOA 接触時間(分)', y_label='分')
    # axes[1,0] cocoa score
    setup_bar_chart(axes[1, 0], x_axis, a3_y_axis,
                    bar_color=COLOR_KANZOUIRO, title_color=COLOR_KUROKAWACHA,
                    title='COCOA スコア', y_label='ポイント')
    # axes[1,0] calculated score
    setup_bar_chart(axes[1, 1], x_axis, a4_y_axis,
                    bar_color=COLOR_KANZOUIRO, title_color=COLOR_KUROKAWACHA,
                    title='COCOA 算出スコア', y_label='Calc Score')

    # axes[1,1].axis('off')
    #pd.plotting.table(axes[0,0], df)
    plt.show()

    return
