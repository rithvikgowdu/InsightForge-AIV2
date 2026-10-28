"use client";

import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { api, setStoredToken } from "./api";
import { User } from "./types";

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (usernameOrEmail: string, password: string) => Promise<void>;
  register: (
    email: string,
    username: string,
    password: string,
    fullName?: string
  ) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(() => {
    if (typeof window !== "undefined") {
      const cached = localStorage.getItem("insightforge_user");
      if (cached) {
        try {
          return JSON.parse(cached);
        } catch {
          // Ignore
        }
      }
    }
    return null;
  });

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const router = useRouter();

  const refreshUser = useCallback(async () => {
    try {
      const currentUser = await api.auth.me();
      setUser(currentUser);
      localStorage.setItem("insightforge_user", JSON.stringify(currentUser));
    } catch {
      setUser(null);
      setStoredToken(null);
      localStorage.removeItem("insightforge_user");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    const token = localStorage.getItem("insightforge_token");
    if (token) {
      refreshUser();
    } else {
      setIsLoading(false);
    }

    const handleUnauthorized = () => {
      setUser(null);
      setStoredToken(null);
      localStorage.removeItem("insightforge_user");
      router.push("/login");
    };

    window.addEventListener("insightforge_unauthorized", handleUnauthorized);
    return () => {
      window.removeEventListener("insightforge_unauthorized", handleUnauthorized);
    };
  }, [router, refreshUser]);

  const login = async (usernameOrEmail: string, password: string) => {
    const res = await api.auth.login({
      username_or_email: usernameOrEmail,
      password,
    });
    setStoredToken(res.access_token);
    setUser(res.user);
    localStorage.setItem("insightforge_user", JSON.stringify(res.user));
    router.push("/dashboard");
  };

  const register = async (
    email: string,
    username: string,
    password: string,
    fullName?: string
  ) => {
    await api.auth.register({
      email,
      username,
      password,
      full_name: fullName,
    });
    await login(username, password);
  };

  const logout = () => {
    setUser(null);
    setStoredToken(null);
    localStorage.removeItem("insightforge_user");
    router.push("/login");
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
