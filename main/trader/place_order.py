def _():
	order = ApiStructure.InputOrderField(
		BrokerID = env.broker,
		InvestorID = env.investor,
		UserID = env.investor,
		OrderPriceType = 2, # 1: 市价; 2: 限价
		LimitPrice = 869,
		Direction = 1, # 0: 卖; 1: 买
		CombOffsetFlag = 0, # 0: 开仓; 1: 平仓; 3: 平今; 4: 平昨
		CombHedgeFlag = 1, # 1: 投机;
		VolumeTotalOriginal = 1,
		TimeCondition = 1, # 1: 立即
		VolumeCondition = 1, # 1: 任何数量
		# MinVolume = 2, # 最小成交量 (在 VolumeCondition 为 “最小数量” 时有效)
		ContingentCondition = 1, # 1: 立即
		ForceCloseReason = 0, # 0: 非强平
		ExchangeID = 'SHFE',
		InstrumentID = 'sp2608',
	)
	ret = trader.ReqOrderInsert(order, trader._next_request_id())
	logging.info('order sent')
	print(ret)
