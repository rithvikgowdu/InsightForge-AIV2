"use client";

import React from "react";
import { useAuth } from "@/lib/auth-context";
import { formatDate } from "@/lib/utils";
import {
  Mail,
  Calendar,
  LogOut,
} from "lucide-react";

export default function AccountPage() {
  const { user, logout } = useAuth();

  return (
    <div className="max-w-3xl mx-auto space-y-8 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Account Settings
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Manage your personal profile, credentials, and workspace preferences.
        </p>
      </div>

      {/* Profile Card */}
      <div className="bg-white rounded-2xl border border-slate-200/90 shadow-2xs p-8 space-y-6">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-indigo-600 to-violet-500 text-white flex items-center justify-center font-bold text-2xl shadow-sm uppercase">
            {user?.username ? user.username.slice(0, 2) : "U"}
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-900">
              {user?.full_name || user?.username}
            </h2>
            <p className="text-xs text-slate-500">@{user?.username}</p>
          </div>
        </div>

        <div className="h-px bg-slate-100" />

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 space-y-1">
            <div className="flex items-center gap-2 text-slate-500 text-xs font-semibold uppercase tracking-wider">
              <Mail className="w-4 h-4 text-indigo-600" />
              <span>Email Address</span>
            </div>
            <p className="text-sm font-semibold text-slate-900">{user?.email}</p>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 space-y-1">
            <div className="flex items-center gap-2 text-slate-500 text-xs font-semibold uppercase tracking-wider">
              <Calendar className="w-4 h-4 text-indigo-600" />
              <span>Member Since</span>
            </div>
            <p className="text-sm font-semibold text-slate-900">
              {formatDate(user?.created_at)}
            </p>
          </div>
        </div>

        {/* System & Privacy Info */}
        <div className="space-y-3 pt-2">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
            System & Security Status
          </h3>
          <div className="p-4 rounded-xl border border-slate-200 space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="text-slate-600 font-medium">Session Protection:</span>
              <span className="font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded border border-emerald-200">
                JWT Auth Active
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-600 font-medium">Data Isolation:</span>
              <span className="font-semibold text-slate-800">
                Enforced per user_id
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-600 font-medium">GitHub API Connector:</span>
              <span className="font-semibold text-slate-800">
                Public Read-Only API
              </span>
            </div>
          </div>
        </div>

        {/* Logout Button */}
        <div className="pt-4 border-t border-slate-100 flex justify-end">
          <button
            onClick={logout}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold text-rose-700 bg-rose-50 hover:bg-rose-100 border border-rose-200 transition-colors cursor-pointer"
          >
            <LogOut className="w-4 h-4" />
            <span>Sign Out of Account</span>
          </button>
        </div>
      </div>
    </div>
  );
}
