from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from .models import Lecture, LectureTime, Reservation
from time import sleep
import pandas as pd
from datetime import datetime, timedelta
import time
import math
import numpy as np
from .functions import getClassName

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
            if floors.__contains__(tmp_floor):  # 중복검사
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

        # GET 인자로 filterType 가져오기
        ### filterType ###
        # 0 : 전체강의실
        # 1 : 사용중
        # 2 : 빈강의실
        filterType = '0'
        if self.request.GET:
            try:
                filterType = self.request.GET.get('typeNum', None)
                if(filterType != '0' and filterType != '1' and filterType != '2'):
                    # 0, 1, 2 이외의 숫자는 다 0으로 보내버림
                    filterType = '0'
            except:
                filterType = '0'

        lectures_in_building = Lecture.objects.filter(building=BUILDINGS[building_index][1])
        floors = []
        dataframe = pd.DataFrame(columns=["room_num", "day_of_week", "start_time_sec", "end_time_sec"])
        now_time = datetime.now()
        for lec in lectures_in_building:
            # 강의 까지 남은 시간
            tmp_day_of_the_week = lec.lecture_times.get().day_of_the_week
            tmp_start_time = datetime(now_time.year, now_time.month, now_time.day,
                                      math.floor(8.5 + int(lec.lecture_times.get().start_time) * 0.5),
                                      0 if int(lec.lecture_times.get().start_time)%2 == 1 else 30)
            tmp_end_time = datetime(now_time.year, now_time.month, now_time.day,
                                      math.floor(9.0 + int(lec.lecture_times.get().end_time) * 0.5),
                                      0 if int(lec.lecture_times.get().end_time)%2 == 0 else 30)
            tmp_floor = lec.lecture_times.get().floor #강의실 번호
            # print(str(tmp_floor) + str(tmp_day_of_the_week) + str(tmp_start_time) + str(lec.lecture_times.get().start_time)) # This is Log
            # print(str(tmp_floor) + str(tmp_day_of_the_week) + str(tmp_end_time) + str(lec.lecture_times.get().end_time)) # This is Log
            diff_min = 0
            #dataframe에 강의실정보 다 넣기(화면에 보여주기 위한 재구성)
            tmp_start_time_sec = tmp_start_time.hour*3600 + tmp_start_time.minute*60 + tmp_start_time.second
            tmp_end_time_sec = tmp_end_time.hour*3600 + tmp_end_time.minute*60 + tmp_end_time.second
            dataframe.loc[len(dataframe)] = [tmp_floor, tmp_day_of_the_week, tmp_start_time_sec, tmp_end_time_sec]

        # print(dataframe) # This is Log
        room_num_list = list(dataframe.groupby(['room_num']))
        for room_num in room_num_list:
            cur_room_num = room_num[0]
            cur_class_list = dataframe[dataframe['room_num']==cur_room_num]
            cur_today_class_list = cur_class_list[cur_class_list['day_of_week']==now_day_of_week]
            cur_today_class_list = cur_today_class_list.sort_values(by=['start_time_sec'])

            res_start_time_sec = -1 # 빈강의실
            res_end_time_sec = -1 # 빈강의실
            for now_class in cur_today_class_list.iloc:
                now_time_sec = now_time.hour * 3600 + now_time.minute * 60 + now_time.second
                # print(room_num) # This is Log
                # print(str(now_time.hour) + "시" + str(now_time.minute) + "분") # This is Log
                # print(str(now_class['start_time_sec']/3600) + "시" + str((now_class['start_time_sec']%3600)/60)+"분") # This is Log
                # print(str(now_class['end_time_sec']/3600) + "시" + str((now_class['end_time_sec']%3600)/60)+"분") # This is Log
                if(now_time_sec < now_class['start_time_sec'] and res_start_time_sec==-1 and res_end_time_sec==-1):
                    #시작 전
                    res_start_time_sec = now_class['start_time_sec']
                    res_end_time_sec = now_class['end_time_sec']
                elif(now_class['start_time_sec'] < now_time_sec and now_time_sec < now_class['end_time_sec']):
                    #수업 중
                    res_start_time_sec = 0
                    res_end_time_sec = 0

            if(res_start_time_sec == -1 and res_end_time_sec == -1):
                # 강의실 비어있음
                if(filterType=="0" or filterType=="2"):
                    floors.append((
                        cur_room_num,
                        res_start_time_sec,
                        res_end_time_sec
                    ))
            elif(res_start_time_sec == 0 and res_end_time_sec == 0):
                # 사용 중(수업 중)
                if(filterType=="0" or filterType=="1"):
                    floors.append((
                        cur_room_num,
                        res_start_time_sec,
                        res_end_time_sec
                    ))
            else:
                # 강의 시작 N분전
                if(filterType=="0" or filterType=="2"):
                    if(res_start_time_sec - now_time_sec > 3600):
                        #1시간 보다 더 뒤
                        floors.append((
                            cur_room_num,
                            int((res_start_time_sec - now_time_sec)/3600),
                            0
                        ))
                    else:
                        #1시간 안쪽
                        floors.append((
                            cur_room_num,
                            0,
                            int(((res_start_time_sec - now_time_sec) / 60) % 60)
                        ))
        context['building_index'] = building_index
        context['building_name'] = BUILDINGS[building_index][0]
        context['lectures_in_building'] = lectures_in_building
        context['floors'] = floors
        context['filterType'] = filterType
        return context


class Room(ListView):
    template_name = "room.html"
    model = Lecture

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        floor = self.kwargs['floor']
        building_index = self.kwargs['building_index']
        lectures = Lecture.objects.filter(building=BUILDINGS[building_index][1])
        lecture_information = []
        for lecture in lectures:
            times_same_floor = lecture.lecture_times.filter(floor=floor)
            if (times_same_floor.exists()):
                for times in times_same_floor:
                    tmp_info = {
                        'title': times.lecture.title,
                        'day_of_the_week': times.day_of_the_week,
                        'start_time': times.start_time,
                        'end_time': times.end_time,
                    }
                    lecture_information.append(tmp_info)

        context['lecture_information'] = lecture_information
        time_table_arr = [[0 for _ in range(22)] for _ in range(5)]  # 오전 9시~19시

        for li in lecture_information:
            day_dict = {'월': 0, '화': 1, '수': 2, '목': 3, '금': 4}
            day_idx = day_dict[li['day_of_the_week']]
            start_time = int(li['start_time'])
            end_time = int(li['end_time'])
            len = end_time - start_time 
            # for i in range(len + 1):
                # if i is 0:
            time_table_arr[day_idx][start_time - 1] = {'is_using':1, 'title': li['title'], 'length': len+1}
            time_table_arr[day_idx][start_time - 1 + len -1 ] = {'is_using':1 }
            # time_table_arr[day_idx][start_time - 1 + len ] = {'is_using':1 }
                # else:
                    # time_table_arr[day_idx][start_time + i] = {'is_using':1, 'title': ''}

        # time_table_arr = np.transpose(time_table_arr)
        context['floor'] = floor
        context['time_table_arr'] = time_table_arr
        context['building_index'] = self.kwargs['building_index']
        context['building_name'] = BUILDINGS[building_index][0]
        context['range_5'] = range(5)
        context['range_24'] = range(24)



        #### 강의실의 수업까지 남은 시간 구하기 ####
        # 현재 요일 가져오기
        DAYOFWEEK = ['월', '화', '수', '목', '금', '토', '일']
        n = time.localtime().tm_wday
        now_day_of_week = DAYOFWEEK[n]

        lectures_in_building = Lecture.objects.filter(building=BUILDINGS[building_index][1])
        floors = []
        dataframe = pd.DataFrame(columns=["room_num", "day_of_week", "start_time_sec", "end_time_sec"])
        now_time = datetime.now()
        for lec in lectures_in_building:
            # 강의 까지 남은 시간
            tmp_day_of_the_week = lec.lecture_times.get().day_of_the_week
            tmp_start_time = datetime(now_time.year, now_time.month, now_time.day,
                                      math.floor(8.5 + int(lec.lecture_times.get().start_time) * 0.5),
                                      0 if int(lec.lecture_times.get().start_time) % 2 == 1 else 30)
            tmp_end_time = datetime(now_time.year, now_time.month, now_time.day,
                                    math.floor(9.0 + int(lec.lecture_times.get().end_time) * 0.5),
                                    0 if int(lec.lecture_times.get().end_time) % 2 == 0 else 30)
            tmp_floor = lec.lecture_times.get().floor  # 강의실 번호
            # print(str(tmp_floor) + str(tmp_day_of_the_week) + str(tmp_start_time) + str(lec.lecture_times.get().start_time)) # This is Log
            # print(str(tmp_floor) + str(tmp_day_of_the_week) + str(tmp_end_time) + str(lec.lecture_times.get().end_time)) # This is Log
            diff_min = 0
            # dataframe에 강의실정보 다 넣기(화면에 보여주기 위한 재구성)
            tmp_start_time_sec = tmp_start_time.hour * 3600 + tmp_start_time.minute * 60 + tmp_start_time.second
            tmp_end_time_sec = tmp_end_time.hour * 3600 + tmp_end_time.minute * 60 + tmp_end_time.second

            dataframe.loc[dataframe.shape[0]] = [tmp_floor, tmp_day_of_the_week, tmp_start_time_sec, tmp_end_time_sec]

        # print(dataframe) # This is Log
        room_num_list = list(dataframe.groupby(['room_num']))
        for room_num in room_num_list:
            cur_room_num = room_num[0]
            cur_class_list = dataframe[dataframe['room_num'] == cur_room_num]
            cur_today_class_list = cur_class_list[cur_class_list['day_of_week'] == now_day_of_week]
            cur_today_class_list = cur_today_class_list.sort_values(by=['start_time_sec'])

            res_start_time_sec = -1  # 빈강의실
            res_end_time_sec = -1  # 빈강의실
            for now_class in cur_today_class_list.iloc:
                now_time_sec = now_time.hour * 3600 + now_time.minute * 60 + now_time.second
                # print(room_num) # This is Log
                # print(str(now_time.hour) + "시" + str(now_time.minute) + "분") # This is Log
                # print(str(now_class['start_time_sec']/3600) + "시" + str((now_class['start_time_sec']%3600)/60)+"분") # This is Log
                # print(str(now_class['end_time_sec']/3600) + "시" + str((now_class['end_time_sec']%3600)/60)+"분") # This is Log
                if (now_time_sec < now_class['start_time_sec'] and res_start_time_sec == -1 and res_end_time_sec == -1):
                    # 시작 전
                    res_start_time_sec = now_class['start_time_sec']
                    res_end_time_sec = now_class['end_time_sec']
                elif (now_class['start_time_sec'] < now_time_sec and now_time_sec < now_class['end_time_sec']):
                    # 수업 중
                    res_start_time_sec = 0
                    res_end_time_sec = 0

            if (res_start_time_sec == -1 and res_end_time_sec == -1):
                # 강의실 비어있음
                floors.append((
                    cur_room_num,
                    res_start_time_sec,
                    res_end_time_sec,
                ))
            elif (res_start_time_sec == 0 and res_end_time_sec == 0):
                # 사용 중(수업 중)
                floors.append((
                    cur_room_num,
                    res_start_time_sec,
                    res_end_time_sec,
                ))
            else:
                # 강의 시작 N분전
                floors.append((
                    cur_room_num,
                    int(res_start_time_sec - now_time_sec),
                    int(res_end_time_sec - now_time_sec)
                ))
        floorInfo = []
        for curFloor in floors:
            curRoomNum = curFloor[0] # 방 번호
            if(int(curRoomNum) == int(floor)):
                floorInfo.append(curFloor) # 현재 선택한 방 정보를 floorInfo로 전송

        # 남은시간 추출
        leftTime = []
        if(floorInfo[0][1]==-1 and floorInfo[0][2]==-1):
            leftTime.append(-1)
            leftTime.append(-1)
        else:
            leftTime.append(int(int(floorInfo[0][1]) / 3600))
            leftTime.append(int(int(int(floorInfo[0][2]) % 3600)/60))

        context['leftTime'] = leftTime
        context['className'] = getClassName(building_index, floorInfo[0])
        return context


class RoomReservation(ListView):
    template_name = "room_reservation.html"
    model = Lecture

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def post(self, request, building_index, floor):
        import datetime
        username = request.POST['username']
        description = request.POST['description']
        start_time = datetime.time(int(request.POST['start_time_hour']), int(request.POST['start_time_min']))
        minutes_to_add = datetime.timedelta(hours=1)
        end_time = (datetime.datetime.combine(datetime.date.today(), start_time) + minutes_to_add).time() # time에 timedelta 더하려면 이렇게 해야됨 ㅋ..

        new_reservation = Reservation.objects.create(
            username=username, building=BUILDINGS[building_index][1], floor=floor, description=description,
            start_time=start_time, end_time=end_time, day_of_the_week='월'
        )
        return redirect(f'../../room_list/{building_index}/{floor}')
