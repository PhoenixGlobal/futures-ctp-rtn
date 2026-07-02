import logging
from typing import Callable
from ctpwrapper import ApiStructure, TraderApiPy
import env
from . import _

class BaseTrader(TraderApiPy):
	def __init__(self, on_login: Callable[[BaseTrader], None]):
		self.request_id = _.req_id_start()
		self.on_login = on_login

	def req_id(self):
		id = self.request_id
		self.request_id += 1
		return id

	def OnRspError(self, pRspInfo, nRequestID, bIsLast):
		logging.info('OnRspError:')
		logging.info(f'requestID: {nRequestID}')
		logging.info(pRspInfo)
		logging.info(bIsLast)

	def OnHeartBeatWarning(self, nTimeLapse):
		"""心跳超时警告。当长时间未收到报文时，该方法被调用。
		@param nTimeLapse 距离上次接收报文的时间
		"""
		logging.info(f'OnHeartBeatWarning time: {nTimeLapse}')

	def OnFrontDisconnected(self, nReason):
		logging.error('FrontDisconnected:', nReason)

	def OnFrontConnected(self):
		logging.info('FrontConnected')
		req = ApiStructure.ReqAuthenticateField(
			BrokerID=env.broker,
			UserID=env.investor,
			AppID=env.app_id,
			AuthCode=env.auth_code,
		)
		self.ReqAuthenticate(req, self.req_id())

	def OnRspAuthenticate(self, pRspAuthenticateField, pRspInfo, nRequestID, bIsLast):
		logging.info('OnRspAuthenticate')
		logging.info(f'pRspInfo: {pRspInfo}')
		logging.info(f'nRequestID: {nRequestID}')
		logging.info(f'bIsLast: {bIsLast}')

		if pRspInfo.ErrorID == 0:
			logging.info('auth success')
			req = ApiStructure.ReqUserLoginField(
				BrokerID = env.broker,
				UserID = env.investor,
				Password = env.password,
			)
			self.ReqUserLogin(req, self.req_id())
		else:
			logging.error('auth failed')

	def OnRspUserLogin(self, pRspUserLogin, pRspInfo, nRequestID, bIsLast):
		logging.info('OnRspUserLogin')
		logging.info(f'nRequestID: {nRequestID}')
		logging.info(f'bIsLast: {bIsLast}')
		logging.info(f'pRspInfo: {pRspInfo}')

		if pRspInfo.ErrorID != 0:
			logging.error('login failed')
		else:
			logging.info('trader user login successfully')
			logging.info(f'pRspUserLogin: {pRspUserLogin}')
			self.on_login(self)

class Trader(BaseTrader):
	# 期货公司响应
	def OnRspOrderInsert(self, pInputOrder, pRspInfo, nRequestID, bIsLast):
		pass

	# 订单实时状态推送
	def OnRtnOrder(self, pOrder):
		logging.info(pOrder)
	
	# 报单插入错误（交易所）
	def OnErrRtnOrderInsert(self, pInputOrder, pRspInfo):
		logging.error('order insert failed')
		logging.error(pInputOrder)
		logging.error(pRspInfo)
