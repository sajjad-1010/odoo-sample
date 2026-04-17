/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class CustomerBalanceDialog extends Component {
    static template = "sales_field.CustomerBalanceDialog";

    setup() {
        this.action = useService("action");
        this.state = useState({ data: null, loading: true, error: null });
        this.partnerId = this.props.action?.context?.partner_id || null;
        onWillStart(() => this._load());
    }

    async _load() {
        if (!this.partnerId) {
            this.state.error = "No customer selected.";
            this.state.loading = false;
            return;
        }
        const response = await fetch("/sales_field/customer_balance", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                jsonrpc: "2.0", method: "call", id: 1,
                params: { partner_id: this.partnerId },
            }),
        });
        const json = await response.json();
        if (json.result?.error) {
            this.state.error = json.result.error;
        } else {
            this.state.data = json.result || null;
        }
        this.state.loading = false;
    }

    fmt(val) {
        return (val || 0).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }

    close() {
        this.action.doAction({ type: "ir.actions.act_window_close" });
    }
}

registry.category("actions").add("sales_field.CustomerBalanceDialog", CustomerBalanceDialog);
