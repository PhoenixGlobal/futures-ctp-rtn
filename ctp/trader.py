import logging
from typing import Callable, Optional
from ctpwrapper import ApiStructure, TraderApiPy
import env
from . import req_id_start

class BaseTrader(TraderApiPy):
	def __init__(self,
		after_login: Callable[[BaseTrader], None],
		logger: Optional[str] = None,
	):
		if logger is None:
			self.log = logging
		else:
			self.log = logging.getLogger(logger)

		self.request_id = req_id_start()
		self.after_login = after_login

	def req_id(self):
		id = self.request_id
		self.request_id += 1
		return id

	def OnRspError(self, pRspInfo, nRequestID, bIsLast):
		self.log.info('OnRspError:')
		self.log.info(f'requestID: {nRequestID}')
		self.log.info(pRspInfo)
		self.log.info(bIsLast)

	def OnHeartBeatWarning(self, nTimeLapse):
		"""心跳超时警告。当长时间未收到报文时，该方法被调用。
		@param nTimeLapse 距离上次接收报文的时间
		"""
		self.log.info(f'OnHeartBeatWarning time: {nTimeLapse}')

	def OnFrontDisconnected(self, nReason):
		self.log.error('FrontDisconnected:', nReason)

	def OnFrontConnected(self):
		self.log.info('FrontConnected')
		req = ApiStructure.ReqAuthenticateField(
			BrokerID=env.broker,
			UserID=env.investor,
			AppID=env.app_id,
			AuthCode=env.auth_code,
		)
		self.ReqAuthenticate(req, self.req_id())

	def OnRspAuthenticate(self, pRspAuthenticateField, pRspInfo, nRequestID, bIsLast):
		self.log.info('OnRspAuthenticate')
		self.log.info(f'pRspInfo: {pRspInfo}')
		self.log.info(f'nRequestID: {nRequestID}')
		self.log.info(f'bIsLast: {bIsLast}')

		if pRspInfo.ErrorID == 0:
			self.log.info('auth success')
			req = ApiStructure.ReqUserLoginField(
				BrokerID = env.broker,
				UserID = env.investor,
				Password = env.password,
			)
			self.ReqUserLogin(req, self.req_id())
		else:
			self.log.error('auth failed')

	def OnRspUserLogin(self, pRspUserLogin, pRspInfo, nRequestID, bIsLast):
		self.log.info('OnRspUserLogin')
		self.log.info(f'nRequestID: {nRequestID}')
		self.log.info(f'bIsLast: {bIsLast}')
		self.log.info(f'pRspInfo: {pRspInfo}')

		if pRspInfo.ErrorID != 0:
			self.log.error('login failed')
		else:
			self.log.info('trader user login successfully')
			self.log.info(f'pRspUserLogin: {pRspUserLogin}')
			self.after_login(self)
