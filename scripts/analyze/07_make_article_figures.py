import argparse
import csv
import html
from pathlib import Path

try:
    from summarize_lzma_storage import generate as generate_lzma_summary
except ImportError:  # pragma: no cover - optional helper
    generate_lzma_summary = None


PNG_CONTROL_VARIANT = "b8"

COLORS = {
    "original": "#222222",
    "jpeg": "#d95f02",
    "bpc": "#1b9e77",
    "png_control": "#6a51a3",
    "map50": "#7570b3",
    "map50_95": "#66a61e",
    "grid": "#dddddd",
    "axis": "#333333",
}

DEFAULT_OUTPUT_DIR = "article/latex_project/results/article_figures"


def parse_args():
    parser = argparse.ArgumentParser(description="Create article-ready SVG figures from final experiment CSV files.")
    parser.add_argument(
        "--metrics-csv",
        default="results/val5k/summary/metrics.csv",
        help="Path to detection metrics CSV.",
    )
    parser.add_argument(
        "--image-quality-csv",
        default="results/val5k/summary/image_quality.csv",
        help="Path to PSNR/SSIM CSV.",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for article-ready figures.",
    )
    parser.add_argument(
        "--lzma-root",
        default="data/processed/val5k/bpc_lzma",
        help="Optional root directory for the auxiliary BMP+LZMA experiment.",
    )
    return parser.parse_args()


def is_png_control(row):
    return row["variant"] == PNG_CONTROL_VARIANT


def bpc_quantized_rows(rows):
    return [row for row in rows if row["type"] == "bpc" and not is_png_control(row)]


def png_control_rows(rows):
    return [row for row in rows if is_png_control(row)]


def variant_color(row):
    if is_png_control(row):
        return COLORS["png_control"]
    return COLORS.get(row["type"], COLORS["bpc"])


def read_csv(path):
    with Path(path).open("r", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def as_float(row, key):
    return float(row[key])


def optional_float(value):
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"inf", "nan"}:
        return None
    return float(text)


def load_article_rows(metrics_csv, image_quality_csv):
    metric_rows = read_csv(metrics_csv)
    quality_rows = {row["variant"]: row for row in read_csv(image_quality_csv)}
    baseline = next(row for row in metric_rows if row["quantization_type"] == "original")
    baseline_size = as_float(baseline, "dataset_size_mb")
    baseline_map50 = as_float(baseline, "map50")
    baseline_map50_95 = as_float(baseline, "map50_95")

    rows = []
    for row in metric_rows:
        variant = row["variant"]
        quality = quality_rows.get(variant, {})
        dataset_size = as_float(row, "dataset_size_mb")
        map50 = as_float(row, "map50")
        map50_95 = as_float(row, "map50_95")
        rows.append(
            {
                "variant": variant,
                "type": row["quantization_type"],
                "size_mb": dataset_size,
                "compression_ratio": baseline_size / dataset_size,
                "precision": as_float(row, "precision"),
                "recall": as_float(row, "recall"),
                "map50": map50,
                "map50_95": map50_95,
                "map50_drop_pct": ((baseline_map50 - map50) / baseline_map50) * 100.0,
                "map50_95_drop_pct": ((baseline_map50_95 - map50_95) / baseline_map50_95) * 100.0,
                "psnr": optional_float(quality.get("mean_psnr")) if quality else None,
                "ssim": optional_float(quality.get("mean_ssim")) if quality else None,
            }
        )
    return rows


def by_type(rows, quantization_type):
    return [row for row in rows if row["type"] == quantization_type]


def escape(value):
    return html.escape(str(value), quote=True)


def nice_range(values, lower_padding=0.05, upper_padding=0.08):
    minimum = min(values)
    maximum = max(values)
    if minimum == maximum:
        return minimum - 1, maximum + 1
    span = maximum - minimum
    return minimum - span * lower_padding, maximum + span * upper_padding


def tick_values(minimum, maximum, count=5):
    if count <= 1:
        return [minimum]
    step = (maximum - minimum) / (count - 1)
    return [minimum + step * index for index in range(count)]


class SvgChart:
    def __init__(self, title, xlabel, ylabel, width=920, height=620):
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.width = width
        self.height = height
        self.left = 95
        self.right = 35
        self.top = 70
        self.bottom = 90
        self.elements = []

    @property
    def plot_width(self):
        return self.width - self.left - self.right

    @property
    def plot_height(self):
        return self.height - self.top - self.bottom

    def set_ranges(self, x_values, y_values):
        self.x_min, self.x_max = nice_range(x_values)
        self.y_min, self.y_max = nice_range(y_values)

    def x(self, value):
        return self.left + ((value - self.x_min) / (self.x_max - self.x_min)) * self.plot_width

    def y(self, value):
        return self.top + (1 - ((value - self.y_min) / (self.y_max - self.y_min))) * self.plot_height

    def add(self, element):
        self.elements.append(element)

    def draw_axes(self):
        self.add(f'<rect x="0" y="0" width="{self.width}" height="{self.height}" fill="white"/>')
        self.add(
            f'<text x="{self.width / 2}" y="32" text-anchor="middle" '
            f'font-family="Arial" font-size="22" font-weight="700">{escape(self.title)}</text>'
        )
        for tick in tick_values(self.x_min, self.x_max):
            x = self.x(tick)
            self.add(
                f'<line x1="{x:.2f}" y1="{self.top}" x2="{x:.2f}" y2="{self.top + self.plot_height}" '
                f'stroke="{COLORS["grid"]}" stroke-width="1"/>'
            )
            self.add(
                f'<text x="{x:.2f}" y="{self.top + self.plot_height + 24}" text-anchor="middle" '
                f'font-family="Arial" font-size="12">{tick:.2f}</text>'
            )
        for tick in tick_values(self.y_min, self.y_max):
            y = self.y(tick)
            self.add(
                f'<line x1="{self.left}" y1="{y:.2f}" x2="{self.left + self.plot_width}" y2="{y:.2f}" '
                f'stroke="{COLORS["grid"]}" stroke-width="1"/>'
            )
            self.add(
                f'<text x="{self.left - 12}" y="{y + 4:.2f}" text-anchor="end" '
                f'font-family="Arial" font-size="12">{tick:.3f}</text>'
            )
        self.add(
            f'<line x1="{self.left}" y1="{self.top + self.plot_height}" '
            f'x2="{self.left + self.plot_width}" y2="{self.top + self.plot_height}" '
            f'stroke="{COLORS["axis"]}" stroke-width="1.5"/>'
        )
        self.add(
            f'<line x1="{self.left}" y1="{self.top}" x2="{self.left}" y2="{self.top + self.plot_height}" '
            f'stroke="{COLORS["axis"]}" stroke-width="1.5"/>'
        )
        self.add(
            f'<text x="{self.left + self.plot_width / 2}" y="{self.height - 28}" text-anchor="middle" '
            f'font-family="Arial" font-size="15">{escape(self.xlabel)}</text>'
        )
        self.add(
            f'<text x="24" y="{self.top + self.plot_height / 2}" text-anchor="middle" '
            f'transform="rotate(-90 24 {self.top + self.plot_height / 2})" '
            f'font-family="Arial" font-size="15">{escape(self.ylabel)}</text>'
        )

    def add_line(self, rows, x_key, y_key, color, label):
        points = " ".join(f'{self.x(row[x_key]):.2f},{self.y(row[y_key]):.2f}' for row in rows)
        self.add(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2.5"/>')
        for row in rows:
            x = self.x(row[x_key])
            y = self.y(row[y_key])
            self.add(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="5" fill="{color}"/>')
            self.add(
                f'<text x="{x + 7:.2f}" y="{y - 7:.2f}" font-family="Arial" '
                f'font-size="12">{escape(row["variant"])}</text>'
            )
        self.add_legend_item(label, color)

    def add_scatter(self, rows, x_key, y_key, color, label):
        for row in rows:
            x = self.x(row[x_key])
            y = self.y(row[y_key])
            self.add(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="5.5" fill="{color}"/>')
            self.add(
                f'<text x="{x + 7:.2f}" y="{y - 7:.2f}" font-family="Arial" '
                f'font-size="12">{escape(row["variant"])}</text>'
            )
        self.add_legend_item(label, color)

    def add_control_markers(self, rows, x_key, y_key, color, label):
        for row in rows:
            x = self.x(row[x_key])
            y = self.y(row[y_key])
            size = 7
            points = (
                f"{x:.2f},{y - size:.2f} {x + size:.2f},{y:.2f} "
                f"{x:.2f},{y + size:.2f} {x - size:.2f},{y:.2f}"
            )
            self.add(
                f'<polygon points="{points}" fill="{color}" fill-opacity="0.25" '
                f'stroke="{color}" stroke-width="2.2"/>'
            )
            self.add(
                f'<text x="{x + 9:.2f}" y="{y - 9:.2f}" font-family="Arial" '
                f'font-size="12">{escape(row["variant"])}</text>'
            )
        self.add_legend_item(label, color)

    def add_legend_item(self, label, color):
        index = sum(1 for element in self.elements if 'data-legend="true"' in element)
        x = self.left + 20 + index * 115
        y = self.top - 22
        self.add(
            f'<g data-legend="true"><rect x="{x}" y="{y - 10}" width="13" height="13" fill="{color}"/>'
            f'<text x="{x + 20}" y="{y + 1}" font-family="Arial" font-size="13">{escape(label)}</text></g>'
        )

    def write(self, path):
        content = "\n".join(
            [
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.height}" '
                f'viewBox="0 0 {self.width} {self.height}">',
                *self.elements,
                "</svg>",
            ]
        )
        path.write_text(content, encoding="utf-8")


def write_line_chart(rows, output_path, title, xlabel, ylabel, x_key, y_key, groups):
    chart = SvgChart(title, xlabel, ylabel)
    selected_rows = [row for group in groups.values() for row in group]
    chart.set_ranges([row[x_key] for row in selected_rows], [row[y_key] for row in selected_rows])
    chart.draw_axes()
    for label, group in groups.items():
        if not group:
            continue
        color_key = label.lower()
        if color_key == "png_control":
            chart.add_control_markers(
                group,
                x_key,
                y_key,
                COLORS["png_control"],
                "PNG control (b8)",
            )
        else:
            chart.add_line(group, x_key, y_key, COLORS[color_key], label.upper())
    chart.write(output_path)


def pareto_optimal(rows, size_key="size_mb", quality_key="map50"):
    """Return non-dominated points: lower size and higher mAP50 are better."""
    candidates = sorted(rows, key=lambda row: (row[size_key], -row[quality_key]))
    frontier = []
    best_map = -1.0
    for row in candidates:
        if row[quality_key] > best_map:
            frontier.append(row)
            best_map = row[quality_key]
    return sorted(frontier, key=lambda row: row[size_key])


def is_pareto_optimal(row, rows, size_key="size_mb", quality_key="map50"):
    for other in rows:
        if other["variant"] == row["variant"]:
            continue
        if other[size_key] <= row[size_key] and other[quality_key] >= row[quality_key]:
            if other[size_key] < row[size_key] or other[quality_key] > row[quality_key]:
                return False
    return True


def write_pareto_chart(rows, output_path):
    chart = SvgChart(
        "Storage-detection Pareto frontier",
        "Dataset size (MB)",
        "mAP50",
    )
    tradeoff_rows = [row for row in rows if row["type"] != "original"]
    pareto_rows = [row for row in tradeoff_rows if not is_png_control(row)]
    chart.set_ranges(
        [row["size_mb"] for row in tradeoff_rows],
        [row["map50"] for row in tradeoff_rows],
    )
    chart.draw_axes()
    jpeg_rows = by_type(tradeoff_rows, "jpeg")
    if jpeg_rows:
        chart.add_scatter(jpeg_rows, "size_mb", "map50", COLORS["jpeg"], "JPEG")
    bpc_rows = bpc_quantized_rows(tradeoff_rows)
    if bpc_rows:
        chart.add_scatter(bpc_rows, "size_mb", "map50", COLORS["bpc"], "BPC")
    control_rows = png_control_rows(tradeoff_rows)
    if control_rows:
        chart.add_control_markers(
            control_rows,
            "size_mb",
            "map50",
            COLORS["png_control"],
            "PNG control (b8)",
        )

    frontier = pareto_optimal(pareto_rows)
    if len(frontier) >= 2:
        points = " ".join(f'{chart.x(row["size_mb"]):.2f},{chart.y(row["map50"]):.2f}' for row in frontier)
        chart.add(
            f'<polyline points="{points}" fill="none" stroke="#444444" '
            f'stroke-width="2.5" stroke-dasharray="8 5"/>'
        )
    for row in frontier:
        x = chart.x(row["size_mb"])
        y = chart.y(row["map50"])
        chart.add(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="7" fill="none" stroke="#444444" stroke-width="2"/>')
    chart.add_legend_item("Pareto frontier", "#444444")
    chart.write(output_path)


def write_scatter_chart(rows, output_path, title, xlabel, ylabel, x_key, y_key):
    chart = SvgChart(title, xlabel, ylabel)
    selected_rows = [
        row for row in rows if row[x_key] is not None and not is_png_control(row)
    ]
    chart.set_ranges([row[x_key] for row in selected_rows], [row[y_key] for row in selected_rows])
    chart.draw_axes()
    jpeg_rows = by_type(selected_rows, "jpeg")
    if jpeg_rows:
        chart.add_scatter(jpeg_rows, x_key, y_key, COLORS["jpeg"], "JPEG")
    bpc_rows = bpc_quantized_rows(selected_rows)
    if bpc_rows:
        chart.add_scatter(bpc_rows, x_key, y_key, COLORS["bpc"], "BPC")
    chart.write(output_path)


def write_bar_chart(rows, output_path, title, ylabel, value_key):
    width = 980
    height = 620
    left = 80
    right = 30
    top = 70
    bottom = 95
    plot_width = width - left - right
    plot_height = height - top - bottom
    max_value = max(row[value_key] for row in rows) * 1.12
    bar_gap = 12
    bar_width = (plot_width - bar_gap * (len(rows) - 1)) / len(rows)
    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="white"/>',
        f'<text x="{width / 2}" y="32" text-anchor="middle" font-family="Arial" font-size="22" font-weight="700">{escape(title)}</text>',
    ]
    for tick in tick_values(0, max_value):
        y = top + (1 - tick / max_value) * plot_height
        elements.append(f'<line x1="{left}" y1="{y:.2f}" x2="{left + plot_width}" y2="{y:.2f}" stroke="{COLORS["grid"]}"/>')
        elements.append(f'<text x="{left - 10}" y="{y + 4:.2f}" text-anchor="end" font-family="Arial" font-size="12">{tick:.2f}</text>')
    for index, row in enumerate(rows):
        x = left + index * (bar_width + bar_gap)
        bar_height = (row[value_key] / max_value) * plot_height
        y = top + plot_height - bar_height
        elements.append(
            f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_width:.2f}" height="{bar_height:.2f}" '
            f'fill="{variant_color(row)}"/>'
        )
        elements.append(f'<text x="{x + bar_width / 2:.2f}" y="{height - 62}" text-anchor="middle" font-family="Arial" font-size="12">{escape(row["variant"])}</text>')
    elements.append(f'<line x1="{left}" y1="{top + plot_height}" x2="{left + plot_width}" y2="{top + plot_height}" stroke="{COLORS["axis"]}" stroke-width="1.5"/>')
    elements.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_height}" stroke="{COLORS["axis"]}" stroke-width="1.5"/>')
    elements.append(f'<text x="24" y="{top + plot_height / 2}" text-anchor="middle" transform="rotate(-90 24 {top + plot_height / 2})" font-family="Arial" font-size="15">{escape(ylabel)}</text>')
    elements.append("</svg>")
    output_path.write_text("\n".join(elements), encoding="utf-8")


def write_detection_bars(rows, output_path):
    ordered_names = [
        "original",
        "q94",
        "q88",
        "q75",
        "q50",
        "q25",
        "b8",
        "b7",
        "b4",
        "b3",
        "b2",
        "b1",
    ]
    row_map = {row["variant"]: row for row in rows}
    ordered = [row_map[name] for name in ordered_names if name in row_map]
    width = 1040
    height = 620
    left = 80
    right = 30
    top = 70
    bottom = 95
    plot_width = width - left - right
    plot_height = height - top - bottom
    max_value = max(max(row["map50"], row["map50_95"]) for row in ordered) * 1.12
    group_width = plot_width / len(ordered)
    bar_width = group_width * 0.34
    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="white"/>',
        f'<text x="{width / 2}" y="32" text-anchor="middle" font-family="Arial" font-size="22" font-weight="700">Detection metrics by variant</text>',
        f'<rect x="{left + 20}" y="{top - 30}" width="13" height="13" fill="{COLORS["map50"]}"/>',
        f'<text x="{left + 40}" y="{top - 19}" font-family="Arial" font-size="13">mAP50</text>',
        f'<rect x="{left + 120}" y="{top - 30}" width="13" height="13" fill="{COLORS["map50_95"]}"/>',
        f'<text x="{left + 140}" y="{top - 19}" font-family="Arial" font-size="13">mAP50-95</text>',
    ]
    for tick in tick_values(0, max_value):
        y = top + (1 - tick / max_value) * plot_height
        elements.append(f'<line x1="{left}" y1="{y:.2f}" x2="{left + plot_width}" y2="{y:.2f}" stroke="{COLORS["grid"]}"/>')
        elements.append(f'<text x="{left - 10}" y="{y + 4:.2f}" text-anchor="end" font-family="Arial" font-size="12">{tick:.2f}</text>')
    for index, row in enumerate(ordered):
        center = left + group_width * index + group_width / 2
        if is_png_control(row):
            outline_x = center - group_width * 0.42
            outline_y = top + 2
            outline_w = group_width * 0.84
            outline_h = plot_height - 4
            elements.append(
                f'<rect x="{outline_x:.2f}" y="{outline_y:.2f}" width="{outline_w:.2f}" '
                f'height="{outline_h:.2f}" fill="none" stroke="{COLORS["png_control"]}" '
                f'stroke-width="2" stroke-dasharray="6 4"/>'
            )
        for offset, key, color in [(-bar_width / 2, "map50", COLORS["map50"]), (bar_width / 2, "map50_95", COLORS["map50_95"])]:
            bar_height = (row[key] / max_value) * plot_height
            x = center + offset - bar_width / 2
            y = top + plot_height - bar_height
            elements.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_width:.2f}" height="{bar_height:.2f}" fill="{color}"/>')
        label_color = COLORS["png_control"] if is_png_control(row) else "#333333"
        elements.append(
            f'<text x="{center:.2f}" y="{height - 62}" text-anchor="middle" font-family="Arial" '
            f'font-size="12" fill="{label_color}">{escape(row["variant"])}</text>'
        )
    elements.append(f'<line x1="{left}" y1="{top + plot_height}" x2="{left + plot_width}" y2="{top + plot_height}" stroke="{COLORS["axis"]}" stroke-width="1.5"/>')
    elements.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_height}" stroke="{COLORS["axis"]}" stroke-width="1.5"/>')
    elements.append(f'<text x="24" y="{top + plot_height / 2}" text-anchor="middle" transform="rotate(-90 24 {top + plot_height / 2})" font-family="Arial" font-size="15">Detection metric</text>')
    elements.append("</svg>")
    output_path.write_text("\n".join(elements), encoding="utf-8")


def write_article_table(rows, output_dir):
    output_path = output_dir / "article_metrics_table.csv"
    fieldnames = [
        "variant",
        "type",
        "size_mb",
        "compression_ratio",
        "map50",
        "map50_95",
        "map50_drop_pct",
        "psnr",
        "ssim",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: (
                        round(row[key], 6)
                        if isinstance(row[key], float)
                        else ("" if row[key] is None else row[key])
                    )
                    for key in fieldnames
                }
            )


def main():
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = load_article_rows(args.metrics_csv, args.image_quality_csv)
    non_original = [row for row in rows if row["type"] != "original"]

    write_article_table(rows, output_dir)
    lzma_root = Path(args.lzma_root)
    if lzma_root.exists() and generate_lzma_summary is not None:
        generate_lzma_summary(
            output_dir / "article_metrics_table.csv",
            lzma_root,
            output_dir / "lzma_storage.csv",
            [7, 4, 3, 2, 1],
        )
        print(f"Saved LZMA summary to {output_dir / 'lzma_storage.csv'}")
    tradeoff_non_control = [row for row in non_original if not is_png_control(row)]
    write_line_chart(
        rows,
        output_dir / "fig1_map50_vs_size.svg",
        "Detection quality vs dataset size",
        "Dataset size (MB)",
        "mAP50",
        "size_mb",
        "map50",
        {
            "original": by_type(rows, "original"),
            "jpeg": sorted(by_type(rows, "jpeg"), key=lambda row: row["size_mb"]),
            "bpc": sorted(bpc_quantized_rows(rows), key=lambda row: row["size_mb"]),
            "png_control": png_control_rows(rows),
        },
    )
    write_line_chart(
        tradeoff_non_control,
        output_dir / "fig2_compression_ratio_vs_map50.svg",
        "Compression ratio vs detection quality",
        "Compression ratio vs original",
        "mAP50",
        "compression_ratio",
        "map50",
        {
            "jpeg": sorted(by_type(tradeoff_non_control, "jpeg"), key=lambda row: row["compression_ratio"]),
            "bpc": sorted(bpc_quantized_rows(tradeoff_non_control), key=lambda row: row["compression_ratio"]),
        },
    )
    write_line_chart(
        tradeoff_non_control,
        output_dir / "fig3_relative_map50_drop.svg",
        "Detection loss under compression",
        "Compression ratio vs original",
        "Relative mAP50 drop (%)",
        "compression_ratio",
        "map50_drop_pct",
        {
            "jpeg": sorted(by_type(tradeoff_non_control, "jpeg"), key=lambda row: row["compression_ratio"]),
            "bpc": sorted(bpc_quantized_rows(tradeoff_non_control), key=lambda row: row["compression_ratio"]),
        },
    )
    write_bar_chart(
        sorted(rows, key=lambda row: row["size_mb"]),
        output_dir / "fig4_dataset_size_bars.svg",
        "Dataset size by variant",
        "Dataset size (MB)",
        "size_mb",
    )
    write_detection_bars(rows, output_dir / "fig5_detection_metric_bars.svg")
    write_scatter_chart(
        non_original,
        output_dir / "fig6_psnr_vs_map50.svg",
        "PSNR vs detection quality",
        "Mean PSNR",
        "mAP50",
        "psnr",
        "map50",
    )
    write_scatter_chart(
        non_original,
        output_dir / "fig7_ssim_vs_map50.svg",
        "SSIM vs detection quality",
        "Mean SSIM",
        "mAP50",
        "ssim",
        "map50",
    )
    write_pareto_chart(rows, output_dir / "fig10_pareto_storage_map50.svg")
    print(f"Saved article figures to {output_dir}")


if __name__ == "__main__":
    main()
