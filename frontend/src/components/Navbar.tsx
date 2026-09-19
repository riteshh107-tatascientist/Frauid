/**
 * Navigation Navbar
 * Main navigation with user menu and logout
 */

import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Menu, X, LogOut } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';

export const Navbar: React.FC = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <nav className="backdrop-blur-md bg-white/10 border-b border-white/20 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/dashboard" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">FG</span>
            </div>
            <span className="text-white font-bold hidden sm:inline">FraudGuard</span>
          </Link>

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center gap-6">
            <Link to="/dashboard" className="text-gray-300 hover:text-white transition">
              Dashboard
            </Link>
            <Link to="/transactions" className="text-gray-300 hover:text-white transition">
              Transactions
            </Link>
            {user?.role === 'ADMIN' && (
              <>
                <Link to="/admin" className="text-gray-300 hover:text-white transition">
                  Admin
                </Link>
                <Link to="/admin/alerts" className="text-gray-300 hover:text-white transition">
                  Alerts
                </Link>
              </>
            )}
          </div>

          {/* User Menu */}
          <div className="flex items-center gap-4">
            <div className="text-right hidden sm:block">
              <p className="text-white text-sm font-medium">{user?.username}</p>
              <p className="text-gray-400 text-xs">{user?.role}</p>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-3 py-2 text-gray-300 hover:text-white transition"
              title="Logout"
            >
              <LogOut className="w-5 h-5" />
              <span className="hidden sm:inline">Logout</span>
            </button>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setMenuOpen(!menuOpen)}
              className="md:hidden text-gray-300 hover:text-white"
            >
              {menuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {menuOpen && (
          <div className="md:hidden pb-4 space-y-2">
            <Link
              to="/dashboard"
              className="block px-4 py-2 text-gray-300 hover:text-white hover:bg-white/10 rounded transition"
              onClick={() => setMenuOpen(false)}
            >
              Dashboard
            </Link>
            <Link
              to="/transactions"
              className="block px-4 py-2 text-gray-300 hover:text-white hover:bg-white/10 rounded transition"
              onClick={() => setMenuOpen(false)}
            >
              Transactions
            </Link>
            {user?.role === 'ADMIN' && (
              <>
                <Link
                  to="/admin"
                  className="block px-4 py-2 text-gray-300 hover:text-white hover:bg-white/10 rounded transition"
                  onClick={() => setMenuOpen(false)}
                >
                  Admin
                </Link>
                <Link
                  to="/admin/alerts"
                  className="block px-4 py-2 text-gray-300 hover:text-white hover:bg-white/10 rounded transition"
                  onClick={() => setMenuOpen(false)}
                >
                  Alerts
                </Link>
              </>
            )}
          </div>
        )}
      </div>
    </nav>
  );
};
