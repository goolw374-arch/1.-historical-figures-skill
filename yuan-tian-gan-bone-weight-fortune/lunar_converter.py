#!/usr/bin/env python3
"""公历转农历 + 时辰转换工具。用于袁天罡称骨算命 Skill。"""

import sys
import json
from datetime import date, datetime

# ============================================================
# 农历数据：1900-2100 年
# 每个整数编码：低4位=闰月(0=无)，高16位=每月天数(1=30天，0=29天)
# ============================================================
LUNAR_INFO = [
    0x04bd8, 0x04ae0, 0x0a570, 0x054d5, 0x0d260, 0x0d950, 0x16554, 0x056a0, 0x09ad0, 0x055d2,
    0x04ae0, 0x0a5b6, 0x0a4d0, 0x0d250, 0x1d255, 0x0b540, 0x0d6a0, 0x0ada2, 0x095b0, 0x14977,
    0x04970, 0x0a4b0, 0x0b4b5, 0x06a50, 0x06d40, 0x1ab54, 0x02b60, 0x09570, 0x052f2, 0x04970,
    0x06566, 0x0d4a0, 0x0ea50, 0x06e95, 0x05ad0, 0x02b60, 0x186e3, 0x092e0, 0x1c8d7, 0x0c950,
    0x0d4a0, 0x1d8a6, 0x0b550, 0x056a0, 0x1a5b4, 0x025d0, 0x092d0, 0x0d2b2, 0x0a950, 0x0b557,
    0x06ca0, 0x0b550, 0x15355, 0x04da0, 0x0a5b0, 0x14573, 0x052b0, 0x0a9a8, 0x0e950, 0x06aa0,
    0x0aea6, 0x0ab50, 0x04b60, 0x0aae4, 0x0a570, 0x05260, 0x0f263, 0x0d950, 0x05b57, 0x056a0,
    0x096d0, 0x04dd5, 0x04ad0, 0x0a4d0, 0x0d4d4, 0x0d250, 0x0d558, 0x0b540, 0x0b6a0, 0x195a6,
    0x095b0, 0x049b0, 0x0a974, 0x0a4b0, 0x0b27a, 0x06a50, 0x06d40, 0x0af46, 0x0ab60, 0x09570,
    0x04af5, 0x04970, 0x064b0, 0x074a3, 0x0ea50, 0x06b58, 0x05ac0, 0x0ab60, 0x096d5, 0x092e0,
    0x0c960, 0x0d954, 0x0d4a0, 0x0da50, 0x07552, 0x056a0, 0x0abb7, 0x025d0, 0x092d0, 0x0cab5,
    0x0a950, 0x0b4a0, 0x0baa4, 0x0ad50, 0x055d9, 0x04ba0, 0x0a5b0, 0x15176, 0x052b0, 0x0a930,
    0x07954, 0x06aa0, 0x0ad50, 0x05b52, 0x04b60, 0x0a6e6, 0x0a4e0, 0x0d260, 0x0ea65, 0x0d530,
    0x05aa0, 0x076a3, 0x096d0, 0x04afb, 0x04ad0, 0x0a4d0, 0x1d0b6, 0x0d250, 0x0d520, 0x0dd45,
    0x0b5a0, 0x056d0, 0x055b2, 0x049b0, 0x0a577, 0x0a4b0, 0x0aa50, 0x1b255, 0x06d20, 0x0ada0,
    0x14b63, 0x09370, 0x049f8, 0x04970, 0x064b0, 0x168a6, 0x0ea50, 0x06aa0, 0x1a6c4, 0x0aae0,
    0x092e0, 0x0d2e3, 0x0c960, 0x0d557, 0x0d4a0, 0x0da50, 0x05d55, 0x056a0, 0x0a6d0, 0x055d4,
    0x052d0, 0x0a9b8, 0x0a950, 0x0b4a0, 0x0b6a6, 0x0ad50, 0x055a0, 0x0aba4, 0x0a5b0, 0x052b0,
    0x0b273, 0x06930, 0x07337, 0x06aa0, 0x0ad50, 0x14b55, 0x04b60, 0x0a570, 0x054e4, 0x0d160,
    0x0e968, 0x0d520, 0x0daa0, 0x16aa6, 0x056d0, 0x04ae0, 0x0a9d4, 0x0a4d0, 0x0d150, 0x0f252,
    0x0d520,
]

# 天干地支
TIAN_GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DI_ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
SHENG_XIAO = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]

# 农历月份名
LUNAR_MONTHS = ["正", "二", "三", "四", "五", "六", "七", "八", "九", "十", "冬", "腊"]
LUNAR_DAYS = [
    "", "初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十",
    "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
    "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十",
]

# 时辰对照表
SHI_CHEN_MAP = {
    "子": (23, 1), "丑": (1, 3), "寅": (3, 5), "卯": (5, 7),
    "辰": (7, 9), "巳": (9, 11), "午": (11, 13), "未": (13, 15),
    "申": (15, 17), "酉": (17, 19), "戌": (19, 21), "亥": (21, 23),
}
SHI_CHEN_LIST = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]


def lunar_year_days(y):
    """计算农历 y 年的总天数"""
    info = LUNAR_INFO[y - 1900]
    total = 0
    for i in range(0, 12):
        total += 29 + ((info >> (15 - i)) & 1)
    leap = info & 0xf
    if leap:
        total += 29 + ((info >> 16) & 1)
    return total


def lunar_leap_month(y):
    """返回农历 y 年的闰月，0 表示无闰月"""
    return LUNAR_INFO[y - 1900] & 0xf


def lunar_month_days(y, m):
    """返回农历 y 年 m 月的天数"""
    info = LUNAR_INFO[y - 1900]
    leap = info & 0xf
    if leap and m == leap + 1:
        # 闰月跟随前一个月
        return 29 + ((info >> 16) & 1)
    if m > 12:
        return 0
    return 29 + ((info >> (16 - m)) & 1)


def solar_to_lunar(year, month, day):
    """
    公历转农历
    返回: (lunar_year, lunar_month, lunar_day, is_leap, ganzhi_year, shengxiao)
    """
    # 基准: 1900-01-31 = 农历 1900 年正月初一
    base_date = date(1900, 1, 31)
    target_date = date(year, month, day)

    if target_date < base_date:
        # 1900年之前，用简化算法
        return _solar_to_lunar_old(year, month, day)

    days_diff = (target_date - base_date).days

    # 逐年跳过
    ly = 1900
    while ly <= 2100:
        y_days = lunar_year_days(ly)
        if days_diff < y_days:
            break
        days_diff -= y_days
        ly += 1

    if ly > 2100:
        raise ValueError("年份超出范围（1900-2100）")

    # 逐月跳过
    leap = lunar_leap_month(ly)
    is_leap = False
    lm = 1
    while lm <= 12:
        m_days = lunar_month_days(ly, lm)
        if days_diff < m_days:
            break
        days_diff -= m_days
        if leap and lm == leap:
            # 闰月
            leap_days = lunar_month_days(ly, lm + 1)  # 闰月天数
            if days_diff < leap_days:
                is_leap = True
                lm = leap  # 是闰月
                break
            days_diff -= leap_days
        lm += 1

    lunar_day = days_diff + 1

    # 干支纪年
    ganzhi_idx = (ly - 4) % 60
    tg = TIAN_GAN[ganzhi_idx % 10]
    dz = DI_ZHI[ganzhi_idx % 12]
    ganzhi_year = tg + dz

    # 生肖
    sx = SHENG_XIAO[ganzhi_idx % 12]

    return ly, lm, lunar_day, is_leap, ganzhi_year, sx


def _solar_to_lunar_old(year, month, day):
    """1900年之前的简化农历转换，基于干支推算"""
    # 用年份干支+公历月日做近似推算
    ganzhi_idx = (year - 4) % 60
    tg = TIAN_GAN[ganzhi_idx % 10]
    dz = DI_ZHI[ganzhi_idx % 12]
    ganzhi_year = tg + dz
    sx = SHENG_XIAO[ganzhi_idx % 12]

    # 1900年前的月日无法精确转换，用公历月日作为近似
    # 实际使用中极少遇到，给出提示
    return year, month, day, False, ganzhi_year, sx


def format_lunar_date(ly, lm, ld, is_leap):
    """格式化农历日期为可读字符串"""
    month_name = LUNAR_MONTHS[lm - 1] if lm <= 12 else "?"
    prefix = "闰" if is_leap else ""
    day_name = LUNAR_DAYS[ld] if ld <= 30 else "?"
    return f"{prefix}{month_name}月{day_name}"


def hour_to_shichen(hour, minute=0):
    """
    将小时转换为时辰
    返回: (时辰名, 日期偏移)
    - 日期偏移: 0=当天, 1=次日（23点后子时算次日）
    """
    if hour == 23 or hour == 0:
        if hour == 23:
            return "子", 1  # 算次日
        return "子", 0
    for name, (start, end) in SHI_CHEN_MAP.items():
        if start <= hour < end:
            return name, 0
    return "子", 0


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "用法: python lunar_converter.py YYYY-MM-DD [HH:MM]"}))
        sys.exit(1)

    date_str = sys.argv[1]
    time_str = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        parts = date_str.split("-")
        y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
    except (ValueError, IndexError):
        print(json.dumps({"error": "日期格式错误，请使用 YYYY-MM-DD"}))
        sys.exit(1)

    try:
        ly, lm, ld, is_leap, ganzhi, sx = solar_to_lunar(y, m, d)

        # 处理时辰
        shichen = None
        day_offset = 0
        if time_str:
            try:
                h, mi = map(int, time_str.split(":"))
                shichen, day_offset = hour_to_shichen(h, mi)
            except (ValueError, IndexError):
                pass

        # 如果时辰导致日期偏移（子时23点后）
        if day_offset == 1:
            # 农历日期+1
            next_date = date(y, m, d) + date.resolution
            ly2, lm2, ld2, is_leap2, ganzhi2, sx2 = solar_to_lunar(
                next_date.year, next_date.month, next_date.day
            )
            ly, lm, ld, is_leap, ganzhi, sx = ly2, lm2, ld2, is_leap2, ganzhi2, sx2

        result = {
            "solar_date": f"{y}-{m:02d}-{d:02d}",
            "lunar_year": ly,
            "lunar_month": lm,
            "lunar_day": ld,
            "is_leap": is_leap,
            "ganzhi_year": ganzhi,
            "shengxiao": sx,
            "lunar_date_display": format_lunar_date(ly, lm, ld, is_leap),
            "shichen": shichen,
            "solar_time": time_str,
        }
        print(json.dumps(result, ensure_ascii=False))

    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()