import session
import requests
from login import login
from getpass import getpass
from bs4 import BeautifulSoup
from deleter import minor_delete
import time
from common import pause

print("***로그인***")
#loop until login success
while True:
    user_id = input("사용자 아이디를 입력해주세요　 : ")
    user_pw = getpass("사용자 비밀번호를 입력해주세요 : ")
    print("로그인중... ",end='')
    login_result = login(user_id,user_pw)
    if login_result:
        print("로그인 성공!")
        break
    print("로그인 실패! 다시 입력해주세요")
print("\n***탐색 조건 수집***")
while True:
    gall_id = input("마이너 갤러리의 아이디를 입력해주세요 : ")
    res = session.get("https://gall.dcinside.com/mgallery/board/lists?id="+gall_id)
    bf = BeautifulSoup(res.text,'html.parser')
    gall_name = bf.find('meta',{'name':"title"})
    if gall_name is not None:
        gall_name = gall_name.get('content')
        user_name = input("사용하셨던 닉네임을 입력해주세요 : ")
        decision = input("\n{0}의 {1} 닉네임을 사용한 모든 글을 삭제하시겠습니까?[y/n] ".format(gall_name,user_name)).lower()
        if decision == 'y' or decision == 'yes':
            break
    else:
        print("잘못된 마이너 갤러리 아이디입니다.")


b_box = {'class' : "bottom_paging_box"}
p_first = {'class' : "page_first"}
p_prev = {'class' : "page_prev"}
p_next = {'class' : "page_next"}
p_end = {'class' : "page_end"}
s_prev = {'class' : "search_prev"}
s_next = {'class' : "search_next"}

search_url = "https://gall.dcinside.com/mgallery/board/lists?id=" + gall_id + "&s_type=search_name&s_keyword=" + user_name + "&page=1"
#search_url = "https://gall.dcinside.com/board/lists?id=" + gall_id + "&s_type=search_name&s_keyword=" + name + "&page=1"   #major gallery
article_list = []
loop_cnt = 0
while(True):
    time.sleep(0.1)
    try:
        response = requests.get(search_url)
    except Exception:
        continue
    bfdoc = BeautifulSoup(response.text,'html.parser')
    bottom_box = bfdoc.find('div',{'class' : 'bottom_paging_box'})
    atags = []
    atags.append(0 if bottom_box.find('a',p_first) is None else 1)  #0, page first
    atags.append(0 if bottom_box.find('a',p_prev) is None else 1)   #1, page prev
    atags.append(0 if bottom_box.find('a',p_next) is None else 1)   #2, page next
    atags.append(0 if bottom_box.find('a',p_end) is None else 1)    #3, page end
    atags.append(0 if bottom_box.find('a',s_prev) is None else 1)   #4, search prev
    atags.append(0 if bottom_box.find('a',s_next) is None else 1)   #5, search next
    atags.append(0 if bottom_box.find('em') is None else 1)         #6, page exist
    loop_cnt += 1
    if atags[6] == 0:   #if search result not found, go next
        print("게시물 갯수 : {0}, 루프 횟수 : {1}".format(len(article_list),loop_cnt),end = '\r')
        if atags[5] == 0:   #if last search page, stop loop
            break
        search_url = "https://gall.dcinside.com" + bottom_box.find('a',s_next).get('href')
        continue
    x = bottom_box.find_all('a')
    y = bfdoc.find_all('tr',{'class' : "ub-content us-post"})
    for art in y:
        z = art.find('td',{'class' : "gall_writer ub-writer"})
        if(z.get('data-uid')==user_id):
            article_list.append(art.get('data-no'))
    print("게시물 갯수 : {0}, 루프 횟수 : {1}".format(len(article_list),loop_cnt),end = '\r')
    page_num = len(bottom_box.find_all('a'))
    for i in range(6):
        page_num -= atags[i]
    page_num += 1
    cur_page = int(bottom_box.find('em').get_text())
    if page_num >cur_page%10:  #if current page is not the end of page 
        search_url = search_url.replace("page="+ str(cur_page),"page=" + str(cur_page+1))
    elif atags[2] == 1:     #if other more page exist
        search_url = "https://gall.dcinside.com" + bottom_box.find('a',p_next).get('href')
    elif atags[5] == 1:     #if next search exist
        search_url = "https://gall.dcinside.com" + bottom_box.find('a',s_next).get('href')
    else:   #if last search page, stop loop
        break
print("\n탐색 완료\n")

cur = 0
if len(article_list) == 0:
    print("검색된 글이 없습니다!")
    pause()
    quit()
for article in article_list:
    while True:
        isDeleted = minor_delete(gall_id,article)
        if isDeleted.find('true') != -1:
            cur += 1
            print("글 삭제중... [{0}/{1}]".format(cur,len(article_list)),end='\r')
            break
print("\n삭제 완료!")
pause()