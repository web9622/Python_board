--게시판 사용하는 user정보
CREATE TABLE USERS(
	userId varchar2(50) PRIMARY KEY,
	username varchar2(50) NOT NULL,
	userpassword varchar2(60) NOT NULL,
	userage number NOT NULL,
	usermail varchar2(50) NOT NULL
);
SELECT * FROM USERS;
DROP TABLE USERS;

-- cno컬럼추가
ALTER TABLE USERS ADD cno NUMBER;
-- cno foreigin key  
ALTER TABLE USERS
ADD CONSTRAINT fk_users_cno
FOREIGN KEY (cno)
REFERENCES comments(cno);
-- cno foreigin key 취소 
ALTER TABLE USERS DROP CONSTRAINT fk_users_cno;
-- cno컬럼삭제
ALTER TABLE USERS DROP COLUMN cno;

-- bno컬럼추가
ALTER TABLE USERS ADD bno NUMBER;
-- bno foreigin key  
ALTER TABLE USERS
ADD CONSTRAINT fk_users_bno
FOREIGN KEY (bno)
REFERENCES cinemaboards(bno);

ALTER TABLE users MODIFY userage NUMBER NULL;
ALTER TABLE users MODIFY userpassword varchar2(64);
SELECT * FROM users;


-- USERS테이블 INSERT INTO
INSERT INTO users(userId,username,userpassword,userage,usermail,cno) 
VALUES('red','정렬이',1234,11,'red@gmail.com',1); 
DELETE FROM users WHERE userId='red';


--시네마게시판
CREATE TABLE CINEMABOARDS(
	bno number PRIMARY KEY,
	btitle varchar2(100) NOT NULL,
	bcontent clob NOT NULL, --게시판내용
	bwriter varchar2(50) NOT NULL,
	bdate date DEFAULT sysdate,
	blike NUMBER DEFAULT 0,
	bfilename varchar2(50) NULL,--게시판 첨부파일 이름
	bfiledata blob NULL --게시판 첨부파일 실제데이터
);
-- bwriter컬럼명을 userId로 변경
ALTER TABLE cinemaboards RENAME COLUMN userId TO bwriter;
-- userId foreigin key  
ALTER TABLE cinemaboards
ADD CONSTRAINT fk_users_userId
FOREIGN KEY (userId)
REFERENCES users(userId);

--ALTER TABLE cinemaboards MODIFY blike NUMBER DEFAULT 0;
-- UPDATE cinemaboards SET blike = 0 WHERE blike IS NULL;
DROP TABLE CINEMABOARDS;
SELECT * FROM CINEMABOARDS;

INSERT INTO CINEMABOARDS(bno,btitle,bcontent,bwriter,bdate,blike) 
VALUES(seq_bno.NEXTVAL,'타이틀','컨텐츠','작성자',SYSDATE,10);

TRUNCATE TABLE cinemaboards ;

CREATE SEQUENCE seq_bno NOCACHE;

DELETE FROM comments WHERE bno = 80;
DELETE FROM likes WHERE bno = 80;
DELETE FROM CINEMABOARDS WHERE bno=80;
--comments테이블
CREATE TABLE comments(
	cno NUMBER PRIMARY KEY,
	bno NUMBER NOT NULL, 
	writer VARCHAR2(30), 
	content VARCHAR2(1000),
	cdate DATE DEFAULT SYSDATE, 
FOREIGN KEY (bno) REFERENCES cinemaboards(bno)
);
ALTER TABLE comments RENAME COLUMN writer TO userId;
CREATE SEQUENCE seq_cno START WITH 1 INCREMENT BY 1;
SELECT * FROM comments;
DROP TABLE comments;
-- cno foreigin key  
ALTER TABLE comments
ADD CONSTRAINT fk_users_userId
FOREIGN KEY (userId)
REFERENCES users(userId);


-- like테이블
CREATE TABLE likes(
	userId varchar2(50) NOT NULL,
	bno NUMBER NOT NULL,
	blike NUMBER DEFAULT 0,
	PRIMARY KEY(userId,bno),
	FOREIGN KEY(userId) REFERENCES users(userId),
	FOREIGN KEY(bno) REFERENCES cinemaboards(bno)
);
SELECT * FROM likes;
DROP TABLE likes;
INSERT INTO likes(userId,bno,blike) VALUES('pink',66,1);

-- 좋아요 조회
SELECT c.bcontent,c.blike,u.userId,l.bno
FROM likes l
JOIN cinemaboards c ON c.bno=l.bno
JOIN users u ON u.userId=l.userId
WHERE u.userId='gogoon'
ORDER BY c.bdate DESC
;

SELECT * FROM users WHERE userId = 'gogoon';
SELECT * FROM cinemaboards WHERE bno IN (SELECT bno FROM likes WHERE userId = 'gogoon');

-- 사용자조회
SELECT u.userId,u.username,u.USERPASSWORD,u.USERAGE ,u.USERMAIL,cm.CONTENT,c.BLIKE FROM users u
JOIN COMMENTS cm ON u.cno=cm.cno
JOIN CINEMABOARDS c ON c.bno=cm.bno
WHERE u.userId='red'
ORDER BY u.userId DESC
;
--
SELECT * FROM users WHERE userId = 'gogoon';

-- 트리거 likes테이블에서 좋아요 1 올리면 cinemaboards에서 +1이 자동으로 됨
CREATE OR REPLACE TRIGGER trg_likes_insert
AFTER INSERT ON likes
FOR EACH ROW
BEGIN
  UPDATE cinemaboards
  SET blike = blike + 1
  WHERE bno = :NEW.bno;
END;

SELECT * FROM user_errors WHERE name = 'TRG_LIKES_INSERT'; -- 트리거 에러확인




