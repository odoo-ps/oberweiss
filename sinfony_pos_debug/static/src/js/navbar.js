/** @odoo-module **/

import { Navbar } from "@point_of_sale/app/navbar/navbar";
import { PosDebugButton } from "@sinfony_pos_debug/js/pos_debug_button";
import { patch } from "@web/core/utils/patch";

// Add SaleOrderFetchButton to Navbar's components
Navbar.components = {
    ...Navbar.components,
    PosDebugButton,
};
