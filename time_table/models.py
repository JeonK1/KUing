from django.db import models


class Lecture(models.Model):
    title = models.CharField(max_length=30)
    professor = models.CharField(max_length=15)
    building = models.CharField(max_length=10, default="건물이름")  # 앞차시 뒷차시 건물이 다를경우 두개의 레코드가 생성됨


class LectureTime(models.Model):
    DAY_OF_THE_WEEK = (
        ('MON', '월'),
        ('TUE', '화'),
        ('WED', '수'),
        ('THR', '목'),
        ('FRI', '금'),
        ('SAT', '토'),
        ('SUN', '일')
    )
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name="lecture_times")
    floor = models.CharField(max_length=10)
    start_time = models.CharField(max_length=2)
    end_time = models.CharField(max_length=2)
    day_of_the_week = models.CharField(max_length=1)
