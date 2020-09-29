from django.shortcuts import render
from .models import Lecture, LectureTime
import pandas as pd
from time import sleep


def index(request):
    return render(request, 'index.html', {"lectures": Lecture.objects.all()})


def init(request):
    init_db()
    return render(request, 'index.html', {"lectures": Lecture.objects.all()})


def delete(request):
    Lecture.objects.all().delete()
    return render(request, 'index.html')

def login(request):
    return render(request, 'login.html')

def init_db():
    data = pd.read_excel("종합강의시간표내역.xlsx")[["교과목명", "강의요시/강의실", "담당교수"]].astype(str)
    for i, row in data.iterrows():
        row_data = row["강의요시/강의실"].split(", ")  # 공백 기준으로 나누면 앞차시, 뒷차시로 나뉨
        for j, tmp in enumerate(row_data):
            if tmp[0] != 'n' and tmp[0] != '(':  # 강의요시/강의실이 빈칸인 경우 "nan",(e-러닝) 인 경우를 제외
                tmp = tmp.replace(' ', '')
                building = tmp[7:]  # 건물 정보
                building_char_len = 0
                if len(building) == 0:
                    continue
                if building[0] in ['n', '온', ' ']:
                    continue
                elif building[0] == '상':  # 3글자
                    building_char_len = 3
                elif building[0] in ['종', '경', '산', '신']:  # 2글자
                    building_char_len = 2
                else:
                    building_char_len = 1
                floor = building[building_char_len:-1]  # 끝괄호 전까지 슬라이스, 즉 층수 얻어냄
                building = building[0:building_char_len]
                lecture = Lecture(title=row["교과목명"], professor=row["담당교수"], building=building)
                lecture.save()
                print(lecture.title)
                sleep(0.01)
                time_data = tmp[1:6].split('-')  # 시간은 00-00 꼴
                if len(time_data) != 1:  # 봉사 과목같은 경우 "화00" 같은 형식, 즉 길이가 1인경우 제외
                    lecture_time = LectureTime(lecture=lecture, day_of_the_week=tmp[0],
                                               start_time=time_data[0], end_time=time_data[1], floor=floor)
                    lecture_time.save()
    print("done")
