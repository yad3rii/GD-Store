import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout.jsx";
import StorePage from "./pages/StorePage.jsx";
import GamePage from "./pages/GamePage.jsx";
import CartPage from "./pages/CartPage.jsx";
import LibraryPage from "./pages/LibraryPage.jsx";
import ProfilePage from "./pages/ProfilePage.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import RegisterPage from "./pages/RegisterPage.jsx";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<StorePage />} />
        <Route path="/game/:slug" element={<GamePage />} />
        <Route path="/cart" element={<CartPage />} />
        <Route path="/library" element={<LibraryPage />} />
        <Route path="/profile/:id" element={<ProfilePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
      </Route>
    </Routes>
  );
}
