# -*- coding: utf-8
from browser import Browser
import json, time
from datetime import datetime
from datetime import timedelta
import cv2

venueUrl = {
	"羽毛球":"https://epe.pku.edu.cn/venue/pku/venue-reservation/60",
	"篮球":"https://epe.pku.edu.cn/venue/pku/venue-reservation/68",
	"台球":"https://epe.pku.edu.cn/venue/pku/venue-reservation/64"
}

timeList = {
	"羽毛球":["8:00-9:00","9:00-10:00","10:00-11:00","11:00-12:00","12:00-13:00","13:00-14:00",
	"14:00-15:00","15:00-16:00","16:00-17:00","17:00-18:00","18:00-19:00","19:00-20:00","20:00-21:00","21:00-22:00"],
	"篮球":["8:00-9:00","9:00-10:00","10:00-11:00","11:00-12:00","12:00-13:00","13:00-14:00",
	"14:00-15:00","15:00-16:00","16:00-17:00","17:00-18:00","18:00-19:00","19:00-20:00","20:00-21:00","21:00-22:00"],
	"台球":["8:00-9:00","9:00-10:00","10:00-11:00","11:00-12:00","12:00-13:00","13:00-14:00",
	"14:00-15:00","15:00-16:00","16:00-17:00","17:00-18:00","18:00-19:00","19:00-20:00","20:00-21:00","21:00-22:00"]
}

courtPriorityList = {
	"羽毛球":["3号", "4号", "9号", "10号", "1号", "2号", "5号", "6号", "7号", "8号", "11号", "12号"],
	"篮球":["北1", "南1", "北2", "南2"],
	"台球":["3号", "4号", "9号", "10号", "1号", "2号", "5号", "13号", "7号", "8号", "11号", "12号"]
}

courtIndexDict = {
	"羽毛球":{
			"1号" : {"page": 0, "column": 1},
			"2号" : {"page": 0, "column": 2},
			"3号" : {"page": 0, "column": 3},
			"4号" : {"page": 0, "column": 4},
			"5号" : {"page": 0, "column": 5},
			"6号" : {"page": 1, "column": 1},
			"7号" : {"page": 1, "column": 2},
			"8号" : {"page": 1, "column": 3},
			"9号" : {"page": 1, "column": 4},
			"10号": {"page": 1, "column": 5},
			"11号": {"page": 2, "column": 1},
			"12号": {"page": 2, "column": 2}
		},
	"篮球":{
			"北1" : {"page": 0, "column": 1},
			"南1" : {"page": 0, "column": 2},
			"北2" : {"page": 0, "column": 3},
			"南2" : {"page": 0, "column": 4}
		},
	"台球":{
			"1号" : {"page": 0, "column": 1},
			"2号" : {"page": 0, "column": 2},
			"3号" : {"page": 0, "column": 3},
			"4号" : {"page": 0, "column": 4},
			"5号" : {"page": 0, "column": 5},
			"7号" : {"page": 1, "column": 1},
			"8号" : {"page": 1, "column": 2},
			"9号" : {"page": 1, "column": 3},
			"10号": {"page": 1, "column": 4},
			"11号": {"page": 1, "column": 5},
			"12号": {"page": 2, "column": 1},
			"13号": {"page": 2, "column": 2},
			"14号": {"page": 2, "column": 3},
			"15号": {"page": 2, "column": 4},
			"16号": {"page": 2, "column": 5},
			"17号": {"page": 3, "column": 1},
			"18号": {"page": 3, "column": 2},
			"19号": {"page": 3, "column": 3},
			"20号": {"page": 3, "column": 4},
			"21号": {"page": 3, "column": 5},
			"22号": {"page": 4, "column": 1},
			"23号": {"page": 4, "column": 2},
			"斯诺克": {"page": 4, "column": 3},
			"24号": {"page": 4, "column": 4}
		}
}

class PKUVenue():
	def __init__(self, config):
		self.username = config["username"]
		self.password = config["password"]
		self.phone = config["phone"]
		self.orderStatement = []
		self.browser = Browser()

	def __reqListToDict(self, reqList):
		reqDict = {}
		for req in reqList:
			orderDate = req.split(" ")[0]
			orderTime = req.split(" ")[1]
			if len(orderDate) < 2:
				try:
					dayDelta = int(orderDate)
				except:
					print("配置文件出错：请按格式输入预定时间")
					dayDelta = 3
				orderDate = (datetime.now()+timedelta(days = dayDelta)).strftime("%Y-%m-%d")
			if orderDate in reqDict.keys():
				reqDict[orderDate].append(orderTime)
			else:
				reqDict[orderDate] = [orderTime]
		return reqDict

	def __jumpToDate(self, orderDate):
		print("selecting date %s" % orderDate)
		today = datetime.now()
		orderDatetime = datetime.strptime(orderDate, "%Y-%m-%d")
		dayDelta = (orderDatetime - today).days + 1
		for i in range(0, dayDelta):
			self.browser.clickByXPath("/html/body/div[1]/div/div/div[3]/div[2]/div/div[2]/form/div/div/button[2]/i")
		# waiting for the table to show up
		self.browser.findElementByXPath("/html/body/div[1]/div/div/div[3]/div[2]/div/div[2]/div[3]/div[1]/div/div/div/div/div/table/tbody/tr[15]/td[1]/div")

	def __matchImage(self, target, background) -> int:
		"""Match target and the corresponding area of background, and return the x ordinate"""

		# denoising
		target = cv2.GaussianBlur(target,(3,3),0)
		target = cv2.Canny(target,50,150)

		background = cv2.GaussianBlur(background,(3,3),0)
		background = cv2.Canny(background,50,150)
		
		# match
		res = cv2.matchTemplate(target,background,cv2.TM_CCOEFF_NORMED)
		min_val,max_val,min_loc,max_loc = cv2.minMaxLoc(res)

		return max_loc[0]

	def __submitOrder(self):
		print("read & agree ✅!!!!")
		self.browser.clickByXPath("/html/body/div[1]/div/div/div[3]/div[2]/div/div[2]/div[4]/label/span/input")

		# # no submit
		# a = input()
		# return

		print("click to make order......")
		self.browser.clickByXPath("/html/body/div[1]/div/div/div[3]/div[2]/div/div[2]/div[5]/div/div[2]")

		print("submiting order ....... ")
		self.browser.typeByXPath("/html/body/div[1]/div/div/div[3]/div[2]/div/div[2]/form/div/div[4]/div/div/div/div/input", self.phone)
		self.browser.clickByXPath("/html/body/div[1]/div/div/div[3]/div[2]/div/div[2]/div/div/div[2]")

		background = cv2.imdecode(
			self.browser.getDecodedRawImageByXPath("/html/body/div[1]/div/div/div[3]/div[2]/div/div[2]/div[2]/div/div[2]/div/div[1]/div/img"),
			cv2.IMREAD_GRAYSCALE
			)
		target = cv2.imdecode(
			self.browser.getDecodedRawImageByXPath("/html/body/div[1]/div/div/div[3]/div[2]/div/div[2]/div[2]/div/div[2]/div/div[2]/div/div/div/img"),
			cv2.IMREAD_GRAYSCALE
			)

		sildeDist = self.__matchImage(target, background) + 10
		self.browser.sildeBarByXPath("/html/body/div[1]/div/div/div[3]/div[2]/div/div[2]/div[2]/div/div[2]/div/div[2]/div/span", sildeDist)

		self.browser.clickByXPath("/html/body/div[1]/div/div/div[3]/div[2]/div/div[3]/div[7]/div[2]")

	def __makeOrder(self, sportsName, timeList, courtPriorityList, courtIndexDict, orderDate, orderTimeList):
		orderEnable = False
		currentPageIndex = 0
		pageJumpButtonIndex = [None, 6, 2]
		for ot in orderTimeList:
			print("selecting time %s ........." % ot)
			timeTableRow = timeList.index(ot)+1
			courtSelected = False
			for court in courtPriorityList:
				courtPageIndex = courtIndexDict[court]["page"]
				courtTableColumn = courtIndexDict[court]["column"]
				# judge whether jump page or not
				pageDelta = courtPageIndex - currentPageIndex
				jumpDirection = 1 if pageDelta > 0 else -1
				for _ in range(0, pageDelta, jumpDirection):
					self.browser.clickByXPath("/html/body/div[1]/div/div/div[3]/div[2]/div/div[2]/div[3]/div[1]/div/div/div/div/div/table/thead/tr/td[%d]/div/span/i" % pageJumpButtonIndex[jumpDirection])
					currentPageIndex += jumpDirection
				# select court block
				courtBlockElment = self.browser.findElementByXPath("/html/body/div[1]/div/div/div[3]/div[2]/div/div[2]/div[3]/div[1]/div/div/div/div/div/table/tbody/tr[%d]/td[%d]/div" % (timeTableRow, courtTableColumn+1))
				if "free" in courtBlockElment.get_attribute('class'):
					courtBlockElment.click()
					courtSelected = True
					self.orderStatement.append("%s %s %s %s" % (sportsName, orderDate, ot, court))
					print("selected %s %s %s" % (orderDate, ot, court))
					break
			if not courtSelected:
				self.orderStatement.append("%s %s %s %s" % (sportsName, orderDate, ot, "无场"))
				print("without court left at %s %s" % (orderDate, ot))
			else:
				orderEnable = True

		return orderEnable

	def __makeOrderDay(self, sportsName, timeList, courtPriorityList, courtIndexDict, orderDate, orderTimeList):
		orderEnable = False
		currentPageIndex = 0
		pageJumpButtonIndex = [None, 6, 2]

		self.browser.gotoPage(venueUrl[sportsName])
		self.__jumpToDate(orderDate)
		print("selecting date %s ........." % orderDate)
		courtSelected = 0

		for court in courtPriorityList:
			courtPageIndex = courtIndexDict[court]["page"]
			courtTableColumn = courtIndexDict[court]["column"]

			# judge whether jump page or not
			pageDelta = courtPageIndex - currentPageIndex
			jumpDirection = 1 if pageDelta > 0 else -1
			for _ in range(0, pageDelta, jumpDirection):
				self.browser.clickByXPath("/html/body/div[1]/div/div/div[3]/div[2]/div/div[2]/div[3]/div[1]/div/div/div/div/div/table/thead/tr/td[%d]/div/span/i" % pageJumpButtonIndex[jumpDirection])
				currentPageIndex += jumpDirection

			# select court block
			currentOrder = []
			for ot in orderTimeList:
				timeTableRow = timeList.index(ot)+1
				courtBlockElment = self.browser.findElementByXPath("/html/body/div[1]/div/div/div[3]/div[2]/div/div[2]/div[3]/div[1]/div/div/div/div/div/table/tbody/tr[%d]/td[%d]/div" % (
					timeTableRow, courtTableColumn + 1
					))

				if "free" not in courtBlockElment.get_attribute('class'):
					continue

				courtSelected = 1
				currentOrder = ["%s %s %s %s" % (sportsName, orderDate, timeList[timeTableRow - 1], court)]
				courtBlockElment.click()

				if timeTableRow == len(timeList):
					continue
				
				courtBlockElmentNext = self.browser.findElementByXPath("/html/body/div[1]/div/div/div[3]/div[2]/div/div[2]/div[3]/div[1]/div/div/div/div/div/table/tbody/tr[%d]/td[%d]/div" % (
					timeTableRow + 1, courtTableColumn + 1
					))

				if "free" in courtBlockElmentNext.get_attribute('class'):
					courtBlockElmentNext.click()
					courtSelected = 2
					currentOrder.append("%s %s %s %s" % (sportsName, orderDate, timeList[timeTableRow], court))
					break

		if courtSelected == 0:
			self.orderStatement.append("%s %s %s %s" % (sportsName, orderDate, ot, "无场"))
			print("without court left at %s %s" % (orderDate, ot))
		else:
			self.orderStatemen += currentOrder
			orderEnable = True

		return orderEnable

	def login(self):
		self.browser.gotoPage("https://epe.pku.edu.cn/ggtypt/login?service=https://epe.pku.edu.cn/venue-server/loginto")
		print("trying to login ......")
		self.browser.typeByCssSelector("#user_name", self.username)
		self.browser.typeByCssSelector("#password", self.password)
		self.browser.clickByCssSelector("#logon_button")
		self.browser.findElementByCssSelector("body > div.fullHeight > div > div > div.isLogin > div > div.loginUser")
		print("login success !!!!")

	def order(self, sportsName, reqList):
		# check
		if sportsName not in timeList.keys():
			print("\n错误：运动 " + sportsName + " 不支持！\n")
			return

		reqDict = self.__reqListToDict(reqList)
		for orderDate in reqDict:
			# if self.__makeOrderDay(sportsName, timeList[sportsName], courtPriorityList[sportsName], courtIndexDict[sportsName], orderDate, reqDict[orderDate]):
			#  	self.__submitOrder()
			
			for i in range(0, len(reqDict[orderDate]), 2):
				self.browser.gotoPage(venueUrl[sportsName])
				self.__jumpToDate(orderDate)
				if self.__makeOrder(sportsName, timeList[sportsName], courtPriorityList[sportsName], courtIndexDict[sportsName], orderDate, reqDict[orderDate][i:i+2]):
					self.__submitOrder()

	def outputOrderStatement(self):
		for i in range(0, len(self.orderStatement)):
			print("{:^52}".format(" " + "-" * 50 + " "))
			print("| " + "{:^48}".format(self.orderStatement[i]) + " |")
			print("{:^52}".format(" " + "-" * 50 + " "))

	def __del__(self):
		self.browser.close()

def main():
	with open("config.json", "r", encoding="utf8") as f:
		config = json.load(f)

	# waiting until logintime
	now = datetime.now()
	logintime = datetime.strptime(config["logintime"], "%H:%M:%S").replace(
		year=now.year, month= now.month, day= now.day
	)
	if (logintime - now).total_seconds() > 0:
		print("程序将在" + datetime.strftime(logintime, "%H:%M:%S") + "启动...\n")
		time.sleep((logintime - now).total_seconds())

	pkuvenue = PKUVenue(config["user_info"])
	pkuvenue.login()

	# waiting until rushtime
	now = datetime.now()
	rushtime = datetime.strptime(config["rushtime"], "%H:%M:%S").replace(
		year=now.year, month= now.month, day= now.day
	)
	if (rushtime - now).total_seconds() > 0:
		time.sleep((rushtime - now).total_seconds())

	for k in config["order"].keys():
		pkuvenue.order(k,config["order"][k])

	pkuvenue.outputOrderStatement()

	del pkuvenue

if __name__=="__main__":
	main()