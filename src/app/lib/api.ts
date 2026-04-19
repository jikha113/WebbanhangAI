import type { CatalogQuery, CategoryNode, Product } from "../data/products";

const API_BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ??
  "http://127.0.0.1:8000/api";

async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    throw new Error(`API error ${response.status}`);
  }
  return response.json() as Promise<T>;
}

function buildProductQueryString(query: CatalogQuery = {}) {
  const params = new URLSearchParams();

  if (query.category) {
    params.set("category", query.category);
  }
  if (query.search) {
    params.set("search", query.search);
  }
  if (query.isNew) {
    params.set("new", "true");
  }
  if (query.isSale) {
    params.set("sale", "true");
  }
  if (query.minPrice != null) {
    params.set("min_price", String(query.minPrice));
  }
  if (query.maxPrice != null) {
    params.set("max_price", String(query.maxPrice));
  }
  if (query.sort && query.sort !== "featured") {
    params.set("sort", query.sort);
  }
  for (const subcategory of query.subcategory ?? []) {
    params.append("subcategory", subcategory);
  }

  return params.toString();
}

export async function fetchProducts(query: CatalogQuery = {}): Promise<Product[]> {
  const queryString = buildProductQueryString(query);
  const querySuffix = queryString ? `?${queryString}` : "";
  return apiGet<Product[]>(`/products/${querySuffix}`);
}

export async function fetchCategories(): Promise<CategoryNode[]> {
  return apiGet<CategoryNode[]>("/products/categories/");
}

export async function fetchProductById(id: string): Promise<Product> {
  return apiGet<Product>(`/products/${id}/`);
}

export async function fetchForYouRecommendations(
  userId?: string,
  limitOrSession: number | string = 8,
  maybeLimitOrSession?: number | string,
): Promise<Product[]> {
  let limit = 8;
  let sessionId = "guest-demo";

  if (typeof limitOrSession === "number") {
    limit = limitOrSession;
    if (typeof maybeLimitOrSession === "string") {
      sessionId = maybeLimitOrSession;
    }
  } else {
    sessionId = limitOrSession;
    if (typeof maybeLimitOrSession === "number") {
      limit = maybeLimitOrSession;
    }
  }

  const params = new URLSearchParams({ limit: String(limit) });
  if (userId) {
    params.set("user_id", userId);
  } else {
    params.set("session_id", sessionId);
  }
  return apiGet<Product[]>(`/recommendations/for-you/?${params.toString()}`);
}

export async function fetchRelatedProducts(
  productId: string,
  limit = 4,
): Promise<Product[]> {
  const params = new URLSearchParams({ limit: String(limit) });
  return apiGet<Product[]>(
    `/recommendations/related/${productId}/?${params.toString()}`,
  );
}
