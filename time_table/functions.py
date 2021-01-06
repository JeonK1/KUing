import pandas as pd
import time
from .models import Lecture, LectureTime
from datetime import datetime, timedelta


BUILDINGS = [
    ('null', 'null'), ('상허연구관', '상허관'), ('종합강의동', '종강'), ('경영관', '경영'), ('산학협동관', '산학'),
    ('신공학관', '신공'), ('생명과학관', '생'), ('동물생명과학관', '동'), ('새천년관', '새'), ('의생명과학연구관', '수'),
    ('교육과학관', '사'), ('예술문화관', '예'), ('해봉부동산학관', '부'), ('건축관', '건'), ('인문학관', '문'),
    ('창의관', '창'), ('과학관', '이'), ('공학관 A', '공A'), ('공학관 B', '공B'), ('공학관 C', '공C')]
    
def getClassName(building_index, floorInfo):
  
    # 남은 시간과 건물번호로 강의이름을 알아내자
    DAYOFWEEK = ['월', '화', '수', '목', '금', '토', '일']
    n = time.localtime().tm_wday
    now_day_of_week = DAYOFWEEK[n]

    now_time = datetime.now()
    

    if(floorInfo[1]==-1 and floorInfo[2]==-1):
        # 강의 없음
        return 'none'
    else:
        # 강의가 존재할 경우
        # floorInfo[1] : 시작 시간 초
        # floorInfo[2] : 끝나는 시간 초

        now_time_hour = now_time.hour # 현재 시간
        now_time_min = now_time.minute # 현재 분

        if(floorInfo[1]==0):
            # 수업 중 일때
            # 현재시간 start_time의 형식으로 변환(9시=1, 9시 30분=2)
            start_time_hour = now_time_hour
            start_time_min = now_time_min

            start_time = 1 + (start_time_hour-9) * 2
            # 분은 내림으로 계산하여, 30~60분일때 1증가 시켜주기
            if(start_time_min > 30 and start_time_min < 60):
                start_time+=1

            curStartTime = "{:02d}".format(int(start_time))
            curFloor = "{:02d}".format(int(floorInfo[0]))
            res = LectureTime.objects.filter(start_time__lt=curStartTime,
                                             end_time__gt=curStartTime,
                                             day_of_the_week=now_day_of_week,
                                              floor=curFloor,
                                              lecture_id__building = BUILDINGS[building_index][1])
            return res[0].lecture.title
        else:
            # 수업 N분 남음
            left_time_hour = int(int(floorInfo[1]) / (60*60))
            left_time_min = int((int(floorInfo[1]) % (60*60)) / 60)
            start_time_hour = now_time_hour + left_time_hour
            start_time_min = now_time_min + left_time_min

            if(start_time_min > 60):
                start_time_min-=60
                start_time_hour+=1

            if(start_time_min > 57):
                # 시작시간이 58분이나 59분이면 00분으로 만들고, 시작시간 +1 하기
                start_time_hour = start_time_hour+1
                start_time_min = 0
            elif(start_time_min>27 and start_time_min < 30):
                # 시작시간이 30분 가까이 언저리면 30분으로 만들기
                start_time_min = 30

            # 1교시 = 09시
            start_time = 1 + (start_time_hour-9) * 2
            if start_time_min==30:
                start_time+=1 # 30분이면 1 더 추가

            curFloor = "{:02d}".format(int(floorInfo[0]))
            curStartTime = "{:02d}".format(int(start_time))
            res = LectureTime.objects.filter(start_time=curStartTime,
                                              day_of_the_week=now_day_of_week,
                                              floor=curFloor,
                                              lecture_id__building = BUILDINGS[building_index][1])
            return res[0].lecture.title


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
                elif building[0] in ['종', '경', '산', '신', '공']:  # 2글자
                    building_char_len = 2
                else:
                    building_char_len = 1
                floor = building[building_char_len:-1]  # 끝괄호 전까지 슬라이스, 즉 층수 얻어냄
                building = building[0:building_char_len]
                lecture = Lecture(title=row["교과목명"], professor=row["담당교수"], building=building)
                lecture.save()
                # print(lecture.title)
                # sleep(0.01)
                time_data = tmp[1:6].split('-')  # 시간은 00-00 꼴
                if len(time_data) != 1:  # 봉사 과목같은 경우 "화00" 같은 형식, 즉 길이가 1인경우 제외
                    lecture_time = LectureTime(lecture=lecture, day_of_the_week=tmp[0],
                                               start_time=time_data[0], end_time=time_data[1], floor=floor)
                    lecture_time.save()