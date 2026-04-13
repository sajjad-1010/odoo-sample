/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class GpsCapture extends Component {
    static template = "sales_field.GpsCapture";
    static props = { record: Object };

    setup() {
        const lat = this.props.record.data.latitude;
        const lng = this.props.record.data.longitude;
        this.state = useState({
            loading: false,
            captured: !!(lat || lng),
            message: lat ? `Lat: ${lat.toFixed(6)}, Lng: ${lng.toFixed(6)}` : "",
            msgType: "success",
        });
    }

    captureGPS() {
        if (!navigator.geolocation) {
            this.state.message = "Geolocation not supported by this browser.";
            this.state.msgType = "error";
            return;
        }
        this.state.loading = true;
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                const lat = pos.coords.latitude;
                const lng = pos.coords.longitude;
                this.props.record.update({ latitude: lat, longitude: lng });
                this.state.loading = false;
                this.state.captured = true;
                this.state.message = `Lat: ${lat.toFixed(6)}, Lng: ${lng.toFixed(6)}`;
                this.state.msgType = "success";
            },
            (err) => {
                this.state.loading = false;
                this.state.message = `Error: ${err.message}`;
                this.state.msgType = "error";
            },
            { enableHighAccuracy: true, timeout: 10000 }
        );
    }
}

registry.category("view_widgets").add("gps_capture", { component: GpsCapture });
