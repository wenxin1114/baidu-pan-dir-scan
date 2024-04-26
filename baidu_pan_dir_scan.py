import json
import re
import os
import requests
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BaiduScript:
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    verify_url = "https://pan.baidu.com/share/verify"
    list_url = "https://pan.baidu.com/share/list"
    re_surl = re.compile("s/\\d([-\\w]+)")
    re_pwd = re.compile("pwd=([a-zA-Z\\d]+)")

    def __init__(self, bd_url, pwd=None):
        self.shareid = None
        self.share_uk = None
        self.surl = None
        self.cookies = None
        self.url = bd_url
        self.pwd = pwd

    def validate_url(self, url):
        # 一个基本的URL格式验证
        if not re.match(r'^https?://.*', url):
            raise ValueError("Invalid URL")

    def get_cookie(self):
        try:
            self.surl = self.re_surl.search(self.url).group(1)
            if not self.pwd:
                self.pwd = self.re_pwd.search(self.url).group(1)
            print(self.surl, self.pwd)
            params = {"surl": self.surl}
            data = {"pwd": self.pwd}
            session = requests.session()
            headers = {
                "User-Agent": self.ua,
                "Referer": f"https://pan.baidu.com/share/init?surl={self.surl}&pwd={self.pwd}"
            }
            r = session.post(self.verify_url, headers=headers, params=params, data=data)
            if r.status_code == 200:
                json_data = r.json()
                if json_data['errno'] == 0:
                    self.cookies = session.cookies.get_dict()
                    return
                else:
                    logging.error("链接或密码不正确")
            else:
                logging.error("获取cookie接口请求失败")
            exit()
        except Exception as e:
            logging.error(f"链接解析异常: {e}")
            exit()

    def download_image(self, image_url, file_name, download_path):
        headers = {"User-Agent": self.ua}
        r = requests.get(image_url, headers=headers)
        if r.status_code == 200:
            with open(os.path.join(download_path, file_name), "wb") as f:
                f.write(r.content)
            # logging.info(f"{file_name} 下载成功")
        else:
            logging.error("请求图片数据失败")

    def set_nested_value(self, data_dict, path_list, new_value):
        nested_dict = data_dict
        for key in path_list[:-1]:
            nested_dict = nested_dict.setdefault(key, {})
        nested_dict[path_list[-1]] = new_value

    def get_file_list(self, file_list, deep=0):
        for file in file_list:
            file_name = file['server_filename']
            if file['isdir'] == 1:
                print("\t" * deep, file_name)
                list_by_path = self.get_file_list_by_path(file['path'])
                self.get_file_list(list_by_path, deep + 1)
            else:
                print("\t" * deep, "|--", file_name)
                if file['category'] == 3:
                    thumbs = file['thumbs']
                    image_url = thumbs.get("url3") or thumbs.get("url2") or thumbs.get("url1")
                    if image_url:
                        self.download_image(image_url, file_name, "download")
                    else:
                        logging.error(f"{file_name} 无法获取下载URL")


    def get_file_list_by_path(self, path):
        params = {
            "uk": self.share_uk,
            "shareid": self.shareid,
            "order": "other",
            "desc": 1,
            "showempty": 0,
            "web": 1,
            "page": 1,
            "num": 100,
            "dir": path,
        }
        headers = {"User-Agent": self.ua}
        r = requests.get(self.list_url, headers=headers, params=params, cookies=self.cookies)
        if r.status_code == 200:
            json_data = r.json()
            if json_data['errno'] == 0:
                return json_data['list']
            else:
                logging.error(f"目录列表接口无有效数据: {json_data}")
        else:
            logging.error("目录列表接口请求失败")

    def run(self):
        self.validate_url(self.url)
        self.get_cookie()
        headers = {"User-Agent": self.ua}
        r = requests.get(self.url, headers=headers, cookies=self.cookies)
        if r.status_code == 200:
            local_data = re.search('locals.mset\\((.*)\\)', r.content.decode())
            if local_data:
                json_local_data = json.loads(local_data.group(1))
                self.share_uk = json_local_data['share_uk']
                self.shareid = json_local_data['shareid']
                file_list = json_local_data['file_list']
                self.get_file_list(file_list)
            else:
                logging.error("链接无法正常获取local_data数据")
        else:
            logging.error("分享链接请求失败")


if __name__ == '__main__':
    if not os.path.exists("download"):
        os.mkdir("download")
    url = "https://pan.baidu.com/s/1a9-u1yeDbjByv9eE0-Lowg"
    bs = BaiduScript(url, "menv")
    bs.run()
