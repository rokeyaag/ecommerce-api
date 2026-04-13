import React from 'react';
import { useCart } from '../context/CartContext';

const CartPage = ({ onClose }) => {
  const { cartItems, removeFromCart, increaseQty, decreaseQty, totalPrice, clearCart } = useCart();

  return (
    <div style={{
      position: 'fixed', top: 0, right: 0,
      width: '400px', height: '100vh',
      background: '#0f3460',
      boxShadow: '-4px 0 20px rgba(0,0,0,0.5)',
      zIndex: 1000, display: 'flex',
      flexDirection: 'column',
      animation: 'slideIn 0.3s ease',
    }}>

      {/* Header */}
      <div style={{
        padding: '20px', borderBottom: '1px solid rgba(255,255,255,0.1)',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
      }}>
        <h2 style={{ color: '#fff', fontSize: '22px', fontWeight: '800' }}>
          🛒 আমার Cart
        </h2>
        <button onClick={onClose} style={{
          background: 'rgba(255,255,255,0.1)',
          border: 'none', color: '#fff',
          width: '36px', height: '36px',
          borderRadius: '50%', cursor: 'pointer',
          fontSize: '18px',
        }}>✕</button>
      </div>

      {/* Cart Items */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '16px' }}>
        {cartItems.length === 0 ? (
          <div style={{
            textAlign: 'center', padding: '60px 20px',
            color: 'rgba(255,255,255,0.5)',
          }}>
            <div style={{ fontSize: '64px', marginBottom: '16px' }}>🛒</div>
            <p style={{ fontSize: '18px' }}>Cart খালি আছে!</p>
            <button onClick={onClose} style={{
              marginTop: '16px', padding: '10px 24px',
              background: 'linear-gradient(135deg, #e94560, #0f3460)',
              color: 'white', border: 'none', borderRadius: '25px',
              cursor: 'pointer', fontWeight: '700',
            }}>
              Shopping করুন
            </button>
          </div>
        ) : (
          cartItems.map(item => (
            <div key={item.id} style={{
              background: 'rgba(255,255,255,0.05)',
              borderRadius: '12px', padding: '16px',
              marginBottom: '12px',
              border: '1px solid rgba(255,255,255,0.1)',
            }}>
              <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>

                {/* Image */}
                <div style={{
                  width: '60px', height: '60px',
                  background: 'rgba(255,255,255,0.1)',
                  borderRadius: '8px', display: 'flex',
                  alignItems: 'center', justifyContent: 'center',
                  fontSize: '24px', flexShrink: 0,
                }}>
                  {item.image ? (
                    <img src={item.image} alt={item.name}
                         style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: '8px' }} />
                  ) : '🛍️'}
                </div>

                {/* Info */}
                <div style={{ flex: 1 }}>
                  <div style={{ color: '#fff', fontWeight: '700', marginBottom: '4px' }}>
                    {item.name}
                  </div>
                  <div style={{
                    fontSize: '16px', fontWeight: '800',
                    background: 'linear-gradient(135deg, #e94560, #0f3460)',
                    WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
                  }}>
                    ৳{item.price}
                  </div>
                </div>

                {/* Remove */}
                <button onClick={() => removeFromCart(item.id)} style={{
                  background: 'rgba(233,69,96,0.2)',
                  border: 'none', color: '#e94560',
                  width: '30px', height: '30px',
                  borderRadius: '50%', cursor: 'pointer',
                  fontSize: '14px',
                }}>✕</button>
              </div>

              {/* Quantity Control */}
              <div style={{
                display: 'flex', alignItems: 'center',
                justifyContent: 'space-between', marginTop: '12px',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <button onClick={() => decreaseQty(item.id)} style={{
                    width: '32px', height: '32px',
                    background: 'rgba(255,255,255,0.1)',
                    border: 'none', color: '#fff',
                    borderRadius: '8px', cursor: 'pointer',
                    fontSize: '18px', fontWeight: '700',
                  }}>−</button>
                  <span style={{ color: '#fff', fontWeight: '700', fontSize: '16px' }}>
                    {item.quantity}
                  </span>
                  <button onClick={() => increaseQty(item.id)} style={{
                    width: '32px', height: '32px',
                    background: 'rgba(255,255,255,0.1)',
                    border: 'none', color: '#fff',
                    borderRadius: '8px', cursor: 'pointer',
                    fontSize: '18px', fontWeight: '700',
                  }}>+</button>
                </div>
                <div style={{ color: '#fff', fontWeight: '700' }}>
                  ৳{item.price * item.quantity}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Footer */}
      {cartItems.length > 0 && (
        <div style={{
          padding: '20px',
          borderTop: '1px solid rgba(255,255,255,0.1)',
        }}>
          <div style={{
            display: 'flex', justifyContent: 'space-between',
            marginBottom: '16px',
          }}>
            <span style={{ color: 'rgba(255,255,255,0.7)', fontSize: '16px' }}>
              মোট:
            </span>
            <span style={{
              color: '#fff', fontSize: '22px', fontWeight: '800',
            }}>
              ৳{totalPrice}
            </span>
          </div>

          <button style={{
            width: '100%', padding: '14px',
            background: 'linear-gradient(135deg, #e94560, #0f3460)',
            color: 'white', border: 'none',
            borderRadius: '12px', cursor: 'pointer',
            fontWeight: '800', fontSize: '16px',
            marginBottom: '8px',
          }}>
            💳 Checkout করুন
          </button>

          <button onClick={clearCart} style={{
            width: '100%', padding: '10px',
            background: 'rgba(255,255,255,0.1)',
            color: 'rgba(255,255,255,0.7)',
            border: 'none', borderRadius: '12px',
            cursor: 'pointer', fontSize: '14px',
          }}>
            🗑️ Cart খালি করুন
          </button>
        </div>
      )}
    </div>
  );
};

export default CartPage;