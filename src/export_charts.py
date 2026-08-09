"""Generate static PNG exports of all dashboard charts for README."""
import sys
sys.path.insert(0, '.')
from charts import (
    get_price_distribution_chart, get_room_type_pie_chart, get_map,
    get_occupancy_chart, get_revenue_boxplot, get_demand_supply_chart,
    get_host_concentration_chart, get_pricing_position_chart,
    get_rating_price_matrix, get_revenue_treemap,
    get_minimum_nights_chart, get_license_compliance_chart,
    get_occupancy_timeline,
)

ASSETS = "../assets"

def export_all():
    # Tab 1 — Market Overview
    get_price_distribution_chart([0, 250]).write_image(
        f"{ASSETS}/chart-price-histogram.png", width=900, height=400, scale=2)
    get_room_type_pie_chart(None).write_image(
        f"{ASSETS}/chart-room-type-pie.png", width=700, height=400, scale=2)
    get_map(None).write_image(
        f"{ASSETS}/chart-map.png", width=1000, height=600, scale=2)

    # Tab 2 — Business Intelligence
    get_occupancy_chart(None).write_image(
        f"{ASSETS}/bi-occupancy.png", width=900, height=500, scale=2)
    get_revenue_boxplot(None).write_image(
        f"{ASSETS}/bi-revenue-box.png", width=800, height=450, scale=2)
    get_demand_supply_chart().write_image(
        f"{ASSETS}/bi-demand-supply.png", width=900, height=550, scale=2)
    get_host_concentration_chart(None).write_image(
        f"{ASSETS}/bi-host-concentration.png", width=700, height=450, scale=2)
    get_pricing_position_chart().write_image(
        f"{ASSETS}/bi-pricing-position.png", width=900, height=500, scale=2)
    get_rating_price_matrix().write_image(
        f"{ASSETS}/bi-value-matrix.png", width=800, height=500, scale=2)
    get_revenue_treemap(None).write_image(
        f"{ASSETS}/bi-revenue-treemap.png", width=900, height=550, scale=2)

    # Tab 3 — Policy & Compliance
    get_minimum_nights_chart(None).write_image(
        f"{ASSETS}/policy-min-nights.png", width=800, height=450, scale=2)
    get_license_compliance_chart().write_image(
        f"{ASSETS}/policy-license.png", width=900, height=500, scale=2)
    get_occupancy_timeline().write_image(
        f"{ASSETS}/policy-occupancy-timeline.png", width=900, height=500, scale=2)

    print("✅ All 14 charts exported to assets/")

if __name__ == "__main__":
    export_all()
