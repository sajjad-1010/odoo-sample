/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

const ODOO_PURPLE = "#875A7B";

export class WarehouseMinimap extends Component {
    static template = "my_inventory.WarehouseMinimap";
    static components = {};

    _hideTimer = null;

    setup() {
        this.rpc = useService("rpc");
        this.state = useState({
            locations: [],      // fallback: raw locations from /data
            zoneConfigs: [],    // primary: structured zones from /zones
            searchQuery: "",
            tooltip: null,
        });
        onWillStart(async () => {
            const [data, zones] = await Promise.all([
                this.rpc("/warehouse_minimap/data", {}),
                this.rpc("/warehouse_minimap/zones", {}),
            ]);
            this.state.locations = data;
            this.state.zoneConfigs = zones;
        });
    }

    // ── Mode detection ───────────────────────────────────────────────────────
    get useZoneConfig() {
        return this.state.zoneConfigs.length > 0;
    }

    // ── All visible shelf/location objects (for stats & maxQty) ─────────────
    get allItems() {
        const configItems = this.state.zoneConfigs.flatMap(z => z.rows.flatMap(r => r.shelves));
        return [...configItems, ...this.legacyLocations];
    }

    // ── Locations NOT managed by any zone config (old x_pos/y_pos style) ─────
    get legacyLocations() {
        return this.state.locations.filter(l => !l.zone_config_id);
    }

    // ── Zone tree for legacy locations ───────────────────────────────────────
    get legacyZoneTree() {
        return this._buildZoneTree(this.legacyLocations);
    }

    // ── Zone tree (pure fallback — no zone configs at all) ───────────────────
    get zoneTree() {
        return this._buildZoneTree(this.state.locations);
    }

    _buildZoneTree(locs) {
        if (!locs.length) return [];
        const byDepth = {};
        for (const loc of locs) {
            const d = loc.name.split("/").length;
            (byDepth[d] = byDepth[d] || []).push(loc);
        }
        const depths = Object.keys(byDepth).map(Number).sort();
        if (depths.length < 2) {
            return (byDepth[depths[0]] || [])
                .sort((a, b) => a.x - b.x)
                .map(zone => ({ zone, rows: [] }));
        }
        const zoneDepth = depths[depths.length - 2];
        const rowDepth  = depths[depths.length - 1];
        const zones = (byDepth[zoneDepth] || []).sort((a, b) => a.x - b.x);
        const rows  = (byDepth[rowDepth]  || []);
        return zones.map(zone => ({
            zone,
            rows: rows
                .filter(r => r.name.startsWith(zone.name + "/"))
                .sort((a, b) => a.x - b.x),
        }));
    }

    // ── Stats include both zone config and legacy ────────────────────────────
    get stats() {
        const locs = this.allItems;
        return {
            total:   locs.length,
            stocked: locs.filter(l => l.products.length > 0).length,
            empty:   locs.filter(l => l.products.length === 0).length,
        };
    }

    // ── Max qty across all items (used for fill % in fallback mode) ──────────
    get maxQty() {
        const max = Math.max(...this.allItems.map(l => this.totalQty(l)));
        return max > 0 ? max : 1;
    }

    // ── Fill level: empty / low / mid / high ─────────────────────────────────
    fillLevel(loc) {
        const qty = this.totalQty(loc);
        if (qty === 0) return "empty";
        const cap = loc.capacity || this.maxQty;
        const pct = qty / cap;
        if (pct < 0.33) return "low";
        if (pct < 0.66) return "mid";
        return "high";
    }

    fillPercent(loc) {
        const cap = loc.capacity || this.maxQty;
        return Math.min(100, Math.round((this.totalQty(loc) / cap) * 100));
    }

    // ── Cell CSS class ───────────────────────────────────────────────────────
    cellClass(loc) {
        const q = this.state.searchQuery.trim().toLowerCase();
        if (q && loc.products.some(p => p.product_name.toLowerCase().includes(q)))
            return "o_mm_cell o_mm_search_match";
        return `o_mm_cell o_mm_${this.fillLevel(loc)}`;
    }

    // ── Badge CSS class ──────────────────────────────────────────────────────
    badgeClass(loc) {
        const level = this.fillLevel(loc);
        if (level === "empty") return "o_mm_badge";
        if (this.cellClass(loc).includes("search_match")) return "o_mm_badge o_mm_badge_match";
        return `o_mm_badge o_mm_badge_${level}`;
    }

    // ── Translated getters ───────────────────────────────────────────────────
    get searchPlaceholder() { return _t("Search product..."); }

    // ── Zone config helpers ──────────────────────────────────────────────────
    zoneStocked(zone) {
        return zone.rows.flatMap(r => r.shelves).filter(s => s.products.length > 0).length;
    }

    zoneTotalShelves(zone) {
        return zone.rows.flatMap(r => r.shelves).length;
    }

    zoneMeta(zone) {
        const stocked = this.zoneStocked(zone);
        const total   = this.zoneTotalShelves(zone);
        return `${zone.num_rows} ${_t("rows")} × ${zone.num_shelves} ${_t("shelves")} · ${stocked}/${total} ${_t("stocked")}`;
    }

    tooltipTotal(loc) {
        if (!loc.products.length) return _t("Empty");
        const qty = this.totalQty(loc);
        const n   = loc.products.length;
        return `${qty} ${_t("units")} · ${n} ${n === 1 ? _t("product") : _t("products")}`;
    }

    // ── Helpers ──────────────────────────────────────────────────────────────
    totalQty(loc) {
        return loc.products.reduce((s, p) => s + p.quantity, 0);
    }

    shortName(full) { return full.split("/").pop().trim(); }

    formatPath(full) { return full.split("/").join(" › "); }

    zoneColor() { return ODOO_PURPLE; }

    // ── Search highlight ─────────────────────────────────────────────────────
    highlightParts(text) {
        const q = this.state.searchQuery.trim().toLowerCase();
        if (!q) return [{ text, match: false }];
        const idx = text.toLowerCase().indexOf(q);
        if (idx === -1) return [{ text, match: false }];
        return [
            { text: text.slice(0, idx),              match: false },
            { text: text.slice(idx, idx + q.length), match: true  },
            { text: text.slice(idx + q.length),      match: false },
        ];
    }

    isProductMatch(name) {
        const q = this.state.searchQuery.trim().toLowerCase();
        return q && name.toLowerCase().includes(q);
    }

    // ── Tooltip: show / move / hide with 80ms delay ──────────────────────────
    _tooltipPos(clientX, clientY) {
        const TW = 310, TH = 200;
        const x = clientX + TW + 12 > window.innerWidth  ? clientX - TW - 4 : clientX + 12;
        const y = clientY + TH + 12 > window.innerHeight ? clientY - TH - 4 : clientY + 12;
        return { screenX: x, screenY: y };
    }

    showTooltip(loc, ev) {
        if (this._hideTimer) { clearTimeout(this._hideTimer); this._hideTimer = null; }
        this.state.tooltip = { ...this._tooltipPos(ev.clientX, ev.clientY), location: loc };
    }

    moveTooltip(ev) {
        if (!this.state.tooltip) return;
        const pos = this._tooltipPos(ev.clientX, ev.clientY);
        this.state.tooltip.screenX = pos.screenX;
        this.state.tooltip.screenY = pos.screenY;
    }

    hideTooltip() {
        if (this._hideTimer) return;
        this._hideTimer = setTimeout(() => {
            this.state.tooltip = null;
            this._hideTimer = null;
        }, 80);
    }

    // ── Search ───────────────────────────────────────────────────────────────
    onSearchInput(ev) { this.state.searchQuery = ev.target.value; }
}

registry.category("actions").add("warehouse_minimap", WarehouseMinimap);
