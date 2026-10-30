from html import escape
from pathlib import Path

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import models


class Command(BaseCommand):
    """Export model relationship diagrams for the Sphinx documentation.

    The command writes a Graphviz DOT file and a lightweight SVG fallback using
    Django's model metadata. If Graphviz is installed, the DOT file can be
    rendered with ``dot -Tsvg`` for a more sophisticated diagram.
    """

    help = "Export herbs app model relationship diagrams for documentation."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output-dir",
            default="docs/_static",
            help="Directory that will receive model_relationships.dot and .svg.",
        )

    def handle(self, *args, **options):
        output_dir = Path(options["output_dir"])
        output_dir.mkdir(parents=True, exist_ok=True)

        model_list = list(apps.get_app_config("herbs").get_models())
        relationships = list(_model_relationships(model_list))

        dot_path = output_dir / "model_relationships.dot"
        svg_path = output_dir / "model_relationships.svg"
        dot_path.write_text(_render_dot(model_list, relationships), encoding="utf-8")
        svg_path.write_text(_render_svg(model_list, relationships), encoding="utf-8")

        self.stdout.write(self.style.SUCCESS(f"Wrote {dot_path}"))
        self.stdout.write(self.style.SUCCESS(f"Wrote {svg_path}"))


def _model_relationships(model_list):
    model_set = set(model_list)
    for model in model_list:
        for field in model._meta.get_fields():
            if not getattr(field, "is_relation", False):
                continue
            related_model = getattr(field, "related_model", None)
            if related_model not in model_set:
                continue
            if field.auto_created and not field.concrete:
                continue
            if isinstance(field, models.ManyToManyField):
                relation = "many-to-many"
            elif isinstance(field, models.OneToOneField):
                relation = "one-to-one"
            elif isinstance(field, models.ForeignKey):
                relation = "foreign key"
            else:
                relation = "relation"
            yield {
                "source": model,
                "target": related_model,
                "field": field.name,
                "relation": relation,
            }


def _render_dot(model_list, relationships):
    lines = [
        "digraph herbs_models {",
        "  graph [rankdir=LR, splines=true, overlap=false];",
        "  node [shape=record, style=\"rounded,filled\", fillcolor=\"#f8fafc\", color=\"#64748b\", fontname=\"Arial\"];",
        "  edge [color=\"#475569\", fontname=\"Arial\", fontsize=10];",
    ]
    for model in model_list:
        field_names = [
            field.name
            for field in model._meta.fields
            if field.name not in {"created_at", "updated_at"}
        ]
        label = "{" + model.__name__ + "|" + "\\l".join(field_names) + "\\l}"
        lines.append(f'  {model.__name__} [label="{label}"];')
    for relationship in relationships:
        lines.append(
            "  {source} -> {target} [label=\"{field}\\n{relation}\"];".format(
                source=relationship["source"].__name__,
                target=relationship["target"].__name__,
                field=relationship["field"],
                relation=relationship["relation"],
            )
        )
    lines.append("}")
    return "\n".join(lines) + "\n"


def _render_svg(model_list, relationships):
    box_width = 270
    row_height = 26
    gap_x = 90
    gap_y = 36
    columns = 3
    positions = {}
    heights = {}
    for index, model in enumerate(model_list):
        col = index % columns
        row = index // columns
        x = 24 + col * (box_width + gap_x)
        y = 24 + row * (210 + gap_y)
        positions[model] = (x, y)
        heights[model] = row_height * (len(model._meta.fields) + 1)

    rows = (len(model_list) + columns - 1) // columns
    width = 24 + columns * box_width + (columns - 1) * gap_x + 24
    height = 24 + rows * 210 + (rows - 1) * gap_y + 24

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<defs>",
        '<marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">',
        '<path d="M0,0 L0,6 L9,3 z" fill="#475569" />',
        "</marker>",
        "</defs>",
        '<rect width="100%" height="100%" fill="#ffffff" />',
    ]

    for relationship in relationships:
        source = relationship["source"]
        target = relationship["target"]
        sx, sy = positions[source]
        tx, ty = positions[target]
        start_x = sx + box_width
        start_y = sy + min(heights[source] / 2, 120)
        end_x = tx
        end_y = ty + min(heights[target] / 2, 120)
        if tx < sx:
            start_x = sx
            end_x = tx + box_width
        mid_x = (start_x + end_x) / 2
        label_x = mid_x
        label_y = (start_y + end_y) / 2 - 4
        path = f"M {start_x} {start_y} C {mid_x} {start_y}, {mid_x} {end_y}, {end_x} {end_y}"
        svg.append(
            f'<path d="{path}" fill="none" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#arrow)" />'
        )
        svg.append(
            f'<text x="{label_x}" y="{label_y}" text-anchor="middle" font-family="Arial" font-size="10" fill="#334155">{escape(relationship["field"])}</text>'
        )

    for model in model_list:
        x, y = positions[model]
        fields = [
            field
            for field in model._meta.fields
            if field.name not in {"created_at", "updated_at"}
        ]
        box_height = row_height * (len(fields) + 1)
        svg.append(
            f'<rect x="{x}" y="{y}" width="{box_width}" height="{box_height}" rx="8" fill="#f8fafc" stroke="#64748b" />'
        )
        svg.append(
            f'<rect x="{x}" y="{y}" width="{box_width}" height="{row_height}" rx="8" fill="#e2e8f0" stroke="#64748b" />'
        )
        svg.append(
            f'<text x="{x + 12}" y="{y + 18}" font-family="Arial" font-size="14" font-weight="700" fill="#0f172a">{model.__name__}</text>'
        )
        for index, field in enumerate(fields, start=1):
            field_type = field.__class__.__name__
            text = f"{field.name}: {field_type}"
            svg.append(
                f'<text x="{x + 12}" y="{y + 18 + index * row_height}" font-family="Arial" font-size="11" fill="#334155">{escape(text)}</text>'
            )
    svg.append("</svg>")
    return "\n".join(svg) + "\n"
