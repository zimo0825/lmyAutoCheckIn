import smtplib
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import requests
import threading
import hashlib
import hmac
import datetime
import time
import sys

md5 = "9579D1CB25BADE7F8A3EB479DD0A2AC3";

# 位置信息  可以自行添加经纬度信息   默认使用empty,教师端显示未获取位置
location = {"input": {"lat": "", "lng": ""}}


# 登录蓝墨云
def login(name, pwd):
    try:
        loginUrl = "http://api.mosoteach.cn/mssvc/index.php/passport/login"
        headers = {"Accept-Encoding": "gzip;q=0.7,*;q=0.7",
                   "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 7.1.1; MX6 Build/NMF26O)",
                   "Accept-Encoding": "gzip, deflate, br", "Date": "", "X-mssvc-signature": "",
                   "X-app-id": "MTANDROID", "X-app-version": "3.1.2",
                   "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
        loginFormdata = {"account_name": "", "app_id": "MTANDROID", "app_version_name": "3.1.2",
                         "app_version_number": "76", "device_code": "39285fe4_d165_46d6_a716_d017dd1ad4a4",
                         "device_pn_code": "39285fe4_d165_46d6_a716_d017dd1ad4a4", "device_type": "ANDROID",
                         "dpr": "3.0",
                         "public_key": "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCmQVJFfoyV3ewxIjlCambLMFfJLlToOhoSV31qVieZYwz6kI3JywW2OEORSqZn9w1UkSkCMRjI5szT1fKe8XA93M8ZjKsnRrFt4U7VRyWpBYrVKiLuY7mukU7wumoEgi6ILTT1BECAbBQFF21vnpJnkfPwzKiAV825FnzRCINanQIDAQAB",
                         "system_version": "7.1.1", "user_pwd": ""}
        loginFormdata["account_name"] = name
        loginFormdata["user_pwd"] = pwd
        headers["Date"] = getDate()
        headers["X-mssvc-signature"] = getLoginSignature(loginUrl, getDate(), loginFormdata)
        r = requests.post(loginUrl, headers=headers, data=loginFormdata);
        return r.json()
    except:
        print("login wrong!")
        return None


# 获得所有已经加入的班级信息
def getAllClazzInfo(userInfo):
    try:
        getAllClazzUrl = "http://api.mosoteach.cn/mssvc/index.php/clazzcourse/my_cc"
        headers = {"Accept-Encoding": "gzip;q=0.7,*;q=0.7",
                   "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 7.1.1; MX6 Build/NMF26O)",
                   "Date": "", "X-device-code": "8faffe60_ebd5_4890_a532_c68523f6daae", "X-mssvc-signature": "",
                   "X-mssvc-access-id": userInfo['access_id'], "X-app-id": "MTANDROID", "X-app-version": "3.1.2",
                   "X-mssvc-sec-ts": userInfo['last_sec_update_ts_s'],
                   "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
        getAllClazzFormdata = {"dpr": "2"}
        headers["Date"] = getDate()
        headers["X-mssvc-signature"] = getSignature(getAllClazzUrl, userInfo['user_id'], getDate(),
                                                    userInfo['access_secret'], getAllClazzFormdata)
        r = requests.post(getAllClazzUrl, headers=headers, data=getAllClazzFormdata);
        return r.json()
    except:
        print("getAllClazzInfo wrong!")
        return None

# 发送检测签到是否开启的请求
def checkIsOpen(userInfo, clazzId):
    try:
        checkOpenUrl = "http://api.mosoteach.cn/mssvc/index.php/checkin/current_open"
        headers = {"Accept-Encoding": "gzip;q=0.7,*;q=0.7",
                   "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 7.1.1; MX6 Build/NMF26O)",
                   "Date": "", "X-device-code": "39285fe4_d165_46d6_a716_d017dd1ad4a4", "X-mssvc-signature": "",
                   "X-mssvc-access-id": userInfo['access_id'], "X-app-id": "MTANDROID", "X-app-version": "3.1.2",
                   "X-mssvc-sec-ts": userInfo['last_sec_update_ts_s'],
                   "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
        checkOpenFormdata = {"clazz_course_id": clazzId}
        headers["Date"] = getDate()
        headers["X-mssvc-signature"] = getSignature(checkOpenUrl, userInfo['user_id'], getDate(),
                                                    userInfo['access_secret'], checkOpenFormdata)
        r = requests.post(checkOpenUrl, headers=headers, data=checkOpenFormdata);
        return r.json()
    except:
        print("checkIsOpen wrong!")
        return None


# 发送签到请求
def checkIn(userInfo, checkId, location):
    global check_late
    check_lates = check_late
    while check_lates >= 0:
        print("延迟 " + str(check_lates) + " 秒后签到。", end='\r')
        check_lates = check_lates - 1
        time.sleep(1)
        if check_lates < 0:
            print("")
            break
    try:
        checkInUrl = "http://checkin.mosoteach.cn:19527/checkin"
        headers = {"Accept-Encoding": "gzip;q=0.7,*;q=0.7",
                   "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 7.1.1; MX6 Build/NMF26O)",
                   "Date": "", "X-device-code": "39285fe4_d165_46d6_a716_d017dd1ad4a4", "X-mssvc-signature": "",
                   "X-mssvc-access-id": userInfo['access_id'], "X-app-id": "MTANDROID", "X-app-version": "3.1.2",
                   "X-mssvc-sec-ts": userInfo['last_sec_update_ts_s'],
                   "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
        checkOpenFormdata = {"checkin_id": checkId, "report_pos_flag": "Y", "lat": location['lat'],
                             "lng": location['lng']}
        headers["Date"] = getDate()
        headers["X-mssvc-signature"] = getSignature(checkInUrl, userInfo['user_id'], getDate(),
                                                    userInfo['access_secret'], None)
        r = requests.post(checkInUrl, headers=headers, data=checkOpenFormdata);
        return r.json()
    except:
        print("checkIn wrong!")
        return None


# 获得格式化后的日期字符串
def getDate():
    times = datetime.datetime.now() + datetime.timedelta(hours=-8)
    formatDate = times.strftime("%a, %d %b %Y-%m-%d %H:%M:%S GMT+00:00")
    return formatDate


def getMD5(data):
    md5 = hashlib.md5()
    md5.update(data.encode('utf-8'))
    return md5.hexdigest()


def getMacSHA1(data1, data2):
    hmacSha1 = hmac.new(data1.encode('utf-8'), data2.encode('utf-8'), hashlib.sha1)
    return hmacSha1.hexdigest()


def getLoginSignature(url, gmtTime, formdata):
    global md5
    str1 = "%s|%s" % (url, gmtTime)
    for name in formdata:
        str1 = str1 + "|%s=%s" % (name, formdata[name])
    return getMacSHA1(md5, str1)


def getSignature(url, user_id, gmtTime, access_secret, formdata):
    if formdata == None or len(formdata) == 0:
        str1 = "%s|%s|%s" % (url, user_id, gmtTime)
        return getMacSHA1(access_secret, str1)
    else:
        str1 = ""
        for name in formdata:
            str1 = str1 + "%s=%s|" % (name, formdata[name])
        str1 = str1[0:len(str1) - 1]
        str1 = "%s|%s|%s|%s" % (url, user_id.upper(), gmtTime, getMD5(str1).upper())
        return getMacSHA1(access_secret, str1)


# 开始签到程序
def startAtuoCheckIn(name, pwd, check_late, safe_time, input_location):
    dt = datetime.datetime.now()
    day = dt.weekday()

    # 在此处选择签到位置
    classRom = "input"

    loginInfo = login(name, pwd)
    if loginInfo == None:
        print("登陆失败")
    elif loginInfo['result_code'] == 1007:
        print("用户名或密码错误！")
    else:
        userInfo = loginInfo['user']
        print(userInfo['full_name'] + " 登陆成功!")
        print("设定的签到延迟为 " + str(check_late) + " 秒。")
        print("设定的安全间隔为 " + str(safe_time) + " 秒。")
        if input_location['lat'] == "":
            print("不设定经纬度")
        else:
            print("设定的经纬度为东经：" + str(input_location['lat']) + "，北纬：" + str(input_location['lng']) + " 。")
        print("")
        clazzInfo = getAllClazzInfo(userInfo)['data']
        clazzList = list()
        for clazz in clazzInfo:
            clazzList.append({'clazz_id': clazz['id'], 'clazz_name': clazz['course_name'], 'flag': 0})
        count = 0
        while (True):
            if count > 5:
                count = 0;
                print('正在检测签到           ', end='\r')
            for clazz in clazzList:
                if clazz['flag'] > 0:
                    clazz['flag'] -= 1;
                msg = checkIsOpen(userInfo, clazz['clazz_id'])
                print('正在检测签到' + "." * count, end='\r')
                if msg != None and msg['result_msg'] == "OK" and clazz['flag'] == 0:
                    print("正在签到 " + clazz['clazz_name'])
                    checkInMsg = checkIn(userInfo, msg['id'], location[classRom])
                    if checkInMsg != None and checkInMsg['result_code'] == 2409:
                        print(datetime.datetime.today().strftime("%Y/%m/%d %H:%M:%S") + " " + clazz[
                            'clazz_name'] + " 重复签到!")
                        clazz['flag'] = 10;
                        safe_times = safe_time
                        while safe_times >= 0:
                            print("防止蓝墨云侦测异常重复签到，请等待安全倒计时 " + str(safe_times) + " 秒。", end='\r')
                            safe_times = safe_times - 1
                            time.sleep(1)
                            if safe_times < 0:
                                print("")
                                break
                    elif checkInMsg != None and checkInMsg['result_msg'] == 'OK':
                        clazz['flag'] = 10;
                        print(datetime.datetime.today().strftime("%Y/%m/%d %H:%M:%S") + " " + clazz[
                            'clazz_name'] + " 签到成功!")
                        # 签到成功发送邮件
                        my_sender = my_sender  # 发件人邮箱账号
                        my_pass = my_pass("qq邮箱授权码：")  # 发件人邮箱密码
                        my_user = my_user("收件人邮箱：")  # 收件人邮箱账号，我这边发送给自己

                        def mail():
                            ret = True
                            try:
                                msg = MIMEText('蓝墨云班课签到成功', 'plain', 'utf-8')
                                msg['From'] = formataddr(["zimo", my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
                                msg['To'] = formataddr(["FK", my_user])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
                                msg['Subject'] = "蓝墨云签到程序"  # 邮件的主题，也可以说是标题

                                server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是25
                                server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
                                server.sendmail(my_sender, [my_user, ], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
                                server.quit()  # 关闭连接
                            except Exception:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
                                ret = False
                            return ret

                        ret = mail()
                        if ret:
                            print("邮件发送成功")
                        else:
                            print("邮件发送失败")
            time.sleep(1)
            count = count + 1;


name = input("账号：")
pwd = input("密码：")
my_sender =input("输入qq邮箱账号：")  # 发件人邮箱账号
my_pass = input("qq邮箱授权码：")  # 发件人邮箱密码
my_user = input("收件人邮箱：")

print("")

check_late = input("签到延迟（秒）：")
if check_late == "":
    check_late = 1
    print("数值为空，则使用默认数值：1 秒")
check_late = int(check_late)

print("")

safe_time = input("重复签到安全间隔（秒）：")
if safe_time == "":
    safe_time = 300
    print("数值为空，则使用默认数值：300 秒")
safe_time = int(safe_time)

print("")

input_lat = input("经度：")
if input_lat == "":
    input_lng = ""
    print("不设置经纬度")
else:
    input_lng = input("维度：")
print("")

input_location = {}
input_location['lat'] = input_lat
input_location['lng'] = input_lng
location['input'] = input_location

startAtuoCheckIn(name, pwd, check_late, safe_time, input_location)
