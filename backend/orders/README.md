# Coffee Orders Directory

This directory stores coffee orders placed through the Coffee Shop Barista agent.

Each order is saved as a JSON file with a timestamp in the filename format: `order_YYYYMMDD_HHMMSS.json`

## Order Format

Each order JSON file contains:

```json
{
  "drinkType": "latte",
  "size": "medium",
  "milk": "oat",
  "extras": ["vanilla syrup", "extra shot"],
  "name": "Customer Name",
  "timestamp": "2024-01-23T14:30:25.123456"
}
```

## Fields

- **drinkType**: The type of coffee drink (e.g., latte, cappuccino, espresso, americano, mocha)
- **size**: Small, medium, or large
- **milk**: Type of milk (whole, skim, oat, almond, soy, coconut, or none)
- **extras**: Array of additional items (e.g., extra shot, syrups, whipped cream)
- **name**: Customer's name for the order
- **timestamp**: ISO format timestamp when the order was placed

## Note

This directory is created automatically when the first order is placed. Order files are not tracked in git by default (see .gitignore).
