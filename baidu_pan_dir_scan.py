import json
import re
import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
    "Cookie": """XFI=807995ae-5385-6fad-485c-6d373c2e644f; XFCS=EEF84FA970B2409AF7D12CA752EFC99CAA1F88C83BC86ECA708EA82C66E3475F; XFT=BjEf8++13lOLQsptMLmXxv72hQkvgq7/kvUR9cfII7I=; BAIDUID_BFESS=7E70EA03F684611CB7A1C3F6F639134F:FG=1; __bid_n=18c5b7afee05072bf996d0; BIDUPSID=7E70EA03F684611CB7A1C3F6F639134F; PSTM=1702879669; BAIDU_WISE_UID=wapp_1703728970751_523; BDUSS=jYwbENndmN1YkhQY3dqV04yT2w5WkhWMEc2RVEtc0RjMn4xYUtlMUo4LXNFUEZsSVFBQUFBJCQAAAAAAQAAAAEAAACIbRhAd2VueGluMTExNDQ0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKyDyWWsg8llS; BDUSS_BFESS=jYwbENndmN1YkhQY3dqV04yT2w5WkhWMEc2RVEtc0RjMn4xYUtlMUo4LXNFUEZsSVFBQUFBJCQAAAAAAQAAAAEAAACIbRhAd2VueGluMTExNDQ0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKyDyWWsg8llS; PANWEB=1; STOKEN=2635bb493efc8a619be01da72ef1e3d1ab39e7bf4c5c788f5d8dc6c265909a4e; Hm_lvt_fa0277816200010a74ab7d2895df481b=1711456093; ZFY=ueWX9sB9z4N0wl3zgh3HhtdEb2WTyslXch9uul9jGmU:C; H_PS_PSSID=40373_40369_40416_40304_40499_40511_40446_40080_60142; MCITY=-349%3A; arialoadData=false; RT="z=1&dm=baidu.com&si=aa32a36f-8739-44a4-b428-f7fe145f53e1&ss=lvekj5t2&sl=3&tt=4rn&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf&ld=3yfo&ul=q8up&hd=q8ve"; csrfToken=DEZn_EpzXGzty_WJu7kKH5vC; Hm_lvt_7a3960b6f067eb0085b7f96ff5e660b0=1713158088,1713323795,1713966018,1714013045; BDCLND=esvsAxVxQfOptORlxMN2v8erZ88URIzYTimo88eFgI0%3D; Hm_lpvt_7a3960b6f067eb0085b7f96ff5e660b0=1714013085; PANPSC=13370188859818997264%3AKkwrx6t0uHCdGJyYdAmKkqR2i86mCVGDjQDHhR1urkBy%2FWBHfWel%2FM%2FNbbUaC9LQ0zX9%2ByKuQoNc38lvrwFQSLLJ7OgLwP14IeyF%2FPchmo8TWYDOj44sDlKXmJxobaxp0eEnlpk%2Bm2jAXGDKrHzGknePlzJEAU4tsxlXBl73BMSG0UMXpe3R%2BoxWP4%2FywVFo; ndut_fmt=20DBC243E2B41FA4CF396D208F9CA4D7C55BCBB17B3530EFE97AAA0FAA342F80; ab_sr=1.0.1_YThkMDg3YzcxMjlmMzIwYWE3ZTk5NzFkMGFhZTRlMDU4NjAxYWUxZWRlMzhhMmQ5MmJjZmIzY2QwODBmZjY4Mjg3ZDcwNmYxZWI5M2VkNDBkNzNlZmJiNzQ3NDFiZjExNGRlNTNlYzRjMmQyZjA0YTdjY2FmZGJlODNlYmRlMTQ4MmEyZGQ3OGJmMGExM2E3OGEwYzJiYzQxMmNiZmFkMjQzMDc4MmY2YzkzZGM4ZjE1OGQxYjdhZWJmOTc2YTg1"""
}

def get_file_list(uk, shareid, file_list, deep = 0):
    for file in file_list:
        file_name = file['server_filename']
        # 判断是否为文件夹
        if file['isdir'] == 1:
            print("\t" * deep, file_name)
            list = get_file_list_by_path(uk, shareid, file['path'])
            get_file_list(uk, shareid, list, deep + 1)
        else:
            print("\t" * deep, "|--", file_name)


def get_file_list_by_path(uk, shareid, dir):
    url = "https://pan.baidu.com/share/list"
    params = {
        "uk": uk,
        "shareid": shareid,
        "order": "other",
        "desc": 1,
        "showempty": 0,
        "web": 1,
        "page": 1,
        "num": 100,
        "dir": dir,
    }
    r = requests.get(url, headers=headers, params=params)
    return r.json().get('list')


def run(url, pwd=None):
    params = {"pwd": pwd}
    if pwd:
        r = requests.get(url, headers=headers, params=params)
    else:
        r = requests.get(url, headers=headers)
    local_data = re.search('locals.mset\\((.*)\\)', r.content.decode())
    if local_data:
        json_local_data = json.loads(local_data.group(1))
        share_uk = json_local_data['share_uk']
        shareid = json_local_data['shareid']
        file_list = json_local_data['file_list']
        get_file_list(share_uk, shareid, file_list)


url = "https://pan.baidu.com/s/19BB6krTVM33VYWeI1E-SRA?pwd=d7qs"
pwd = "d7qs"
run(url)



