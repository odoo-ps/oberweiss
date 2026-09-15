# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class PosConfig(models.Model):
    _inherit = 'pos.config'

    debug_printer = fields.Boolean(string='Debug Printer', help="Debug Printer in Popup Window.")
    active_session_login_numbers = fields.Char(string='Login numbers of open session')

    def register_login_number(self, login_number):
        if self.active_session_login_numbers:
            login_numbers = self.active_session_login_numbers.split(', ')
        else:
            login_numbers = []
        if login_number not in login_numbers:
            login_numbers.append(login_number)
        self.active_session_login_numbers = ', '.join(login_numbers)

