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

@app.route('/getTasksByDate')
def getTasksByDate():

	#链接数据库
	conn = pymysql.connect(user='root', password='Winyra123', database='Winyra', charset='utf8')
	cursor = conn.cursor()
	#从数据库中读取数据的脚本
	sqlString = "SELECT UserTaskNo, Category, SubCategory, TaskName, Tasks.Point, UserTasks.Status  FROM UserTasks \
		INNER JOIN Tasks ON UserTasks.TaskNo = Tasks.TaskNo \
		WHERE UserNo = 23 \
		AND FromDate = '2019-07-14'"

	#开始读取数据
	query = (sqlString)
	cursor.execute(query)

	payload = []

	for (UserTaskNo, Category, SubCategory, TaskName, Point, Status) in cursor:
		content = dict()
		content["UserTaskNo"] = UserTaskNo
		content["Category"] = Category
		content["SubCategory"] = SubCategory
		content["TaskName"] = TaskName
		content["Point"] = Point
		content["Status"] = Status
		payload.append(content)

	cursor.close()
	conn.close()

	return jsonify(payload)


@app.route('/handleUserTask/<usertask_no>')
def handleUserTask(usertask_no):

	conn = pymysql.connect(user='root', password='Winyra123', database='Winyra', charset='utf8')
	cursor = conn.cursor()
	sqlString = "UPDATE UserTasks \
		SET Status = (Status - 1)*(Status - 1) \
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

	conn = pymysql.connect(user='root', password='Winyra123', database='Winyra', charset='utf8')
	cursor = conn.cursor()
	sqlString = "SELECT UserTaskNo, Tasks.TaskNo, Category, SubCategory, TaskName, TaskDesc, UserTasks.Status, Tasks.Point, \
					DATE_FORMAT(FromDate, '%Y-%m-%d') FromDate, \
					DATE_FORMAT(ToDate, '%Y-%m-%d') ToDate, \
					DATE_FORMAT(CheckDate,'%Y-%m-%d') CheckDate \
				FROM Tasks \
				INNER JOIN UserTasks ON Tasks.TaskNo = UserTasks.TaskNo \
				WHERE IsValid = 1 \
				AND UserTasks.UserNo = "+ my_no +" \
				AND FromDate BETWEEN date_add('"+ from_date +"', interval -10 day) AND date_add('"+ from_date +"', interval 100 day) \
				ORDER BY FromDate, UserTaskNo \
				LIMIT 1, 500"

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


@app.route('/login', methods=['POST'])
def login():
	data = json.loads(request.get_data(as_text=True))
	userNo = data['username']
	password = data['password']

	conn = pymysql.connect(user='root', password='Winyra123', database='Winyra', charset='utf8')
	cursor = conn.cursor()
	query = ('select NO, NAME from Users WHERE NO="'+ userNo +'" AND PWD="'+ password +'"')
	cursor.execute(query)

	for (NO, NAME) in cursor:
		content = dict()
		content["NO"] = NO
		content["NAME"] = NAME

	cursor.close()
	conn.close()

	return jsonify(content)

@app.route('/getMemberList')
def getMemberList():

	htmlString = ""

	conn = pymysql.connect(user='root', password='Winyra123', database='Winyra', charset='utf8')
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