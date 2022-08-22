# -*- coding: utf-8 -*-
"""Cocoa Log Checker for windows console less 

"""
import cocoa
import cocoaConfig as cc

__author__ = "hyuasa"
__version__ = "0.0.1"
__date__ = "Aug 22 2022"

if __name__ == '__main__':
    logger = cc.create_logger()
    cocoa.main(logger)
