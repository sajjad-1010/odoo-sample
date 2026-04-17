/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { user } from "@web/core/user";

export class Dashboard extends Component {
    static template = "sales_field.Dashboard";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            todayCount: 0, weekCount: 0, totalCount: 0,
            commission: null,
            debtors: null,
        });
        onWillStart(() => this._loadStats());
    }

    get userName() { return user.name; }

    async _loadStats() {
        const uid = user.userId;
        const now = new Date();
        const today = now.toISOString().slice(0, 10) + " 00:00:00";
        const weekAgo = new Date(now - 7 * 86400000).toISOString().slice(0, 10) + " 00:00:00";
        const [t, w, total] = await Promise.all([
            this.orm.searchCount("field.visit", [["salesperson_id", "=", uid], ["timestamp", ">=", today]]),
            this.orm.searchCount("field.visit", [["salesperson_id", "=", uid], ["timestamp", ">=", weekAgo]]),
            this.orm.searchCount("field.visit", [["salesperson_id", "=", uid]]),
        ]);
        Object.assign(this.state, { todayCount: t, weekCount: w, totalCount: total });

        // Load debtors summary
        const debtorsResp = await fetch("/sales_field/debtors_summary", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ jsonrpc: "2.0", method: "call", id: 2, params: {} }),
        });
        const debtorsJson = await debtorsResp.json();
        this.state.debtors = debtorsJson.result || { count: 0, total: 0 };

        // Load commission stats
        const users = await this.orm.read("res.users", [uid], [
            "current_month_sales", "current_month_commission",
            "current_month_target", "target_progress",
            "total_commission_earned", "total_commission_paid", "commission_balance",
        ]);
        // Check if config exists
        const configs = await this.orm.searchCount("sales.commission.config", [
            ["salesperson_id", "=", uid], ["is_active", "=", true]
        ]);
        this.state.commission = { ...users[0], hasConfig: configs > 0 };
    }

    fmt(val) {
        return (val || 0).toLocaleString("en-US", { minimumFractionDigits: 0, maximumFractionDigits: 0 });
    }

    _openForm(visit_type) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "field.visit",
            view_mode: "form",
            views: [[false, "form"]],
            target: "new",
            context: { default_visit_type: visit_type },
        });
    }

    onVisit()       { this._openForm("visit"); }
    onNewCustomer() { this._openForm("new_customer"); }
    onNewInvoice()  { this._openForm("invoice"); }
    onDebtors() { this.action.doAction("sales_field.action_field_customers_debtors"); }
}

registry.category("actions").add("sales_field.Dashboard", Dashboard);
