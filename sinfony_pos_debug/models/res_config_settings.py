# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_debug_printer = fields.Boolean(compute='_compute_pos_debug_printer', store=True, readonly=False)

    @api.depends('pos_other_devices', 'pos_config_id')
    def _compute_pos_debug_printer(self):
        for res_config in self:
            if not res_config.pos_other_devices:
                res_config.pos_debug_printer = False
            else:
                res_config.pos_debug_printer = res_config.pos_config_id.debug_printer
