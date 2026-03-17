import argparse
import random
from collections import Counter

from rich.console import Console
from rich.table import Table


def get_random_loot() -> dict:
    rand = random.random()
    if rand < 0.6:
        return {"name": "Common Sword", "rarity": "Common"}
    elif rand < 0.9:
        return {"name": "Rare Shield", "rarity": "Rare"}
    else:
        return {"name": "Epic Armor", "rarity": "Epic"}


def simulate_loot(num_chests: int) -> None:
    console = Console()
    drops = [get_random_loot() for _ in range(num_chests)]

    # Таблица выпадений
    table = Table(title=f"LootGen Simulation — {num_chests} chests opened")
    table.add_column("Chest", style="cyan", justify="right")
    table.add_column("Item Name", style="green")
    table.add_column("Rarity", style="magenta")
    for i, drop in enumerate(drops, start=1):
        table.add_row(str(i), drop["name"], drop["rarity"])
    console.print(table)

    # Сводка вероятностей
    summary = Counter(drop["rarity"] for drop in drops)
    console.print("\n[bold]Summary of drops:[/bold]")
    for rarity, count in summary.items():
        percent = (count / num_chests) * 100
        console.print(f"{rarity}: {count} times ({percent:.1f}%)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="LootGen: Simulate probability of rare loot drops from chests."
    )
    parser.add_argument(
        "-n",
        "--num-chests",
        type=int,
        default=10,
        help="Number of chests to open (default: 10)",
    )
    args = parser.parse_args()
    simulate_loot(args.num_chests)