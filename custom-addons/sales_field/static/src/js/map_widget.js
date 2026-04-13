/** @odoo-module **/

import { Component, useState, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

const COLORS = { visit: "#667eea", new_customer: "#11998e", invoice: "#f7971e" };

function loadLeaflet() {
    return new Promise((resolve) => {
        if (window.L) return resolve();
        const link = document.createElement("link");
        link.rel = "stylesheet";
        link.href = "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css";
        document.head.appendChild(link);
        const script = document.createElement("script");
        script.src = "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js";
        script.onload = resolve;
        document.head.appendChild(script);
    });
}

function makeIcon(types) {
    const hasNew = types.includes('new_customer');
    const hasInvoice = types.includes('invoice');
    let rings = '';
    let pad = 0;
    if (hasNew && hasInvoice) {
        rings = `0 0 0 4px #11998e, 0 0 0 8px #f7971e`;
        pad = 8;
    } else if (hasNew) {
        rings = `0 0 0 4px #11998e`;
        pad = 4;
    } else if (hasInvoice) {
        rings = `0 0 0 4px #f7971e`;
        pad = 4;
    }
    const shadow = rings ? `${rings}, 0 2px 6px rgba(0,0,0,.3)` : `0 2px 6px rgba(0,0,0,.3)`;
    const total = 14 + pad * 2;
    return window.L.divIcon({
        className: "",
        html: `<div style="width:14px;height:14px;border-radius:50%;background:#667eea;border:2px solid #fff;box-shadow:${shadow};margin:${pad}px;"></div>`,
        iconSize: [total, total], iconAnchor: [total / 2, total / 2],
    });
}

export class MapView extends Component {
    static template = "sales_field.MapView";

    setup() {
        this.orm = useService("orm");
        this.state = useState({ visits: [], salespeople: [], salespersonId: null, dateFrom: "", dateTo: "" });
        this._map = null;
        this._markers = [];

        onMounted(async () => {
            await loadLeaflet();
            this._map = window.L.map("sf_map", {
                minZoom: 5,
                maxBounds: [[36.5, 67.5], [41.0, 75.5]],
                maxBoundsViscosity: 1.0,
            }).setView([38.8, 71.3], 7);
            window.L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
                attribution: "© OpenStreetMap contributors", maxZoom: 19,
            }).addTo(this._map);
            const sps = await this.orm.searchRead("res.users", [["share", "=", false]], ["id", "name"], { limit: 100 });
            this.state.salespeople = sps;
            await this.loadVisits();
        });

        onWillUnmount(() => { if (this._map) { this._map.remove(); this._map = null; } });
    }

    async loadVisits() {
        const response = await fetch("/sales_field/visits", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                jsonrpc: "2.0", method: "call", id: 1,
                params: {
                    salesperson_id: this.state.salespersonId || null,
                    date_from: this.state.dateFrom || null,
                    date_to: this.state.dateTo || null,
                },
            }),
        });
        const json = await response.json();
        const visits = json.result || [];
        this.state.visits = visits;
        this._markers.forEach(m => m.remove());
        this._markers = [];
        const bounds = [];

        // Group visits by location
        const locMap = {};
        for (const v of visits) {
            if (!v.latitude && !v.longitude) continue;
            const key = `${v.latitude},${v.longitude}`;
            if (!locMap[key]) locMap[key] = { lat: v.latitude, lng: v.longitude, items: [] };
            locMap[key].items.push(v);
        }

        for (const loc of Object.values(locMap)) {
            const types = [...new Set(loc.items.map(v => v.visit_type))];
            const m = window.L.marker([loc.lat, loc.lng], { icon: makeIcon(types) });
            const rows = loc.items.map(v => {
                const color = COLORS[v.visit_type] || "#888";
                return `<div style="padding:4px 0;border-bottom:1px solid #eee;">
                    <strong>${v.salesperson}</strong>
                    <span style="float:right;background:${color};color:#fff;border-radius:4px;padding:1px 6px;font-size:11px;">${v.visit_type}</span><br/>
                    <span style="color:#999;font-size:11px;">${v.timestamp}</span><br/>
                    👤 ${v.customer || "—"}
                    ${v.notes ? `<br/><span style="color:#555;font-size:12px;">${v.notes}</span>` : ""}
                </div>`;
            }).join("");
            m.bindPopup(`<div style="font-size:13px;min-width:180px;max-height:240px;overflow-y:auto;">${rows}</div>`);
            m.addTo(this._map);
            this._markers.push(m);
            bounds.push([loc.lat, loc.lng]);
        }

        if (bounds.length) this._map.fitBounds(bounds, { padding: [40, 40] });
    }

    onSalesperson(ev) { this.state.salespersonId = ev.target.value ? parseInt(ev.target.value) : null; }
    onDateFrom(ev)    { this.state.dateFrom = ev.target.value; }
    onDateTo(ev)      { this.state.dateTo = ev.target.value; }
}

registry.category("actions").add("sales_field.MapView", MapView);
