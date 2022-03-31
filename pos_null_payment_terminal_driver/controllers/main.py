from odoo.addons.hw_proxy.controllers import main as hw_proxy
from threading import Thread, Lock
import time
from odoo import http


class NullPaymentTerminalDriver(Thread):
    def __init__(self):
        self.status = {
            'transactions': {}
        }
        self.lock = Lock()

    def add_transaction(self, payment_info):
        if 'line_id' in payment_info:
            transaction_id = payment_info['line_id']
        else:
            transaction_id = payment_info['payment_id']

        with self.lock:
            self.status['transactions'][transaction_id] = {
                'transaction_id': transaction_id,
                'success': True,
                'status': 'Transaction Approved',
                'status_details': '',
                'reference': ''
            }

    def get_status(self):
        with self.lock:
            return self.status

    def run(self):
        while True:
            time.sleep(1.0)


driver = NullPaymentTerminalDriver()

hw_proxy.drivers['chess_pt_payment_terminal'] = driver


class NullPaymentTerminalProxy(hw_proxy.Proxy):
    @http.route(
        '/hw_proxy/payment_terminal_transaction_start',
        type='json', auth='none', cors='*')
    def payment_terminal_transaction_start(self, payment_info):
        _logger.debug(
            'ChessPt: Call pos_null_payment_terminal_driver with '
            'payment_info=%s', payment_info)
        payment_info = simplejson.loads(payment_info)
        driver.add_transaction(payment_info)

        return {
            'transaction_id': transaction_id,
            'status': 'In Progress'
        }
