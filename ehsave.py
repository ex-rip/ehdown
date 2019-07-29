# -*- coding: cp936 -*-

import sys

if __name__ == "__main__":
	if len(sys.argv) == 1:
		print("使用方法：python3 ehsave.py 链接\n链接例如 https://e-hentai.org/g/1405639/0c0418348f/\n且末尾必须有'/'\n另，使用需安装requests\n方法：在cmd中执行pip3 install requests\n且仅支持python3")
		sys.exit(0)

import re
import requests
import sys
import os

header = {
	'authority': 'e-hentai.org',
	'cache-control': 'max-age=0',
	'upgrade-insecure-requests': '1',
	'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
	'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
	'accept-encoding': 'gzip, deflate, br',
	'accept-language': 'zh-CN,zh;q=0.9',
	"cookie": cookie
}

title = ""

def request(url):
	print("下载：" + url)
	return requests.get(url, headers=header)

def down(url, id, refer):
	url = url.replace("&amp;", "&")
	print("下载第" + id + "张图片")
	res = requests.get(url, headers={
		'authority': 'e-hentai.org',
		'cache-control': 'max-age=0',
		'upgrade-insecure-requests': '1',
		'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
		'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
		'referer': refer,
		'accept-encoding': 'gzip, deflate, br',
		'accept-language': 'zh-CN,zh;q=0.9',
		'cookie': cookie,
	}, stream=True)
	chunksize = 1024
	length = int(res.headers['content-length'])
	downloaded = 0
	result = b""
	for data in res.iter_content(chunk_size = chunksize):
		result += data
		downloaded += len(data)
		print("{:.2f}% {} / {}          ".format(100 * downloaded / length, downloaded, length), end='\r')
	f = open(title + id + ".jpg", "wb")
	f.write(result)
	f.close()

def downpage(html):
	pat = r'<a href="(https:\/\/e-hentai\.org\/s\/[0-9a-f]+\/[0-9]+-[0-9]+)">'
	match = re.search(pat, html)
	while match:
		html = html[match.span()[1]:]
		result = match.group(1)
		id = result[result.find("-", len(result) - 4) + 1:]
		if os.path.exists(title + id + ".jpg"):
			print(id + ".jpg already exists, skip!")
		else:
			ht = request(result).text
			mat = re.search(r'<a href="(https:\/\/e-hentai\.org\/fullimg.php\?.+)">Download', ht)
			if mat:
				down(mat.group(1), id, result)
			else:
				down(re.search(r'<img id="img" src="(.*)" style', ht).group(1), id, result)
		match = re.search(pat, html)

if __name__ == "__main__":
	root = sys.argv[1]
	res = request(root)
	if False:
		f = open("index.html", "wb")
		f.write(res.content)
		f.close()
		sys.exit(0)
	html = res.text
	if html.find('Content Warning') != -1:
		res = request(root + "?nw=always")
		if False:
			f = open("index.html", "wb")
			f.write(res.content)
			f.close()
			sys.exit(0)
		html = res.text
	match = re.search(r'<p class="gpc">Showing 1 - ([0-9]+) of ([0-9]+) images</p>', html)
	perpage = int(match.group(1))
	pagecount = int(match.group(2))
	npage = 0
	if pagecount % perpage == 0:
		npage = pagecount // perpage
	else:
		npage = pagecount // perpage + 1
	match = re.search(r'<h1 id="gj">(.+?)</h1>', html)
	if not match:
		match = re.search(r'<h1 id="gn">(.+?)</h1>', html)
	title = match.group(1)
	print("书名：" + title + "\n页数：" + str(pagecount))
	if os.path.exists(title):
		print("警告：目录" + title + "已存在！")
	else:
		os.mkdir(title)
	title = title + os.sep
	downpage(html)
	for i in range(1, npage):
		downpage(request(root + "?p=" + str(i)).text)