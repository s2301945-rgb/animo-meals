import { useState } from "react";

export default function Photo({
  src,
  alt,
  className = "",
  fallback = null,
  loading = "lazy",
}) {
  const [failed, setFailed] = useState(null);
  return src && failed !== src ? (
    <img
      className={className}
      src={src}
      alt={alt}
      loading={loading}
      decoding="async"
      referrerPolicy="no-referrer"
      onError={() => setFailed(src)}
    />
  ) : (
    fallback
  );
}
