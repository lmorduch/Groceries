// ABOUTME: Typed API client for all backend endpoints
// ABOUTME: Uses axios with a base URL from env var

import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000",
});

export interface TemplateItem {
  id: number;
  template_list_id: number;
  name: string;
  category: string | null;
  position: number;
}

export interface TemplateList {
  id: number;
  name: string;
  created_at: string;
  updated_at: string;
  items: TemplateItem[];
}

export interface SessionItem {
  id: number;
  session_id: number;
  name: string;
  category: string | null;
  position: number;
  checked: boolean;
  in_cart: boolean;
  store_section_id: number | null;
  section_overridden: boolean;
}

export interface ShoppingSession {
  id: number;
  template_list_id: number | null;
  store_id: number | null;
  name: string;
  date: string;
  completed: boolean;
  created_at: string;
  items: SessionItem[];
}

export interface SectionKeyword {
  id: number;
  section_id: number;
  keyword: string;
}

export interface StoreSection {
  id: number;
  store_id: number;
  name: string;
  position: number;
  keywords: SectionKeyword[];
}

export interface Store {
  id: number;
  name: string;
  sections: StoreSection[];
}

export interface InventoryCheck {
  id: number;
  session_id: number | null;
  name: string;
  have_it: boolean | null;
  notes: string | null;
  created_at: string;
}

// Templates
export const getTemplates = () => api.get<TemplateList[]>("/templates/").then((r) => r.data);
export const getTemplate = (id: number) => api.get<TemplateList>(`/templates/${id}`).then((r) => r.data);
export const createTemplate = (data: { name: string; items?: { name: string; category?: string }[] }) =>
  api.post<TemplateList>("/templates/", data).then((r) => r.data);
export const updateTemplate = (id: number, data: { name?: string }) =>
  api.patch<TemplateList>(`/templates/${id}`, data).then((r) => r.data);
export const deleteTemplate = (id: number) => api.delete(`/templates/${id}`);
export const addTemplateItem = (templateId: number, data: { name: string; category?: string }) =>
  api.post<TemplateItem>(`/templates/${templateId}/items`, data).then((r) => r.data);
export const updateTemplateItem = (templateId: number, itemId: number, data: Partial<TemplateItem>) =>
  api.patch<TemplateItem>(`/templates/${templateId}/items/${itemId}`, data).then((r) => r.data);
export const deleteTemplateItem = (templateId: number, itemId: number) =>
  api.delete(`/templates/${templateId}/items/${itemId}`);

// Sessions
export const getSessions = () => api.get<ShoppingSession[]>("/sessions/").then((r) => r.data);
export const getSession = (id: number) => api.get<ShoppingSession>(`/sessions/${id}`).then((r) => r.data);
export const createSession = (data: { name: string; template_list_id?: number; store_id?: number }) =>
  api.post<ShoppingSession>("/sessions/", data).then((r) => r.data);
export const updateSession = (id: number, data: { name?: string; completed?: boolean; store_id?: number | null }) =>
  api.patch<ShoppingSession>(`/sessions/${id}`, data).then((r) => r.data);
export const deleteSession = (id: number) => api.delete(`/sessions/${id}`);
export const addSessionItem = (sessionId: number, data: { name: string; category?: string }) =>
  api.post<SessionItem>(`/sessions/${sessionId}/items`, data).then((r) => r.data);
export const updateSessionItem = (sessionId: number, itemId: number, data: Partial<SessionItem>) =>
  api.patch<SessionItem>(`/sessions/${sessionId}/items/${itemId}`, data).then((r) => r.data);
export const deleteSessionItem = (sessionId: number, itemId: number) =>
  api.delete(`/sessions/${sessionId}/items/${itemId}`);

// Stores
export const getStores = () => api.get<Store[]>("/stores/").then((r) => r.data);
export const getStore = (id: number) => api.get<Store>(`/stores/${id}`).then((r) => r.data);
export const createStore = (data: { name: string }) => api.post<Store>("/stores/", data).then((r) => r.data);
export const updateStore = (id: number, data: { name?: string }) =>
  api.patch<Store>(`/stores/${id}`, data).then((r) => r.data);
export const deleteStore = (id: number) => api.delete(`/stores/${id}`);
export const addStoreSection = (storeId: number, data: { name: string; position?: number }) =>
  api.post<StoreSection>(`/stores/${storeId}/sections`, data).then((r) => r.data);
export const updateStoreSection = (storeId: number, sectionId: number, data: { name?: string; position?: number }) =>
  api.patch<StoreSection>(`/stores/${storeId}/sections/${sectionId}`, data).then((r) => r.data);
export const deleteStoreSection = (storeId: number, sectionId: number) =>
  api.delete(`/stores/${storeId}/sections/${sectionId}`);
export const addSectionKeyword = (storeId: number, sectionId: number, keyword: string) =>
  api.post<SectionKeyword>(`/stores/${storeId}/sections/${sectionId}/keywords`, { keyword }).then((r) => r.data);
export const deleteSectionKeyword = (storeId: number, sectionId: number, keywordId: number) =>
  api.delete(`/stores/${storeId}/sections/${sectionId}/keywords/${keywordId}`);

// Inventory
export const getInventory = (sessionId?: number) =>
  api.get<InventoryCheck[]>("/inventory/", { params: sessionId ? { session_id: sessionId } : {} }).then((r) => r.data);
export const createInventoryCheck = (data: { name: string; session_id?: number; notes?: string }) =>
  api.post<InventoryCheck>("/inventory/", data).then((r) => r.data);
export const updateInventoryCheck = (id: number, data: { have_it?: boolean | null; notes?: string }) =>
  api.patch<InventoryCheck>(`/inventory/${id}`, data).then((r) => r.data);
export const deleteInventoryCheck = (id: number) => api.delete(`/inventory/${id}`);
