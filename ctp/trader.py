from typing import Callable, Self
import time
from ctpwrapper import ApiStructure, TraderApiPy
from fommon.app_config.read import app_config
from fommon import log

class BaseTrader(TraderApiPy):
	def __init__(self,
		after_login: Callable[[Self], None],
	):
		self.request_id = 1
		self.after_login = after_login
		self.__connected = False
		self.__initing = False
		self.__ready_to_trade = False

	def wait_ready_to_trade(self):
		if not self.__connected:
			raise Exception('CTP 未连接')
		if self.__ready_to_trade:
			return

		log.inf('等待 CTP 重新初始化...')
		retry = 1
		self.__auth()
		while not self.__ready_to_trade:
			if retry > 20:
				raise Exception('CTP 重新初始化等待超时')
			retry += 1
			time.sleep(.1)

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
		self.__connected = False
		self.__ready_to_trade = False
		self.__initing = False

	def OnFrontConnected(self):
		self.__connected = True
		log.inf('FrontConnected')
		self.__auth()

	def __auth(self):
		if self.__initing:
			return
		self.__initing = True
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
			self.__initing = False

	def OnRspUserLogin(self, pRspUserLogin, pRspInfo, nRequestID, bIsLast):
		log.inf('OnRspUserLogin')
		log.inf(f'nRequestID: {nRequestID}')
		log.inf(f'bIsLast: {bIsLast}')
		log.inf(f'pRspInfo: {pRspInfo}')

		if pRspInfo.ErrorID != 0:
			log.err('login failed')
			self.__initing = False
		else:
			log.inf('trader user login successfully')
			# log.inf(f'pRspUserLogin: {pRspUserLogin}')
			self.__confirm_settlement()

	# 确认结算单
	def __confirm_settlement(self):
		log.inf('confirming settlement')
		settlement = ApiStructure.SettlementInfoConfirmField(
			BrokerID = app_config['ctp']['broker'],
			InvestorID = app_config['ctp']['investor'],
		)
		ret = self.ReqSettlementInfoConfirm(settlement, self.req_id())
		if ret != 0:
			log.err2(f'确认结算单失败: {ret}')
			self.__initing = False

	def OnRspSettlementInfoConfirm(self, pSettlementInfoConfirm, pRspInfo, nRequestID, bIsLast):
		log.inf(f'确认结算单响应(req_id: {nRequestID}):')
		log.inf(pRspInfo)
		self.__initing = False
		if pRspInfo.ErrorID == 0:
			log.inf('(success) 确认结算单')
			self.__ready_to_trade = True
			self.after_login(self)
		else:
			log.err('(failed) 确认结算单')
			log.inf(pSettlementInfoConfirm)
