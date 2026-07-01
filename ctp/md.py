import sys
from ctpwrapper import ApiStructure, MdApiPy

class MD(MdApiPy):
	def __init__(self, broker_id, investor_id, password, request_id):
		self.login = False
		self.broker_id = broker_id
		self.investor_id = investor_id
		self.password = password
		self._request_id = request_id

	@property
	def request_id(self):
		self._request_id += 1
		return self._request_id

	def OnRspError(self, pRspInfo, nRequestID, bIsLast):
		print('OnRspError:')
		print('requestID:', nRequestID)
		print(pRspInfo)
		print(bIsLast)

	def OnFrontConnected(self):
		user_login = ApiStructure.ReqUserLoginField(BrokerID=self.broker_id, UserID=self.investor_id, Password=self.password)
		self.ReqUserLogin(user_login, self.request_id)

	def OnFrontDisconnected(self, nReason):
		print('Md OnFrontDisconnected {0}'.format(nReason))
		sys.exit()

	def OnHeartBeatWarning(self, nTimeLapse):
		print('Md OnHeartBeatWarning, time = {0}'.format(nTimeLapse))

	def OnRspUserLogin(self, pRspUserLogin, pRspInfo, nRequestID, bIsLast):
		print('OnRspUserLogin')
		print('requestID:', nRequestID)
		print('RspInfo:', pRspInfo)

		if pRspInfo.ErrorID != 0:
			print('RspInfo:', pRspInfo)
		else:
			print('user login successfully')
			print('RspUserLogin:', pRspUserLogin)
			self.login = True
