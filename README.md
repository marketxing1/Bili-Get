# Bili-Get
[![alt text](https://img.shields.io/github/license/xAsiimov/Bili-Get.svg)](https://github.com/xAsiimov/Bili-Get/blob/master/LICENSE)

---

Download Video from Bilibili

Bili-Get is licensed under Apache License 2.0

Runtime Environment: [Python 3](https://www.python.org/downloads/)

---

Here's a basic Python script which could download videos from Bilibili.

Run the script and follow steps(Input Video ID, PID, and Quality ID).

The video will be download with MultiThreads (8 threads as default) (You could change the value of variable 'threadnum' of the function 'dl()' in Bili-Get.py)

---

API is provided by [KanBilibili](https://kanbilibili.com). A brief introduction to that API is listed below.

Get basic information about a specific video:

```
GET https://www.kanbilibili.com/api/video/<Video ID>
```

This will return a JSON Document includes title, number of pages, number of favorites, CID and Quality ID etc. 


Get download link of a specific video:
```
GET https://www.kanbilibili.com/api/video/<Video ID>/download?cid=<CID>
```

This will return a JSON Document includes Video Url, format, size and Quality Information etc.