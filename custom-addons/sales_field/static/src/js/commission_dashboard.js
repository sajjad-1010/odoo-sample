/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class CommissionDashboard extends Component {
    static template = "sales_field.CommissionDashboard";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({ rows: [], loading: true });
        onWillStart(() => this._load());
    }

    async _load() {
        const users = await this.orm.searchRead(
            "res.users",
            [["share", "=", false]],
            ["id", "name", "current_month_sales", "current_month_commission",
             "current_month_target", "target_progress",
             "total_commission_earned", "total_commission_paid", "commission_balance"],
            { limit: 100 }
        );
        this.state.rows = users;
        this.state.loading = false;
    }

    openPaymentForm(userId, userName) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "sales.commission.payment",
            view_mode: "form",
            views: [[false, "form"]],
            target: "new",
            context: { default_salesperson_id: userId },
        });
    }

    fmt(val) {
        return (val || 0).toLocaleString("en-US", { minimumFractionDigits: 0, maximumFractionDigits: 0 });
    }
}

registry.category("actions").add("sales_field.CommissionDashboard", CommissionDashboard);
