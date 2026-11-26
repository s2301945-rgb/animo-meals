# Menu cover artwork

All 28 currently recorded meals use 12 coordinated illustrations selected by food name in `frontend/src/FoodCover.jsx`. These are illustrative covers, not vendor photographs or guarantees of serving size. Menu cards and the carousel label this distinction. Catalog records, recorded prices and saved meal boxes are unchanged.

The built-in image-generation tool produced the original artwork. The production asset is `frontend/public/images/menu-food-atlas.webp`, a 1086 × 1448 image encoded as WebP at quality 90 (about 288 KiB). All cards share one cached asset. CSS selects one of its twelve square tiles; each food image retains its square proportions. The original PNG was generated at about 2.3 MiB; the WebP encoding reduces transfer size by about 88% without resizing the artwork.

Prompt direction: Create one precise 3-column by 4-row food illustration atlas for a Philippine student food-budget website. Equal square tiles; cream background, forest-green bowls and warm golden food colors. Consistent three-quarter overhead view, refined editorial food illustration, centered dishes, soft lighting, no brands, text, faces or watermarks. Rows, left to right:

1. Fried chicken, burger, Filipino spaghetti.
2. Hungarian sausage with rice and fries, chicken pastil rice bowl, pork sisig rice bowl.
3. Siomai rice bowl, spare ribs with rice, flavored fries.
4. Chicken popcorn, chicken fries, fries and chicken popcorn snack mix.

Matching prioritizes mixes and specific dish names before broad chicken/fries terms. Meal variants within a food family share its cover; the written menu remains the source of included components and price. Unrecognized future meals receive a category cover rather than an unrelated food illustration. If a real `image_url` is provided later, that image appears automatically; failed photo loads fall back to the cover.

To change a family’s artwork, replace the corresponding tile in a new atlas and update its file URL. To change classification, edit the ordered matching rules in `FoodCover.jsx`. Keep the per-card illustration caption and accessible image description when using synthetic artwork.

Verification: lint/build pass; browser checks cover all 28 menu items, 12 distinct artwork positions, the carousel and no horizontal overflow at 1440, 390 and 320 pixels. Existing Meal Box editor browser checks also pass.
