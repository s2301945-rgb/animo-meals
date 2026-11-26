import Photo from "./Photo.jsx";

// Row-major positions in the shared 3 × 4 illustration atlas.
const covers = [
  [/mix|party/i, 11, "Snack mix"],
  [/chicken fries/i, 10, "Chicken fries"],
  [/chicken pops|popcorn/i, 9, "Chicken bites"],
  [/spare ribs|ribs/i, 7, "Spare ribs"],
  [/siomai/i, 6, "Siomai rice bowl"],
  [/sisig/i, 5, "Sisig rice bowl"],
  [/pastil/i, 4, "Chicken pastil"],
  [/hungarian|sausage/i, 3, "Sausage meal"],
  [/spaghetti|pasta/i, 2, "Spaghetti"],
  [/burger/i, 1, "Burger"],
  [/chicken|manok/i, 0, "Chicken"],
  [/fries/i, 8, "Flavored fries"],
];

export default function FoodCover({ item }) {
  const cover = covers.find(([pattern]) => pattern.test(item.name));
  const index = cover?.[1];
  const fallback = (
    <div className={`food-cover ${cover ? "" : "food-cover-generic"}`}>
      {cover ? (
        <div
          className="food-cover-art"
          role="img"
          aria-label={`${cover[2]} illustration; not an actual photo of ${item.name}`}
          style={{ backgroundPosition: `${(index % 3) * 50}% ${Math.floor(index / 3) * 100 / 3}%` }}
        />
      ) : (
        <span className="food-cover-type" aria-hidden="true">{item.category}</span>
      )}
      <span className="food-cover-caption">Menu illustration</span>
    </div>
  );
  return <Photo src={item.image_url} alt={item.name} className="food-photo" fallback={fallback} />;
}
