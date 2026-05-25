#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""探针：打印 record_result 内部 traceback"""
import sys; sys.path.insert(0, '..')
import traceback, linecache, os

# Patch record_result to print traceback
import base_tester
orig_rr = base_tester.record_result

def traced_record_result(name, api, response, status, group="sy", source_file=""):
    tb = traceback.extract_stack()
    print(f"\n=== record_result traceback for {name} ===")
    print(f"Stack depth: {len(tb)}")
    for i, frame in enumerate(reversed(tb)):
        fname = frame.filename
        lineno = frame.lineno
        frame_line = linecache.getline(fname, lineno).strip() if os.path.exists(fname) else '<missing>'
        is_import = frame_line.startswith("import ")
        skips = []
        if 'record_result' in fname: skips.append('rec')
        if fname.endswith('zhihuifangdong_fy.py'): skips.append('fy')
        if fname.endswith('base_tester.py'): skips.append('base')
        print(f"  [{i}] {os.path.basename(fname):<35} L{lineno:<4} skip={skips} import={is_import}")
        print(f"       {repr(frame_line[:60])}")
    return orig_rr(name, api, response, status, group, source_file)

base_tester.record_result = traced_record_result

# Run just test_cotenancy_list
from base_tester import set_token, TEST_RESULTS
set_token("fake_token")

import test_cotenancy_list as t03
try:
    t03.TestCotenancy().test_03_cotenancy_list()
except Exception as e:
    pass
