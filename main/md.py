import time
import env
from ctp.md import MD

class PriceListener(MD):
	def OnRtnDepthMarketData(self, pDepthMarketData):
		"""
		行情订阅推送信息
		"""
		print('OnRtnDepthMarketData')
		# print('DepthMarketData:', pDepthMarketData)
		print(f'bid 1: {pDepthMarketData.BidPrice1}, ask 1: {pDepthMarketData.AskPrice1}')

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

def main():
	md = PriceListener()
	md.Create()
	md.RegisterFront(f'tcp://{env.md_server[0]}:{env.md_server[1]}')
	md.Init()
	print('trading day:', md.GetTradingDay())
	md.SubscribeMarketData(['au2608'])
	time.sleep(3)
	# md.UnSubscribeMarketData(['au2608'])

main()
