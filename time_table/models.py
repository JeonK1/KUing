from django.db import models

BUILDINGS = [
    ('상허연구관', '상허관'),
    ('종합강의동', '종강'),
    ('경영관', '경영'),
    ('산학협동관', '산학'),
    ('신공학관', '신공'),
    ('생명과학관', '생'),
    ('동물생명과학관', '동'),
    ('새천년관', '새'),
    ('의생명과학연구관', '수'),
    ('교육과학관', '사'),
    ('예술문화관', '예'),
    ('해봉부동산학관', '부'),
    ('건축관', '건'),
    ('인문학관', '문'),
    ('창의관', '창'),
    ('과학관', '이'),
    ('공학관 A', '공A'),
    ('공학관 B', '공B'),
    ('공학관 C', '공C'),
    # ('공예관', '공예'),
]


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
