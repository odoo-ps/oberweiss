import { Component, onMounted, useState } from "@odoo/owl";
import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { rpc } from "@web/core/network/rpc";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { WarningDialog } from "@web/core/errors/error_dialogs";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
 
export class PosDebugButton extends Component {
    static template = 'PosDebugButton';
    static props = {};


    setup() {
        super.setup();
        this.pos = usePos();
        this.orm = useService("orm");
        this.popupService = useService("dialog");
        this.state = useState({
            status: this.pos._get_pos_debug_state().active ? 'running' : 'stopped',
        });
        onMounted(() => this._onMounted());
    }
    _onMounted() {
        //this.setup_PosDebug();
    }
    setup_PosDebug() {
        //PosDebug.setComponent(this);
    }
    get message() {
        return {
            running: _t('Running'),
            fetching: _t('Fetching'),
            warning: _t('Connected, Not Owned'),
            failure: _t('Disconnected'),
            stopped: _t('Stopped'),
            not_found: _t('Customer Screen Unsupported. Please upgrade the IoT Box'),
        }[this.state.status];
    }
    async onClick() {
        // This approaches uses a Promise pattern directly with dialog service, similar to event_track_form_view.js
        if (this.state.status == 'running') {
            this.state.status = 'stopped';
        } else if (this.state.status == 'stopped') {
            this.state.status = 'running';
        }
        let pos_debug_state = this.pos._get_pos_debug_state();
        pos_debug_state.active = this.state.status === 'running';
        this.pos._set_pos_debug_state(pos_debug_state);
        this.pos.log_pos_debug_message('state: ' + this.state.status)
    }
    async printPosOrderFromPopup(pos_order) {
        await this.pos.sendOrderInPreparationUpdateLastChange(pos_order);
        await this.pos.printBill(pos_order);
        await this.pos.syncAllOrders();
    }
    async printPosOrder(pos_order) {
        if (pos_order.hasChangesToPrint()) {
            const isPrintSuccessful = await pos_order.printChanges();
            if (isPrintSuccessful) {
                pos_order.updatePrintedResume();
            } else {
                this.popupService.add({
                    title: _t('Printing failed'),
                    body: _t('Failed in printing the changes in the order'),
                });
            }
        }

        await this.popupService.add("AutoPrintBillScreen", {
            order: pos_order,
        });
    }

}
