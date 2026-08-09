"""Generate static PNG exports of all dashboard charts for README."""
import sys
sys.path.insert(0, '.')
from charts import get_price_distribution_chart, get_room_type_pie_chart, get_map

ASSETS = "../assets"

def export_all():
    # Price histogram
    fig1 = get_price_distribution_chart([0, 250])
    fig1.write_image(f"{ASSETS}/chart-price-histogram.png", width=900, height=400, scale=2)

    # Room type pie
    fig2 = get_room_type_pie_chart(None)
    fig2.write_image(f"{ASSETS}/chart-room-type-pie.png", width=700, height=400, scale=2)

    # Map
    fig3 = get_map(None)
    fig3.write_image(f"{ASSETS}/chart-map.png", width=1000, height=600, scale=2)

    print("✅ All charts exported to assets/")

if __name__ == "__main__":
    export_all()
