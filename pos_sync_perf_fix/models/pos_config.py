from odoo import models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    def read_config_open_orders(self, domain, record_ids=[]):
        """Same as core, except pos.order (and any other key already produced
        by read_pos_data()) is not read a second time with the exact same
        recordset and the exact same fields.
        """
        delete_record_ids = {}
        dynamic_records = {}

        for model, dom in domain.items():
            ids = record_ids.get(model, [])
            browsed = self.env[model].browse(ids)

            dynamic_records[model] = self.env[model].search(dom)
            delete_record_ids[model] = browsed.filtered(lambda r: not r.exists()).ids
            if model == "pos.order":
                delete_record_ids[model] += browsed.exists().filtered(lambda r: r.state == "cancel").ids

        pos_order_data = dynamic_records.get('pos.order') or self.env['pos.order']
        data = pos_order_data.read_pos_data([], self.id)

        for key, records in dynamic_records.items():
            if key in data:
                # read_pos_data() already produced this exact read() for this
                # exact recordset/fields: reuse it instead of reading twice.
                dynamic_records[key] = data[key]
                continue
            fields = self.env[key]._load_pos_data_fields(self.id)
            dynamic_records[key] = self.env[key].browse(records.ids).read(fields, load=False)

        for key, value in data.items():
            if key not in dynamic_records:
                dynamic_records[key] = value

        return {
            'dynamic_records': dynamic_records,
            'deleted_record_ids': delete_record_ids,
        }
