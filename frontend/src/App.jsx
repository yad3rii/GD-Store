import { Routes, Route } from "react-router-dom";
import { DemoProvider } from "./demo/context";
import { Shell, Store, NotFound } from "./studio/Studio";
import { Game, Collection, Profile } from "./studio/Personal";
import { Friends, Community, Workshop } from "./studio/Social";
import { Settings, Account, Orders } from "./studio/Account";
export default function App() {
  return (
    <DemoProvider>
      <Routes>
        <Route element={<Shell />}>
          <Route index element={<Store />} />
          <Route path="game/:slug" element={<Game />} />
          <Route
            path="library"
            element={<Collection key="library" kind="library" />}
          />
          <Route
            path="wishlist"
            element={<Collection key="wishlist" kind="wishlist" />}
          />
          <Route path="cart" element={<Collection key="cart" kind="cart" />} />
          <Route path="profile" element={<Profile />} />
          <Route path="profile/:id" element={<Profile />} />
          <Route path="friends" element={<Friends />} />
          <Route path="messages/:id" element={<Friends />} />
          <Route path="community" element={<Community />} />
          <Route path="community/:id" element={<Community />} />
          <Route path="workshop" element={<Workshop />} />
          <Route path="workshop/:id" element={<Workshop />} />
          <Route path="settings" element={<Settings />} />
          <Route path="login" element={<Account />} />
          <Route path="register" element={<Account register />} />
          <Route path="orders" element={<Orders />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </DemoProvider>
  );
}
