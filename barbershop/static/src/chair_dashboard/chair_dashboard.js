/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { formatCurrency } from "@web/core/currency";
import {
    deserializeDateTime,
    formatDateTime,
    serializeDateTime,
    today,
} from "@web/core/l10n/dates";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";

export class BarbershopChairDashboard extends Component {
    static template = "barbershop.ChairDashboard";
    static props = { ...standardActionServiceProps };

    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.state = useState({
            shops: [],
            selectedChairId: null,
            orders: null,
            ordersLoading: false,
        });
        onWillStart(() => this.loadChairs());
    }

    async loadChairs() {
        const chairs = await this.orm.searchRead(
            "barbershop.chair",
            [["active", "=", true]],
            ["name", "shop_id", "barber_id", "is_busy", "active"],
            { order: "shop_id, sequence, name" }
        );
        const shopsMap = new Map();
        for (const chair of chairs) {
            const [shopId, shopName] = chair.shop_id;
            if (!shopsMap.has(shopId)) {
                shopsMap.set(shopId, { id: shopId, name: shopName, chairs: [] });
            }
            shopsMap.get(shopId).chairs.push(chair);
        }
        this.state.shops = [...shopsMap.values()];
        if (this.state.selectedChairId === null && chairs.length) {
            await this.selectChair(chairs[0].id);
        }
    }

    get stateLabels() {
        return { draft: _t("Draft"), paid: _t("Paid"), cancelled: _t("Cancelled") };
    }

    get selectedChair() {
        for (const shop of this.state.shops) {
            const chair = shop.chairs.find((c) => c.id === this.state.selectedChairId);
            if (chair) {
                return { ...chair, shopName: shop.name };
            }
        }
        return null;
    }

    async selectChair(chairId) {
        this.state.selectedChairId = chairId;
        await this.loadOrders();
    }

    async loadOrders() {
        if (!this.state.selectedChairId) {
            this.state.orders = null;
            return;
        }
        this.state.ordersLoading = true;
        const start = today();
        const end = start.plus({ days: 1 });
        const orders = await this.orm.searchRead(
            "barbershop.order",
            [
                ["chair_id", "=", this.state.selectedChairId],
                ["date_order", ">=", serializeDateTime(start)],
                ["date_order", "<", serializeDateTime(end)],
            ],
            [
                "name",
                "partner_id",
                "barber_id",
                "payment_method_id",
                "amount_total",
                "tip_amount",
                "currency_id",
                "state",
                "date_order",
            ],
            { order: "date_order desc" }
        );
        this.state.orders = orders.map((order) => ({
            ...order,
            timeLabel: formatDateTime(deserializeDateTime(order.date_order), { format: "HH:mm" }),
            amountLabel: formatCurrency(order.amount_total, order.currency_id && order.currency_id[0]),
            tipLabel: formatCurrency(order.tip_amount, order.currency_id && order.currency_id[0]),
        }));
        this.state.ordersLoading = false;
    }

    editChair(chairId) {
        this.actionService.doAction(
            {
                type: "ir.actions.act_window",
                res_model: "barbershop.chair",
                view_mode: "form",
                views: [[false, "form"]],
                res_id: chairId,
                target: "new",
            },
            { onClose: () => this.loadChairs() }
        );
    }

    async createOrder(chairId) {
        const action = await this.orm.call("barbershop.chair", "action_create_order", [chairId]);
        this.actionService.doAction(
            { ...action, target: "new" },
            { onClose: () => this.loadOrders() }
        );
    }

    openOrder(orderId) {
        this.actionService.doAction(
            {
                type: "ir.actions.act_window",
                res_model: "barbershop.order",
                view_mode: "form",
                views: [[false, "form"]],
                res_id: orderId,
                target: "new",
            },
            { onClose: () => this.loadOrders() }
        );
    }
}

registry.category("actions").add("barbershop_chair_dashboard", BarbershopChairDashboard);
