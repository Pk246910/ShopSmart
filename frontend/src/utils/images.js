const PRODUCT_PLACEHOLDER = "/products/product-placeholder.svg";
const DATA_URI_FALLBACK = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 350'%3E%3Cdefs%3E%3ClinearGradient id='bg' x1='0%25' y1='0%25' x2='100%25' y2='100%25'%3E%3Cstop offset='0%25' style='stop-color:%230f172a;stop-opacity:1'/%3E%3Cstop offset='100%25' style='stop-color:%231e293b;stop-opacity:1'/%3E%3C/linearGradient%3E%3C/defs%3E%3Crect width='400' height='350' rx='12' fill='url(%23bg)'/%3E%3Crect x='155' y='110' width='90' height='120' rx='10' fill='none' stroke='%2306b6d4' stroke-width='3' opacity='0.3'/%3E%3Ccircle cx='200' cy='190' r='8' fill='%2306b6d4' opacity='0.2'/%3E%3Ctext x='200' y='290' text-anchor='middle' font-family='system-ui' font-size='13' font-weight='600' fill='%2364748b' opacity='0.6'%3ENo Image%3C/text%3E%3C/svg%3E";

export function getProductImage(imageUrl) {
  if (!imageUrl) return PRODUCT_PLACEHOLDER;
  if (imageUrl.startsWith("/products/") && imageUrl.endsWith(".svg")) {
    return imageUrl;
  }
  return imageUrl;
}

export function handleImageError(e) {
  if (e.target.dataset.fallback) return;
  e.target.dataset.fallback = "1";
  const original = e.target.src;
  if (original && !original.includes("data:image")) {
    e.target.src = PRODUCT_PLACEHOLDER;
  } else {
    e.target.src = DATA_URI_FALLBACK;
  }
}
