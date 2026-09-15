/* @odoo-module */

import { BasePrinter } from "@point_of_sale/app/printer/base_printer";
import { patch } from "@web/core/utils/patch";

patch(BasePrinter.prototype, {
        async printReceipt(receipt) {
            var debug_printer;
            var printer_name;
            if (this.config) {
                debug_printer = this.config.debug_printer;
                printer_name = this.config.name;
            } else {
                // 
                debug_printer = this.debug_printer;
                printer_name = 'Ticket';
            }
            if (!debug_printer) {
                return super.printReceipt(receipt);
            }
            var w = window.open('', printer_name,
                'toolbar=no,location=no,directories=no,status=no,menubar=no,' +
                'scrollbars=yes,resizable=yes,width=400,height=1000');
            w.document.body.innerHTML = receipt.outerHTML;
            return {
                successful: true,
            };
        }
});
