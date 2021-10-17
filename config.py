login_url = 'https://changjiang.yuketang.cn/v2/web/index'
lesson_list_url = 'https://changjiang.yuketang.cn/v2/api/web/courses/list?identity=2'
get_skuid_url = 'https://changjiang.yuketang.cn/v2/api/web/classrooms/{classroom_id}?role=5'
score_detail_url = 'https://changjiang.yuketang.cn/c27/online_courseware/schedule/score_detail/single/{sku_id}/0/'
leaf_info_url = 'https://changjiang.yuketang.cn/mooc-api/v1/lms/learn/leaf_info/{classroom_id}/{video_id}/'
playurl_info_url = 'https://changjiang.yuketang.cn/api/open/audiovideo/playurl?video_id={ccid}&provider=cc&file_type=1&is_single=0&domain=changjiang.yuketang.cn'
video_watch_progress_url = 'https://changjiang.yuketang.cn/video-log/get_video_watch_progress/?cid={course_id}&user_id={user_id}&classroom_id={classroom_id}&video_type=video&vtype=rate&video_id={video_id}&snapshot=1'
heartbeat_url = 'https://changjiang.yuketang.cn/video-log/heartbeat/'
video_detail_url = 'https://changjiang.yuketang.cn/video-log/detail/?classroom_id={classroom_id}&user_id=0&video_id={video_id}'


def cookie_str2dict(cookiestr):
    cookie_dict = {}
    cookie_list = cookiestr.split(';')
    for i in cookie_list:
        if i != "":
            key, value = i.strip().split('=')
            cookie_dict[key] = value
    return cookie_dict


homepage_headers = {
    'authority': 'changjiang.yuketang.cn',
    'pragma': 'no-cache',
    'cache-control': 'no-cache',
    'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    'dnt': '1',
    'sec-ch-ua-mobile': '?0',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
    'xt-agent': 'web',
    'accept': 'application/json, text/plain, */*',
    'xtbz': 'ykt',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://changjiang.yuketang.cn/v2/web/index',
    'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6',
}

classroompage_headers = {
    'authority': 'changjiang.yuketang.cn',
    'pragma': 'no-cache',
    'cache-control': 'no-cache',
    'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    'x-client': 'web',
    'dnt': '1',
    'sec-ch-ua-mobile': '?0',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
    'xt-agent': 'web',
    'accept': 'application/json, text/plain, */*',
    'xtbz': 'ykt',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6',
}

videopage_headers = {
    'authority': 'changjiang.yuketang.cn',
    'pragma': 'no-cache',
    'cache-control': 'no-cache',
    'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    'dnt': '1',
    'sec-ch-ua-mobile': '?0',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
    'xt-agent': 'web',
    'accept': 'application/json, text/plain, */*',
    'xtbz': 'ykt',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6',
}

heartbeat_headers = {
    'authority': 'changjiang.yuketang.cn',
    'pragma': 'no-cache',
    'cache-control': 'no-cache',
    'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    'dnt': '1',
    'sec-ch-ua-mobile': '?0',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
    'content-type': 'application/json',
    'accept': '*/*',
    'x-requested-with': 'XMLHttpRequest',
    'xtbz': 'ykt',
    'sec-ch-ua-platform': '"Windows"',
    'origin': 'https://changjiang.yuketang.cn',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6',
}
