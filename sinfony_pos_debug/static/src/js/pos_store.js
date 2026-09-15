/** @odoo-module */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";

patch(PosStore.prototype, {
        async setup() {
            await super.setup(...arguments);
            this.data.connectWebSocket("SIMULATE_COMMAND",
                async (payload) => this.simulate_command(payload));

        },
        async log_pos_debug_message(message) {
            await this.data.call(
                "pos.session",
                "log_pos_debug_message",
                [this.session.id, this.user.partner_id.id, message],
                {},
                true
            );
        },
        afterProcessServerData() {
            var self = this;
            return super.afterProcessServerData(...arguments).then(function () {
                    if (self.hardwareProxy.printer) {
                        self.hardwareProxy.printer.debug_printer = self.config.debug_printer;
                    }
            });
        },
        create_printer(config) {
            var printer = super.create_printer(config);
            printer.debug_printer = config.debug_printer;
            return printer;
        },
        _pos_debug_state_key() {
            return `pos_debug_state_${this.config.id}`;
        },
        _get_pos_debug_state() {
            let pos_debug_state, pos_debug_state_item = sessionStorage.getItem(this._pos_debug_state_key());
            if (pos_debug_state_item !== null) {
                try {
                    pos_debug_state = JSON.parse(pos_debug_state_item);
                } catch (error) {
                    this.log_pos_debug_message('JSON.parse() failed, item: ' + pos_debug_state_item.toString())
                    pos_debug_state_item = null;
                }
            }
            if (pos_debug_state_item !== null) {
                if (pos_debug_state.session_id != this.config.current_session_id.id) {
                    // new session, remove old fetch state except activated
                    pos_debug_state.session_id = this.config.current_session_id.id;
                    this._set_pos_debug_state(pos_debug_state);
                }
            } else {
                pos_debug_state = {
                    active: false,
                    session_id: this.config.current_session_id.id,
                };
                this._set_pos_debug_state(pos_debug_state);
            }
            return pos_debug_state;
        },
        _set_pos_debug_state(pos_debug_state) {
            sessionStorage.setItem(this._pos_debug_state_key(), JSON.stringify(pos_debug_state));
        },
        async simulate_command(payload) {
            // commands:
            //     create_ticket: create a ticket on the specified table
            //     add_products: add the given products to the ticket on the given table
            //     print_changes: print kitchen tickets
            //     validate_ticket: add a payment line and validate the ticket
            //     login_number: report own login number so that the backend can determine running POSs
            // filter login_number
            if (!this._get_pos_debug_state().active) {
                return;
            }
            if (payload.pos_session_id != odoo.pos_session_id) {
                return;
            }
            if (payload.command != 'login_number' && payload.login_number != odoo.login_number) {
                return;
            }
            if (payload.command == 'create_ticket') {
                let table = this.models["restaurant.table"].get(payload.table_id);
                let orders = this.getTableOrders(payload.table_id);
                if (orders.length != 0) {
                    alert('there is already a ticket on table ' + table.table_number)
                    return;
                }
                let order = this.createNewOrder({
                        customer_count: payload.customer_count,
                        guests_count_defined: true,
                        table_id: table,
                });
            } else if (payload.command == 'add_products') {
                let orders = this.getTableOrders(payload.table_id);
                if (orders.length != 1) {
                    alert('oops')
                }
                for (let product_id of payload.product_ids) { 
                    let product = this.models["product.product"].get(product_id);
                    await this.addLineToOrder({ product_id: product }, orders[0], {}, false);
                }
            } else if (payload.command == 'print_changes') {
                let table = this.models["restaurant.table"].get(payload.table_id);
                await this.setTableFromUi(table);
                let orders = this.getTableOrders(payload.table_id);
                if (orders.length != 1) {
                    alert('oops')
                }
                await this.sendOrderInPreparation(orders[0]);
            } else if (payload.command == 'delete_tickets') {
                let orders = this.getTableOrders(payload.table_id);
                if (orders && orders.length) {
                    await this.deleteOrders(orders);
                }
            } else if (payload.command == 'validate_ticket') {
                let table = this.models["restaurant.table"].get(payload.table_id);
                let orders = this.getTableOrders(payload.table_id);
                if (orders.length == 0) {
                    alert('no order to validate')
                }
                let order = orders[0];
                await this.setTableFromUi(table, order.uuid);
                let payment_method = this.config.payment_method_ids.find(m => m.name === 'Cash');
                if (!payment_method) {
                    alert('no payment method with name "Cash" found');
                }
                order.add_paymentline(payment_method);
                // validate ticket via patched payment_screen
                await this.pay();
                if (payload.print_receipt) {
                    await this.printReceipt();
                }
            } else if (payload.command == 'goto_screen') {
                let props = {};
                if (payload.screen_name == 'FloorScreen') {
                    let table = this.models["restaurant.table"].get(payload.table_id);
                    props.floor = table ? table.floor_id : null;
                } else if (payload.screen_name == 'ProductScreen') {
                    let table = this.models["restaurant.table"].get(payload.table_id);
                    let orders = this.getTableOrders(payload.table_id);
                    if (orders.length == 0) {
                        alert('no order to validate')
                        return;
                    }
                    let order = orders[0];
                    this.set_order(order);
                } 
                this.showScreen(payload.screen_name, props);
            } else if (payload.command == 'login_number') {
                const response = await this.data.call("pos.config", "register_login_number", [
                    odoo.pos_config_id,
                    odoo.login_number,
                ]);
            }

        },
});
