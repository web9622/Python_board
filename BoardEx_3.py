import oracledb
import os
from getpass import getpass
import hashlib
import math
from db_connection import get_db_connection

# def get_db_connection():
#     """오라클 데이터베이스 연결 객체를 반환합니다."""
#     try:
#         # 한글 인코딩 문제를 해결하기 위해 시스템 환경변수를 설정합니다.
#         os.environ['NLS_LANG'] = 'KOREAN_KOREA.AL32UTF8'
#         conn = oracledb.connect(
#             user="gogoon1", 
#             password="1234", 
#             dsn="localhost:1521/orcl"
#         )
#         print("데이터베이스 연결성공")
#         return conn
#     except oracledb.DatabaseError as e:
#         print("데이터베이스 연결오류: ", e)
#         return None

class BoardEx:
    def __init__(self):
        self.login_user_id = None
        self.conn = get_db_connection()
        if self.conn is None:
            # 연결에 실패하면 프로그램이 제대로 동작하지 않으므로,
            # 여기에서 적절한 오류 처리를 수행해야 합니다.
            # 이 예제에서는 단순히 None으로 둡니다.
            pass

    def __del__(self):
        if self.conn:
            self.conn.close()
            print("데이터베이스 연결해제")

    def main_menu(self):
        while True:
            print(" ")
            print("==========메인메뉴==========")
            print("-"*100)
            print("1. 글 작성 | 2. 전체 삭제 | 3. 회원 가입 | 4. 로그인 | 5. 게시물 목록 | 6. 게시판 종료 | 7. 조회")
            print("-"*100)
            menu_no = input("메뉴 선택: ")
            print(" ")
            if menu_no == "1":
                self.write_board()
            elif menu_no == "2":
                if self.login_user_id is None:
                    print("로그인해야 게시물을 읽을 수 있습니다.")
                    self.login()
                else:
                    self.delete_all_boards()
            elif menu_no == "3":
                self.join()
            elif menu_no == "4":
                self.login()
            elif menu_no == "5":
                self.paging_list()
            elif menu_no == "6":
                print("게시판을 종료합니다.")
                break
            elif menu_no == "7":
                self.search()
            else:
                print("잘못된 메뉴 번호입니다. 다시 선택해주세요.")

    def join(self):
        print("희망 아이디와 비밀번호 입력")
        user_id = input("아이디: ")
        password = getpass("비밀번호: ")
        username = input("이름: ")
        userage = input("나이: ")
        usermail = input("이메일: ")

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO users (userId, userpassword, username, userage, usermail) VALUES (:userId, :userpassword, :username, :userage, :usermail)", 
                           userId=user_id, userpassword=hashed_password, username=username, userage=userage, usermail=usermail)
            self.conn.commit()
            print(f"{user_id}님, 회원 가입이 완료되었습니다.")
        except oracledb.DatabaseError as e:
            print("회원 가입 오류: ", e)
        finally:
            cursor.close()

    def login(self):
        print("로그인해 주세요.")
        user_id = input("아이디: ")
        password = getpass("비밀번호: ")

        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT userpassword from users WHERE userId=:userId", userId=user_id)
            result = cursor.fetchone()
            if result is None:
                print("존재하지 않는 아이디입니다.")
            else:
                hashed_password = result[0]
                if hashed_password == hashlib.sha256(password.encode()).hexdigest():
                    self.login_user_id = user_id
                    print(f"{user_id}님, 환영합니다!")
                else:
                    print("비밀번호가 틀렸습니다.")
        except oracledb.DatabaseError as e:
            print("로그인 오류: ", e)
        finally:
            cursor.close()

    def logout(self):
        if self.login_user_id:
            print(f"{self.login_user_id}님, 로그아웃되었습니다.")
            self.login_user_id = None
        else:
            print("로그인 상태가 아닙니다.")
    
    def write_board(self):
        if self.login_user_id is None:
            print("로그인해야 글을 작성할 수 있습니다.")
            self.login()
            if self.login_user_id is None:
                return

        title = input("글 제목: ")
        content = input("글 내용: ")

        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO CINEMABOARDS (bno, btitle, bcontent, bwriter) VALUES (seq_bno.NEXTVAL, :btitle, :bcontent, :bwriter)", 
                           btitle=title, bcontent=content, bwriter=self.login_user_id)
            self.conn.commit()
            print("글이 성공적으로 작성되었습니다.")
        except oracledb.DatabaseError as e:
            print("글 작성 오류: ", e)
        finally:
            cursor.close()

    def delete_all_boards(self):
        confirm = input("정말로 모든 게시물을 삭제하시겠습니까? (y/n): ")
        if confirm.lower() != 'y':
            print("삭제가 취소되었습니다.")
            return

        cursor = self.conn.cursor()
        try:
            cursor.execute("DELETE FROM CINEMABOARDS")
            self.conn.commit()
            print("모든 게시물이 성공적으로 삭제되었습니다.")
        except oracledb.DatabaseError as e:
            print("게시물 삭제 오류: ", e)
        finally:
            cursor.close()
    

    # def list_boards(self):
    #     self.paging_list()
    #     self.main_menu()

    def paging_list(self):
        pageSize=5
        totalPosts=0
        totalPages=0
        currentPage=1

        cursor=None # cursor 변수를 미리 선언합니다.
        try:
            cursor=self.conn.cursor()
            count_sql="SELECT COUNT(*) FROM cinemaboards"
            cursor.execute(count_sql)
            count_result=cursor.fetchone()
            if count_result:
                totalPosts=count_result[0]
            if totalPosts==0:
                print("게시물이 없습니다.")
                return
            totalPages=math.ceil(totalPosts/pageSize)

            while True:
                start=(currentPage-1)*pageSize+1
                end=currentPage*pageSize

                print()
                print("[목록]"+"로그인:"+(self.login_user_id if self.login_user_id else "게시물 상세보기는 로그인 필요" ))
                print("-"*100)
                print(f"{'no':<6}{'제목':<34}{'작성자':<10}{'작성일':<16}{'좋아요':<6}{'첨부파일':<20}")
                print("-"*100)

                sql="""
                    SELECT bno, btitle, bwriter, bdate, blike, bfilename
                    FROM(
                        SELECT ROWNUM rn, A.*
                        FROM (
                            SELECT bno, btitle, bwriter, bdate, blike, bfilename
                            FROM CINEMABOARDS
                            ORDER BY bno DESC
                        ) A
                        WHERE ROWNUM <= :end_row
                    )
                    WHERE rn >= :start_row
                """
                cursor.execute(sql, end_row=end, start_row=start )
                results=cursor.fetchall()

                for row in results:
                    # LOB 객체 또는 문자열일 경우를 모두 처리
                    bfilename_obj=row[5]
                    if isinstance(bfilename_obj, oracledb.LOB):
                        bfilename = bfilename_obj.read()
                    elif bfilename_obj is not None:
                        bfilename = bfilename_obj
                    else:
                        bfilename = ""
                    print (f"{row[0]:<6}{row[1]:<30}{row[2]:<16}{row[3].strftime('%Y-%m-%d'):<16}{row[4]:<16}{bfilename:<20}")
                
                # cursor.close() 코드를 이 위치에서 제거합니다.

                print("-" * 100)
                #페이징
                print("[페이지번호]", end="")
                for i in range(1, totalPages+1):
                    print(f"[{' ' if i != currentPage else '*'}{i}{' ' if i != currentPage else '*'}]", end="")
                print()

                print("-" * 100)
                print("[게시물 상세보기:'엔터키'] | [페이지번호:'숫자입력'] | [ 나가기: 'x 입력'] ")
                input_val=input()

                if input_val.lower()=='x':
                    return
                #페이지번호
                elif input_val.isdigit():
                    selected_page=int(input_val)
                    if 1 <= selected_page <= totalPages:
                        currentPage=selected_page
                    else:
                        print("없는 페이지입니다.")
                elif input_val == '':
                    if self.login_user_id is None:
                        print("✎⁾⁾⁾ 로그인이 필요한 페이지입니다.")
                        self.login()
                    else:
                        board_no_input=input("조회할 게시물 번호를 입력하세요: ")
                        if board_no_input.isdigit():
                            self.read(int(board_no_input))
                        else:
                            print("유효한 게시물 번호를 입력해 주세요.")
                else:
                    print(" ")
                    print("[ 잘못된 입력입니다. 아래 형식대로 입력해 주세요. ]")
                    print("1. 게시판 상세보기 : 엔터키를 입력하세요.")
                    print("2. 페이지번호[1][2] : 숫자 입력하세요. ")
                    print("3. 나가기 : x 입력하세요. ")
        
        except oracledb.DatabaseError as e:
            print(f"데이터베이스 오류:{e}")
        finally:
            if cursor:
                cursor.close()


    def read(self, board_no):
        cursor = self.conn.cursor()
        try:
            sql = """
                SELECT bno, btitle, bcontent, bwriter, bdate, blike, bfilename, bfiledata
                FROM CINEMABOARDS
                WHERE bno = :bno
            """
            cursor.execute(sql, bno=board_no)
            board = cursor.fetchone()

            if board:
                bno, btitle, bcontent, bwriter, bdate, blike, bfilename, bfiledata = board
                
                print("-" * 100)
                print("번호:", bno)
                print("제목:", btitle)
                print("내용:", bcontent)
                print("작성자:", bwriter)
                print("날짜:", bdate.strftime('%Y-%m-%d %H:%M:%S'))
                print("좋아요:", blike)
                print("첨부파일:", bfilename if bfilename else "없음")

                if bfilename and bfiledata:
                    try:
                        download_path = os.path.join(os.getcwd(), f"downloaded_{bfilename}")
                        with open(download_path, 'wb') as f:
                            f.write(bfiledata.read())
                        print(f"첨부파일 다운로드 완료: {download_path}")
                    except Exception as e:
                        print(f"파일 다운로드 오류: {e}")

                self.listComments(bno)

                print("-" * 100)
                print("게시글 관리: 1.수정 | 2.삭제 | 3.좋아요 | 4.댓글 | 5.목록 | 6.홈 ")
                menu_no = input("메뉴선택: ")
                
                if menu_no == "1":
                    self.update(bno)
                elif menu_no == "2":
                    self.delete(bno)
                elif menu_no == "3":
                    self.like(bno)
                elif menu_no == "4":
                    self.addComment(bno)
                elif menu_no == "5":
                    self.paging_list()
                elif menu_no == "6":
                    self.main_menu()
            else:
                print("존재하지 않는 게시물 번호입니다.")

        except oracledb.DatabaseError as e:
            print("게시물 조회 오류:", e)
        finally:
            cursor.close()

    def listComments(self, bno):
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT cno, content, userid, cdate FROM COMMENTS WHERE bno=:bno ORDER BY cno", bno=bno)
            comments = cursor.fetchall()
            if not comments:
                print("댓글: 없음")
                return
            print("댓글번호 | 내용 | 작성자 | 작성일")
            print("-" * 100)
            for comment in comments:
                print(f"{comment[0]} | {comment[1]} | {comment[2]} | {comment[3]}")
        except oracledb.DatabaseError as e:
            print("댓글 목록 조회 오류: ", e)
        finally:
            cursor.close()
    
    def like(self, bno):
        print("[댓글 목록]")
        print("-" * 100)
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT * FROM likes WHERE userId= :userId AND bno = :bno", userId=self.login_user_id, bno=bno)
            if cursor.fetchone():
                print("이미 좋아요를 누른 게시물입니다.")
                return
            cursor.execute("INSERT INTO likes(userId, bno, blike) VALUES(:userId, :bno, 1)", userId=self.login_user_id, bno=bno)
            self.conn.commit()
            print("좋아요가 등록되었습니다.")
        except oracledb.DatabaseError as e:
            print("좋아요 오류:", e)
        finally:
            cursor.close()
    
    def addComment(self, bno):
        print("-"*100)
        print("[댓글 작성]")
        if self.login_user_id is None:
            print("로그인해야 댓글을 작성할 수 있습니다.")
            self.login()
            if self.login_user_id is None:
                return
        comment_content = input("댓글 내용: ")
        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO comments(cno, bno, userid, content, cdate) VALUES(seq_cno.NEXTVAL, :bno, :userid, :content, SYSDATE)", 
                           bno=bno, content=comment_content, userid=self.login_user_id)
            self.conn.commit()
            print("댓글이 성공적으로 등록")
        except oracledb.DatabaseError as e:
            print("댓글 작성 오류: ", e)
        finally:
            cursor.close()
        
    def update(self, bno):
        if self.login_user_id is None:
            print("로그인 후 이용해 주세요.")
            return
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT bwriter FROM cinemaboards WHERE bno = :bno", bno=bno)
            result = cursor.fetchone()
            if result is None or result[0] != self.login_user_id:
                print("게시물 수정 권한이 없습니다.")
                return
            new_title = input("새로운 제목: ")
            new_content = input("새로운 내용: ")

            sql = "UPDATE cinemaboards SET btitle = :new_title, bcontent = :new_content, bdate = SYSDATE WHERE bno = :bno"
            cursor.execute(sql, new_title=new_title, new_content=new_content, bno=bno)
            self.conn.commit()
            print("게시물 성공적으로 수정 완료")
        except oracledb.DatabaseError as e:
            print("게시물 수정 오류:", e)
        finally:
            cursor.close()

    def search(self):
        cursor = self.conn.cursor()
        while True:
            print("-" * 100)
            print("1.좋아요 조회 | 2.댓글 조회 | 3.검색어로 조회 | 4.게시물번호로 조회 | 5.나가기")
            print("-------------------------------------------------------------------------------------")

            menu_no = input("[메뉴선택] : ")
            
            if menu_no == "1":
                print("조회 아이디: ", end="")
                user_id = input()
                try:
                    sql = """
                    SELECT u.userId, u.username, c.btitle, c.bcontent, c.blike, c.bdate
                    FROM likes l
                    JOIN users u ON u.userId = l.userId
                    JOIN cinemaboards c ON c.bno = l.bno
                    WHERE u.userId = :userId
                    ORDER BY c.bdate DESC
                    """
                    cursor.execute(sql, userId=user_id)
                    results = cursor.fetchall()
                    
                    print(f"{'ID':<12}{'이름':<10}{'제목':<16}{'게시글':<20}{'좋아요':<8}{'날짜':<20}")
                    print("-" * 100)
                    
                    if results:
                        for row in results:
                            bcontent_lob = row[3]
                            bcontent = bcontent_lob.read() if bcontent_lob else ""
                            if bcontent and len(bcontent) > 20:
                                bcontent = bcontent[:17] + "..."
                            
                            bdate_str = row[5].strftime("%Y-%m-%d %H:%M:%S") if row[5] else ""
                            
                            print(f"{row[0]:<12}{row[1]:<10}{row[2]:<16}{bcontent:<20}{row[4]:<8}{bdate_str:<20}")
                    else:
                        print("::::: 해당 사용자의 좋아요 내역이 없습니다. :::::")
                
                except oracledb.Error as e:
                    print(f":::: 조회 중 오류 발생:{e}::::")

            elif menu_no == "2":
                print("게시물 작성자 아이디: ", end="")
                user_id = input()
                try:
                    sql = """
                    SELECT u.userId AS userId, u.username AS username, c.btitle AS btitle, c.bcontent AS bcontent, cm.content AS content 
                    FROM comments cm
                    JOIN users u ON u.userId = cm.userId
                    JOIN CINEMABOARDS c ON c.bno = cm.bno
                    WHERE u.userId = :userId
                    ORDER BY u.userId DESC
                    """
                    cursor.execute(sql, userId=user_id)
                    results = cursor.fetchall()

                    print(f"{'ID':<10}{'이름':<10}{'제목':<20}{'게시글':<30}{'댓글':<20}")
                    print("-" * 80)
                    
                    if results:
                        for row in results:
                            bcontent_lob = row[3]
                            bcontent = bcontent_lob.read() if bcontent_lob else ""
                            if bcontent and len(bcontent) > 20:
                                bcontent = bcontent[:17] + "..."
                            
                            content = row[4]
                            if content and len(content) > 20:
                                content = content[:17] + "..."
                            
                            print(f"{row[0]:<10}{row[1]:<10}{row[2]:<20}{bcontent:<30}{content:<20}")
                    else:
                        print("::::: 해당 사용자의 내역이 없습니다. :::::")

                except oracledb.Error as e:
                    print(f"::::: 조회 중 오류 발생: {e} :::::")

            elif menu_no == "3":
                print("검색어: ", end="")
                keyword = input()
                try:
                    sql = """
                    SELECT bno, btitle, bcontent, bwriter, bdate FROM CINEMABOARDS
                    WHERE TO_CLOB(bcontent) LIKE :keyword
                    ORDER BY bdate DESC
                    """
                    cursor.execute(sql, keyword=f"%{keyword}%")
                    results = cursor.fetchall()
                    
                    print(f"{'No.':<6}{'제목':<20}{'게시글':<40}{'작성자':<14}{'작성일':<20}")
                    print("-" * 100)

                    if results:
                        for row in results:
                            bcontent_lob = row[2]
                            bcontent = bcontent_lob.read() if bcontent_lob else ""
                            if bcontent and len(bcontent) > 20:
                                bcontent = bcontent[:17] + "..."
                            
                            bdate_str = row[4].strftime("%Y-%m-%d %H:%M:%S") if row[4] else ""
                            
                            print(f"{row[0]:<6}{row[1]:<20}{bcontent:<40}{row[3]:<14}{bdate_str:<20}")
                    else:
                        print("::::: 검색된 게시물이 없습니다. :::::")
                
                except oracledb.Error as e:
                    print(f"::::: 조회 중 오류 발생: {e} :::::")

            elif menu_no == "4":
                print("게시물 번호로 조회")
                print("-" * 100)
                self.paging_list()

            elif menu_no == "5":
                print("메인메뉴")
                break

            else:
                print("1~5번을 입력해 주세요.")
        
        self.conn.close()

if __name__ == "__main__":
    board = BoardEx()
    if board.conn:
        board.main_menu()
