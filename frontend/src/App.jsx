import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import "./App.css";
import { ThemeProvider } from "./context/ThemeContext";
import { AuthProvider } from "./context/AuthContext";
import ErrorBoundary from "./components/ErrorBoundary";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import ProductDetail from "./pages/ProductDetail";
import ProductCatalog from "./pages/ProductCatalog";
import Recent from "./pages/Recent";
import Wishlist from "./pages/Wishlist";
import Alerts from "./pages/Alerts";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Profile from "./pages/Profile";
import Admin from "./pages/Admin";
import ForgotPassword from "./pages/ForgotPassword";
import AnalysisPage from "./pages/AnalysisPage";
import DecisionReport from "./pages/DecisionReport";
import NotFound from "./pages/NotFound";

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Router>
          <Toaster position="top-right" toastOptions={{ duration: 3000, style: { background: "var(--bg-secondary)", color: "var(--text-primary)", border: "1px solid var(--border-color)", borderRadius: "10px", fontSize: "0.88rem", fontWeight: 600 } }} />
          <div>
            <Navbar />
            <ErrorBoundary>
              <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/recent" element={<Recent />} />
              <Route path="/products" element={<ProductCatalog />} />
              <Route path="/product/:id" element={<ProductDetail />} />
              <Route path="/wishlist" element={<Wishlist />} />
              <Route path="/alerts" element={<Alerts />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/profile" element={<Profile />} />
              <Route path="/admin" element={<Admin />} />
              <Route path="/forgot-password" element={<ForgotPassword />} />
              <Route path="/analysis/:id" element={<AnalysisPage />} />
              <Route path="/report/:id" element={<DecisionReport />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
            </ErrorBoundary>
          </div>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
