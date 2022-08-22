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
       - GUI window
       - Excel 接触履歴　グラフ
       - matplotlib グラフ

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

import cocoaConfig as cc
import cocoaGui as cg

__author__ = "hyuasa"
__version__ = "0.0.1"
__date__ = "Aug 16 2022"


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
        score = duration * 2.5
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


def verify_and_build_dataframe(logger, exposure):
    """Verify COCOA log and build dataframe

    Args:
        logger (logging): ロガー
        exposure (list/dict): exposure_data.jsonを辞書形式で読み込んだもの

    Returns:
        DataFrame : valid cocoa log dataframe

    """
    # verify cocoa log
    result = False
    log_information = []
    try:
        log_information.append(f"# of exprosure_windows: {len(exposure['exposure_windows'])}")
        log_information.append(f"# of daily_summariese: {len(exposure['daily_summaries'])}")
        log_information.append(f"app_version: {exposure['app_version']}")
        log_information.append(f"platform: {exposure['platform']}")
        log_information.append(f"platform_version: {exposure['platform_version']}")
        log_information.append(f"model: {exposure['model']}")
        log_information.append(f"device_type: {exposure['device_type']}")
        log_information.append(f"build_number: {exposure['build_number']}")
        log_information.append(f"en_version: {exposure['en_version']}")
        result = True
    except KeyError as ke:
        log_information.append(f'正しいcocoa_logファイルではありません。{cc.COCOA_LOG}')

    cc.COCOA_LOG_INFORMATION = log_information

    # build dataframe
    merge_df = None
    if result:
        # valid ccoa log then build cocoa Dataframs
        merge_df = build_dfs(logger, exposure)
        if len(merge_df) > 0:
            # valid dataframe of cocoa log
            cc.NEED_VALID_COCOA_LOG = False
        else:
            # but empty cocoa log
            merge_df = None
            cc.NEED_VALID_COCOA_LOG = True
    else:
        # not valid cocoa log
        cc.NEED_VALID_COCOA_LOG = True

    return merge_df


def build_dfs(logger, exposure):
    """Build DataFrame from exposure_data.json

    Args:
        logger (logging): ロガー
        exposure (list/dict): exposure_data.jsonを辞書形式で読み込んだもの

    Returns:
        df : merge_df, daily_summary_df

    """
    daily_summary = []
    for ds in exposure['daily_summaries']:
        t = pd.Timestamp(ds['DateMillisSinceEpoch'], unit='ms', tz=cc.TZ)
        dt = str(t)[:10]
        # print(dt, t.strftime('%a'), ds['DaySummary'])
        duration = ds['DaySummary']['WeightedDurationSum']
        data = {'date': dt, 'dow': t.strftime('%a'),
                'cocoa_score': duration, 'pv': 'cocoa_score'}
        daily_summary.append(data)

    exposures = []
    events = []
    for ew in exposure['exposure_windows']:
        t = pd.Timestamp(ew['DateMillisSinceEpoch'], unit='ms', tz=cc.TZ)
        dt = str(t)[:10]
        # print(dt)
        dow = t.strftime("%a")
        for si in ew['ScanInstances']:
            # pprint(si)
            db, duration, str_dist, score, mindb_score = get_instance_score(
                logger, si=si)
            data = {'date': dt, 'dow': dow, 'dt': t,
                    'db': db,
                    'distance': str_dist,
                    'duration': duration,
                    'score': score,
                    'mindb_score': mindb_score}
            exposures.append(data)
        data = {'date': dt, 'dow': dow, 'contact_event': t, 'pv': 'contact'}
        events.append(data)

    daily_summary_df = pd.DataFrame(daily_summary)
    exposures_df = pd.DataFrame(exposures)
    events_df = pd.DataFrame(events)

    # ex_pv not used so far
    ex_pv = pd.pivot_table(exposures_df, index=['date', 'dow'],
                           columns=['distance'],
                           values=['score', 'duration'],
                           aggfunc=[np.sum, exposure_minutes],
                           fill_value=0,
                           margins=True,
                           margins_name='合計')

    ex_pv.applymap('{:,.0f}'.format)
    ex_pv = ex_pv.drop(labels=('sum', 'duration'), axis=1)
    ex_pv = ex_pv.drop(labels=('exposure_minutes', 'score'), axis=1)

    # exposure duration(min)
    duration_pv = pd.pivot_table(exposures_df, index=['date', 'dow'],
                                 columns=['distance'],
                                 values=['duration'],
                                 aggfunc=[exposure_minutes],
                                 fill_value=0,
                                 margins=True,
                                 margins_name='接触時間計(分)')

    # caluculated score
    calculate_score_pv = pd.pivot_table(exposures_df, index=['date', 'dow'],
                                        columns=['distance'],
                                        values=['score'],
                                        aggfunc=[calc_score_sum],
                                        fill_value=0,
                                        margins=True,
                                        margins_name='算出スコア計')
    # 接触回数
    events_pv = pd.pivot_table(events_df, index=['date', 'dow'],
                               columns=['pv'],
                               values=['contact_event'],
                               aggfunc=['count'])
    # COCOAスコア
    cocoa_score_pv = pd.pivot_table(daily_summary_df, index=['date', 'dow'],
                                    columns=['pv'],
                                    values=['cocoa_score'],
                                    aggfunc=[np.sum])

    # dfのマージ
    merge_df = pd.merge(duration_pv, events_pv, on=('date', 'dow'))
    merge_df = pd.merge(merge_df, cocoa_score_pv, on=('date', 'dow'))
    merge_df = pd.merge(merge_df, calculate_score_pv, on=('date', 'dow'))

    return merge_df


def read_cocoa_log(logger):
    """Read Cocoa Log(json) to dict

    Args:
        logger (logging): ロガー

    Returns:
        dict : exposure

    """
    exposure = {}
    try:
        # logger.info(f'cocoa_log: {cc.COCOA_LOG}')
        with open(cc.COCOA_LOG, 'r') as exposure_data:
            exposure = json.load(exposure_data)
    except FileNotFoundError as e:
        logger.info(f"ファイルが見つかりません。 {cc.COCOA_LOG}")
        cc.NEED_VALID_COCOA_LOG = True
    except Exception as e:
        stack_trace = traceback.format_exc()
        logger.info(f"Catch Exception: {e}\nSTACK_TRACE:\n{stack_trace}")
        cc.NEED_VALID_COCOA_LOG = True    
    return exposure
    

def update_dataframe(logger):
    """update Dataframe with current json file

    Args:
        logger (logging): ロガー

    Returns:
        DataFrame : valid cocoa log dataframe

    """
    exposure = read_cocoa_log(logger)
    merge_df = verify_and_build_dataframe(logger, exposure)
    return merge_df


def main(logger):
    """Cocoa Log Checker Main

    Args:
        logger (logging): ロガー

    Returns:
        None

    """
    merge_df = update_dataframe(logger)
    cg.main(logger, merge_df)  # open gui
    return


if __name__ == '__main__':
    logger = cc.create_logger()
    parser = cc.setup_args()
    cc.parse_args(parser)
    main(logger)
