"""Benchmark: ztml vs fasthtml rendering performance."""

import time
import statistics

# --- ztml ---
from ztml import Div, Span, P, H1, H2, Ul, Li, A, Section, Article, render

# --- fasthtml ---
from fasthtml.common import (
    Div as FDiv, Span as FSpan, P as FP, H1 as FH1, H2 as FH2,
    Ul as FUl, Li as FLi, A as FA, Section as FSection, Article as FArticle,
    to_xml,
)


def build_ztml_tree(n_sections: int, items_per_section: int):
    """Build a large DOM tree using ztml."""
    return Div(
        H1("Benchmark Page"),
        *[
            Section(
                H2(f"Section {i}"),
                P(f"Description for section {i}").cls("desc"),
                Ul(*[
                    Li(
                        A(f"Item {i}-{j}").href(f"/item/{i}/{j}"),
                        Span(f" (detail {j})").cls("detail"),
                    )
                    for j in range(items_per_section)
                ]),
                Article(
                    P(f"Content block {i} with some text. " * 3),
                ).cls("content"),
            ).cls(f"section-{i}")
            for i in range(n_sections)
        ],
    ).id("root")


def build_fasthtml_tree(n_sections: int, items_per_section: int):
    """Build the same DOM tree using fasthtml."""
    return FDiv(
        FH1("Benchmark Page"),
        *[
            FSection(
                FH2(f"Section {i}"),
                FP(f"Description for section {i}", cls="desc"),
                FUl(*[
                    FLi(
                        FA(f"Item {i}-{j}", href=f"/item/{i}/{j}"),
                        FSpan(f" (detail {j})", cls="detail"),
                    )
                    for j in range(items_per_section)
                ]),
                FArticle(
                    FP(f"Content block {i} with some text. " * 3),
                    cls="content",
                ),
                cls=f"section-{i}",
            )
            for i in range(n_sections)
        ],
        id="root",
    )


def bench(name: str, build_fn, render_fn, n_sections, items_per, warmup=3, runs=10):
    """Time tree building and rendering separately."""
    # warmup
    for _ in range(warmup):
        render_fn(build_fn(n_sections, items_per))

    build_times = []
    render_times = []
    total_times = []
    for _ in range(runs):
        t0 = time.perf_counter()
        tree = build_fn(n_sections, items_per)
        t1 = time.perf_counter()
        render_fn(tree)
        t2 = time.perf_counter()
        build_times.append(t1 - t0)
        render_times.append(t2 - t1)
        total_times.append(t2 - t0)

    total_elements = n_sections * (4 + items_per * 2)  # approximate
    return {
        "name": name,
        "elements": total_elements,
        "build_ms": statistics.median(build_times) * 1000,
        "render_ms": statistics.median(render_times) * 1000,
        "total_ms": statistics.median(total_times) * 1000,
    }


def main():
    scenarios = [
        (10, 50),      # ~1,000 elements
        (50, 100),     # ~10,000 elements
        (100, 200),    # ~40,000 elements
    ]

    print(f"{'Scenario':<16} {'Library':<12} {'Elements':>8} {'Build (ms)':>12} {'Render (ms)':>13} {'Total (ms)':>12}")
    print("-" * 75)

    for n_sec, n_items in scenarios:
        label = f"{n_sec}x{n_items}"

        r_ztml = bench("ztml", build_ztml_tree, render, n_sec, n_items)
        r_fast = bench("fasthtml", build_fasthtml_tree, to_xml, n_sec, n_items)

        for r in [r_ztml, r_fast]:
            print(f"{label:<16} {r['name']:<12} {r['elements']:>8} {r['build_ms']:>12.2f} {r['render_ms']:>13.2f} {r['total_ms']:>12.2f}")

        build_x = r_fast["build_ms"] / r_ztml["build_ms"]
        render_x = r_fast["render_ms"] / r_ztml["render_ms"]
        total_x = r_fast["total_ms"] / r_ztml["total_ms"]
        print(f"{'':>28} speedup: build {build_x:.1f}x, render {render_x:.1f}x, total {total_x:.1f}x")
        print()


if __name__ == "__main__":
    main()
