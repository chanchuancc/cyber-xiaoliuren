import datetime
from borax.calendars.lunardate import LunarDate

def get_shichen_index(hour):
    if hour >= 23 or hour < 1:
        return 1
    return (hour + 1) // 2 + 1

def calculate_xiaoliuren(m, d, h):
    return (m + d + h - 2) % 6

# Mock Test
now = datetime.datetime.now()
lunar = LunarDate.from_solar_date(now.year, now.month, now.day)
M, D = lunar.month, lunar.day
H = get_shichen_index(now.hour)
res = calculate_xiaoliuren(M, D, H)

print(f"Time: {now}")
print(f"Lunar: {M}/{D}, Shichen: {H}")
print(f"Result Index: {res}")
