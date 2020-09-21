from django.db import models
import pandas as pd


def init_db():
    data = pd.read_excel("종합강의시간표내역.xlsx")[["교과목명", "강의요시/강의실", "담당교수"]]
    print(data)
    for i, row in data.iterrows():


class LectureTime(models.Model):
    DAY_OF_THE_WEEK = (
        ('MON', '월요일'),
        ('TUE', '화요일'),
        ('WED', '수요일'),
        ('THR', '목요일'),
        ('FRI', '금요일'),
        ('SAT', '토요일'),
        ('SUN', '일요일')
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    day_of_the_week = models.CharField(choices=DAY_OF_THE_WEEK, max_length=3)


class Lecture(models.Model):
    BUILDINGS = [
        ('SY', '상허연구관'),
        ('JG', '종합강의동'),
        ('SG', '생명과학관'),
        ('DS', '동물생명과학관'),
        ('SH', '산학협동관'),
        ('SC', '새천년관'),
        ('UG', '의생명과학연구관'),
        ('GG', '교육과학관'),
        ('YM', '예술문화관'),
        ('HB', '해봉부동산학관'),
        ('GC', '건축관'),
        ('IM', '인문학관'),
        ('GY', '경영관'),
        ('CU', '창의관'),
        ('GH', '과학관'),
        ('ENG', '공학관'),
    ]

    title = models.CharField(max_length=30)
    building = models.CharField(choices=BUILDINGS, max_length=10)
    time = models.ForeignKey(LectureTime, on_delete=models.CASCADE, related_name="lectures")
    professor = models.CharField(max_length=15)

