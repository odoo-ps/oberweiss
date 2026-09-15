from odoo import models

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_pos_printer(self):
        result = super()._loader_params_pos_printer()
        result['search_params']['fields'].append('debug_printer')
        return result

    def log_pos_debug_message(self, partner_id, message):
        self.message_post(body=f'POS {self.config_id.name}, Session {self.id}: {message}', author_id=partner_id)
