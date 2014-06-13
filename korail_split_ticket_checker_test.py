# -*- coding: utf-8 -*-
import unittest
import korail_split_ticket_checker

import datetime

class TestKorailSplitTickerChecker(unittest.TestCase):

	def setUp(self):		
		tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
		self.date = tomorrow.strftime('%Y%m%d')

	def test_get_train_routes_ktx(self):
		# 2014년 6월 9일 개정 시간표 기준
		self.train_type = "KTX"
		self.train_no = 101
		self.stations = 8

		train_type, stations = korail_split_ticket_checker.get_train_routes(self.date, self.train_no)

		self.assertEqual(self.train_type, train_type, "Failed to get train type")
		self.assertEqual(self.stations, len(stations), "Failed to get station list")

	def test_get_train_routes_ktx_sanchon(self):
		# 2014년 6월 9일 개정 시간표 기준
		self.train_type = u"KTX-산천"
		self.train_no = 407
		self.stations = 10

		train_type, stations = korail_split_ticket_checker.get_train_routes(self.date, self.train_no)

		self.assertEqual(self.train_type, train_type, "Failed to get train type")
		self.assertEqual(self.stations, len(stations), "Failed to get station list")

	def test_get_train_routes_itx_saemaul(self):
		# 2014년 6월 9일 개정 시간표 기준
		self.train_type = u"ITX-새마을"
		self.train_no = 1081
		self.stations = 17

		train_type, stations = korail_split_ticket_checker.get_train_routes(self.date, self.train_no)

		self.assertEqual(self.train_type, train_type, "Failed to get train type")
		self.assertEqual(self.stations, len(stations), "Failed to get station list")

	def test_get_train_routes_mugungwha(self):
		# 2014년 6월 9일 개정 시간표 기준
		self.train_type = u"무궁화호"
		self.train_no = 1221
		self.stations = 24

		train_type, stations = korail_split_ticket_checker.get_train_routes(self.date, self.train_no)

		self.assertEqual(self.train_type, train_type, "Failed to get train type")
		self.assertEqual(self.stations, len(stations), "Failed to get station list")


if __name__ == '__main__':
    unittest.main()
