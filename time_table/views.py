from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from .models import Lecture, LectureTime
from time import sleep
import pandas as pd
from datetime import datetime, timedelta
import time
import math

# url의 인자로 들어오는 각 건물의 index값에 대한 건물 이름을 저장한 리스트 (0번째는 편의상 채워넣음)
# 0 인덱스로 접근시 풀네임, 1 인덱스로 접근시 축악어 - DB에는 축약어로 저장되어 있음에 유의
BUILDINGS = [
    ('null', 'null'), ('상허연구관', '상허관'), ('종합강의동', '종강'), ('경영관', '경영'), ('산학협동관', '산학'),
    ('신공학관', '신공'), ('생명과학관', '생'), ('동물생명과학관', '동'), ('새천년관', '새'), ('의생명과학연구관', '수'),
    ('교육과학관', '사'), ('예술문화관', '예'), ('해봉부동산학관', '부'), ('건축관', '건'), ('인문학관', '문'),
    ('창의관', '창'), ('과학관', '이'), ('공학관 A', '공A'), ('공학관 B', '공B'), ('공학관 C', '공C')]


def index(request):
    buildingList = []
    for i in range(1, len(BUILDINGS)):
        buildingList.append({"number": '%02d' % i, "name": BUILDINGS[i][0]})
    return render(request, 'index.html', {"buildings": buildingList})


def init(request):
    init_db()
    return render(request, 'index.html', {"lectures": Lecture.objects.all()})


def delete(request):
    Lecture.objects.all().delete()
    return render(request, 'index.html')


def login(request):
    return render(request, 'login.html')

class RoomFilter(ListView):
    template_name = "room_filter.html"
    model = Lecture

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # self.kwargs['building_index']를 통해서 url에서 building_index값을 받을 수 있습니다.
        building_index = self.kwargs['building_index']
        lectures_in_building = Lecture.objects.filter(building=BUILDINGS[building_index][1])
        floors = []
        for lec in lectures_in_building:
            tmp_floor = lec.lecture_times.get().floor
            if floors.__contains__(tmp_floor): # 중복검사
                continue
            else:
                floors.append(tmp_floor)
        context['building_index'] = building_index
        context['building_name'] = BUILDINGS[building_index][0]
        context['lectures_in_building'] = lectures_in_building
        context['floors'] = floors
        return context

class RoomList(ListView):
    template_name = "room_list.html"
    model = Lecture

    def get_context_data(self, **kwargs):
        # 현재 요일 가져오기
        DAYOFWEEK = ['월', '화', '수', '목', '금', '토', '일']
        n = time.localtime().tm_wday
        now_day_of_week = DAYOFWEEK[n]

        context = super().get_context_data(**kwargs)
        # self.kwargs['building_index']를 통해서 url에서 building_index값을 받을 수 있습니다.
        building_index = self.kwargs['building_index']
        lectures_in_building = Lecture.objects.filter(building=BUILDINGS[building_index][1])
        floors = []
        for lec in lectures_in_building:
            #강의 까지 남은 시간
            tmp_day_of_the_week = lec.lecture_times.get().day_of_the_week
            now_time = datetime.now()
            tmp_start_time = datetime(now_time.year, now_time.month, now_time.day,
                                      math.floor(8.5 + int(lec.lecture_times.get().start_time) * 0.5),
                                      0 if int(lec.lecture_times.get().start_time)%2 == 1 else 30)
            diff_min = 0
            if((tmp_start_time- now_time).seconds < 0):
                diff_min = -1 # 지낫을떈 -1 출력
            else:
                diff_min = math.floor(((tmp_start_time- now_time).seconds / 60)) # 남은 분
            tmp_floor = lec.lecture_times.get().floor #강의실 번호

            isDouble = False # true(중복), false(중복아님)
            for floor in floors:
                if tmp_floor==floor[0]:
                    isDouble = True
                    break
            # if floors.__contains__(tmp_floor): # 중복검사
            #     continue
            if isDouble:
                continue
            elif tmp_floor in floors:
                continue
            else:
                if now_day_of_week != tmp_day_of_the_week:  # 현재 요일 아니면 -1, -1을 넘겨줌
                    floors.append((
                        tmp_floor,
                        -1,
                        -1))
                else:
                    floors.append((
                        tmp_floor,
                        -1 if diff_min < 0 else math.floor(diff_min/60),
                        -1 if diff_min < 0 else math.floor(diff_min%60)))
        context['building_index'] = building_index
        context['building_name'] = BUILDINGS[building_index][0]
        context['lectures_in_building'] = lectures_in_building
        context['floors'] = floors
        return context


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
