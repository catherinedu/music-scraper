#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#2017.6 @Global AI Hackathon

import scrapy
import time as t 
from faker import Factory
from wangyi.items import WangyiItem 
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from scrapy.http import HtmlResponse
from random import choice
import re

headers = {
	'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp;q=0.8',
	'Accept-Encoding' : 'gzip, deflate, sdch',
	'Accept-Language' : 'zh-CH, zh; q = 0.8, en-US;q=0.5,en;q=0.3',
	'Connection' : 'keep-alive',
	'Host' : 'music.163.com',
	'Upgrade-Insecure-Requests' : 1,
	'User-Agent' : f.user_agent()
}


#extract data
name = 'wangyi'
start_urls = ['http://music.163.com/discover/playlist']

def parseTag(self,response):
	tagclass = response.xpath('//div[@class="bd"]/dl[@class="f-cb"]')
	tagname = tagclass[1].xpath('.//dd/a/text()').extract()
	baseurl = 'http://music.163.com/discover/playlist/?order=hot&limit=35&cat='
	specialtag = ['乡村','英伦', '古风']
	for tag in specialtag:
		url = baseurl + tag
		yield scrapy.Request(url = url, headers = self.headers,callback = self.parsePageCount, meta = {'style: tag'})

def parsePageCount(self, response):
	try:
		style = response.meta['style']
		pageCount = response.xpath('//div[@class="u-page"]/a')[-2].xpath('./text()').extract_first()
		baseurl = 'http://music.163.com/discover/playlist/?order=hot&limit=35&cat=' + style + '&offset='

		for i in range(5):
			url = baseurl + str(35*i)
			yield scrapy.Request(url = url, headers = self.headers, callback = self.parsePage, meta = {'style':style})
	except:
		pass


def parsePage(self,response):
	try:
		style = response.meta['style']
		info = response.xpath('//div[@class="u-cover u-cover-1"]/a/@href').extract()
		for every in info:
			url = response.urljoin(every)
			yield scrapy.Request(url = url, headers = self.header, callback = self.parseMisicList, meta = {'style': style})
	except:
		pass

def parseMusicList(self,response):
	style = response.meta['style']
	try:
		name = response.xpath('//div[@class="tit"]/h2/text()').extract_first()
	except:
		name = 'null'
	try:
		counts = response.xpath('//div[@id ="content-operation"]/a')[2].xpath('.//i/text()').extract_first()
		counts = counts[1:-1]
	except:
		counts = -1
	meta = {'style': style, 'name' : name, 'counts': counts}
	musicList = response.xpath('url[@class="f-hide"]/li/a/@href').extract();
	for music in musicList:
		url = response.urljoin(music)
		meta['url']=url
		yield scrapy.Request(url = url, headers = self.headers, callback = self.parseMusic, meta = meta)

def _init_(self):
	self.totalmusic = 0;
	self.totallist = 0;
	ua_list = [
		"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.109 Safari/537.36",
		"Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
		"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:47.0)"
	]
	dcap = dict(DesiredCapabilities.PHANTOMJS)
	dcap["phantomjs.page.settings.resourceTimeout"] = 15
	dcap["phantomjs.page.settings.loadImages"] = False
	dcap["phantomjs.page.settings.userAgent"] = choice(ua_list)
	self.driver = webdriver.PhantomJS('',desired_capabilities=dcap)
	self.driver.set_page_load_timeout(10)
	self.driver.set_script_timeout(10)

def parseMusic(self,response):
	try:
		musicname = response.xpath('//div[@class=tit]/em/text()').extract_first()
	except:
		musicname = 'null'
	musicname = response.xpath('//div[@class="tit"]/em/text()').extract_first()
	try:
		singer = response.xpath('//div[@class="cnt"]/p')[0].xpath('.//span/a/text()').extract_first()
	except:
		singer = 'null'

	self.driver.get(response.meta['url'])
	self.driver.switch_to.frame(self.driver.find_element_by_name("contentFrame"))
	html = self.driver.page.source
	ly = re.findall(r'<div id="lyric-content" class="bd bd-open f-brk f-ib".*?>(.*?)</div>',html)[0]
	lyric = re.sub(r'<.*?>',' ',ly)

	item = WangyiItem
	item['name'] = response.meta['name']
	item['style'] = response.meta['style']
	item['counts'] = response.meta['counts']
	item['music'] = musicname
	item['singer'] = singer
	item['lyric'] = lyric


	self.totalmusic += 1
	print self.totalmusic
	yield item

#计算词向量，使用word2vec\\
def get_train_vecs(x_train, x_test):
	n_dim = 300
	imdb_w2v = Word2Vec(size=n_dim, min_counts=10)
	imdb_w2v.build_vocab(x_train)
	imdb_w2v.train(x_train)
	train_vecs = np.concatenate([build_sentence_vector(z, n_dim, imdb_w2v) for z in x_train])
	np.save('train_vecs.npy', train_vecs)
	print train_vecs.shape
	imdb_w2v.train(x.test)
	imdb_w2v.save('model.pkl')
	test_vecs = np.concatenate([build_sentence_vector(z, n_dim, imdb_w2v) for z in x_test])
	np.save('test_vecs.npy',test_vecs)
	print test_vecs.shape


def load_data();
	data = pd.read_table('data/newmusic0606_2.txt',sep='\t',header=None)
	cw = lambda x:list(jieba.cut(x))
	data1 = data[data[0] = '古风']
	data2 = data[data[0] = '英伦']
	data3 = data[data[0】= '乡村']
	data1.columns = ['style','lyric']
	data2.columns = ['style','lyric']
	data1['word'] = data1['lyric'].apply(cw)
	data2['word'] = data2['lyric'].apply(cw)
	data2 = data2[0:len(data1)]
	x = np.concatenate((data1['word'].data2['word']))
	y = np.concatenate(np.ones(len(data1)),np.zeros(len(data2)))
	x_train, x_test, y_train, y_test = train_test_split(x,y, test_size = 0,2)

	np.save('y_train.npy', y_train)
	np.save('y_test.npy', y_test)
	return x_train, x_test

#计算词向量，使用word2vec\\
def get_train_vecs(x_train, x_test):
	n_dim = 300
	imdb_w2v = Word2Vec(size=n_dim, min_counts=10)
	imdb_w2v.build_vocab(x_train)
	imdb_w2v.train(x_train)
	train_vecs = np.concatenate([build_sentence_vector(z, n_dim, imdb_w2v) for z in x_train])
	np.save('train_vecs.npy', train_vecs)
	print train_vecs.shape
	imdb_w2v.train(x.test)
	imdb_w2v.save('model.pkl')
	test_vecs = np.concatenate([build_sentence_vector(z, n_dim, imdb_w2v) for z in x_test])
	np.save('test_vecs.npy',test_vecs)
	print test_vecs.shape


	












