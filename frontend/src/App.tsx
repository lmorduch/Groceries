// ABOUTME: Root app component with nav and route definitions
// ABOUTME: Three main areas: Templates, Shopping Sessions, Inventory

import { Route, Routes, NavLink } from "react-router-dom";
import TemplatesPage from "./pages/TemplatesPage";
import TemplatePage from "./pages/TemplatePage";
import SessionsPage from "./pages/SessionsPage";
import SessionPage from "./pages/SessionPage";
import StoresPage from "./pages/StoresPage";
import StorePage from "./pages/StorePage";
import InventoryPage from "./pages/InventoryPage";
import "./App.css";

function App() {
  return (
    <div className="app">
      <nav className="nav">
        <span className="nav-brand">🛒 Groceries</span>
        <NavLink to="/" end>Sessions</NavLink>
        <NavLink to="/templates">Templates</NavLink>
        <NavLink to="/stores">Stores</NavLink>
        <NavLink to="/inventory">Inventory</NavLink>
      </nav>
      <main className="main">
        <Routes>
          <Route path="/" element={<SessionsPage />} />
          <Route path="/sessions/:id" element={<SessionPage />} />
          <Route path="/templates" element={<TemplatesPage />} />
          <Route path="/templates/:id" element={<TemplatePage />} />
          <Route path="/stores" element={<StoresPage />} />
          <Route path="/stores/:id" element={<StorePage />} />
          <Route path="/inventory" element={<InventoryPage />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
