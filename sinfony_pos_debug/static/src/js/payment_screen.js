import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";

patch(PaymentScreen.prototype, {
    async onMounted() {
        await super.onMounted();
        if (!this.pos._get_pos_debug_state().active) {
            return;
        }
        const order = this.pos.get_order();
        if (order) {
            // Check if the order is fully paid or can be validated natively
            if (this.check_cash_rounding_has_been_well_applied()) { 
                console.log("Conditions met. Auto-validating current POS order...");
                // Directly invokes the native validation mechanism on the screen instance
                await this.validateOrder(false); 
            } else {
                console.warn("Auto-validation skipped: Order is not fully paid yet.");
            }
        }
    },
});
