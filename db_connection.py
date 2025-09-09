import oracledb
import os

def get_db_connection():
    """오라클 데이터베이스 연결 객체를 반환합니다."""
    try:
        # 한글 인코딩 문제를 해결하기 위해 시스템 환경변수를 설정합니다.
        os.environ['NLS_LANG'] = 'KOREAN_KOREA.AL32UTF8'
        conn = oracledb.connect(
            user="gogoon1", 
            password="1234", 
            dsn="localhost:1521/orcl"
        )
        print("데이터베이스 연결성공")
        return conn
    except oracledb.DatabaseError as e:
        print("데이터베이스 연결오류: ", e)
        return None