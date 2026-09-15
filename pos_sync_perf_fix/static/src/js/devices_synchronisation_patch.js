/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { debounce } from "@web/core/utils/timing";
import DevicesSynchronisation from "@point_of_sale/app/store/devices_synchronisation";

patch(DevicesSynchronisation.prototype, {
    setup(dynamicModels, staticModels, posStore) {
        super.setup(dynamicModels, staticModels, posStore);
        // Coalesce bursts of SYNCHRONISATION messages received in the same
        // 500ms window into a single read_config_open_orders RPC instead of
        // one RPC per message.
        this._debouncedReadDataFromServer = debounce(super.readDataFromServer.bind(this), 500);
    },
    async readDataFromServer() {
        return this._debouncedReadDataFromServer();
    },
});
