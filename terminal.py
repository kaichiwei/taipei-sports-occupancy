from rich.console import Console
from rich.progress_bar import ProgressBar
from rich.table import Table

from sites import SITES


def build_table(record: dict) -> Table:
    table = Table(box=None, title=f"{record["name_zh"]} {record["name_en"]}", 
                  title_style="bold white on gray23", show_footer=True)
    table.add_column("設施 Facility", justify="center")
    table.add_column("現在人數 Current", justify="right")
    table.add_column("容留人數 Capacity", justify="right")
    table.add_column("擁擠程度 Occupancy", justify="right")
    table.add_column("", justify="right")
    return table
    

def print_to_cla(unknown_terms, records) -> None:
    if unknown_terms:
        print(f'\n找不到場館：{"、".join(unknown_terms)}\n')
        print(f'Cannot find sites: {", ".join(unknown_terms)}\n')
        print(f'可選場館：\n{"、".join(s["name_zh"] for s in SITES)}\n')
        print(f'Available sites:\n{", ".join(s["name_en"] for s in SITES)}\n')

    key = {"gym": "健身房", "pool": "游泳池", "rink": "冰宮"}
    console = Console()
    for record in records:
        table = build_table(record)
        for facility in record["facilities"]:
            cur, cap = record["facilities"][facility][:2]
            if cur is not None:
                if cap is None:
                    table.add_row(f"{key.get(facility)} {facility}", f"{cur:>4}", "-", "-",)
                else:
                    ratio = cur / cap
                    style = "green3" if ratio < 0.3 else "yellow" if ratio < 0.6 else "red" if ratio < 1 else "dark_magenta"
                    table.add_row(
                        f"{key.get(facility)} {facility}", 
                        f"{cur:>4}",
                        f"{cap:>4}", 
                        ProgressBar(total=cap, completed=cur, width=30, complete_style=style, finished_style="dark_magenta", style="grey42"),
                        f"[bold {style}]{ratio:.0%}[/]"
                    )

        table.caption = f"[dim italic gray23]time: {record['timestamp']}\nwebsite: {record['website']}[/]"
        table.caption_justify = "right"
        console.print(table)
        print()