"use client";

import React, { useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import {
  History,
  PlusCircle,
  LogOut,
  Menu,
  X,
} from "lucide-react";

export function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-200/80 bg-white/95 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo */}
        <Link href={isAuthenticated ? "/dashboard" : "/"} className="flex items-center gap-2.5 group">
          <div className="w-9 h-9 rounded-xl overflow-hidden bg-white border border-slate-200/90 flex items-center justify-center shadow-xs transition-transform group-hover:scale-105 p-1">
            <Image
              src="/logo.png"
              alt="InsightForge AI Logo"
              width={32}
              height={32}
              className="w-full h-full object-contain"
              priority
            />
          </div>
          <div className="flex flex-col">
            <span className="font-bold text-lg text-slate-900 tracking-tight leading-none">
              InsightForge<span className="text-indigo-600 font-extrabold ml-0.5">AI</span>
            </span>
            <span className="text-[10px] text-slate-500 font-medium tracking-wide">
              Product Opportunity Intelligence
            </span>
          </div>
        </Link>

        {/* Desktop Nav */}
        <nav className="hidden md:flex items-center gap-6">
          {isAuthenticated ? (
            <>
              <Link
                href="/dashboard"
                className={`text-sm font-medium transition-colors ${
                  pathname === "/dashboard"
                    ? "text-indigo-600 font-semibold"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                Dashboard
              </Link>
              <Link
                href="/dashboard/new"
                className={`flex items-center gap-1.5 text-sm font-medium transition-colors ${
                  pathname === "/dashboard/new"
                    ? "text-indigo-600 font-semibold"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                <PlusCircle className="w-4 h-4" />
                New Analysis
              </Link>
              <Link
                href="/dashboard/history"
                className={`flex items-center gap-1.5 text-sm font-medium transition-colors ${
                  pathname === "/dashboard/history"
                    ? "text-indigo-600 font-semibold"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                <History className="w-4 h-4" />
                History
              </Link>

              <div className="h-5 w-px bg-slate-200 mx-1" />

              <div className="flex items-center gap-3">
                <Link
                  href="/dashboard/account"
                  className="flex items-center gap-2 text-sm text-slate-700 hover:text-slate-900 font-medium py-1 px-2.5 rounded-lg hover:bg-slate-100 transition-colors"
                >
                  <div className="w-7 h-7 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-xs uppercase">
                    {user?.username ? user.username.slice(0, 2) : "U"}
                  </div>
                  <span className="max-w-[120px] truncate">{user?.username}</span>
                </Link>

                <button
                  onClick={logout}
                  title="Sign Out"
                  className="text-slate-500 hover:text-rose-600 p-2 rounded-lg hover:bg-slate-100 transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            </>
          ) : (
            <>
              <Link
                href="/#features"
                className="text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors"
              >
                Features
              </Link>
              <Link
                href="/#how-it-works"
                className="text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors"
              >
                How It Works
              </Link>
              <Link
                href="/#sample-report"
                className="text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors"
              >
                Example Report
              </Link>

              <div className="h-5 w-px bg-slate-200 mx-1" />

              <Link
                href="/login"
                className="text-sm font-medium text-slate-700 hover:text-slate-900 px-3 py-2 rounded-lg hover:bg-slate-100 transition-colors"
              >
                Sign In
              </Link>

              <Link
                href="/register"
                className="text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 px-4 py-2 rounded-lg shadow-sm shadow-indigo-200 hover:shadow transition-all"
              >
                Get Started
              </Link>
            </>
          )}
        </nav>

        {/* Mobile menu button */}
        <div className="flex md:hidden items-center gap-2">
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 text-slate-600 hover:text-slate-900 rounded-lg hover:bg-slate-100"
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden border-b border-slate-200 bg-white px-4 pt-2 pb-6 space-y-3">
          {isAuthenticated ? (
            <>
              <div className="py-2 border-b border-slate-100 flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-xs uppercase">
                  {user?.username ? user.username.slice(0, 2) : "U"}
                </div>
                <div>
                  <p className="text-sm font-semibold text-slate-900">{user?.username}</p>
                  <p className="text-xs text-slate-500">{user?.email}</p>
                </div>
              </div>
              <Link
                href="/dashboard"
                onClick={() => setMobileMenuOpen(false)}
                className="block text-sm font-medium text-slate-700 hover:text-indigo-600 py-2"
              >
                Dashboard
              </Link>
              <Link
                href="/dashboard/new"
                onClick={() => setMobileMenuOpen(false)}
                className="block text-sm font-medium text-slate-700 hover:text-indigo-600 py-2"
              >
                New Analysis
              </Link>
              <Link
                href="/dashboard/history"
                onClick={() => setMobileMenuOpen(false)}
                className="block text-sm font-medium text-slate-700 hover:text-indigo-600 py-2"
              >
                Analysis History
              </Link>
              <Link
                href="/dashboard/account"
                onClick={() => setMobileMenuOpen(false)}
                className="block text-sm font-medium text-slate-700 hover:text-indigo-600 py-2"
              >
                Account Settings
              </Link>
              <button
                onClick={() => {
                  setMobileMenuOpen(false);
                  logout();
                }}
                className="w-full text-left text-sm font-medium text-rose-600 hover:text-rose-700 py-2 flex items-center gap-2"
              >
                <LogOut className="w-4 h-4" />
                Sign Out
              </button>
            </>
          ) : (
            <>
              <Link
                href="/#features"
                onClick={() => setMobileMenuOpen(false)}
                className="block text-sm font-medium text-slate-700 py-2"
              >
                Features
              </Link>
              <Link
                href="/#how-it-works"
                onClick={() => setMobileMenuOpen(false)}
                className="block text-sm font-medium text-slate-700 py-2"
              >
                How It Works
              </Link>
              <Link
                href="/#sample-report"
                onClick={() => setMobileMenuOpen(false)}
                className="block text-sm font-medium text-slate-700 py-2"
              >
                Example Report
              </Link>
              <div className="pt-2 border-t border-slate-100 flex flex-col gap-2">
                <Link
                  href="/login"
                  onClick={() => setMobileMenuOpen(false)}
                  className="w-full text-center text-sm font-semibold text-slate-800 bg-slate-100 py-2.5 rounded-lg"
                >
                  Sign In
                </Link>
                <Link
                  href="/register"
                  onClick={() => setMobileMenuOpen(false)}
                  className="w-full text-center text-sm font-semibold text-white bg-indigo-600 py-2.5 rounded-lg"
                >
                  Get Started
                </Link>
              </div>
            </>
          )}
        </div>
      )}
    </header>
  );
}
