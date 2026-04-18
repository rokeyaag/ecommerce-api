import React, { useState, useEffect } from 'react';
import { getToken } from '../api';

const API = 'http://localhost:8000';

const ProfilePage = ({ user, onClose }) => {
  const [tab, setTab] = useState('info');
  const [orders, setOrders] = useState([]);
  const [loadingOrders, setLoadingOrders] = useState(false);
  const [editing, setEditing] = useState(false);
  const [saved, setSaved] = useState(false);

  const [form, setForm] = useState({
    name: user || '',
    email: localStorage.getItem('email') || '',
    phone: localStorage.getItem('phone') || '',
  });

  const [addresses, setAddresses] = useState(
    JSON.parse(localStorage.getItem('addresses') || '[]')
  );
  const [newAddress, setNewAddress] = useState('');
  const [addingAddress, setAddingAddress] = useState(false);

  useEffect(() => {
    if (tab === 'orders') {
      setLoadingOrders(true);
      const token = getToken();
      fetch(`${API}/api/orders/`, {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then(r => r.json())
        .then(d => {
          const data = d.results || d;
          setOrders(Array.isArray(data) ? data : []);
          setLoadingOrders(false);
        })
        .catch(() => setLoadingOrders(false));
    }
  }, [tab]);

  const handleSave = () => {
    localStorage.setItem('email', form.email);
    localStorage.setItem('phone', form.phone);
    setSaved(true);
    setEditing(false);
    setTimeout(() => setSaved(false), 2000);
  };

  const handleAddAddress = () => {
    if (!newAddress.trim()) return;
    const updated = [...addresses, { id: Date.now(), text: newAddress, default: addresses.length === 0 }];
    setAddresses(updated);
    localStorage.setItem('addresses', JSON.stringify(updated));
    setNewAddress('');
    setAddingAddress(false);
  };

  const handleDeleteAddress = (id) => {
    const updated = addresses.filter(a => a.id !== id);
    setAddresses(updated);
    localStorage.setItem('addresses', JSON.stringify(updated));
  };

  const handleSetDefault = (id) => {
    const updated = addresses.map(a => ({ ...a, default: a.id === id }));
    setAddresses(updated);
    localStorage.setItem('addresses', JSON.stringify(updated));
  };

  const payLabel = (method) => ({
    cod: 'Cash on Delivery', bkash: 'bKash', nagad: 'Nagad',
    rocket: 'Rocket', ssl: 'SSL Commerz', upay: 'Upay',
  })[method] || method;

  const statusColor = (status) => ({
    confirmed: '#16a34a', pending: '#f97316',
    cancelled: '#ef4444', delivered: '#2563eb',
  })[status] || '#94a3b8';

  const inp = {
    width: '100%', padding: '11px 14px', borderRadius: '10px',
    border: '1.5px solid #e2e8f0', background: '#f8fafc',
    color: '#1e293b', fontSize: '14px', outline: 'none',
    boxSizing: 'border-box', marginBottom: '12px',
  };

  const tabs = [
    { id: 'info', label: 'My Profile', icon: '👤' },
    { id: 'orders', label: 'My Orders', icon: '📦' },
    { id: 'address', label: 'Address Book', icon: '📍' },
  ];

  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 2000,
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: 'rgba(0,0,0,0.5)', padding: '1rem',
    }} onClick={e => e.target === e.currentTarget && onClose()}>
      <div style={{
        background: '#fff', borderRadius: '20px', width: '100%',
        maxWidth: '680px', maxHeight: '90vh', overflow: 'hidden',
        boxShadow: '0 24px 64px rgba(0,0,0,0.18)',
        display: 'flex', flexDirection: 'column',
      }}>

        {/* Header */}
        <div style={{
          background: 'linear-gradient(135deg, #f97316, #ea580c)',
          padding: '1.5rem', display: 'flex', alignItems: 'center', gap: '16px',
        }}>
          <div style={{
            width: '60px', height: '60px', borderRadius: '50%',
            background: 'rgba(255,255,255,0.25)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '24px', fontWeight: '900', color: '#fff',
            border: '3px solid rgba(255,255,255,0.4)',
          }}>
            {(user || 'U')[0].toUpperCase()}
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ color: '#fff', fontWeight: '900', fontSize: '20px' }}>{user}</div>
            <div style={{ color: 'rgba(255,255,255,0.8)', fontSize: '13px' }}>
              {form.email || 'No email set'}
            </div>
          </div>
          <button onClick={onClose} style={{
            background: 'rgba(255,255,255,0.2)', border: 'none',
            color: '#fff', width: '36px', height: '36px',
            borderRadius: '50%', cursor: 'pointer', fontSize: '18px',
          }}>✕</button>
        </div>

        {/* Tabs */}
        <div style={{
          display: 'flex', borderBottom: '1px solid #e2e8f0',
          background: '#fff',
        }}>
          {tabs.map(t => (
            <button key={t.id} onClick={() => setTab(t.id)} style={{
              flex: 1, padding: '12px 8px', border: 'none', cursor: 'pointer',
              background: 'none', fontSize: '13px', fontWeight: tab === t.id ? '700' : '500',
              color: tab === t.id ? '#f97316' : '#64748b',
              borderBottom: tab === t.id ? '2px solid #f97316' : '2px solid transparent',
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px',
              transition: 'all 0.2s',
            }}>
              <span>{t.icon}</span> {t.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '1.5rem' }}>

          {/* ─── Profile Info Tab ─── */}
          {tab === 'info' && (
            <div>
              {saved && (
                <div style={{
                  background: '#f0fdf4', border: '1px solid #86efac',
                  borderRadius: '10px', padding: '10px 14px',
                  color: '#16a34a', fontWeight: '700', fontSize: '13px',
                  marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px',
                }}>✅ Profile saved successfully!</div>
              )}

              <div style={{
                background: '#f8fafc', borderRadius: '14px',
                padding: '20px', marginBottom: '16px',
                border: '1px solid #e2e8f0',
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                  <h3 style={{ color: '#1e293b', fontSize: '16px', fontWeight: '700' }}>Personal Information</h3>
                  <button onClick={() => setEditing(!editing)} style={{
                    background: editing ? '#fee2e2' : '#fff7ed',
                    color: editing ? '#ef4444' : '#f97316',
                    border: `1px solid ${editing ? '#fecaca' : '#fed7aa'}`,
                    borderRadius: '20px', padding: '6px 14px',
                    cursor: 'pointer', fontSize: '12px', fontWeight: '700',
                  }}>{editing ? '✕ Cancel' : '✏️ Edit'}</button>
                </div>

                <div style={{ display: 'grid', gap: '12px' }}>
                  <div>
                    <label style={{ color: '#64748b', fontSize: '12px', fontWeight: '600', display: 'block', marginBottom: '6px' }}>👤 Username</label>
                    <div style={{ ...inp, marginBottom: 0, background: '#f1f5f9', color: '#94a3b8', cursor: 'not-allowed' }}>{user}</div>
                  </div>
                  <div>
                    <label style={{ color: '#64748b', fontSize: '12px', fontWeight: '600', display: 'block', marginBottom: '6px' }}>✉️ Email</label>
                    <input
                      type="email"
                      value={form.email}
                      onChange={e => setForm({ ...form, email: e.target.value })}
                      disabled={!editing}
                      placeholder="your@email.com"
                      style={{ ...inp, marginBottom: 0, background: editing ? '#f8fafc' : '#f1f5f9', cursor: editing ? 'text' : 'not-allowed' }}
                    />
                  </div>
                  <div>
                    <label style={{ color: '#64748b', fontSize: '12px', fontWeight: '600', display: 'block', marginBottom: '6px' }}>📞 Phone</label>
                    <input
                      type="tel"
                      value={form.phone}
                      onChange={e => setForm({ ...form, phone: e.target.value })}
                      disabled={!editing}
                      placeholder="01XXXXXXXXX"
                      style={{ ...inp, marginBottom: 0, background: editing ? '#f8fafc' : '#f1f5f9', cursor: editing ? 'text' : 'not-allowed' }}
                    />
                  </div>
                </div>

                {editing && (
                  <button onClick={handleSave} style={{
                    marginTop: '16px', width: '100%', padding: '12px',
                    background: 'linear-gradient(135deg, #f97316, #ea580c)',
                    color: '#fff', border: 'none', borderRadius: '10px',
                    fontWeight: '700', cursor: 'pointer', fontSize: '14px',
                  }}>💾 Save Changes</button>
                )}
              </div>

              {/* Stats */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px' }}>
                {[
                  { icon: '📦', label: 'Total Orders', value: orders.length || '—' },
                  { icon: '❤️', label: 'Wishlist', value: '0' },
                  { icon: '📍', label: 'Addresses', value: addresses.length },
                ].map(s => (
                  <div key={s.label} style={{
                    background: '#f8fafc', borderRadius: '12px',
                    padding: '16px', border: '1px solid #e2e8f0', textAlign: 'center',
                  }}>
                    <div style={{ fontSize: '24px', marginBottom: '6px' }}>{s.icon}</div>
                    <div style={{ color: '#f97316', fontWeight: '900', fontSize: '22px' }}>{s.value}</div>
                    <div style={{ color: '#94a3b8', fontSize: '11px', marginTop: '4px' }}>{s.label}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* ─── Orders Tab ─── */}
          {tab === 'orders' && (
            <div>
              <h3 style={{ color: '#1e293b', fontSize: '16px', fontWeight: '700', marginBottom: '16px' }}>
                📦 Order History
              </h3>
              {loadingOrders ? (
                <div style={{ textAlign: 'center', padding: '40px', color: '#94a3b8' }}>
                  <div style={{ fontSize: '32px', marginBottom: '8px' }}>⏳</div>
                  Loading orders...
                </div>
              ) : orders.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '40px', color: '#94a3b8' }}>
                  <div style={{ fontSize: '48px', marginBottom: '12px' }}>📭</div>
                  <p style={{ fontWeight: '600' }}>No orders yet</p>
                  <p style={{ fontSize: '13px', marginTop: '6px' }}>Your orders will appear here</p>
                </div>
              ) : (
                <div style={{ display: 'grid', gap: '12px' }}>
                  {orders.map(order => (
                    <div key={order.id} style={{
                      background: '#f8fafc', borderRadius: '14px',
                      padding: '16px', border: '1px solid #e2e8f0',
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
                        <div>
                          <div style={{ color: '#1e293b', fontWeight: '700', fontSize: '14px' }}>
                            {order.product?.name || 'Product'}
                          </div>
                          <div style={{ color: '#94a3b8', fontSize: '12px', marginTop: '2px' }}>
                            Order #{order.id} • Qty: {order.quantity}
                          </div>
                        </div>
                        <span style={{
                          background: `${statusColor(order.order_status)}20`,
                          color: statusColor(order.order_status),
                          padding: '4px 10px', borderRadius: '20px',
                          fontSize: '11px', fontWeight: '700',
                          textTransform: 'capitalize',
                        }}>{order.order_status}</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div style={{ display: 'flex', gap: '12px' }}>
                          <span style={{ color: '#64748b', fontSize: '12px' }}>
                            💳 {payLabel(order.payment_method)}
                          </span>
                          <span style={{ color: '#64748b', fontSize: '12px' }}>
                            🚚 {order.address?.slice(0, 20)}{order.address?.length > 20 ? '...' : ''}
                          </span>
                        </div>
                        <div style={{ color: '#f97316', fontWeight: '800', fontSize: '15px' }}>
                          ৳{order.total_amount || '—'}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* ─── Address Book Tab ─── */}
          {tab === 'address' && (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <h3 style={{ color: '#1e293b', fontSize: '16px', fontWeight: '700' }}>📍 Address Book</h3>
                <button onClick={() => setAddingAddress(!addingAddress)} style={{
                  background: '#f97316', color: '#fff', border: 'none',
                  borderRadius: '20px', padding: '8px 16px',
                  cursor: 'pointer', fontSize: '13px', fontWeight: '700',
                }}>+ Add Address</button>
              </div>

              {addingAddress && (
                <div style={{
                  background: '#fff7ed', border: '1.5px solid #fed7aa',
                  borderRadius: '14px', padding: '16px', marginBottom: '16px',
                }}>
                  <label style={{ color: '#64748b', fontSize: '13px', fontWeight: '600', display: 'block', marginBottom: '8px' }}>
                    New Address
                  </label>
                  <textarea
                    rows={3}
                    placeholder="House no, Road, Area, District..."
                    value={newAddress}
                    onChange={e => setNewAddress(e.target.value)}
                    style={{ ...inp, resize: 'none' }}
                  />
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button onClick={() => setAddingAddress(false)} style={{
                      flex: 1, padding: '10px', background: '#f1f5f9',
                      color: '#475569', border: 'none', borderRadius: '8px',
                      cursor: 'pointer', fontWeight: '700', fontSize: '13px',
                    }}>Cancel</button>
                    <button onClick={handleAddAddress} style={{
                      flex: 2, padding: '10px', background: '#f97316',
                      color: '#fff', border: 'none', borderRadius: '8px',
                      cursor: 'pointer', fontWeight: '700', fontSize: '13px',
                    }}>💾 Save Address</button>
                  </div>
                </div>
              )}

              {addresses.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '40px', color: '#94a3b8' }}>
                  <div style={{ fontSize: '48px', marginBottom: '12px' }}>🏠</div>
                  <p style={{ fontWeight: '600' }}>No addresses saved</p>
                  <p style={{ fontSize: '13px', marginTop: '6px' }}>Add your delivery addresses here</p>
                </div>
              ) : (
                <div style={{ display: 'grid', gap: '10px' }}>
                  {addresses.map(addr => (
                    <div key={addr.id} style={{
                      background: addr.default ? '#fff7ed' : '#f8fafc',
                      border: `1.5px solid ${addr.default ? '#fed7aa' : '#e2e8f0'}`,
                      borderRadius: '14px', padding: '14px',
                      display: 'flex', gap: '12px', alignItems: 'flex-start',
                    }}>
                      <div style={{
                        width: '36px', height: '36px', borderRadius: '50%',
                        background: addr.default ? '#f97316' : '#e2e8f0',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontSize: '16px', flexShrink: 0,
                      }}>📍</div>
                      <div style={{ flex: 1 }}>
                        <div style={{ color: '#1e293b', fontSize: '14px', fontWeight: '600', marginBottom: '4px' }}>
                          {addr.text}
                        </div>
                        {addr.default && (
                          <span style={{
                            background: '#f97316', color: '#fff',
                            fontSize: '10px', fontWeight: '700',
                            padding: '2px 8px', borderRadius: '10px',
                          }}>DEFAULT</span>
                        )}
                      </div>
                      <div style={{ display: 'flex', gap: '6px', flexShrink: 0 }}>
                        {!addr.default && (
                          <button onClick={() => handleSetDefault(addr.id)} style={{
                            background: '#fff7ed', color: '#f97316',
                            border: '1px solid #fed7aa', borderRadius: '8px',
                            padding: '6px 10px', cursor: 'pointer', fontSize: '11px', fontWeight: '700',
                          }}>Set Default</button>
                        )}
                        <button onClick={() => handleDeleteAddress(addr.id)} style={{
                          background: '#fee2e2', color: '#ef4444',
                          border: '1px solid #fecaca', borderRadius: '8px',
                          padding: '6px 10px', cursor: 'pointer', fontSize: '11px', fontWeight: '700',
                        }}>🗑️</button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;