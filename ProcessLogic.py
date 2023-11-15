from PickleSerializer import PickleSerializer
from TenbisLogic import Tenbis
from Processor import *


class ProcessLogic(Processor):
    def __init__(self, args, next_processors=None):
        super().__init__(next_processors)
        self.ten_bis = Tenbis(args)

    @staticmethod
    def compare_coupons_files(c1, c2):
        if len(c1) != len(c2) or c1.keys() != c2.keys():
            return False

        for k in c1.keys():
            l1 = c1[k]['orders']
            l2 = c2[k]['orders']

            if len(l2) != len(l1):
                return False

            coupons_list1 = sorted([item['barcode'] for item in l1])
            coupons_list2 = sorted([item['barcode'] for item in l1])
            if coupons_list1 != coupons_list2:
                return False

        return True

    def process_impl(self, data):
        send_report = False
        budget_available = self.ten_bis.is_budget_available()
        print('Budget available=', budget_available)
        if budget_available:
            self.ten_bis.buy_coupon(40)
            send_report = True
        coupons = self.ten_bis.get_unused_coupons()
        coupons_pickle = PickleSerializer('coupons')
        if coupons_pickle.exists():
            prev_coupons = coupons_pickle.load()
            send_report = send_report or not self.compare_coupons_files(prev_coupons, coupons)
        else:
            send_report = True
        coupons_pickle.create(coupons)
        if not send_report:
            print('No report changes, publish will be skipped')
            return {}
        return coupons.values()
