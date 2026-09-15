/* @odoo-module */

import { PosPrinterService } from "@point_of_sale/app/printer/pos_printer_service";
import { patch } from "@web/core/utils/patch";

patch(PosPrinterService.prototype, {
    async printHtml(el, { webPrintFallback = false } = {}) {
        if (this.hardware_proxy.printer.debug_printer) {
            return this.printWeb(el);
        }
        return await super.printHtml(...arguments);
    }
});
