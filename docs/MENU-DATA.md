# Recorded menu dataset

No daily stock administration is required. The developer imports a reviewed list of regular offerings and prices. Update the dataset when reliable changes are reported or during an occasional review. Visitors must confirm current price and actual availability at the shop.

Start from `backend/data/menu-template.json`. It contains the five selected shops and intentionally blank `menu_items` arrays. Add only supplied, verified menu information. Each menu item needs:

- `name`: actual item name, up to 120 characters.
- `price`: recorded PHP price, positive and at most PHP 10,000, up to two decimal places.
- `category`: Main dish, Drink, Snack or Side.
- `description`: optional verified details; do not infer ingredients or spice level.
- `is_listed`: optional boolean, defaults true. False retires a listing from recommendations; it is not a stock sensor.

From `backend`, validate without writing:

```powershell
.venv/Scripts/python.exe -m app.import_menu data/menu-template.json
```

After reviewing the dataset and intended database, append `--apply` to write it in one transaction. The importer matches exact shop/item names, updates listed data and adds missing entries. Duplicate shops/items and unknown shop names are rejected. Omitted entries are preserved; an empty array never clears a shop. Renaming an item creates a new entry, so explicitly retire the old name if needed. Shop locations and existing image URLs are preserved. No public website endpoint can run this command.

`app.shop_catalog` adds missing selected shops without adding meals. The old `app.seed` is strictly fictional local/test data; never use it for production menus. Alembic revision 0003 preserves all existing catalog records.

Photo uploads are outside the revised scope. Existing public photos can continue to render. Price recommendation logic does not depend on photos. Maria Rosa's location remains unconfirmed; confirm it before changing the recorded location through a reviewed developer data update.

`backend/data/potato-corner-menu.json` lists Potato Corner items under USLS Agora using North Drive's Foodpanda menu as a reference. Confirm current offerings and counter prices at USLS Agora. [Potato Corner North Drive](https://www.foodpanda.ph/restaurant/mjnw/potato-corner-north-drive)

The La Salle delivery dataset includes selected items from two Bacolod branches. It records Foodpanda item prices, or the starting price where the menu lists variants. Delivery fees, minimum order amounts, and promotions are separate. Check the branch for counter prices. [Jollibee Bacolod La Salle](https://www.foodpanda.ph/restaurant/r9ql/jollibee-bacolod-la-salle) · [McDonald's North Drive La Salle](https://www.foodpanda.ph/restaurant/r8sy/mcdonalds-north-drive-la-salle)

## Production snapshot

The four files below mirror 28 published items across nine shops. They preserve the names, prices, and descriptions returned by production. Their starting point is a recorded catalog, so they do not independently verify today's counter prices.

| Dataset | Items |
| --- | --- |
| backend/data/campus-menu.json | 5 |
| backend/data/la-salle-delivery-menu.json | 8 |
| backend/data/potato-corner-menu.json | 12 |
| backend/data/unnamed-rice-bowls.json | 3 |

The eight unimported entries in the older delivery draft were reconciled by replacing that draft with the actual published catalog. The snapshot preserves published names and prices.

The blank shop name in unnamed-rice-bowls.json is intentional. Supply its name and location before relying on it as a destination in the presentation. [Recorded snapshot](verification/catalog-snapshot.json)
