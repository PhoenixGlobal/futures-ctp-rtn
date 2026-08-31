import time
from ctp.md import MD
from lib.fommon.app_config.read import app_config

class PriceListener(MD):
	def OnRtnDepthMarketData(self, pDepthMarketData):
		"""
		行情订阅推送信息
		"""
		print('OnRtnDepthMarketData')
		# print('DepthMarketData:', pDepthMarketData)
		print(f'{pDepthMarketData.InstrumentID} ({fix_2(pDepthMarketData.LowerLimitPrice)}, {fix_2(pDepthMarketData.UpperLimitPrice)}) bid 1: {fix_2(pDepthMarketData.BidPrice1)}, ask 1: {fix_2(pDepthMarketData.AskPrice1)}')

	def OnRspSubMarketData(self, pSpecificInstrument, pRspInfo, nRequestID, bIsLast):
		"""
		订阅行情应答
		"""
		print('OnRspSubMarketData')
		print('RequestId:', nRequestID)
		print('isLast:', bIsLast)
		print('pRspInfo:', pRspInfo)
		print('pSpecificInstrument:', pSpecificInstrument)

	def OnRspUnSubMarketData(self, pSpecificInstrument, pRspInfo, nRequestID, bIsLast):
		"""
		取消订阅行情应答
		"""
		print('OnRspUnSubMarketData')
		print('RequestId:', nRequestID)
		print('isLast:', bIsLast)
		print('pRspInfo:', pRspInfo)
		print('pSpecificInstrument:', pSpecificInstrument)

def fix_2(price):
	return round(price, 2)

def main():
	md = PriceListener()
	md.Create()
	server = app_config['ctp']['market_data_server']
	md.RegisterFront(f'tcp://{server['ip']}:{server['port']}')
	md.Init()
	print('trading day:', md.GetTradingDay())
	md.SubscribeMarketData(['au2610'])
	time.sleep(3)
	md.UnSubscribeMarketData(['au2608'])

main()
