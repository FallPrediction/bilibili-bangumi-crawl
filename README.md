# bilibili番劇爬蟲
使用scrapy框架的爬蟲，抓取[bilibili](https://www.bilibili.com/)連載中番劇的資料存進MYSQL


## 抓取資料
1. 番劇的ssid
2. 番劇名稱
3. 番劇介紹
4. 最新話數
5. 是否完結
6. 番劇的封面圖面
7. 該番各話彈幕的：
    1. 彈幕出現時間
    2. 彈幕內容
    3. 發送彈幕者的ID
8. 該番抓取時間的：
    1. 評分
    2. 評分人數
    3. 撥放量
    4. 追番
    5. 系列追番


## 注意事項
main.py執行爬蟲  
要記得補上settings.py的PROXIES，代理IP，以免被擋  
settings.py的IMAGES_STORE為番劇封面圖儲存路徑  
使用fake_useragent隨機產生useragent  
