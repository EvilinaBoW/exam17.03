import argparse
import json
import csv
import random
from dataclasses import dataclass
from collections import Counter
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.progress import track
import matplotlib.pyplot as plt


@dataclass
class LootItem:
    name: str
    rarity: str
    weight: int


DEFAULT_CONFIG = {
    "loot_table": [
        {"name": "Iron Sword", "rarity": "Common", "weight": 40},
        {"name": "Wooden Shield", "rarity": "Common", "weight": 35},
        {"name": "Health Potion", "rarity": "Common", "weight": 30},
        {"name": "Steel Axe", "rarity": "Rare", "weight": 15},
        {"name": "Leather Armor", "rarity": "Rare", "weight": 12},
        {"name": "Mana Potion", "rarity": "Rare", "weight": 10},
        {"name": "Enchanted Bow", "rarity": "Epic", "weight": 6},
        {"name": "Dragon Scale Mail", "rarity": "Epic", "weight": 4},
        {"name": "Legendary Ring", "rarity": "Epic", "weight": 3},
        {"name": "Godslayer Blade", "rarity": "Legendary", "weight": 1},
        {"name": "Phoenix Feather", "rarity": "Legendary", "weight": 1},
        {"name": "Void Orb", "rarity": "Legendary", "weight": 1},
    ],
    "chest_weights": {
        "common": {"Common": 80, "Rare": 18, "Epic": 2, "Legendary": 0},
        "rare": {"Common": 40, "Rare": 45, "Epic": 13, "Legendary": 2},
        "epic": {"Common": 10, "Rare": 35, "Epic": 45, "Legendary": 10}
    }
}


def load_config(config_path: str = "config.json") -> dict:
    path = Path(config_path)
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    # Создаём дефолтный конфиг при первом запуске
    with open(path, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_CONFIG, f, indent=4, ensure_ascii=False)
    Console().print("[yellow]Создан config.json с настройками по умолчанию[/yellow]")
    return DEFAULT_CONFIG


def simulate_chests(num_chests: int, chest_type: str, config: dict, seed: int | None = None) -> list[LootItem]:
    if seed is not None:
        random.seed(seed)

    config = load_config() if not isinstance(config, dict) else config
    chest_weights = config["chest_weights"].get(chest_type.lower(), config["chest_weights"]["common"])
    loot_table = [LootItem(**item) for item in config["loot_table"]]

    results = []
    for _ in track(range(num_chests), description=f"Открываем {chest_type} сундуки..."):
        rarity = random.choices(list(chest_weights.keys()), weights=list(chest_weights.values()))[0]
        possible = [item for item in loot_table if item.rarity == rarity]
        item = random.choices(possible, weights=[i.weight for i in possible])[0]
        results.append(item)

    return results


def print_summary(results: list[LootItem], total_chests: int) -> None:
    console = Console()
    counter = Counter(item.rarity for item in results)

    table = Table(title=f"Итоговая статистика — {total_chests} сундуков")
    table.add_column("Редкость", style="magenta")
    table.add_column("Количество", style="green")
    table.add_column("Процент", style="cyan")
    for rarity in ["Common", "Rare", "Epic", "Legendary"]:
        count = counter.get(rarity, 0)
        percent = (count / total_chests) * 100
        table.add_row(rarity, str(count), f"{percent:.1f}%")
    console.print(table)


def save_plot(results: list[LootItem], filename: str = "loot_stats.png") -> None:
    counter = Counter(item.rarity for item in results)
    rarities = ["Common", "Rare", "Epic", "Legendary"]
    counts = [counter.get(r, 0) for r in rarities]

    plt.figure(figsize=(8, 5))
    bars = plt.bar(rarities, counts, color=["gray", "blue", "purple", "gold"])
    plt.title("Распределение лута по редкостям")
    plt.ylabel("Количество выпадений")
    plt.xlabel("Редкость")

    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height + 1, f'{height}', ha='center')

    plt.savefig(filename)
    plt.close()
    Console().print(f"[green]График сохранён →[/green] {filename}")


def export_to_csv(results: list[LootItem], filename: str) -> None:
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Предмет", "Редкость"])
        for item in results:
            writer.writerow([item.name, item.rarity])
    Console().print(f"[green]Результаты сохранены в[/green] {filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LootGen — продвинутая утилита симуляции лута")
    parser.add_argument("-n", "--num-chests", type=int, default=100, help="Количество сундуков (по умолчанию 100)")
    parser.add_argument("-t", "--chest-type", choices=["common", "rare", "epic"], default="common", help="Тип сундука")
    parser.add_argument("-r", "--runs", type=int, default=1, help="Количество симуляций")
    parser.add_argument("-s", "--seed", type=int, help="Сид для воспроизводимости")
    parser.add_argument("--export", type=str, help="Сохранить результаты в CSV")
    parser.add_argument("--plot", action="store_true", help="Сохранить график вероятностей (loot_stats.png)")
    parser.add_argument("--config", type=str, default="config.json", help="Путь к config.json")
    parser.add_argument("--version", action="version", version="LootGen v2.0 (Infrastructure Ready)")
    args = parser.parse_args()

    config = load_config(args.config)
    all_results = []

    for run in range(args.runs):
        results = simulate_chests(args.num_chests, args.chest_type, config, args.seed)
        all_results.extend(results)
        if args.runs > 1:
            Console().print(f"[dim]Симуляция {run+1}/{args.runs} завершена[/dim]")

    print_summary(all_results, args.num_chests * args.runs)

    if args.export:
        export_to_csv(all_results, args.export)
    if args.plot:
        save_plot(all_results)
