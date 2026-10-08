/** @odoo-module **/

import { Component, onWillStart, useEffect, useRef, useState } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { loadBundle } from "@web/core/assets";
import { getColor } from "@web/core/colors/colors";
import { cookie } from "@web/core/browser/cookie";
import { formatCurrency } from "@web/core/currency";
import { parseDate, serializeDate, serializeDateTime, today } from "@web/core/l10n/dates";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";

export class BarbershopOrderDashboard extends Component {
    static template = "barbershop.OrderDashboard";
    static props = { ...standardActionServiceProps };

    setup() {
        this.orm = useService("orm");
        this.canvasRef = useRef("chartCanvas");
        this.timeCanvasRef = useRef("timeChartCanvas");
        this.chart = null;
        this.timeChart = null;

        this.state = useState({
            dateFrom: serializeDate(today().startOf("month")),
            dateTo: serializeDate(today()),
            activePreset: "month",
            loading: true,
            kpi: {
                order_count: 0,
                customer_count: 0,
                amount_total: 0,
                shop_amount: 0,
                barber_amount: 0,
                tip_amount: 0,
            },
            byChair: [],
            timeseries: [],
            granularity: "week",
            currencyId: false,
        });

        onWillStart(async () => {
            await loadBundle("web.chartjs_lib");
            await this.loadStats();
        });

        useEffect(
            () => {
                this.renderChart();
                return () => {
                    if (this.chart) {
                        this.chart.destroy();
                        this.chart = null;
                    }
                };
            },
            () => [this.state.byChair]
        );

        useEffect(
            () => {
                this.renderTimeChart();
                return () => {
                    if (this.timeChart) {
                        this.timeChart.destroy();
                        this.timeChart = null;
                    }
                };
            },
            () => [this.state.timeseries]
        );
    }

    setPreset(preset) {
        const t = today();
        let start = t;
        if (preset === "week") {
            start = t.startOf("week");
        } else if (preset === "month") {
            start = t.startOf("month");
        } else if (preset === "year") {
            start = t.startOf("year");
        }
        this.state.activePreset = preset;
        this.state.dateFrom = serializeDate(start);
        this.state.dateTo = serializeDate(t);
        this.loadStats();
    }

    onDateFromChange(ev) {
        this.state.activePreset = false;
        this.state.dateFrom = ev.target.value;
        this.loadStats();
    }

    onDateToChange(ev) {
        this.state.activePreset = false;
        this.state.dateTo = ev.target.value;
        this.loadStats();
    }

    async loadStats() {
        this.state.loading = true;
        const startLocal = parseDate(this.state.dateFrom).startOf("day");
        const endLocal = parseDate(this.state.dateTo).plus({ days: 1 }).startOf("day");
        const result = await this.orm.call("barbershop.order", "get_dashboard_data", [], {
            date_from: serializeDateTime(startLocal),
            date_to: serializeDateTime(endLocal),
        });
        this.state.currencyId = result.currency_id;
        this.state.kpi = result.kpi;
        this.state.byChair = result.by_chair.map((row) => ({
            ...row,
            amountLabel: formatCurrency(row.amount_total, result.currency_id),
            shopLabel: formatCurrency(row.shop_amount, result.currency_id),
            barberLabel: formatCurrency(row.barber_amount, result.currency_id),
            tipLabel: formatCurrency(row.tip_amount, result.currency_id),
            avgLabel: formatCurrency(
                row.order_count ? row.amount_total / row.order_count : 0,
                result.currency_id
            ),
        }));
        this.state.timeseries = result.timeseries;
        this.state.granularity = result.granularity;
        this.state.loading = false;
    }

    get granularityLabel() {
        return this.state.granularity === "month" ? _t("By month") : _t("By week");
    }

    get amountTotalLabel() {
        return formatCurrency(this.state.kpi.amount_total, this.state.currencyId);
    }

    get shopAmountLabel() {
        return formatCurrency(this.state.kpi.shop_amount, this.state.currencyId);
    }

    get barberAmountLabel() {
        return formatCurrency(this.state.kpi.barber_amount, this.state.currencyId);
    }

    get tipAmountLabel() {
        return formatCurrency(this.state.kpi.tip_amount, this.state.currencyId);
    }

    renderTimeChart() {
        if (this.timeChart) {
            this.timeChart.destroy();
            this.timeChart = null;
        }
        if (!this.timeCanvasRef.el || !this.state.timeseries.length) {
            return;
        }
        const colorScheme = cookie.get("color_scheme");
        const rows = this.state.timeseries;
        const ordersColor = getColor(0, colorScheme, "odoo");
        const amountColor = getColor(1, colorScheme, "odoo");
        this.timeChart = new Chart(this.timeCanvasRef.el, {
            data: {
                labels: rows.map((r) => r.label),
                datasets: [
                    {
                        type: "bar",
                        label: _t("Orders"),
                        data: rows.map((r) => r.order_count),
                        backgroundColor: ordersColor,
                        borderRadius: 4,
                        yAxisID: "y",
                        order: 2,
                    },
                    {
                        type: "line",
                        label: _t("Amount"),
                        data: rows.map((r) => r.amount_total),
                        borderColor: amountColor,
                        backgroundColor: amountColor,
                        tension: 0.3,
                        yAxisID: "y1",
                        order: 1,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: "index", intersect: false },
                scales: {
                    y: {
                        beginAtZero: true,
                        position: "left",
                        title: { display: true, text: _t("Orders") },
                        ticks: { precision: 0 },
                    },
                    y1: {
                        beginAtZero: true,
                        position: "right",
                        title: { display: true, text: _t("Amount") },
                        grid: { drawOnChartArea: false },
                    },
                },
            },
        });
    }

    renderChart() {
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
        if (!this.canvasRef.el || !this.state.byChair.length) {
            return;
        }
        const colorScheme = cookie.get("color_scheme");
        const rows = this.state.byChair.slice(0, 10);
        this.chart = new Chart(this.canvasRef.el, {
            type: "bar",
            data: {
                labels: rows.map((r) => r.chair_name),
                datasets: [
                    {
                        label: _t("Total"),
                        data: rows.map((r) => r.amount_total),
                        backgroundColor: rows.map((row, i) => getColor(i, colorScheme, "odoo")),
                        borderRadius: 4,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { y: { beginAtZero: true } },
            },
        });
    }
}

registry.category("actions").add("barbershop_order_dashboard", BarbershopOrderDashboard);
