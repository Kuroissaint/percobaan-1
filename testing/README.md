# Kang Resto

> A 2D Puzzle-Job Simulation game about running a cross-dimensional izakaya — one wrong order could cause a diplomatic incident.

---

## Overview

You are a modern-world professional turned reluctant restaurateur. After inheriting your grandfather's izakaya, you soon discover it doesn't serve ordinary customers — it serves customers from another world entirely.

Armed only with your grandfather's handwritten journal (the *Dietary Codex & Gastronomic Regulations*), you must learn to navigate the customs, beliefs, and biological quirks of Elves, Orcs, Dwarves, Undead, and more — all while paying off the debt your grandfather left behind.

**Platform:** PC only

---

## Core Gameplay

The game follows the **G.R.I.D.** loop:

1. **Greet** — A fantasy creature approaches the counter. Identify their race.
2. **Receive** — Listen to their order and note the key ingredients.
3. **Inspect** — Cross-check the order against the Dietary Codex (racial biology, religion, nationality, and active kingdom decrees).
4. **Decide** — Accept the order, or reject it and suggest a safer alternative.

**Controls (Mouse only):**
- Left Click (Hold & Drag) — Move papers, flip through the guidebook pages.

---

## Win / Fail Conditions

| Condition | Description |
|-----------|-------------|
| **Win** | Earn enough money to pay off your grandfather's debt by Day 7. |
| **Fail** | Run out of time without meeting the debt target. |

---

## Unique Selling Points

- **Rule Deduction Mechanic** — Orders must be cross-checked against layered, sometimes contradictory rules. The regulations grow more absurd as the days progress.
- **Environmental Storytelling** — World-building happens entirely through NPC dialogue. Racial conflicts, kingdom history, and faction politics emerge organically from customer complaints.
- **Knowledge Progression** — Players go from confusing Goblins and Orcs on Day 1, to confidently recommending dishes by Day 7.

---

## Obstacles

- **Time Pressure** — Each day has limited working hours. Slow decisions mean fewer customers served and less income.
- **Wrong Orders** — Some customers will try to order food that violates their own biological or spiritual restrictions.
- **Conflicting Regulations** — Kingdom decrees can override standing rules (e.g., the current Sugar Prohibition limits sugar to Human patrons only).

---

## The Dietary Codex

The in-game reference book. All rules below are sourced directly from the game data files.

### I. Racial Biological Constraints

> Source: `data/species.json`

| Race | Forbidden Ingredient Tags | Required Ingredient Tags | Preferred Tags | Notes |
|------|--------------------------|--------------------------|----------------|-------|
| Elf | `meat` | — | — | Strict vegetarian diet |
| Orc | `holy` | `meat` | — | Refuses holy food; expects meat in every meal |
| Dwarf | — | — | `spicy` | Can eat almost anything; loves strong flavors |
| Undead | `holy` | — | — | Holy food is harmful; unaffected by spoiled food |
| Dragonborn | — | `meat` | — | Prefers protein-rich meals |
| Halfling | `spicy` | — | — | Cannot handle spicy food |
| Tiefling | `holy` | — | `fire`, `spicy` | Avoids holy substances; enjoys fiery foods |
| Gnome | — | — | `sweet` | Has a sweet tooth |

### II. Religious & Spiritual Taboos

> Source: `data/religions.json`

| Religion | Prohibited Ingredient Tags | Lore |
|----------|---------------------------|------|
| Cult of the Eternal Flame | `cold`, `ice`, `frozen` | Ice is seen as a manifestation of the "Great Void" |
| Children of the Tide | `seafood`, `crustacean`, `fish` | One does not eat their brothers of the deep |
| The Order of the Sun | `underground`, `root`, `darkness_grown` | Only food touched by direct sunlight is pure |
| Path of the Silent Forest | `fungi`, `mushroom` | Mycelium are considered the "nervous system" of the woods |

### III. National & Regional Customs

> Source: `data/nationalities.json`

| Nationality | Preferred Tags | Prohibited Tags | Social Faux Pas Tags | Lore |
|-------------|---------------|-----------------|----------------------|------|
| Highland Empire | `sweet`, `tea`, `pastry` | — | `wooden_platter` | A refined mountain civilization that values elegant presentation |
| Frozen Tundra | `fat`, `meat`, `hot`, `broth` | `cold`, `raw`, `vegetable_raw` | — | Survival culture that prioritizes caloric density and warmth |
| Iron Citadel | `solid`, `compact`, `dense` | `foam`, `garnish_decorative`, `fancy_presentation` | — | Militaristic society that values practicality over aesthetics |
| Floating Isles | `poultry`, `avian`, `sky_fruit` | `ground_meat`, `earth_dwelling` | — | Sky-dwelling culture that sees ground food as impure |

### IV. Special Permits & Licenses

> Source: `data/foods.json` — certain dishes require the customer to hold a valid permit.

| Permit / License | Required For |
|-----------------|-------------|
| `open_flame_consumption_license` | Fire, Dragon Breath Chili |
| `holy_substance_consumption_license` | Water (Holy), Soda, Saint's Blessed Cake, Flame Pudding |
| `large_predator_permit` | Whole Cow Roast, Giant Boar Platter |
| `necromantic_consumption_waiver` | Zombie Brain Stew, Skeleton Bone Broth, Ritual Feast Plate |
| `soul_consumption_authorization` | Bottled Soul, Phantom Ice Cream |
| `aquatic_import_permit` | Kraken Sashimi, Sea Depth Platter |
| `ritual_cooking_license` *(café)* | Ritual Feast Plate |

### V. Menu Reference

> Source: `data/foods.json`

| Dish | Key Ingredients | Notes |
|------|----------------|-------|
| Tacos | Meat, Flour, Vegetables, Milk | Contains `meat` and `dairy` |
| Ramen | Flour, Egg, Vegetables, Broth, Shrimp Crackers | Contains `seafood` |
| Hamburger Steak | Meat, Flour, Rice, Vegetables, Chili, Sugar | Contains `meat`, `sweet`, `spicy` |
| Katsudon | Chicken Meat, Rice, Egg, Green Onions | Contains `meat` (bird) |
| English Breakfast | Sausage, Potato, Egg, Oil, Salt, Pepper | Contains `meat`, `spicy` |
| Cake | Flour, Egg, Sugar, Milk | Contains `sweet`, `dairy` |
| Fire | Fire | Requires `open_flame_consumption_license` |
| Water (Holy) | Holy Water | Contains `holy`; requires `holy_substance_consumption_license` |
| Soda | Herb, Holy Water | Contains `holy`; requires `holy_substance_consumption_license` |
| Dragon Breath Chili | Chili, Fire, Meat | Contains `meat`, `fire`, `spicy`; requires `open_flame_consumption_license` |
| Whole Cow Roast | Meat | Requires `large_predator_permit` |
| Giant Boar Platter | Meat | Requires `large_predator_permit` |
| Saint's Blessed Cake | Flour, Egg, Milk, Sugar, Holy Water | Contains `holy`, `sweet`; requires `holy_substance_consumption_license` |
| Zombie Brain Stew | Broth | Requires `necromantic_consumption_waiver` |
| Skeleton Bone Broth | Broth | Requires `necromantic_consumption_waiver` |
| Bottled Soul | — | Requires `soul_consumption_authorization` |
| Phantom Ice Cream | Milk, Sugar | Contains `sweet`; requires `soul_consumption_authorization` |
| Kraken Sashimi | Shrimp Crackers | Contains `seafood`; requires `aquatic_import_permit` |
| Frozen Fruit Parfait | Ice, Sun-Dried Fruit, Milk, Sugar | Contains `cold`, `frozen`, `sweet` |
| Tundra Hearty Stew | Tundra Meat, Potato, Broth | Contains `meat`, `fat`, `warm` |
| Sea Depth Platter | Deep Sea Crab, Shrimp Crackers | Contains `seafood`, `crustacean`; requires `aquatic_import_permit` |
| Forest Mushroom Soup | Forest Mushroom, Broth, Salt | Contains `fungi` |
| Sun Rice Bowl | Sun Rice, Egg, Tundra Meat | Contains `sun_touched`, `meat` |
| Floating Isle Platter | Sky Bird Meat, Sun-Dried Fruit | Contains `avian`, `sky_fruit` |
| Iron Citadel Ration Block | Tundra Meat, Sun Rice | Contains `meat`, `dense` |
| Highland Tea Set | Sun-Dried Fruit, Sugar, Milk | Contains `sweet`, `sun_touched` |
| Flame Pudding | Sugar, Ice, Milk | Contains `sweet`, `cold`, `frozen`; requires `holy_substance_consumption_license` |
| Ritual Feast Plate | Forest Mushroom, Deep Sea Crab, Tundra Meat, Sun-Dried Fruit | Contains `fungi`, `seafood`, `meat`; requires `necromantic_consumption_waiver` + café `ritual_cooking_license` |

---

## Tech Stack

- **Engine:** Godot 4.7
- **Dialogue:** Dialogue Manager (addon)
- **Rendering:** Forward Plus / D3D12 (Windows)
- **Resolution:** 1280 × 720

---

## Project Structure

```
gameseed-2026/
├── assets/          # Sprites and images
├── audio/           # Sound effects and music
├── autoload/        # Global autoload scripts
├── data/            # JSON data files (menus, ingredients, etc.)
├── dialogues/       # Dialogue scripts (.dialogue)
├── dialogue_template/
├── fonts/
├── npc/             # NPC definitions
├── scenes/          # Game scenes (.tscn)
├── scripts/         # GDScript files
├── ui/              # UI scenes and components
└── Main.tscn        # Entry scene
```

---

## Getting Started

1. Clone or download the repository.
2. Open the project in **Godot 4.7+**.
3. Run `Main.tscn` to start the game.
