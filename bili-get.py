import os
import re
import sys
import json
import time
import threading
from urllib import request

class ShowProcess():

    i = 0 
    max_steps = 0 
    max_arrow = 50 
    infoDone = 'done'

    
    def __init__(self, max_steps, infoDone = ''):
        self.max_steps = max_steps
        self.i = 0
        self.infoDone = infoDone


    def show_process(self, i=None):
        if i is not None:
            self.i = i
        else:
            self.i += 1
        num_arrow = int(self.i * self.max_arrow / self.max_steps) 
        num_line = self.max_arrow - num_arrow
        percent = self.i * 100.0 / self.max_steps 
        process_bar = '[' + '>' * num_arrow + '-' * num_line + ']'\
                      + '%.2f' % percent + '%' + '\r' 
        sys.stdout.write(process_bar)
        sys.stdout.flush()
        if self.i >= self.max_steps:
            self.close()

    def close(self):
        print('')
        self.i = 0
        
class MulThreadDownload(threading.Thread):
    def __init__(self,url,startpos,endpos,f,total_size):
        super(MulThreadDownload,self).__init__()
        self.url = url
        self.startpos = startpos
        self.endpos = endpos
        self.fd = f
        self.total_size=total_size
    def download(self):
        #Size of File being downloaded into Memory
        global mem_size
        mem_size=0
        req = request.Request(self.url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.92 Safari/537.36')
        #Range File Size
        req.add_header('Range', 'bytes=%s-%s'%(self.startpos,self.endpos))
        response=request.urlopen(req)
        length=0
        chunk_size=256*1024
        res=bytes()
        while True:
            tmp = response.read(chunk_size)
            if not tmp:
                break
            res=res+tmp
            length=length+len(tmp)
            mem_size=mem_size+len(tmp)
            #Show process bar
            per=mem_size / self.total_size *100
            process_bar = ShowProcess(100,'')
            process_bar.show_process(round(per,1)) 
        #Write data into File
        self.fd.seek(self.startpos)
        self.fd.write(res)
        response.close()
    def run(self):
        self.download()
        
def dl(durl):

    req = request.Request(durl)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.92 Safari/537.36')
    response=request.urlopen(req)
    
    #Get File Size and Type from header
    total_size=int(response.headers['content-length'])
    format=response.headers['Content-Type']
    if format=='video/mp4':
        local=re.findall('/([^/]*.mp4)',durl)
    else:
        local=re.findall('/([^/]*.flv)',durl)
    local=local[0]
    
    #Set tasks for each thread
    threadnum = 8
    threading.BoundedSemaphore(threadnum)
    step = total_size // threadnum
    mtd_list = list()
    start = 0
    end = -1
    #Create Local File
    tempf = open(local,'w')
    tempf.close()
    print('Using',threadnum,'Threads to Download:',local)
    #Start Thread
    with open(local,'rb+') as  f:
        fileno = f.fileno()
        while end < total_size -1:
            start = end +1
            end = start + step -1
            if end > total_size:
                end = total_size
            dup = os.dup(fileno)
            fd = os.fdopen(dup,'rb+',-1)
            t = MulThreadDownload(durl,start,end,fd,total_size)
            t.start()
            mtd_list.append(t)
        #Close Thread
        for i in  mtd_list:
            i.join()
        f.close()

    print('Download Complete: '+local)

url=input('Print video url or aid: ')
if url=='':
    url='https://www.bilibili.com/video/av2663796'
aid=re.findall('.*av([0-9]+)',url)
aid=aid[0]
url='https://www.kanbilibili.com/api/video/' + aid

req = request.Request(url)
req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.92 Safari/537.36')
f=request.urlopen(req)
info=f.read().decode()
info=json.loads(info)

#Get basic info from API
if info['err']==None:
    data=info['data']
    title=data['title']
    typename=data['typename']
    favorites=data['favorites']
    play=data['play']
    video_review=data['video_review']
    review=data['review']
    description=data['description']
    author=data['author']
    created_at=data['created_at']
    coins=data['coins']
    pages=data['pages']
    print('-------------Video Info-------------')
    print('Title:',title,'\nDate:',created_at,'\nAuthor:',author,'\nType:',typename,'\nPage:',pages,'\nPlay:',play,'\nFavorite:',favorites,'\nCoin:',coins,'\nDanmaku:',video_review)
    print('-----------------------------------')
    
    #Parse Page List
    pid=input('Print video pid: ')
    if pid=='':
        pid='1'
    pid=int(pid)-1
    ls=data['list'][pid]
    name=ls['part']
    if name=='':
        name=title
    print('Select Part: ',name)
    
    #Get CID from API
    cid=ls['cid']
    url=url + '/download?cid=' + str(cid)
    req = request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.92 Safari/537.36')
    f=request.urlopen(req)
    dlinfo=f.read().decode()
    
    #Get Quality Info from API
    dlinfo=json.loads(dlinfo)
    data=dlinfo['data']
    af=data['accept_format']
    af=af.split(',')
    aq=data['accept_quality']
    ad=data['accept_description']
    print('-------------Quality Info-------------')
    for i in range(len(aq)):
        r=re.findall('[0-9]+P',ad[i])
        print('Quality:',r[0],'ID:',aq[i])
    print('------------------------------------')
    q=input('Print Quality ID: ')
    if q=='' or int(q) not in aq:
        q='48'
        
    #Get Download Link from API
    url=url+'&quality='+q
    req = request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.92 Safari/537.36')
    f=request.urlopen(req)
    dlinfo=f.read().decode()
    dlinfo=json.loads(dlinfo)
    data=dlinfo['data']['durl']
    
    print('-------------Download Info-------------')
    durl_list=list()
    for pinfo in data:
        size=pinfo['size']
        durl=pinfo['url']
        durl_list.append(durl)
        print('Video Size:',round(size/1000000,2),'MB')
        print('Url:',durl)
        
    print('------------------------------------')
    
    if len(durl_list)!=1:
        print('This video has',len(durl_list),'parts')
    
    start=' '
    while start != '':
        start=input('Press Enter to download: ')

    for durl in durl_list:
        dl(durl)
        
else:
    code=info['err']['code']
    message=info['err']['message']
    print(message)