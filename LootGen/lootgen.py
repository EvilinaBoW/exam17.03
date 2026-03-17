import argparse
import csv
import random
from dataclasses import dataclass
from collections import Counter

from rich.console import Console
from rich.table import Table
from rich.progress import track


@dataclass
class LootItem:
    name: str
    rarity: str
    weight: int

# Полная таблица лута 
LOOT_TABLE = [
    LootItem("Iron Sword", "Common", 40),
    LootItem("Wooden Shield", "Common", 35),
    LootItem("Health Potion", "Common", 30),
    LootItem("Steel Axe", "Rare", 15),
    LootItem("Leather Armor", "Rare", 12),
    LootItem("Mana Potion", "Rare", 10),
    LootItem("Enchanted Bow", "Epic", 6),
    LootItem("Dragon Scale Mail", "Epic", 4),
    LootItem("Legendary Ring", "Epic", 3),
    LootItem("Godslayer Blade", "Legendary", 1),
    LootItem("Phoenix Feather", "Legendary", 1),
    LootItem("Void Orb", "Legendary", 1),
]


CHEST_WEIGHTS = {
    "common": {"Common": 80, "Rare": 18, "Epic": 2, "Legendary": 0},
    "rare": {"Common": 40, "Rare": 45, "Epic": 13, "Legendary": 2},
    "epic": {"Common": 10, "Rare": 35, "Epic": 45, "Legendary": 10},
}


def get_chest_multiplier(chest_type: str) -> dict:
    return CHEST_WEIGHTS.get(chest_type.lower(), CHEST_WEIGHTS["common"])


def simulate_chests(num_chests: int, chest_type: str, seed: int | None = None) -> list[LootItem]:
    if seed is not None:
        random.seed(seed)

    chest_weights = get_chest_multiplier(chest_type)
    results = []

    for _ in track(range(num_chests), description="Opening chests..."):
        # Сначала выбираем редкость с учётом типа сундука
        rarity = random.choices(
            list(chest_weights.keys()), weights=list(chest_weights.values())
        )[0]

        # Затем выбираем конкретный предмет этой редкости
        possible_items = [item for item in LOOT_TABLE if item.rarity == rarity]
        item = random.choices(
            possible_items, weights=[i.weight for i in possible_items]
        )[0]
        results.append(item)

    return results


def print_summary(results: list[LootItem], num_chests: int) -> None:
    console = Console()

    # Таблица всех дропов
    table = Table(title=f"LootGen — {num_chests} × {results[0].rarity} chests")
    table.add_column("№", style="cyan")
    table.add_column("Item", style="green")
    table.add_column("Rarity", style="magenta")
    for i, item in enumerate(results[:15], 1):
        color = {"Common": "white", "Rare": "blue", "Epic": "magenta", "Legendary": "yellow"}.get(
            item.rarity, "white"
        )
        table.add_row(str(i), item.name, f"[{color}]{item.rarity}[/{color}]")
    if len(results) > 15:
        table.add_row("...", "...", "...")
    console.print(table)

    # Статистика
    counter = Counter(item.rarity for item in results)
    console.print("\n[bold]Final drop rates:[/bold]")
    for rarity in ["Common", "Rare", "Epic", "Legendary"]:
        count = counter.get(rarity, 0)
        percent = (count / num_chests) * 100
        console.print(f"{rarity:10} → {count:4} times ({percent:5.1f}%)")


def export_to_csv(results: list[LootItem], filename: str) -> None:
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Item", "Rarity"])
        for item in results:
            writer.writerow([item.name, item.rarity])
    Console().print(f"[green]Results saved to[/green] {filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LootGen — advanced loot simulator")
    parser.add_argument("-n", "--num-chests", type=int, default=50, help="Number of chests (default: 50)")
    parser.add_argument("-t", "--chest-type", choices=["common", "rare", "epic"], default="common",
                        help="Type of chest")
    parser.add_argument("-r", "--runs", type=int, default=1, help="Number of simulation runs")
    parser.add_argument("-s", "--seed", type=int, help="Random seed for reproducibility")
    parser.add_argument("--export", type=str, help="Export results to CSV file")
    args = parser.parse_args()

    all_results = []
    for run in range(args.runs):
        results = simulate_chests(args.num_chests, args.chest_type, args.seed)
        all_results.extend(results)
        if args.runs > 1:
            Console().print(f"[dim]Run {run+1}/{args.runs} completed[/dim]")

    print_summary(all_results, args.num_chests * args.runs)

    if args.export:
        export_to_csv(all_results, args.export)
