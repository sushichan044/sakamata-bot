from datetime import datetime, timedelta, timezone
import discord

jst = timezone(timedelta(hours=9), 'Asia/Tokyo')


class TimeData():
    def __init__(self, x):
        self.x = x

# make time data

    def time_schedule(self):
        created_stamp = self.x.published_at.replace(
            'Z', '+00:00')
        created = datetime.fromisoformat(
            created_stamp).astimezone(jst)
        created_str = created.strftime(
            '%Y/%m/%d %H:%M:%S')
        scheduled_stamp = self.x.start_scheduled.replace(
            'Z', '+00:00')
        scheduled = datetime.fromisoformat(
            scheduled_stamp).astimezone(jst)
        scheduled_timestamp = discord.utils.format_dt(scheduled, style='f')
        scheduled_date = datetime.strftime(
            scheduled, '%Y年%m月%d日')
        scheduled_time = datetime.strftime(
            scheduled, '%H時%M分')
        weekday = datetime.date(scheduled).weekday()
        weekday_str = self.turn_weekday_str(weekday)
        return scheduled_date, scheduled_time, scheduled_timestamp, weekday_str, created_str

    def time_going(self):
        actual_start_stamp = self.x.start_actual.replace(
            'Z', '+00:00')
        actual_start = datetime.fromisoformat(
            actual_start_stamp).astimezone(jst)
        actual_start_str = actual_start.strftime(
            '%Y/%m/%d %H:%M:%S')
        return actual_start_str

    def time_ended(self):
        actual_start_stamp = self.x.available_at.replace(
            'Z', '+00:00')
        actual_end = datetime.fromisoformat(
            actual_start_stamp).astimezone(jst) + timedelta(seconds=self.x.duration)
        end_date = actual_end.strftime('%Y年%m月%d日')
        end_time = actual_end.strftime('%H時%M分')
        actual_end_str = actual_end.strftime('%Y/%m/%d %H:%M:%S')
        ast_m, ast_s = divmod(self.x.duration, 60)
        ast_h, ast_m = divmod(ast_m, 60)
        duration_str = f'{ast_h}時間{ast_m}分{ast_s}秒'
        weekday = datetime.date(actual_end).weekday()
        weekday_str = self.turn_weekday_str(weekday)
        return actual_end_str, end_date, end_time, duration_str, weekday_str

    def turn_weekday_str(self, weekday):
        weekday_dic = {0: '月', 1: '火', 2: '水',
                       3: '木', 4: '金', 5: '土', 6: '日'}
        weekday_str = weekday_dic[weekday]
        return weekday_str
