# -*- coding: utf-8 -*- 

from flask import Flask, render_template, jsonify, request
import pymysql
import json

app = Flask(__name__ ,static_url_path='/static')

@app.route('/getStatic')
def getStatic():
	item2 = {"name":"FANNY", "address":"china"}
	return render_template('a/dog.html', obj=item2)

@app.route('/winyra/<pageUrl>')
def getWebPage(pageUrl):
	return render_template(pageUrl)

@app.route('/winyra/<dir>/<pageUrl>')
def getWebPage2(dir, pageUrl):
	return render_template(dir + "/" + pageUrl)

@app.route('/getTasksByDate/<userNo>/<from_date>')
def getTasksByDate(userNo, from_date):

	#链接数据库
	conn = pymysql.connect(host='94.191.29.192', user='root', password='!QAZ2wsx', database='Winyra', charset='utf8')
	cursor = conn.cursor()
	#从数据库中读取数据的脚本
	sqlString = "SELECT UserTaskNo, Category, SubCategory, TaskName, FromDate, ToDate, CheckDate, Tasks.Point, UserTasks.Status  FROM UserTasks \
		INNER JOIN Tasks ON UserTasks.TaskNo = Tasks.TaskNo \
		WHERE UserNo = "+ userNo +" \
		AND '"+ from_date +"' BETWEEN FromDate AND ToDate"

	#开始读取数据
	query = (sqlString)
	cursor.execute(query)

	payload = []

	for (UserTaskNo, Category, SubCategory, TaskName, FromDate, ToDate, CheckDate, Point, Status) in cursor:
		content = dict()
		content["UserTaskNo"] = UserTaskNo
		content["Category"] = Category
		content["SubCategory"] = SubCategory
		content["TaskName"] = TaskName
		content["Point"] = Point
		content["Status"] = Status
		content["FromDate"] = FromDate
		content["ToDate"] = ToDate
		content["CheckDate"] = CheckDate
		payload.append(content)

	cursor.close()
	conn.close()

	return jsonify(payload)

@app.route('/handleUserEverydayTask', methods=['POST'])
def handleUserEverydayTask():

	data = json.loads(request.get_data(as_text=True))
	A = data['inA']
	B = data['inB']
	C = data['inC']
	D = data['inD']
	E = data['inE']
	F = data['inF']
	UN = data['inUN']
	DESC = data['inDESC']

	conn = pymysql.connect(host='94.191.29.192',user='root', password='!QAZ2wsx', database='Winyra', charset='utf8')
	cursor = conn.cursor()
	sqlString = "INSERT INTO UserTasks(UserNo, TaskNo, Status, Point, 	ExtPoint, `Desc`, A, B, C, D, E, F, LastUpdate) \
		VALUES("+ UN +",100,1,10,0,'"+ DESC +"', '"+A+"','"+B+"','"+C+"','"+D+"','"+E+"','"+F+"',Now())"

	print(sqlString)
	query = (sqlString)
	cursor.execute(query)
	conn.commit()

	cursor.close()
	conn.close()
	return "ok"

@app.route('/handleUserTask/<usertask_no>', methods=['POST'])
def handleUserTask(usertask_no):

	data = json.loads(request.get_data(as_text=True))
	A = data['inA']
	B = data['inB']
	C = data['inC']
	D = data['inD']
	E = data['inE']
	F = data['inF']
	Point = data['Point']

	print Point

	conn = pymysql.connect(host='94.191.29.192',user='root', password='!QAZ2wsx', database='Winyra', charset='utf8')
	cursor = conn.cursor()
	sqlString = "UPDATE UserTasks \
		SET Status = (Status - 1)*(Status - 1), \
            A = '"+ A +"', \
            B = '"+ B +"', \
            C = '"+ C +"', \
            D = '"+ D +"', \
            E = '"+ E +"', \
            F = '"+ F +"', \
			LastUpdate = Now(), \
			Point = "+ str(Point) +" \
		WHERE UserTaskNo = "+ usertask_no +""

	print(sqlString)
	query = (sqlString)
	cursor.execute(query)
	conn.commit()

	cursor.close()
	conn.close()
	return "ok"

@app.route('/getTaskList/<my_no>/<from_date>')
def getTaskList(my_no, from_date):

	conn = pymysql.connect(host='94.191.29.192',user='root', password='!QAZ2wsx', database='Winyra', charset='utf8')
	cursor = conn.cursor()
	sqlString = "SELECT UserTaskNo, Tasks.TaskNo, Category, SubCategory, TaskName, TaskDesc, UserTasks.Status, Tasks.Point, \
					DATE_FORMAT(FromDate, '%Y-%m-%d') FromDate, \
					DATE_FORMAT(ToDate, '%Y-%m-%d') ToDate, \
					DATE_FORMAT(CheckDate,'%Y-%m-%d') CheckDate \
				FROM Tasks \
				INNER JOIN UserTasks ON Tasks.TaskNo = UserTasks.TaskNo \
				WHERE IsValid = 1 \
				AND UserTasks.UserNo = "+ my_no +" \
				AND FromDate BETWEEN date_add('"+ from_date +"', interval -100 day) AND date_add('"+ from_date +"', interval 100 day) \
				ORDER BY FromDate, UserTaskNo \
				LIMIT 0, 500"

	query = (sqlString)
	cursor.execute(query)

	payload = []

	for (UserTaskNo, TaskNo, Category, SubCategory, TaskName, TaskDesc, Status, Point, FromDate, ToDate, CheckDate) in cursor:
		content = dict()
		content["UserTaskNo"] = UserTaskNo
		content["TaskNo"] = TaskNo
		content["Category"] = Category
		content["SubCategory"] = SubCategory
		content["TaskName"] = TaskName
		content["TaskDesc"] = TaskDesc
		content["Point"] = Point
		content["FromDate"] = FromDate
		content["ToDate"] = ToDate
		content["CheckDate"] = CheckDate
		content["Status"] = Status
		payload.append(content)
	cursor.close()
	conn.close()

	return jsonify(payload)


@app.route('/getSummary')
def getSummary():

	conn = pymysql.connect(host='94.191.29.192',user='root', password='!QAZ2wsx', database='Winyra', charset='utf8')
	cursor = conn.cursor()
	sqlString = "SELECT UserNo, Status, SUM(Point) TotalPoints, SUM(ExtPoint) TotalExtPoints, COUNT(1) TotalCnt FROM UserTasks \
		GROUP BY UserNo, Status"

	query = (sqlString)
	cursor.execute(query)

	payload = []

	for (UserNo, Status, TotalPoints, TotalExtPoints, TotalCnt) in cursor:
		content = dict()
		content["UserNo"] = UserNo
		content["Status"] = Status
		content["TotalPoints"] = float(TotalPoints)
		content["TotalExtPoints"] = float(TotalExtPoints)
		content["TotalCnt"] = float(TotalCnt)
		payload.append(content)
	cursor.close()
	conn.close()

	return jsonify(payload)

@app.route('/login', methods=['POST'])
def login():
	data = json.loads(request.get_data(as_text=True))
	userNo = data['username']
	password = data['password']

	conn = pymysql.connect(host='94.191.29.192',user='root', password='!QAZ2wsx', database='Winyra', charset='utf8')
	cursor = conn.cursor()
	query = ('select NO, NAME, PhotoUrl from Users WHERE NO="'+ userNo +'" AND PWD="'+ password +'"')
	cursor.execute(query)

	content = dict()
	for (NO, NAME, PhotoUrl) in cursor:
		content["NO"] = NO
		content["NAME"] = NAME
		content["PhotoUrl"] = PhotoUrl

	cursor.close()
	conn.close()

	return jsonify(content)

@app.route('/getMemberList')
def getMemberList():

	htmlString = ""

	conn = pymysql.connect(host='94.191.29.192',user='root', password='!QAZ2wsx', database='Winyra', charset='utf8')
	cursor = conn.cursor()
	query = ('select ID, NAME from Users')
	cursor.execute(query)
	for (NO, PASSWORD) in cursor:
		htmlString = htmlString + " " + str(NO) +  PASSWORD
	cursor.close()
	conn.close()

	return htmlString

if __name__ == "__main__":
	app.run(host='0.0.0.0', debug=True, port=5000)