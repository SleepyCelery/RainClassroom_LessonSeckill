from gevent import monkey

monkey.patch_all()
import gevent
import requests
from config import *
from urllib3.util import parse_url
import execjs
from subprocess import Popen, PIPE
import re
import time


def get_classinfo_dict(cookie):
    result_list = []
    homepage_headers['cookie'] = cookie
    response = requests.get(url=lesson_list_url, headers=homepage_headers)
    data = response.json()['data']['list']
    for i in data:
        class_dict = {}
        class_dict['course_name'] = i['course']['name']
        class_dict['teacher_name'] = i['teacher']['name']
        class_dict['classroom_id'] = i['classroom_id']
        class_dict['course_id'] = i['course']['id']
        result_list.append(class_dict)
    return result_list


def get_sku_id(cookie, classroom_id):
    classroompage_headers['cookie'] = cookie
    response = requests.get(url=get_skuid_url.format(classroom_id=classroom_id), headers=classroompage_headers)
    return response.json()['data']['free_sku_id']


def get_unfinished_video_id(cookie, sku_id, classroom_id):
    score_detail_headers = classroompage_headers
    score_detail_headers['classroom-id'] = str(classroom_id)
    score_detail_headers['cookie'] = cookie
    response = requests.get(url=score_detail_url.format(sku_id=sku_id), headers=score_detail_headers)
    data = response.json()['data']['leaf_level_infos']
    ids = []
    for i in data:
        info = {}
        if i['leaf_type'] == 0 and i['schedule'] != 1:
            info['name'] = i['leaf_level_title']
            info['id'] = i['id']
            ids.append(info)
    return ids


def get_all_video_id(cookie, sku_id, classroom_id):
    score_detail_headers = classroompage_headers
    score_detail_headers['classroom-id'] = str(classroom_id)
    score_detail_headers['cookie'] = cookie
    response = requests.get(url=score_detail_url.format(sku_id=sku_id), headers=score_detail_headers)
    data = response.json()['data']['leaf_level_infos']
    ids = []
    for i in data:
        info = {}
        if i['leaf_type'] == 0:
            info['name'] = i['leaf_level_title']
            info['id'] = i['id']
            ids.append(info)
    return ids


class VideoSession:
    def __init__(self, cookie, classroom_id, video_id):
        self.classroom_id = classroom_id
        self.video_id = video_id
        self.randomcode = execjs.eval("Math.floor(1048576 * (1 + Math.random())).toString(36)")
        self.cookie = cookie
        leaf_info_headers = videopage_headers
        leaf_info_headers['classroom-id'] = str(self.classroom_id)
        leaf_info_headers['cookie'] = self.cookie
        response = requests.get(url=leaf_info_url.format(classroom_id=self.classroom_id, video_id=self.video_id),
                                headers=leaf_info_headers)

        data = response.json()['data']
        self.sku_id = data['sku_id']
        self.course_id = data['course_id']
        self.video_id = data['id']
        self.user_id = data['user_id']
        self.ccid = data['content_info']['media']['ccid']
        self.classroom_id = data['classroom_id']
        self.class_start_time = data['class_start_time']
        self.class_end_time = data['class_end_time']

    def get_play_domain(self):
        playurl_headers = videopage_headers
        playurl_headers['classroom-id'] = str(self.classroom_id)
        playurl_headers['cookie'] = self.cookie
        response = requests.get(url=playurl_info_url.format(ccid=self.ccid), headers=playurl_headers)
        data = response.json()['data']['playurl']['sources']
        for i in data.keys():
            return parse_url(data[i][0]).host

    def get_video_watch_progress(self):
        video_progress_headers = videopage_headers
        video_progress_headers['classroom-id'] = str(self.classroom_id)
        video_progress_headers['cookie'] = self.cookie
        response = requests.get(
            url=video_watch_progress_url.format(course_id=self.course_id, user_id=self.user_id,
                                                classroom_id=self.classroom_id,
                                                video_id=self.video_id), headers=video_progress_headers)
        print(response.json())

    def get_video_detail(self):
        video_detail_headers = classroompage_headers
        video_detail_headers['classroom-id'] = str(self.classroom_id)
        video_detail_headers['cookie'] = self.cookie
        response = requests.get(video_detail_url.format(classroom_id=self.classroom_id, video_id=self.video_id),
                                headers=video_detail_headers)
        print(response.json())

    def get_play_url(self):
        playurl_headers = videopage_headers
        playurl_headers['classroom-id'] = str(self.classroom_id)
        playurl_headers['cookie'] = self.cookie
        response = requests.get(url=playurl_info_url.format(ccid=self.ccid), headers=playurl_headers)
        data = response.json()['data']['playurl']['sources']
        for i in data.keys():
            return data[i][0]

    def get_video_length(self):
        play_url = self.get_play_url()
        p = Popen('./ffprobe.exe -print_format json {}'.format(play_url), stdout=PIPE, stderr=PIPE, stdin=PIPE)
        p.wait()
        output = p.communicate()[1].decode()
        pattern = 'Duration: (.*?),'
        time_string = re.findall(pattern, output)[0]
        h, m, s = time_string.split(':')
        time = int(h) * 3600 + int(m) * 60 + round(float(s), 1)
        return time

    def _build_heartbeat_packets(self):
        sq_count = 1
        video_duration = self.get_video_length()
        play_domain = self.get_play_domain()
        magic_time = 4.7

        def build_payload(played_time: float, video_duration: float, type: str, sq: int, timestamp: int):
            return {
                'c': self.course_id,
                'cc': self.ccid,
                'classroomid': self.classroom_id,
                'cp': played_time,
                'd': video_duration,
                'et': type,
                'fp': 0,
                'i': 5,
                'lob': 'ykt',
                'n': play_domain,
                'p': 'web',
                'pg': '{}_{}'.format(self.video_id, self.randomcode),
                'skuid': self.sku_id,
                'sp': 1,
                'sq': sq,
                't': 'video',
                'tp': 0,
                'ts': str(timestamp),
                'u': self.user_id,
                'uip': "",
                'v': self.video_id
            }

        payloads = []
        payloads.append(build_payload(played_time=0, video_duration=0, type='loadstart', sq=sq_count,
                                      timestamp=int(time.time() * 1000)))
        sq_count += 1
        payloads.append(build_payload(played_time=0, video_duration=video_duration, type='loadeddata', sq=sq_count,
                                      timestamp=int(time.time() * 1000)))
        sq_count += 1
        payloads.append(build_payload(played_time=0, video_duration=video_duration, type='play', sq=sq_count,
                                      timestamp=int(time.time() * 1000)))
        sq_count += 1
        payloads.append(build_payload(played_time=0, video_duration=video_duration, type='playing', sq=sq_count,
                                      timestamp=int(time.time() * 1000)))
        sq_count += 1
        for i in range(int((video_duration - magic_time) / 5) + 5):
            if magic_time + i * 5 <= video_duration:
                payloads.append(
                    build_payload(played_time=magic_time + i * 5, video_duration=video_duration, type='heartbeat',
                                  sq=sq_count,
                                  timestamp=int(time.time() * 1000)))
                sq_count += 1
            else:
                break
        payloads.append(
            build_payload(played_time=video_duration, video_duration=video_duration, type='videoend', sq=sq_count,
                          timestamp=int(time.time() * 1000)))
        return payloads

    def send_heartbeats(self, coroutine=False):
        heartbeat_headers['cookie'] = self.cookie
        heartbeat_headers['x-csrftoken'] = cookie_str2dict(self.cookie)['csrftoken']
        payloads = self._build_heartbeat_packets()
        pos = 0
        heartbeat_data_list = []
        for i in range(int(len(payloads) / 5)):
            heartbeat_data = {'heart_data': payloads[pos:pos + 5]}
            heartbeat_data_list.append(heartbeat_data)
            pos += 5
        heartbeat_data_list.append({'heart_data': payloads[pos:]})

        def send_packet(json_data):
            requests.post(url=heartbeat_url, headers=heartbeat_headers, json=json_data)

        if not coroutine:
            for i in heartbeat_data_list:
                send_packet(i)
        else:
            gevent.joinall([gevent.spawn(send_packet, i) for i in heartbeat_data_list])


if __name__ == '__main__':
    cookie = ''
    classinfo = get_classinfo_dict(cookie)
    classroom_id = classinfo[0]['classroom_id']
    sku_id = get_sku_id(cookie, classroom_id)
    video_ids = get_unfinished_video_id(cookie, sku_id, str(classroom_id))
    session = VideoSession(cookie, classroom_id, video_ids[0]['id'])
    session.send_heartbeats(coroutine=True)
