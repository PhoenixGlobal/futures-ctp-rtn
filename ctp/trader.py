from typing import Callable, Self
from ctpwrapper import ApiStructure, TraderApiPy
from fommon.app_config.read import app_config
from fommon import log

class BaseTrader(TraderApiPy):
	def __init__(self,
		after_login: Callable[[Self], None],
	):
		self.request_id = 1
		self.after_login = after_login

	def req_id(self):
		id = self.request_id
		self.request_id += 1
		log.inf(f'new req_id: {id}')
		return id

	def OnRspError(self, pRspInfo, nRequestID, bIsLast):
		log.inf('OnRspError:')
		log.inf(f'requestID: {nRequestID}')
		log.inf(pRspInfo)
		log.inf(bIsLast)

	def OnHeartBeatWarning(self, nTimeLapse):
		"""心跳超时警告。当长时间未收到报文时，该方法被调用。
		@param nTimeLapse 距离上次接收报文的时间
		"""
		log.inf(f'OnHeartBeatWarning time: {nTimeLapse}')

	def OnFrontDisconnected(self, nReason):
		log.err(f'FrontDisconnected: {nReason}')

	def OnFrontConnected(self):
		log.inf('FrontConnected')
		req = ApiStructure.ReqAuthenticateField(
			BrokerID=app_config['ctp']['broker'],
			UserID=app_config['ctp']['investor'],
			AppID=app_config['ctp']['app_id'],
			AuthCode=app_config['ctp']['auth_code'],
		)
		self.ReqAuthenticate(req, self.req_id())

	def OnRspAuthenticate(self, pRspAuthenticateField, pRspInfo, nRequestID, bIsLast):
		log.inf('OnRspAuthenticate')
		log.inf(f'pRspInfo: {pRspInfo}')
		log.inf(f'nRequestID: {nRequestID}')
		log.inf(f'bIsLast: {bIsLast}')

		if pRspInfo.ErrorID == 0:
			log.inf('auth success')
			req = ApiStructure.ReqUserLoginField(
				BrokerID = app_config['ctp']['broker'],
				UserID = app_config['ctp']['investor'],
				Password = app_config['ctp']['password'],
			)
			self.ReqUserLogin(req, self.req_id())
		else:
			log.err('auth failed')

	def OnRspUserLogin(self, pRspUserLogin, pRspInfo, nRequestID, bIsLast):
		log.inf('OnRspUserLogin')
		log.inf(f'nRequestID: {nRequestID}')
		log.inf(f'bIsLast: {bIsLast}')
		log.inf(f'pRspInfo: {pRspInfo}')

		if pRspInfo.ErrorID != 0:
			log.err('login failed')
		else:
			log.inf('trader user login successfully')
			# log.inf(f'pRspUserLogin: {pRspUserLogin}')
			self.after_login(self)
