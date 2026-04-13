import React from 'react';
import { useCart } from '../context/CartContext';

const Navbar = ({ onCartClick }) => {
  const { totalItems } = useCart();

  return (
    <nav style={{
      background: 'rgba(15, 52, 96, 0.95)',
      backdropFilter: 'blur(10px)',
      padding: '0 2rem',
      height: '64px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      position: 'sticky',
      top: 0,
      zIndex: 100,
      borderBottom: '1px solid rgba(255,255,255,0.1)',
    }}>
      {/* Logo */}
      <div style={{
        color: '#fff',
        fontSize: '24px',
        fontWeight: '800',
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
      }}>
        🛍️ ShopBD
      </div>

      {/* Search */}
      <div style={{
        flex: 1,
        maxWidth: '400px',
        margin: '0 2rem',
        position: 'relative',
      }}>
        <input
          type="text"
          placeholder="🔍 Product খুঁজুন..."
          style={{
            width: '100%',
            padding: '10px 16px',
            borderRadius: '25px',
            border: '1px solid rgba(255,255,255,0.2)',
            background: 'rgba(255,255,255,0.1)',
            color: '#fff',
            fontSize: '14px',
            outline: 'none',
          }}
        />
      </div>

      {/* Cart Button */}
      <button
        onClick={onCartClick}
        style={{
          background: 'linear-gradient(135deg, #e94560, #0f3460)',
          color: 'white',
          border: 'none',
          borderRadius: '25px',
          padding: '10px 20px',
          cursor: 'pointer',
          fontWeight: '700',
          fontSize: '15px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          position: 'relative',
        }}>
        🛒 Cart
        {totalItems > 0 && (
          <span style={{
            background: '#e94560',
            color: 'white',
            borderRadius: '50%',
            width: '22px',
            height: '22px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '12px',
            fontWeight: '800',
            border: '2px solid white',
          }}>
            {totalItems}
          </span>
        )}
      </button>
    </nav>
  );
};

export default Navbar;