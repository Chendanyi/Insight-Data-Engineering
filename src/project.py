class item:
    def _init_(self):
        self.hostname = ''
        self.timestamp = ''
        self.request = ''
        self.httpcode = 0
        self.byte = 0

        #some condition we need
        self.active = 0 #record how many time we enter this website

        self.timetocount20 = []
        self.timetoblock = []
        self.numberfail = 0
        self.blockstatus = False
        self.startfail = False
        
class timeformat:
    def _init_(self):
        self.year = 0
        self.month = 0
        self.day = 0
        self.hour = 0
        self.minute = 0
        self.second = 0

def inittime(time_str):
    dict_time = {'Jun':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
    t = timeformat()
    t.day = int(time_str[0:2])
    t.month = dict_time[time_str[3:6]]
    t.year = int(time_str[7:11])
    t.hour = int(time_str[12:14])
    t.minute = int(time_str[15:17])
    t.second = int(time_str[18:20])
    return t

def addtime(time_tt, hour, minute, second):
    new_time_tt = timeformat()
    conti_sec = (time_tt.second + second) // 60
    new_time_tt.second = (time_tt.second + second) % 60
    conti_min = (time_tt.minute + minute + conti_sec) // 60
    new_time_tt.minute = (time_tt.minute + minute + conti_sec) % 60
    conti_hour = (time_tt.hour + hour + conti_min) // 24
    new_time_tt.hour = (time_tt.hour + hour + conti_min) % 24
    new_time_tt.day = time_tt.day + conti_hour
    new_time_tt.month = time_tt.month
    new_time_tt.year = time_tt.year
    return new_time_tt
    
def diffsec(time_s, time_e):
    sec = time_e.day*24*60*60 - time_s.day*24*60*60 + time_e.hour*60*60 - time_s.hour*60*60 + time_e.minute*60 - time_s.minute*60 + time_e.second - time_s.second
    return sec
    
def construct_item(line):
    #recode the first place show "--" which will help to find the end of hostname
    Mark_host_e = line.find('- -') - 1

    #record the place show"[" and "-" which will help to find the beginning of the timestamp
    Mark_time_s = line.find('[') + 1
    Mark_time_e = line.find('-',Mark_time_s) 

    #record the place show " " " and second which help to find the request
    Mark_request_s = line.find('"') + 1
    Mark_request_e = line.rfind('"')
    
    #constuct a host info
    hostinfo = item()
    hostinfo.hostname = line[0:Mark_host_e]
    hostinfo.timestamp = line[Mark_time_s:Mark_time_e]
    hostinfo.request = line[Mark_request_s:Mark_request_e]
    hostinfo.httpcode = int(line[Mark_request_e + 2: Mark_request_e + 5])
    byte = line[Mark_request_e + 6: ]
    if byte == "-\n":
        hostinfo.byte = 0
    else:
        hostinfo.byte = int(byte)

    hostinfo.active = 1

    #block information 
    if (hostinfo.httpcode >= 400 & hostinfo.httpcode < 500):
        hostinfo.timetocount20 = inittime(hostinfo.timestamp)
        hostinfo.numberfail = 1
        hostinfo.startfail = True
    else:
        hostinfo.timetocount20 = timeformat()
        hostinfo.numberfail = 0
        hostinfo.startfail = False
    hostinfo.timetoblock = timeformat()
    hostinfo.blockstatus = False
    
    #return this info
    return hostinfo

def feature1(dict):
    activerank = [0 for i in range(10)]
    namerank = ['' for i in range(10)]
    for key in dict.keys():
        for i in range(10):
            if dict[key].active >= activerank[i]: # insert at the place of i
                activerank.insert(i, dict[key].active)
                namerank.insert(i, key)
                activerank.pop()
                namerank.pop()
                break;

    #print out the answer
    hosts = open('hosts.txt', 'w')
    for i in range(10):
        hosts.write(namerank[i]+',')
        hosts.write(str(activerank[i])+'\n')

    hosts.close()

def sourcecount(request, dict_source, byte):
    source_s = request.find(' ') + 1
    if(request.find('HTTP/1.0') != -1):
        source_e = request.rfind(' ')
    else:
        source_e = len(request)
    source = request[source_s:source_e]
    if source in dict_source.keys():
        dict_source[source] += byte
    else:
        dict_source[source] = byte
    return dict_source

def feature2(dict_source):
    bandwrank = [0 for i in range(10)]
    namerank = ['' for i in range(10)]
    for key in dict_source.keys():
        for i in range(10):
            if dict_source[key] >= bandwrank[i]: # insert at the place of i
                bandwrank.insert(i, dict_source[key])
                namerank.insert(i, key)
                bandwrank.pop()
                namerank.pop()
                break;

    #print out the answer
    resources = open('resources.txt','w')
    for i in range(10):
        resources.write(namerank[i] + '\n')
    resources.close()
    
def storetimestamp(timestamp, list):
    time_tt = inittime(timestamp)
    list.append(time_tt)
    return list

def comparetime(busytime, starttime, timerank, namerank):
    for i in range(10):
        if  busytime> timerank[i]: # insert at the place of i
            timerank.insert(i, busytime)
            namerank.insert(i, starttime)
            timerank.pop()
            namerank.pop()
            break;
    return (timerank, namerank)

def feature3(list_time):
    start = 0
    end = 0
    timerank = [0 for i in range(10)]
    namerank = ['' for i in range(10)]
    starttime = list_time[0]
    endtime = addtime(starttime, 1, 0, 0)
    dictmon = {'1':'Jun', '2':'Feb', '3':'Mar', '4':'Apr', '5':'May', '6':'Jun', '7':'Jul', '8':'Aug', '9':'Sep', '10':'Oct', '11':'Nov', '12':'Dec'}
   # print endtime.year, endtime.month, endtime.day, endtime.hour, endtime.minute, endtime.second
    while(end < len(list_time) - 1):
        while(diffsec(list_time[end], endtime) >= 0):
            end += 1
            if (end >= len(list_time)):
                break
        end -= 1
       # print list_time[end].year, list_time[end].month, list_time[end].day, list_time[end].hour, list_time[end].minute, list_time[end].second
        count = end - start + 1
       # print start, end, count
        timerank, namerank = comparetime(count, starttime, timerank, namerank)
        starttime = addtime(starttime,0, 0, 1)
       # print starttime.year, starttime.month, starttime.day, starttime.hour, starttime.minute, starttime.second
        endtime = addtime(starttime, 1, 0, 0)
       # print endtime.year, endtime.month, endtime.day, endtime.hour, endtime.minute, endtime.second
        if(end < (len(list_time) - 1)):
            while(diffsec(list_time[start], starttime) > 0):
                start += 1
       # print list_time[start].year, list_time[start].month, list_time[start].day, list_time[start].hour, list_time[start].minute, list_time[start].second
    hours = open('hours.txt', 'w')
    for i in range(10):
        hours.write(str(namerank[i].day).zfill(2) + '/' + dictmon[str(namerank[i].month)] + '/' + str(namerank[i].year) + ':' + str(namerank[i].hour).zfill(2) + ':' + str(namerank[i].minute).zfill(2) + ':' + str(namerank[i].second).zfill(2) + ' -0400,' + str(timerank[i]) + '\n')
        
    hours.close()
    
def feature4(dict, host, blocked):

    # 400 represent the failure of login
    # first check is there a block for that host before
    if(dict[host.hostname].blockstatus == True):
    # if yes, check the block the time reach 5 minute or not
        if(diffsec(dict[host.hostname].timetoblock, inittime(host.timestamp)) <= 300):
            # print "enter here1"
            blocked.write(host.hostname + ' - - [' + host.timestamp + ' -0400] "' + host.request + '" ' + str(host.httpcode) + ' ' + str(host.byte) + '\n')
        else:
            dict[host.hostname].blockstatus = False
            if (str(host.httpcode)[0] == '4'):
                dict[host.hostname].timetocount20 = inittime(host.timestamp)
                dict[host.hostname].numberfail = 1
                dict[host.hostname].startfail = True
            else:
                dict[host.hostname].timetocount20 = timeformat()
                dict[host.hostname].numberfail = 0
                dict[host.hostname].startfail = False
    # if no
    else:
        # check is this a fail login
        # if yes, then check is it the first time to fail
        if (str(host.httpcode)[0] == '4'):
            # if yes, mark to the time to timetocount20, increment of numberfail
            if (dict[host.hostname].numberfail == 0):
                #print "enter here3"
                dict[host.hostname].timetocount20 = inittime(host.timestamp)
                dict[host.hostname].numberfail = 1
            # if no, check the number of time to fail
            else:
                # if is not 3rd time, then just increase the number of time to fail
                if(dict[host.hostname].numberfail == 2):
                    # if yes, check the time is reach 20 second of not, if yes, start over 
                    if(diffsec(dict[host.hostname].timetocount20,inittime(host.timestamp)) >= 20):
                        #print "enter here4"
                        dict[host.hostname].timetocount20 = inittime(host.timestamp)
                        dict[host.hostname].numberfail = 1
                        dict[host.hostname].startfail = True
                    # not reach 20 second, then, bock the info
                    else:
                        #print "enter here5"
                        dict[host.hostname].blockstatus = True
                        dict[host.hostname].timetoblock = inittime(host.timestamp)
                        dict[host.hostname].numberfail = 0
                        dict[host.hostname].startfail = False
                else:
                    #print "enter here6"
                    dict[host.hostname].numberfail += 1
        # if no, start over
        else:
            #print "enter here7"
            dict[host.hostname].timetocount20 = timeformat()
            dict[host.hostname].numberfail = 0
            dict[host.hostname].startfail = False
            dict[host.hostname].blockstatus = False

    return dict,blocked
    
# open a txt.file and read by row       
file = open("log.txt", mode="r", encoding="latin-1")
#print(file)
dict = {}
dict_source = {}
list_time = []
i = 0
blocked = open('blocked.txt', 'w')
#while 1:
#    line = file.readline()
#    if not line:
#        break
for line in file:
    i += 1
    test = construct_item(line)
    dict_source = sourcecount(test.request, dict_source, test.byte)
    list_time = storetimestamp(test.timestamp, list_time)
   # if test.hostname in dict.keys():
    if(dict.get(test.hostname) is not None):
        (dict,blocked) = feature4(dict, test, blocked)
        dict[test.hostname].active += 1
    else:
        dict[test.hostname] = test
#print "begin feature3"
feature1(dict)
feature2(dict_source)
feature3(list_time)
del dict
del dict_source
del list_time
file.close()
blocked.close()
#0.17kaishi - 
