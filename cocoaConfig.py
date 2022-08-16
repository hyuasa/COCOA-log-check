#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Cocoa Log Checker Config
"""
__author__ = "hyuasa"
__version__ = "0.0.1"
__date__    = "Aug 16 2022"

import argparse
from ast import Store
import logging
import os
import platform
from datetime import date, datetime, timedelta
from datetime import timezone as dttz

global COCOA_LOG, DRAW_GRAPH
DEBUGFILE = os.getenv('DEBUGFILE', default='cocoa_log.txt')
COCOA_LOG = os.getenv('COCOA_LOG', default='exposure_data.json')
COCOA_SCORE_THRESHOLD = 1350
COCOA_EXPOSURE_SHEET_NAME = '接触履歴'
DRAW_GRAPH = False

TZ = 'Asia/Tokyo'
JST = dttz(timedelta(hours=+9), 'JST')
#FONT_NAME= 'IBM Plex Suns JP エクストラ・ライト'
platform_name = platform.system().upper()
if platform_name == 'DARWIN':
    FONT_FAMILY = 'Hiragino sans'
    FONT_NAME = 'IBM Plex Suns JP ExtraLight'
elif platform_name == 'WINDOWS':
    FONT_FAMILY = 'MS Gothic'
    FONT_NAME = 'IBM Plex Suns JP ExtraLight'
else:
    FONT_FAMILY = 'Hiragino sans'
    FONT_NAME = 'IBM Plex Suns JP ExtraLight'


def setup_args():
    """"コマンドライン引数設定

    Args:
        None
    
    Returns:
        (argparse): parser

    """
    parser = argparse.ArgumentParser(description='Cocoa Log Checker')
    parser.add_argument('-l', '--cocoa_log', metavar = 'COCOA_LOGFILE', required = False,
                        help = 'cocoa log file name')
    parser.add_argument('--graph', required = False, action = 'store_true', default = False,
                        help = 'show matplotlib Graph')
    return parser


def parse_args(parser):
    """"parse command line arguments
    
    Args:
        parser (argparse): コマンドライン引数パーサー

    Retuens:
        None
    
    """
    global COCOA_LOG, DRAW_GRAPH
    args = parser.parse_args()
    if args.cocoa_log:
        COCOA_LOG = args.cocoa_log
    if args.graph:
        DRAW_GRAPH = True
    return


def create_logger():
    """ロギングオブジェクトを作成して返す

    Args:
        None

    Returns:
        (logger): logger

    """
    # create logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # create file handler which logs DEBUG level messages
    fh = logging.FileHandler(DEBUGFILE, 'w', 'utf-8')
    fh.setLevel(logging.DEBUG)
    fh_formatter = logging.Formatter(
        '%(asctime)s :%(levelname)s: [%(filename)s: %(funcName)s] %(message)s', '%Y-%m-%d %H:%M:%S')
    fh.setFormatter(fh_formatter)

    # create console handler with a INFO level
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch_formatter = logging.Formatter(
        '%(asctime)s :%(levelname)s: [%(filename)s: %(funcName)s] %(message)s', '%Y-%m-%d %H:%M:%S')
    ch.setFormatter(ch_formatter)

    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger
