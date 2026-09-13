import React, { createContext, useContext, useState, useEffect } from "react";
import API from "../api/axios";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem("shopsmart_user");
    return saved ? JSON.parse(saved) : null;
  });
  const [guestId] = useState(() => {
    let gid = localStorage.getItem("shopsmart_guest_id");
    if (!gid) {
      gid = "guest_" + Math.random().toString(36).substring(2, 9);
      localStorage.setItem("shopsmart_guest_id", gid);
    }
    return gid;
  });

  const login = async (username, password) => {
    const res = await API.post("/users/login/", { username, password });
    const { access, refresh } = res.data;
    localStorage.setItem("shopsmart_access", access);
    localStorage.setItem("shopsmart_refresh", refresh);
    // fetch profile
    try {
      const me = await API.get("/users/me/", { headers: { Authorization: `Bearer ${access}` } });
      setUser(me.data);
      localStorage.setItem("shopsmart_user", JSON.stringify(me.data));
    } catch {
      const fallback = { username };
      setUser(fallback);
      localStorage.setItem("shopsmart_user", JSON.stringify(fallback));
    }
    return res.data;
  };

  const register = async (username, email, password) => {
    const res = await API.post("/users/register/", { username, email, password });
    if (res.data.tokens) {
      localStorage.setItem("shopsmart_access", res.data.tokens.access);
      localStorage.setItem("shopsmart_refresh", res.data.tokens.refresh);
      setUser(res.data.user);
      localStorage.setItem("shopsmart_user", JSON.stringify(res.data.user));
    }
    return res.data;
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem("shopsmart_access");
    localStorage.removeItem("shopsmart_refresh");
    localStorage.removeItem("shopsmart_user");
  };

  // On mount, try to restore user from token
  useEffect(() => {
    const token = localStorage.getItem("shopsmart_access");
    if (token && !user) {
      API.get("/users/me/")
        .then((res) => {
          setUser(res.data);
          localStorage.setItem("shopsmart_user", JSON.stringify(res.data));
        })
        .catch(() => {});
    }
  }, []);

  return (
    <AuthContext.Provider value={{ user, guestId, login, register, logout, setUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
