#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
报告生成器 - 智慧房东 APP 接口测试
"""

import json, os, sys
from datetime import datetime

# ============================================================
# 公共配置
# ============================================================

TEST_GROUPS = {
    "sy": {
        "name": "🏠 智慧房东",
        "icon": "🏠",
        "color": "#3B82F6",
        "display_order": 1,
    },
    "fy": {
        "name": "🏢 房源管理",
        "icon": "🏢",
        "color": "#10B981",
        "display_order": 2,
    },
}

TEST_CLASSES = {
    "TestAuth":        {"name": "🔐 认证登录",    "icon": "🔐", "order": 1},
    "TestUserInfo":    {"name": "👤 用户信息",    "icon": "👤", "order": 2},
    "TestHouse":       {"name": "🏠 房源",        "icon": "🏠", "order": 3},
    "TestContract":    {"name": "📄 合同",        "icon": "📄", "order": 4},
    "TestActivity":    {"name": "🎯 活动",        "icon": "🎯", "order": 5},
    "TestDevice":      {"name": "📱 设备",        "icon": "📱", "order": 6},
    "TestMeter":       {"name": "📊 抄表",        "icon": "📊", "order": 7},
    "TestBindCard":    {"name": "💳 绑卡",        "icon": "💳", "order": 8},
    "TestHousePromotion": {"name": "🏷️ 推广",     "icon": "🏷️", "order": 9},
    "TestFeign":       {"name": "🔧 Feign调用",  "icon": "🔧", "order": 10},
}

TEST_NAME_MAP = {
    # sy 用例（登录）
    "test_01_login_success":               "正常登录成功",
    "test_02_username_not_exist":          "用户名不存在",
    "test_03_wrong_password":              "密码错误",
    "test_04_empty_username":              "用户名为空",
    "test_05_empty_password":              "密码为空",
    "test_07_short_password":              "密码过短",
    "test_08_unregistered_account":        "未注册账号",
    "test_10_concurrent_login":            "并发登录",
    # sy 用例
    "test_02_user_info":                   "用户信息",
    "test_03_self_menu_with_role":         "角色菜单",
    "test_04_self_menu":                   "菜单列表",
    "test_05_self_menu_for_new":           "新用户菜单",
    "test_06_have_guide":                  "引导页标识",
    "test_07_have_iot":                    "IoT标识",
    "test_08_commission_bear":             "佣金承担",
    "test_09_certificate_expiration_remind": "证件过期提醒",
    "test_10_query_user_guidance":         "用户引导",
    "test_11_get_simple_rent":             "简租信息",
    "test_12_new_house_data_up":           "房源数据上传",
    "test_13_count_waiting_read_message":  "待读消息数",
    "test_14_meter_of_water_total":        "水表总量",
    "test_15_my_contract_num":            "我的合同数",
    "test_16_my_contract_approval_num":    "合同审批数",
    "test_17_contract_approval_list":      "合同审批列表",
    "test_18_banner_pic_more":             "Banner更多",
    "test_19_click_pic":                  "点击图片",
    "test_20_click_pic_more":             "图片更多",
    "test_21_platform_pic":               "平台图片",
    "test_22_query_version_info":         "版本信息",
    "test_23_get_door_lock_status_count": "门锁状态数",
    "test_24_get_door_lock_list":         "门锁列表",
    "test_25_flux_remind_window":         "流量提醒(未超)",
    "test_26_flux_remind_window_overdue": "流量提醒(超限)",
    "test_27_get_bind_card_fail_pop":     "绑卡失败弹窗",
    "test_28_zd_bank_migrate_admin":      "银行迁移",
    "test_29_support_tourist":            "游客支持",
    "test_30_add_mec_address":            "新增地址",
    "test_31_water_meter_list":           "水表列表",
    "test_32_meter_list":                 "仪表列表",
    # fy 用例
    "test_02_accurate_search":            "精准搜索",
    "test_03_cotenancy_list":             "合租列表",
    "test_04_get_block":                  "获取楼栋",
    "test_05_whole_add":                  "整租新增",
    "test_06_cotenancy_add":              "合租新增",
    "test_07_cotenancy_house_edit":       "合租编辑",
    "test_08_get_house_index":            "房源首页",
    "test_09_get_cotenancy_house_index":  "合租首页",
    "test_10_check_house_index_plus":    "房源校验",
    "test_11_house_commission_config_save": "佣金配置",
    "test_12_province_choose":            "省份选择",
    "test_13_city_choose":                "城市选择",
    "test_16_show_landlord_community":    "社区列表",
    "test_17_get_community":               "获取社区",
    "test_18_select_device_price":        "设备价格",
    "test_19_template_choose":            "选择模板",
    "test_20_add_more":                   "更多新增",
}

# ============================================================
# 报告生成
# ============================================================

def generate_report(results: list, output_path: str,
                    report_title: str = "智慧房东 APP 接口测试报告",
                    project_name: str = "智慧房东 APP",
                    start_time: str = "",
                    end_time: str = ""):
    total     = len(results)
    passed    = sum(1 for r in results if r["status"] in ("PASS", "PASSED"))
    failed    = sum(1 for r in results if r["status"] in ("FAIL", "FAILED"))
    pass_rate = f"{passed/total*100:.1f}%" if total > 0 else "0.0%"
    duration  = ""
    if start_time and end_time:
        try:
            s = datetime.fromisoformat(start_time)
            e = datetime.fromisoformat(end_time)
            duration = f"{(e-s).total_seconds():.1f}秒"
        except Exception:
            pass

    # ---------- 全局序号 ----------
    seq_counter = [0]
    def next_seq():
        seq_counter[0] += 1
        return seq_counter[0]

    # ---------- 分离失败/通过 ----------
    failed_results = [r for r in results if r["status"] in ("FAIL", "FAILED")]
    passed_results = [r for r in results if r["status"] in ("PASS", "PASSED")]

    def grp_order(k):
        return 1 if k == "sy" else 2

    # 辅助：从 source_file 提取显示名（如 sy/test_login.py），无则用 group 回退
    def src_disp(r):
        sf = r.get("source_file", "")
        if sf:
            return sf.replace("zhihuifangdong_", "")
        grp = r.get("group", "sy")
        icon = "🏠" if grp == "sy" else "🏢"
        return f"{icon} zhihuifangdong_{grp}"

    # ---------- 卡片 HTML ----------
    # 统一计数器，按卡片/modal/row 共用递增，顺序：失败卡片→通过卡片→表格行→弹窗
    card_counter = [0]

    def card_html(r):
        card_counter[0] += 1
        s = card_counter[0]
        status = r["status"]
        cls    = "pass" if status in ("PASS", "PASSED") else "fail"
        icon   = "✅" if cls == "pass" else "❌"
        name   = TEST_NAME_MAP.get(r["name"], r["name"])
        msg    = (r.get("message") or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        src    = src_disp(r)
        return f"""<div class="test-card {cls}" id="card-{s}" onclick="showDetail({s})">
  <div class="card-top">
    <span class="card-icon">{icon}</span>
    <span class="card-name">{name}</span>
    <span class="card-status">{status}</span>
  </div>
  <div class="card-bottom">
    <span class="card-group">{src}</span>
    <span class="card-msg">{msg[:40]}{'…' if len(msg)>40 else ''}</span>
  </div>
</div>"""

    # ---------- Modal HTML ----------
    # 用卡片同款计数器，保证序号和卡片一一对应
    modal_counter = [0]
    def modal_html(r):
        modal_counter[0] += 1
        s = modal_counter[0]
        status = r["status"]
        cls    = "pass" if status in ("PASS", "PASSED") else "fail"
        icon   = "✅" if cls == "pass" else "❌"
        name   = TEST_NAME_MAP.get(r["name"], r["name"])
        grp = r.get("group","sy")
        grp_name = src_disp(r)
        msg  = (r.get("message") or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        req  = json.dumps(r.get("request") or {}, ensure_ascii=False, indent=2)
        # 响应数据过滤：移除内部字段，只保留接口原始返回
        raw_resp = r.get("response") or {}
        internal_keys = ("_http_status", "_request_info", "_elapsed_ms")
        resp_clean = {k: v for k, v in raw_resp.items() if k not in internal_keys}
        resp = json.dumps(resp_clean, ensure_ascii=False, indent=2)
        return f"""<div id="detail-{s}" class="modal hidden">
  <div class="modal-content {cls}">
    <div class="modal-header">
      <h3>{icon} {name}</h3>
      <button class="close-btn" onclick="closeDetail({s})">×</button>
      <button class="export-md-btn" onclick="exportMd({s})">📥 导出MD</button>
    </div>
    <div class="modal-body">
      <div class="detail-tags">
        <span class="tag grp-tag">{grp_name}</span>
        <span class="tag status-tag {cls}">{status}</span>
      </div>
      <div class="detail-row"><strong>用例名称:</strong> <span>{name}</span></div>
      <div class="detail-row"><strong>接口:</strong> <span>{r.get('api','')}</span></div>
      <div class="detail-row"><strong>状态码:</strong> <span>{r.get('response',{}).get('_http_status','-')}</span></div>
      <div class="detail-row"><strong>耗时:</strong> <span>{r.get('duration','-')}ms</span></div>
      <div class="detail-section">
        <div class="detail-label">📌 公共参数（请求头/URL）</div>
        <pre class="detail-pre">{req or '-'}</pre>
      </div>
      <div class="detail-section">
        <div class="detail-label">响应信息</div>
        <pre class="detail-pre">{resp or '-'}</pre>
      </div>
      <div class="detail-section">
        <div class="detail-label">结果信息</div>
        <pre class="detail-pre">{msg or '-'}</pre>
      </div>
    </div>
  </div>
</div>"""

    # ---------- 列表行 HTML ----------
    # 用独立递增计数器，与卡片/modal 顺序一致：失败在前，通过在后
    row_counter = [0]
    def table_row_html(r):
        row_counter[0] += 1
        s = row_counter[0]
        status = r["status"]
        cls    = "pass" if status in ("PASS", "PASSED") else "fail"
        icon   = "✅" if cls == "pass" else "❌"
        name   = TEST_NAME_MAP.get(r["name"], r["name"])
        src    = src_disp(r)
        msg = (r.get("message") or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        raw_resp = r.get("response") or {}
        internal_keys = ("_http_status", "_request_info", "_elapsed_ms")
        resp_clean = {k: v for k, v in raw_resp.items() if k not in internal_keys}
        resp_str = json.dumps(resp_clean, ensure_ascii=False)
        return f"""<tr class="{cls}" onclick="showDetail({s})">
  <td>{s}</td>
  <td>{icon}</td>
  <td>{name}</td>
  <td>{src}</td>
  <td>{r.get('api','-')}</td>
  <td>{r.get('duration','-')}ms</td>
  <td class="msg-cell" title="{resp_str}">{resp_str[:60]}{'…' if len(resp_str)>60 else ''}</td>
  <td class="msg-cell" title="{msg}">{msg[:60]}{'…' if len(msg)>60 else ''}</td>
</tr>"""

    # ---------- 构建失败/通过卡片（按 group 排序） ----------
    def build_card_section(results_list, empty_msg):
        if not results_list:
            return f'<p class="empty-tip">{empty_msg}</p>'
        # 按 group 排序
        by_group = {}
        for r in results_list:
            by_group.setdefault(r.get("group","sy"), []).append(r)
        parts = []
        for grp in sorted(by_group.keys(), key=grp_order):
            grp_color = "#3B82F6" if grp == "sy" else "#10B981"
            grp_icon = "🏠" if grp == "sy" else "🏢"
            gr = by_group[grp]
            parts.append(f'<div class="group-block">')
            parts.append(f'  <div class="group-label" style="border-left:3px solid {grp_color}">')
            parts.append(f'    <span class="group-label-icon">{grp_icon}</span>')
            parts.append(f'    <span class="group-label-name">zhihuifangdong_{grp}</span>')
            parts.append(f'    <span class="group-label-count">{len(gr)}个</span>')
            parts.append(f'  </div>')
            parts.append(f'  <div class="test-grid">')
            for r in gr:
                parts.append(card_html(r))
            parts.append(f'  </div>')
            parts.append(f'</div>')
        return "".join(parts)

    failed_cards = build_card_section(failed_results, "🎉 全部通过，无失败用例")
    passed_cards = build_card_section(passed_results, "⚠️ 暂无通过用例")

    # ---------- 构建列表（全局序号，所有结果） ----------
    all_rows = "".join(table_row_html(r) for r in failed_results + passed_results)

    # ---------- 所有 modal（按卡片顺序：失败在前，通过在后） ----------
    modal_counter = [0]
    def modal_html(r):
        modal_counter[0] += 1
        s = modal_counter[0]
        status = r["status"]
        cls    = "pass" if status in ("PASS", "PASSED") else "fail"
        icon   = "✅" if cls == "pass" else "❌"
        name   = TEST_NAME_MAP.get(r["name"], r["name"])
        grp_name = src_disp(r)
        msg  = (r.get("message") or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        # 请求信息分两部分：公共参数 vs 接口数据
        ri = r.get("request") or {}
        public_keys = ("method", "url", "headers")
        pub_req = {k: ri.get(k) for k in public_keys}
        api_keys = ("params", "json_data", "data")
        api_req = {k: ri.get(k) for k in api_keys}
        req_pub  = json.dumps(pub_req, ensure_ascii=False, indent=2)
        req_api  = json.dumps(api_req, ensure_ascii=False, indent=2)
        # 响应数据过滤：移除内部字段，只保留接口原始返回
        raw_resp = r.get("response") or {}
        internal_keys = ("_http_status", "_request_info", "_elapsed_ms")
        resp_clean = {k: v for k, v in raw_resp.items() if k not in internal_keys}
        resp = json.dumps(resp_clean, ensure_ascii=False, indent=2)
        return f"""<div id="detail-{s}" class="modal hidden">
  <div class="modal-content {cls}">
    <div class="modal-header">
      <h3>{icon} {name}</h3>
      <button class="close-btn" onclick="closeDetail({s})">×</button>
      <button class="export-md-btn" onclick="exportMd({s})">📥 导出MD</button>
    </div>
    <div class="modal-body">
      <div class="detail-tags">
        <span class="tag grp-tag">{grp_name}</span>
        <span class="tag status-tag {cls}">{status}</span>
      </div>
      <div class="detail-row"><strong>用例名称:</strong> <span>{name}</span></div>
      <div class="detail-row"><strong>接口:</strong> <span>{r.get('api','')}</span></div>
      <div class="detail-row"><strong>状态码:</strong> <span>{r.get('response',{}).get('_http_status','-')}</span></div>
      <div class="detail-row"><strong>耗时:</strong> <span>{r.get('duration','-')}ms</span></div>
      <div class="detail-section">
        <div class="detail-label">📌 公共参数（请求头/URL）</div>
        <pre class="detail-pre">{req_pub}</pre>
      </div>
      <div class="detail-section">
        <div class="detail-label">📎 接口数据（参数/Body）</div>
        <pre class="detail-pre">{req_api}</pre>
      </div>
      <div class="detail-section">
        <div class="detail-label">响应信息</div>
        <pre class="detail-pre">{resp or '-'}</pre>
      </div>
      <div class="detail-section">
        <div class="detail-label">结果信息</div>
        <pre class="detail-pre">{msg or '-'}</pre>
      </div>
    </div>
  </div>
</div>"""

    all_modals = "".join(modal_html(r) for r in failed_results) + "".join(modal_html(r) for r in passed_results)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{report_title}</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'PingFang SC','Microsoft YaHei',sans-serif;background:#f0f2f5;color:#333;min-height:100vh}}

/* ---- 顶部标题栏 ---- */
.header{{
  background:linear-gradient(135deg,#1a2538,#2a3f5f);
  color:#fff;
  padding:32px 40px;
  text-align:center;
}}
.header-top{{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:24px;
}}
.header-title{{font-size:22px;font-weight:700;margin-bottom:4px}}
.header-sub{{font-size:13px;opacity:0.7}}
.header-meta{{
  display:flex;
  flex-wrap:wrap;
  gap:16px;
  font-size:13px;
  opacity:0.85;
  margin-top:6px;
  justify-content:center;
}}

/* ---- 统计数据条 ---- */
.stats-bar{{
  background:#fff;
  border-radius:12px;
  padding:20px 28px;
  display:flex;
  gap:0;
  margin:-20px 40px 0;
  position:relative;
  top:-12px;
  box-shadow:0 4px 16px rgba(0,0,0,.08);
  border:1px solid #f0f0f0;
}}
.stat-item{{
  flex:1;
  text-align:center;
  padding:0 16px;
}}
.stat-item:not(:last-child){{
  border-right:1px solid #e8e8e8;
}}
.stat-num{{font-size:30px;font-weight:700}}
.stat-lbl{{font-size:12px;color:#888;margin-top:2px}}
.stat-num.green{{color:#10B981}}
.stat-num.red{{color:#EF4444}}
.stat-num.blue{{color:#3B82F6}}

/* ---- 导航 ---- */
.nav{{
  display:flex;
  gap:6px;
  padding:12px 40px;
  background:#fff;
  border-bottom:1px solid #e8e8e8;
  position:sticky;
  top:0;
  z-index:100;
}}
.nav button{{
  padding:8px 18px;
  border:1px solid #d0d0d0;
  background:#fff;
  border-radius:8px;
  cursor:pointer;
  font-size:13px;
  transition:all .2s;
  color:#555;
}}
.nav button:hover{{border-color:#3B82F6;color:#3B82F6}}
.nav button.active{{background:#2a3f5f;color:#fff;border-color:#2a3f5f}}

/* ---- 内容区 ---- */
.content{{padding:20px 40px 40px;max-width:1400px;margin:0 auto}}

/* ---- 失败卡片区 ---- */
.section-header{{
  display:flex;
  align-items:center;
  gap:10px;
  margin:20px 0 14px;
}}
.section-header h2{{font-size:17px;font-weight:700}}
.section-header .badge{{
  font-size:12px;
  padding:2px 10px;
  border-radius:20px;
  font-weight:600;
}}
.badge-red{{background:#FEE2E2;color:#991B1B}}
.badge-green{{background:#D1FAE5;color:#065F46}}
.badge-gray{{background:#F3F4F6;color:#666}}

.group-block{{margin-bottom:20px}}
.group-label{{
  display:flex;
  align-items:center;
  gap:8px;
  padding:6px 12px;
  background:#f8fafc;
  border-radius:8px;
  margin-bottom:10px;
}}
.group-label-icon{{font-size:16px}}
.group-label-name{{font-weight:600;font-size:14px;color:#333}}
.group-label-count{{margin-left:auto;font-size:12px;color:#888}}

.empty-tip{{text-align:center;padding:40px;color:#aaa;font-size:14px}}

/* ---- 卡片网格 ---- */
.test-grid{{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(280px,1fr));
  gap:12px;
}}
.test-card{{
  background:#fff;
  border-radius:12px;
  padding:14px 16px;
  cursor:pointer;
  transition:all .2s;
  border:2px solid transparent;
  box-shadow:0 1px 6px rgba(0,0,0,.05);
  display:flex;
  flex-direction:column;
  gap:8px;
}}
.test-card:hover{{transform:translateY(-2px);box-shadow:0 6px 20px rgba(0,0,0,.12)}}
.test-card.pass{{border-left:4px solid #10B981}}
.test-card.fail{{border-left:4px solid #EF4444}}

.card-top{{display:flex;align-items:center;gap:8px}}
.card-icon{{font-size:18px}}
.card-name{{flex:1;font-size:14px;font-weight:600;color:#222}}
.card-status{{
  font-size:11px;
  padding:2px 8px;
  border-radius:10px;
  font-weight:600;
  background:#f0f0f0;color:#666;
}}
.pass .card-status{{background:#d1fae5;color:#065f46}}
.fail .card-status{{background:#fee2e2;color:#991b1b}}

.card-bottom{{display:flex;align-items:center;gap:8px;font-size:12px}}
.card-group{{color:#888;white-space:nowrap}}
.card-msg{{color:#999;flex:1;text-align:right;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}

/* ---- 列表 ---- */
.table-wrap{{
  background:#fff;
  border-radius:12px;
  overflow:hidden;
  box-shadow:0 2px 12px rgba(0,0,0,.06);
  margin-top:16px;
}}
.results-table{{width:100%;border-collapse:collapse}}
.results-table th{{
  background:#f5f7fa;
  text-align:left;
  padding:11px 14px;
  font-size:13px;
  color:#666;
  font-weight:600;
  border-bottom:1px solid #e8e8e8;
}}
.results-table td{{
  padding:10px 14px;
  border-bottom:1px solid #f5f5f5;
  font-size:13px;
}}
.results-table tr:last-child td{{border-bottom:none}}
.results-table tr{{cursor:pointer;transition:background .15s}}
.results-table tbody tr:hover{{background:#f8faff}}
.results-table .pass td{{background:#fafffe}}
.results-table .fail td{{background:#fffafa}}
.results-table .msg-cell{{max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#666}}

/* ---- Modal ---- */
.modal{{
  position:fixed;
  inset:0;
  background:rgba(0,0,0,.55);
  display:flex;
  align-items:center;
  justify-content:center;
  z-index:1000;
  padding:20px;
}}
.modal.hidden{{display:none}}
.modal-content{{
  background:#fff;
  border-radius:16px;
  width:100%;
  max-width:700px;
  max-height:88vh;
  overflow-y:auto;
  box-shadow:0 24px 64px rgba(0,0,0,.35);
}}
.modal-header{{
  display:flex;
  align-items:center;
  justify-content:space-between;
  padding:20px 24px;
  border-bottom:1px solid #f0f0f0;
  position:sticky;
  top:0;
  background:#fff;
  border-radius:16px 16px 0 0;
}}
.modal-header h3{{font-size:17px;font-weight:700}}
.close-btn{{
  width:32px;height:32px;
  border-radius:50%;
  border:none;
  background:#f0f0f0;
  font-size:20px;
  cursor:pointer;
  display:flex;align-items:center;justify-content:center;
  color:#666;
}}
.close-btn:hover{{background:#e0e0e0}}
.export-md-btn{{
  padding:6px 14px;
  border-radius:8px;
  border:none;
  background:#3b82f6;
  color:#fff;
  font-size:13px;
  cursor:pointer;
  margin-right:8px;
}}
.export-md-btn:hover{{background:#2563eb}}
.modal-body{{padding:20px 24px}}
.detail-tags{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px}}
.tag{{padding:4px 10px;border-radius:6px;font-size:12px;font-weight:600}}
.tc-tag{{background:#e8f0ff;color:#2a5fc0}}
.grp-tag{{background:#e8f8f0;color:#0f7a45}}
.status-tag.pass{{background:#d1fae5;color:#065f46}}
.status-tag.fail{{background:#fee2e2;color:#991b1b}}
.detail-row{{padding:6px 0;font-size:14px;color:#444}}
.detail-row strong{{color:#222;width:56px;display:inline-block}}
.detail-section{{margin-top:14px}}
.detail-label{{font-size:13px;font-weight:600;color:#555;margin-bottom:6px}}
.detail-pre{{
  background:#f8f9fa;
  border:1px solid #e8e8e8;
  border-radius:8px;
  padding:10px 12px;
  font-size:12px;
  line-height:1.6;
  white-space:pre-wrap;
  word-break:break-all;
  max-height:200px;
  overflow-y:auto;
  color:#333;
}}

.footer{{text-align:center;padding:24px;color:#bbb;font-size:12px}}

@media(max-width:768px){{
  .header{{padding:20px}}
  .header-top{{flex-direction:column}}
  .stats-bar{{margin:-12px 20px 0;gap:0;flex-wrap:wrap}}
  .stat-item{{min-width:50%}}
  .content{{padding:16px}}
  .nav{{padding:12px 16px}}
  .test-grid{{grid-template-columns:1fr}}
}}
</style>
</head>
<body>

<!-- 顶部标题 -->
<div class="header">
  <div class="header-top">
    <div>
      <div class="header-title">📊 {report_title}</div>
      <div class="header-sub">{project_name}</div>
      <div class="header-meta">
        <span>⏱ 开始: {start_time or '-'}</span>
        <span>⏱ 结束: {end_time or '-'}</span>
        <span>⏳ 耗时: {duration or '-'}</span>
      </div>
    </div>
  </div>
</div>

<!-- 数据统计条 -->
<div class="stats-bar">
  <div class="stat-item">
    <div class="stat-num blue">{total}</div>
    <div class="stat-lbl">用例总数</div>
  </div>
  <div class="stat-item">
    <div class="stat-num green">{passed}</div>
    <div class="stat-lbl">通过</div>
  </div>
  <div class="stat-item">
    <div class="stat-num red">{failed}</div>
    <div class="stat-lbl">失败</div>
  </div>
  <div class="stat-item">
    <div class="stat-num blue">{pass_rate}</div>
    <div class="stat-lbl">通过率</div>
  </div>
  <div class="stat-item">
    <div class="stat-num" style="color:#666">{duration or '-'}</div>
    <div class="stat-lbl">执行耗时</div>
  </div>
</div>

<!-- 导航 -->
<div class="nav">
  <button class="active" onclick="switchView('fail')">❌ 失败用例</button>
  <button onclick="switchView('pass')">✅ 通过用例</button>
  <button onclick="switchView('table')">📋 用例列表</button>
</div>

<!-- 内容 -->
<div class="content">

  <!-- 失败用例卡片 -->
  <div id="view-fail" class="view-section">
    <div class="section-header">
      <h2>❌ 失败用例</h2>
      <span class="badge badge-red">{failed} 个</span>
    </div>
    {failed_cards}
  </div>

  <!-- 通过用例卡片 -->
  <div id="view-pass" class="view-section" style="display:none">
    <div class="section-header">
      <h2>✅ 通过用例</h2>
      <span class="badge badge-green">{passed} 个</span>
    </div>
    {passed_cards}
  </div>

  <!-- 用例列表 -->
  <div id="view-table" class="view-section" style="display:none">
    <div class="section-header">
      <h2>📋 用例列表</h2>
      <span class="badge badge-gray">{total} 个</span>
    </div>
    <div class="table-wrap">
      <table class="results-table">
        <thead>
          <tr>
            <th>#</th>
            <th>状态</th>
            <th>用例名称</th>
            <th>来源</th>
            <th>接口</th>
            <th>耗时</th>
            <th>响应内容</th>
            <th>信息</th>
          </tr>
        </thead>
        <tbody>{all_rows}</tbody>
      </table>
    </div>
  </div>

</div>

<!-- 隐藏的 modal -->
{all_modals}

<div class="footer">
  生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 智慧房东 APP 接口测试
</div>

<script>
function switchView(view) {{
  document.getElementById('view-fail').style.display  = view === 'fail'  ? 'block' : 'none';
  document.getElementById('view-pass').style.display  = view === 'pass'  ? 'block' : 'none';
  document.getElementById('view-table').style.display = view === 'table' ? 'block' : 'none';
  document.querySelectorAll('.nav button').forEach(b => b.classList.remove('active'));
  event.target.classList.add('active');
}}

function showDetail(seq) {{
  document.querySelectorAll('.modal').forEach(m => m.classList.add('hidden'));
  const modal = document.getElementById('detail-' + seq);
  if (modal) modal.classList.remove('hidden');
}}

function closeDetail(seq) {{
  const modal = document.getElementById('detail-' + seq);
  if (modal) modal.classList.add('hidden');
}}
</script>
<script src="export_md.js"></script>
</body>
</html>"""
    esc_script = """<script>document.addEventListener('keydown', function(e){if(e.key==='Escape'){document.querySelectorAll('.modal').forEach(function(m){m.classList.add('hidden')})}});</script>"""
    html = html.replace('</body>', esc_script + '\n</body>').replace('</html>', '\n</html>')

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\n✅ 报告已生成: {output_path}")
