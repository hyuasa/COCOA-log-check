#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Cocoa Log Checker

    Input:
       exposure_data.json
   
    Process:
        集計

        - COCOAスコア/日
        - 接触距離ごとの接触時間/日
        - 接触回数/日

    Output:
       - Excel 接触履歴　グラフ
       - matplotlib

"""
__author__ = "hyuasa"
__version__ = "0.0.1"
__date__    = "Aug 16 2022"

import json
import sys  # process関係
import traceback
from datetime import date, datetime, timedelta
from pprint import pformat, pprint

import matplotlib
from matplotlib import pylab as plt

import numpy as np
from openpyxl.comments import Comment
import pandas as pd

import cocoaConfig as cc
import cocoaExcel as cex
import cocoaChart as ccht


def exposure_minutes(s):
    """集計関数 aggfunc
    秒を分にして集計
    """
    return np.sum(s)/60


def calc_score_sum(s):
    """集計関数 aggfunc
    
    """
    return np.sum(s)


def cocoa_score_sum(s):
    """集計関数 aggfunc
    
    """
    return np.sum(s)


def get_instance_score(logger, si=None):
    """ばく露距離に基づくスコア計算
    
    Args:
        Logger (logging): ロガー
        si (scanInstances): スキャンインスタンス

    Returns:
        int: db ばく露中の平均デシベル値 
        int: duration ばく露時間 (秒)
        str: str_dist 距離文字列表記
        float: score ばく露距離考慮のduration値 COCOAスコアに近似
        float: mindb_score: 最強の強度でばく露したと仮定したスコア

    """
    db = si['TypicalAttenuationDb']
    mindb = si['MinAttenuationDb']
    duration = si['SecondsSinceLastScan']
    if db <= 45:
        # immediate
        score = duration * 1.0
        str_dist = '  ~1m'
    elif db <= 59:
        # near
        score = duration  * 2.5
        str_dist = '1m~2m'
    elif db <= 64:
        # medium
        str_dist = '1m~3m'
        score = duration * 1.3
    else:
        # other
        str_dist = '2m~ '
        score = duration * 0.01
    if mindb <= 45:
        # immediate
        mindb_score = duration * 1.0
    elif mindb <= 59:
        # near
        mindb_score = duration * 2.5
    elif mindb <= 64:
        # medium
        mindb_score = duration * 1.3
    else:
        # other
        mindb_score = duration * 0.01
    return db, duration, str_dist, score, mindb_score


def build_dfs(logger, exposure):
    """Build DataFrame from exposure_data.json save to Excel
    
    Args:
        logger (logging): ロガー
        exposure (list/dict): exposure_data.jsonを辞書形式で読み込んだもの

    Returns:
        df : merge_df, daily_summary_df

    """    
    daily_summary = []
    for ds in exposure['daily_summaries']:
        t = pd.Timestamp(ds['DateMillisSinceEpoch'], unit = 'ms', tz = cc.TZ)
        dt = str(t)[:10]
        # print(dt, t.strftime('%a'), ds['DaySummary'])
        duration = ds['DaySummary']['WeightedDurationSum']
        data = {'date': dt, 'dow': t.strftime('%a'), 
                'cocoa_score': duration, 'pv':'cocoa_score'}
        daily_summary.append(data)

    exposures = []
    events = []
    for ew in exposure['exposure_windows']:
        t = pd.Timestamp(ew['DateMillisSinceEpoch'], unit = 'ms', tz = cc.TZ)
        dt = str(t)[:10]
        # print(dt)
        dow = t.strftime("%a")
        for si in ew['ScanInstances']:
            # pprint(si)
            db, duration, str_dist, score, mindb_score = get_instance_score(logger, si = si)
            data = {'date': dt, 'dow': dow, 'dt':t,
                'db': db, 
                'distance': str_dist, 
                'duration': duration,
                'score': score,
                'mindb_score': mindb_score}
            exposures.append(data)
        data = {'date': dt, 'dow': dow, 'contact_event':t, 'pv':'contact'}
        events.append(data)

    daily_summary_df = pd.DataFrame(daily_summary)
    exposures_df = pd.DataFrame(exposures)
    events_df = pd.DataFrame(events)
    # print(daily_summary_df)
    # print(exposures_df)
    # まとめて集計(合計名が重なるので使用せず)
    ex_pv = pd.pivot_table(exposures_df, index = ['date','dow'], 
                        columns = ['distance'], 
                        values = ['score','duration'],
                        aggfunc = [np.sum, exposure_minutes],
                        fill_value = 0,
                        margins = True,
                        margins_name = '合計')

    ex_pv.applymap('{:,.0f}'.format)
    ex_pv=ex_pv.drop(labels = ('sum','duration'), axis = 1)
    ex_pv=ex_pv.drop(labels = ('exposure_minutes','score'), axis = 1)
    #ex_pv = ex_pv.rename(columns={'sum': '累積', 'count':'件数'})
    #ex_pv = ex_pv.rename(columns={'duration':'ばく露時間(秒)', 'score':'算出スコア'})

    # exposure duration(min)
    duration_pv = pd.pivot_table(exposures_df, index = ['date','dow'], 
                        columns = ['distance'], 
                        values = ['duration'],
                        aggfunc = [exposure_minutes],
                        fill_value = 0,
                        margins = True,
                        margins_name = '接触時間計(分)')

    # caluculated score
    calculate_score_pv = pd.pivot_table(exposures_df, index = ['date','dow'], 
                        columns = ['distance'], 
                        values = ['score'],
                        aggfunc = [calc_score_sum],
                        fill_value = 0,
                        margins = True,
                        margins_name = '算出スコア計')
    #接触回数
    events_pv = pd.pivot_table(events_df, index=['date','dow'], 
                        columns = ['pv'],
                        values = ['contact_event'],
                        aggfunc = ['count'])
    #COCOAスコア
    cocoa_score_pv = pd.pivot_table(daily_summary_df, index = ['date','dow'], 
                        columns = ['pv'],
                        values = ['cocoa_score'],
                        aggfunc = [np.sum])
    
    # dfのマージ
    merge_df = pd.merge(duration_pv, events_pv, on = ('date','dow'))
    merge_df = pd.merge(merge_df, cocoa_score_pv, on = ('date','dow'))
    merge_df = pd.merge(merge_df, calculate_score_pv, on = ('date','dow'))
    
    return merge_df


def main(logger):
    """Cocoa Log Checker Main
    
    Args:
        logger (logging): ロガー

    Returns:
        None

    """
    logger.info(f"cocoa_log: {cc.COCOA_LOG}")
    # COCOAログ Read
    try:
        with open(cc.COCOA_LOG, 'r') as exposure_data:
            exposure = json.load(exposure_data)
    except FileNotFoundError as e:
        logger.info(f"ファイルが見つかりません。 {cc.COCOA_LOG}")
        sys.exit()
    except Exception as e:
        stack_trace = traceback.format_exc()
        logger.info(f"Catch Exception: {e}\nSTACK_TRACE:\n{stack_trace}")
        sys.exit()
    
    # COCOAログ Verify
    try:
        logger.info(f"# of exprosure_windows: {len(exposure['exposure_windows'])}")
        logger.info(f"# of daily_summariese: {len(exposure['daily_summaries'])}")
        logger.info(f"app_version: {exposure['app_version']}")
        logger.info(f"platform: {exposure['platform']}")
        logger.info(f"platform_version: {exposure['platform_version']}")
        logger.info(f"model: {exposure['model']}")
        logger.info(f"device_type: {exposure['device_type']}")
        logger.info(f"build_number: {exposure['build_number']}")
        logger.info(f"en_version: {exposure['en_version']}")
    except KeyError as ke:
        logger.info(f'正しいcocoa_logファイルではありません。{cc.COCOA_LOG}')
        sys.exit()
    
    # Build cocoa Dataframs
    merge_df = build_dfs(logger, exposure)
    
    # Output
    if cc.DRAW_GRAPH:
        ccht.draw_cocoa_charts(logger, merge_df)
    else:
        cex.create_cocoa_excel(logger, merge_df)    


if __name__ == '__main__':
    logger = cc.create_logger()
    parser = cc.setup_args()
    cc.parse_args(parser)
    main(logger)
