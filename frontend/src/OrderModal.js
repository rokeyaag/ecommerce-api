// ═══════════════════════════════════════════════════════════════════════
// OrderModal.jsx  —  Production-ready multi-gateway payment modal
// ───────────────────────────────────────────────────────────────────────
// Supported payment methods:
//   1. bKash       — direct bKash Payment Gateway API (production)
//   2. SSL Commerz — card + bKash + Nagad + Rocket + all banks
//   3. Shurjopay   — Bangladeshi gateway (card + MFS)
//   4. COD         — Cash on Delivery
//
// Flow:
//   Step 1 → Enter qty / phone / address
//   Step 2 → Choose payment method
//   Step 3 → Review & confirm → API call → redirect / success
// ═══════════════════════════════════════════════════════════════════════

import React, { useState } from 'react';

const API_BASE = 'http://127.0.0.1:8000/api';

// ── shared inline styles ──────────────────────────────────────────────
const inp = {
  width: '100%', padding: '11px 14px', borderRadius: 10,
  border: '1px solid rgba(255,255,255,.15)',
  background: 'rgba(255,255,255,.07)', color: '#fff',
  fontSize: 14, outline: 'none', fontFamily: 'Outfit,sans-serif',
  boxSizing: 'border-box',
};
const btnPrimary = (disabled) => ({
  flex: 2, padding: '13px', border: 'none', borderRadius: 12,
  background: disabled
    ? 'rgba(233,69,96,.4)'
    : 'linear-gradient(135deg,#e94560,#c0392b)',
  color: '#fff', fontWeight: 700, fontSize: 14,
  cursor: disabled ? 'wait' : 'pointer',
  fontFamily: 'Outfit,sans-serif',
  display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
});
const btnBack = {
  flex: 1, padding: '12px',
  border: '1.5px solid rgba(255,255,255,.2)',
  borderRadius: 12, background: 'transparent',
  color: 'rgba(255,255,255,.7)',
  fontWeight: 600, fontSize: 14, cursor: 'pointer',
  fontFamily: 'Outfit,sans-serif',
};

// ── Spinner ───────────────────────────────────────────────────────────
const Spinner = () => (
  <span style={{
    width: 16, height: 16,
    border: '2px solid rgba(255,255,255,.3)',
    borderTopColor: '#fff', borderRadius: '50%',
    animation: 'spinAnim .7s linear infinite',
    display: 'inline-block',
  }} />
);

// ── Step indicator ────────────────────────────────────────────────────
const StepBar = ({ step }) => (
  <div style={{ display: 'flex', alignItems: 'center', marginBottom: 22 }}>
    {[['1','Details'], ['2','Payment'], ['3','Confirm']].map(([n, label], i) => {
      const done = step > i + 1, cur = step === i + 1;
      return (
        <React.Fragment key={n}>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 }}>
            <div style={{
              width: 32, height: 32, borderRadius: '50%',
              background: done ? '#27ae60' : cur ? '#e94560' : 'rgba(255,255,255,.1)',
              border: `2px solid ${done ? '#27ae60' : cur ? '#e94560' : 'rgba(255,255,255,.15)'}`,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 13, fontWeight: 700,
              color: done || cur ? '#fff' : 'rgba(255,255,255,.4)',
              transition: 'all .3s',
            }}>{done ? '✓' : n}</div>
            <span style={{ fontSize: 11, fontWeight: 600, color: cur ? '#e94560' : done ? '#27ae60' : 'rgba(255,255,255,.3)' }}>{label}</span>
          </div>
          {i < 2 && <div style={{ flex: 1, height: 2, marginBottom: 16, background: done ? '#27ae60' : 'rgba(255,255,255,.1)', transition: 'background .3s' }} />}
        </React.Fragment>
      );
    })}
  </div>
);

// ── Product summary ───────────────────────────────────────────────────
const ProductRow = ({ product, qty }) => {
  const total = (parseFloat(product.price) * qty).toFixed(2);
  return (
    <div style={{
      background: 'rgba(255,255,255,.05)', border: '1px solid rgba(255,255,255,.08)',
      borderRadius: 12, padding: 14, display: 'flex', gap: 14, alignItems: 'center', marginBottom: 20,
    }}>
      <img src={product.image} alt={product.name}
        style={{ width: 64, height: 64, objectFit: 'cover', borderRadius: 10 }}
        onError={e => e.target.style.display = 'none'} />
      <div style={{ flex: 1 }}>
        <div style={{ color: '#fff', fontWeight: 700, fontSize: 15, marginBottom: 3 }}>{product.name}</div>
        <div style={{ color: '#e94560', fontWeight: 800, fontSize: 20 }}>${total}</div>
        <div style={{ color: 'rgba(255,255,255,.4)', fontSize: 12 }}>Qty: {qty} × ${product.price}</div>
      </div>
    </div>
  );
};

// ── Payment method card ───────────────────────────────────────────────
const PayCard = ({ id, selected, onSelect, emoji, title, subtitle, tags, highlight }) => {
  const active = selected === id;
  return (
    <div onClick={() => onSelect(id)} style={{
      border: `2px solid ${active ? (highlight || '#e94560') : 'rgba(255,255,255,.1)'}`,
      borderRadius: 14, padding: '13px 15px', cursor: 'pointer', marginBottom: 10,
      background: active ? `rgba(${highlight ? '255,99,0' : '233,69,96'},.09)` : 'rgba(255,255,255,.03)',
      transition: 'all .2s',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        {/* Radio */}
        <div style={{
          width: 20, height: 20, borderRadius: '50%', flexShrink: 0,
          border: `2px solid ${active ? (highlight || '#e94560') : 'rgba(255,255,255,.3)'}`,
          background: active ? (highlight || '#e94560') : 'transparent',
          display: 'flex', alignItems: 'center', justifyContent: 'center', transition: 'all .2s',
        }}>
          {active && <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#fff' }} />}
        </div>

        <span style={{ fontSize: 26, flexShrink: 0 }}>{emoji}</span>

        <div style={{ flex: 1 }}>
          <div style={{ color: '#fff', fontWeight: 700, fontSize: 14, marginBottom: 3 }}>{title}</div>
          <div style={{ color: 'rgba(255,255,255,.45)', fontSize: 12 }}>{subtitle}</div>
        </div>
      </div>

      {/* Tags */}
      {active && tags && (
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginTop: 10, paddingLeft: 44 }}>
          {tags.map(t => (
            <span key={t} style={{
              background: 'rgba(255,255,255,.08)', border: '1px solid rgba(255,255,255,.12)',
              borderRadius: 6, padding: '3px 9px', fontSize: 11,
              color: 'rgba(255,255,255,.65)', fontWeight: 700,
            }}>{t}</span>
          ))}
        </div>
      )}
    </div>
  );
};

// ── Error box ─────────────────────────────────────────────────────────
const ErrBox = ({ msg }) => msg ? (
  <div style={{
    background: 'rgba(233,69,96,.15)', color: '#f1848e',
    border: '1px solid rgba(233,69,96,.3)',
    borderRadius: 10, padding: '10px 14px', marginBottom: 14, fontSize: 13,
  }}>{msg}</div>
) : null;

// ═══════════════════════════════════════════════════════════════════════
// MAIN COMPONENT
// ═══════════════════════════════════════════════════════════════════════
const OrderModal = ({ product, onClose, getToken }) => {
  const [step,      setStep]    = useState(1);
  const [qty,       setQty]     = useState(1);
  const [phone,     setPhone]   = useState('');
  const [address,   setAddress] = useState('');
  const [payMethod, setPay]     = useState('cod');
  const [loading,   setLoading] = useState(false);
  const [errMsg,    setErr]     = useState('');
  const [result,    setResult]  = useState(null); // null | 'cod_success' | 'redirecting'

  const total     = (parseFloat(product.price) * qty).toFixed(2);
  const totalBDT  = (parseFloat(total) * 110).toFixed(0); // approx USD→BDT

  // ── Step 1 validation ─────────────────────────────────────────────
  const goPayment = () => {
    if (!/^01[3-9]\d{8}$/.test(phone)) { setErr('সঠিক বাংলাদেশি মোবাইল নম্বর দিন (01XXXXXXXXX)।'); return; }
    if (!address.trim()) { setErr('Delivery address দিন।'); return; }
    setErr(''); setStep(2);
  };

  // ── Final confirm ─────────────────────────────────────────────────
  const handleConfirm = async () => {
    setLoading(true); setErr('');
    const token = getToken();

    try {
      // ── POST order to Django ──────────────────────────────────────
      const res = await fetch(`${API_BASE}/orders/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          product_id:     product.id,
          quantity:       qty,
          address,
          phone,
          payment_method: payMethod,  // 'cod' | 'bkash' | 'ssl' | 'shurjopay'
        }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || data.error || 'Order failed');

      // ── Gateway redirect or success ───────────────────────────────
      if (payMethod === 'cod') {
        setResult('cod_success');
      } else if (data.payment_url) {
        setResult('redirecting');
        setTimeout(() => { window.location.href = data.payment_url; }, 1200);
      } else {
        throw new Error('Payment URL পাওয়া যায়নি। Backend চেক করুন।');
      }

    } catch (e) {
      setErr(e.message || 'কিছু একটা ভুল হয়েছে। আবার চেষ্টা করুন।');
    }
    setLoading(false);
  };

  // ── Overlay wrapper ───────────────────────────────────────────────
  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 2000,
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: 'rgba(0,0,0,.82)', padding: '1rem',
      animation: 'fadeIn .2s ease',
    }} onClick={e => e.target === e.currentTarget && onClose()}>

      <div style={{
        background: '#0c1828', borderRadius: 20, padding: '2rem',
        width: '100%', maxWidth: 490,
        border: '1px solid rgba(255,255,255,.1)',
        boxShadow: '0 32px 80px rgba(0,0,0,.75)',
        maxHeight: '92vh', overflowY: 'auto',
        animation: 'fadeUp .25s ease',
      }}>

        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
          <h2 style={{ color: '#fff', fontSize: 20, fontWeight: 800 }}>
            {result ? 'Order Status' : 'Place Order'}
          </h2>
          <button onClick={onClose} style={{
            background: 'rgba(255,255,255,.08)', border: 'none', color: '#fff',
            width: 34, height: 34, borderRadius: '50%', cursor: 'pointer', fontSize: 16,
          }}>✕</button>
        </div>

        {/* ══ RESULT: COD Success ══════════════════════════════════════ */}
        {result === 'cod_success' && (
          <div style={{ textAlign: 'center', padding: '1.5rem .5rem' }}>
            <div style={{ fontSize: 72, marginBottom: 14 }}>✅</div>
            <h2 style={{ color: '#2ecc71', fontSize: 22, fontWeight: 800, marginBottom: 8 }}>Order Confirmed!</h2>
            <p style={{ color: 'rgba(255,255,255,.5)', fontSize: 14, lineHeight: 1.7, marginBottom: 20 }}>
              আপনার order সফলভাবে placed হয়েছে।<br />আমাদের team শীঘ্রই যোগাযোগ করবে।
            </p>
            <div style={{
              background: 'rgba(39,174,96,.1)', border: '1px solid rgba(39,174,96,.25)',
              borderRadius: 12, padding: '14px 18px', marginBottom: 20, textAlign: 'left',
            }}>
              {[['পণ্য', product.name], ['Qty', qty], ['মোট', `$${total}`], ['Payment', 'Cash on Delivery'], ['Phone', phone], ['ঠিকানা', address]].map(([k, v]) => (
                <div key={k} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 7, fontSize: 13 }}>
                  <span style={{ color: 'rgba(255,255,255,.45)' }}>{k}</span>
                  <span style={{ color: '#fff', fontWeight: 600, textAlign: 'right', maxWidth: '60%' }}>{v}</span>
                </div>
              ))}
            </div>
            <button onClick={onClose} style={{
              width: '100%', padding: '12px', border: 'none', borderRadius: 12,
              background: 'linear-gradient(135deg,#27ae60,#2ecc71)', color: '#fff',
              fontWeight: 700, fontSize: 14, cursor: 'pointer', fontFamily: 'Outfit,sans-serif',
            }}>বন্ধ করুন</button>
          </div>
        )}

        {/* ══ RESULT: Gateway redirect ══════════════════════════════════ */}
        {result === 'redirecting' && (
          <div style={{ textAlign: 'center', padding: '2rem 1rem' }}>
            <div style={{ fontSize: 56, marginBottom: 16, animation: 'pulse 1s infinite' }}>🔒</div>
            <h2 style={{ color: '#f5a623', fontSize: 20, fontWeight: 800, marginBottom: 8 }}>
              Payment page-এ যাচ্ছেন...
            </h2>
            <p style={{ color: 'rgba(255,255,255,.5)', fontSize: 13, lineHeight: 1.7 }}>
              কয়েক সেকেন্ডের মধ্যে payment gateway-এ redirect হবেন।<br />
              Page বন্ধ করবেন না।
            </p>
            <div style={{ marginTop: 20 }}>
              <Spinner />
            </div>
          </div>
        )}

        {/* ══ STEP 1: Details ══════════════════════════════════════════ */}
        {!result && step === 1 && (
          <>
            <StepBar step={step} />
            <ProductRow product={product} qty={qty} />

            {/* Qty */}
            <div style={{ marginBottom: 20 }}>
              <label style={{ color: 'rgba(255,255,255,.5)', fontSize: 12, fontWeight: 700, textTransform: 'uppercase', letterSpacing: .8, display: 'block', marginBottom: 8 }}>Quantity</label>
              <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                {['-', '+'].map((s, i) => (
                  <button key={s} onClick={() => setQty(q => i === 0 ? Math.max(1, q - 1) : q + 1)} style={{
                    width: 38, height: 38, background: 'rgba(255,255,255,.1)', border: 'none',
                    color: '#fff', borderRadius: 9, cursor: 'pointer', fontSize: 20,
                  }}>{s}</button>
                ))}
                <span style={{ color: '#fff', fontWeight: 800, fontSize: 22, minWidth: 32, textAlign: 'center' }}>{qty}</span>
                <span style={{
                  marginLeft: 8, background: 'rgba(233,69,96,.15)',
                  color: '#e94560', border: '1px solid rgba(233,69,96,.3)',
                  borderRadius: 10, padding: '6px 14px', fontWeight: 700, fontSize: 15,
                }}>= ${total}</span>
              </div>
            </div>

            {/* Phone */}
            <div style={{ marginBottom: 14 }}>
              <label style={{ color: 'rgba(255,255,255,.5)', fontSize: 12, fontWeight: 700, textTransform: 'uppercase', letterSpacing: .8, display: 'block', marginBottom: 7 }}>Phone Number</label>
              <input style={inp} type="tel" placeholder="01XXXXXXXXX"
                value={phone} onChange={e => setPhone(e.target.value)} />
            </div>

            {/* Address */}
            <div style={{ marginBottom: 18 }}>
              <label style={{ color: 'rgba(255,255,255,.5)', fontSize: 12, fontWeight: 700, textTransform: 'uppercase', letterSpacing: .8, display: 'block', marginBottom: 7 }}>Delivery Address</label>
              <textarea style={{ ...inp, resize: 'none' }} rows={3}
                placeholder="বাড়ি নং, রাস্তা, এলাকা, জেলা..."
                value={address} onChange={e => setAddress(e.target.value)} />
            </div>

            <ErrBox msg={errMsg} />

            <button onClick={goPayment} style={{
              width: '100%', padding: '13px', border: 'none', borderRadius: 12,
              background: 'linear-gradient(135deg,#e94560,#c0392b)',
              color: '#fff', fontWeight: 700, fontSize: 15,
              cursor: 'pointer', fontFamily: 'Outfit,sans-serif',
            }}>Next: Payment Method →</button>
          </>
        )}

        {/* ══ STEP 2: Payment ══════════════════════════════════════════ */}
        {!result && step === 2 && (
          <>
            <StepBar step={step} />
            <ProductRow product={product} qty={qty} />

            <label style={{ color: 'rgba(255,255,255,.5)', fontSize: 12, fontWeight: 700, textTransform: 'uppercase', letterSpacing: .8, display: 'block', marginBottom: 12 }}>
              Payment Method বেছে নিন
            </label>

            {/* bKash */}
            <PayCard id="bkash" selected={payMethod} onSelect={setPay}
              emoji="📱" highlight="#E2136E"
              title="bKash Payment"
              subtitle="বাংলাদেশের সবচেয়ে জনপ্রিয় MFS — direct bKash API"
              tags={['bKash Personal', 'bKash Merchant', 'Instant Confirm']}
            />

            {/* SSL Commerz */}
            <PayCard id="ssl" selected={payMethod} onSelect={setPay}
              emoji="🔒" highlight="#2a7ae2"
              title="SSL Commerz"
              subtitle="Card, bKash, Nagad, Rocket, net banking — সব একসাথে"
              tags={['VISA', 'Mastercard', 'bKash', 'Nagad', 'Rocket', 'DBBL', 'Upay', '50+ options']}
            />

            {/* Shurjopay */}
            <PayCard id="shurjopay" selected={payMethod} onSelect={setPay}
              emoji="🇧🇩" highlight="#f39c12"
              title="Shurjopay"
              subtitle="Bangladeshi gateway — card + MFS, low transaction fee"
              tags={['VISA', 'Mastercard', 'bKash', 'Nagad', 'Rocket', 'Upay']}
            />

            {/* COD */}
            <PayCard id="cod" selected={payMethod} onSelect={setPay}
              emoji="💵" highlight="#27ae60"
              title="Cash on Delivery (COD)"
              subtitle="পণ্য পাওয়ার পর নগদ পরিশোধ করুন"
              tags={['No advance', 'সবচেয়ে নিরাপদ', 'সারা বাংলাদেশ']}
            />

            {/* Info note per gateway */}
            {payMethod !== 'cod' && (
              <div style={{
                background: 'rgba(255,255,255,.04)', border: '1px solid rgba(255,255,255,.08)',
                borderRadius: 10, padding: '10px 14px', fontSize: 12,
                color: 'rgba(255,255,255,.5)', marginBottom: 4, lineHeight: 1.7,
              }}>
                {payMethod === 'bkash' && '📌 Confirm করলে bKash Payment Gateway page-এ redirect হবেন। bKash number ও PIN দিয়ে payment complete করুন।'}
                {payMethod === 'ssl'   && '📌 Confirm করলে SSL Commerz hosted checkout-এ যাবেন। যেকোনো card বা MFS দিয়ে pay করতে পারবেন।'}
                {payMethod === 'shurjopay' && '📌 Confirm করলে Shurjopay checkout-এ redirect হবেন। Card বা mobile banking দিয়ে pay করুন।'}
              </div>
            )}

            <div style={{ display: 'flex', gap: 10, marginTop: 16 }}>
              <button style={btnBack} onClick={() => { setStep(1); setErr(''); }}>← Back</button>
              <button style={{ ...btnPrimary(false), flex: 2 }} onClick={() => { setErr(''); setStep(3); }}>
                Review Order →
              </button>
            </div>
          </>
        )}

        {/* ══ STEP 3: Confirm ══════════════════════════════════════════ */}
        {!result && step === 3 && (
          <>
            <StepBar step={step} />

            {/* Summary card */}
            <div style={{
              background: 'rgba(255,255,255,.04)', border: '1px solid rgba(255,255,255,.08)',
              borderRadius: 14, padding: '16px 18px', marginBottom: 18,
            }}>
              <div style={{ color: 'rgba(255,255,255,.35)', fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: .8, marginBottom: 14 }}>Order Summary</div>

              {[
                ['🛍️ পণ্য',      product.name],
                ['🔢 Quantity',  qty],
                ['📞 Phone',     phone],
                ['📍 Address',   address],
                ['💳 Payment',   { bkash:'bKash', ssl:'SSL Commerz', shurjopay:'Shurjopay', cod:'Cash on Delivery' }[payMethod]],
                ['💵 Subtotal',  `$${total} (~৳${totalBDT})`],
                ['🚚 Delivery',  'Free'],
              ].map(([k, v]) => (
                <div key={k} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid rgba(255,255,255,.06)', fontSize: 13, gap: 12 }}>
                  <span style={{ color: 'rgba(255,255,255,.4)', flexShrink: 0 }}>{k}</span>
                  <span style={{ color: '#fff', fontWeight: 600, textAlign: 'right' }}>{v}</span>
                </div>
              ))}

              {/* Total row */}
              <div style={{ display: 'flex', justifyContent: 'space-between', paddingTop: 12, marginTop: 4 }}>
                <span style={{ color: '#fff', fontWeight: 700, fontSize: 15 }}>Total</span>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ color: '#e94560', fontWeight: 800, fontSize: 20 }}>${total}</div>
                  <div style={{ color: 'rgba(255,255,255,.35)', fontSize: 11 }}>~৳{totalBDT} BDT</div>
                </div>
              </div>
            </div>

            {/* Gateway note */}
            {{
              bkash: (
                <div style={{ background: 'rgba(226,19,110,.12)', border: '1px solid rgba(226,19,110,.25)', borderRadius: 10, padding: '11px 14px', marginBottom: 16, fontSize: 13, color: 'rgba(255,255,255,.65)', display: 'flex', gap: 8 }}>
                  <span>📱</span>
                  <span>Confirm করলে <strong style={{ color: '#E2136E' }}>bKash</strong> payment page-এ redirect হবেন। bKash number ও OTP দিয়ে payment complete করুন।</span>
                </div>
              ),
              ssl: (
                <div style={{ background: 'rgba(42,122,226,.12)', border: '1px solid rgba(42,122,226,.25)', borderRadius: 10, padding: '11px 14px', marginBottom: 16, fontSize: 13, color: 'rgba(255,255,255,.65)', display: 'flex', gap: 8 }}>
                  <span>🔒</span>
                  <span>Confirm করলে <strong style={{ color: '#4a9fe8' }}>SSL Commerz</strong> secure checkout-এ redirect হবেন। Card, bKash, Nagad, Rocket সব option পাবেন।</span>
                </div>
              ),
              shurjopay: (
                <div style={{ background: 'rgba(243,156,18,.12)', border: '1px solid rgba(243,156,18,.25)', borderRadius: 10, padding: '11px 14px', marginBottom: 16, fontSize: 13, color: 'rgba(255,255,255,.65)', display: 'flex', gap: 8 }}>
                  <span>🇧🇩</span>
                  <span>Confirm করলে <strong style={{ color: '#f5a623' }}>Shurjopay</strong> checkout-এ redirect হবেন।</span>
                </div>
              ),
              cod: (
                <div style={{ background: 'rgba(39,174,96,.12)', border: '1px solid rgba(39,174,96,.25)', borderRadius: 10, padding: '11px 14px', marginBottom: 16, fontSize: 13, color: 'rgba(255,255,255,.65)', display: 'flex', gap: 8 }}>
                  <span>💵</span>
                  <span>পণ্য হাতে পেলে <strong style={{ color: '#2ecc71' }}>নগদ ৳{totalBDT}</strong> পরিশোধ করুন। কোনো advance payment নেই।</span>
                </div>
              ),
            }[payMethod]}

            <ErrBox msg={errMsg} />

            <div style={{ display: 'flex', gap: 10 }}>
              <button style={btnBack} onClick={() => { setStep(2); setErr(''); }}>← Back</button>
              <button style={btnPrimary(loading)} onClick={handleConfirm} disabled={loading}>
                {loading
                  ? <><Spinner /> Processing...</>
                  : payMethod === 'cod'
                    ? '✅ Confirm Order'
                    : '🔒 Pay Now'}
              </button>
            </div>
          </>
        )}

      </div>
    </div>
  );
};

export default OrderModal;


/* ═══════════════════════════════════════════════════════════════════════
   DJANGO BACKEND — store/views.py
   ═══════════════════════════════════════════════════════════════════════

pip install sslcommerz-lib requests

─── Order model (store/models.py) ──────────────────────────────────────

PAYMENT_METHODS = [
    ('cod',       'Cash on Delivery'),
    ('bkash',     'bKash'),
    ('ssl',       'SSL Commerz'),
    ('shurjopay', 'Shurjopay'),
]
PAYMENT_STATUS = [
    ('pending',   'Pending'),
    ('paid',      'Paid'),
    ('failed',    'Failed'),
    ('cancelled', 'Cancelled'),
]

class Order(models.Model):
    user           = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    product        = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity       = models.PositiveIntegerField()
    address        = models.TextField()
    phone          = models.CharField(max_length=20)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cod')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True)
    total_amount   = models.DecimalField(max_digits=10, decimal_places=2)
    created_at     = models.DateTimeField(auto_now_add=True)


─── views.py ────────────────────────────────────────────────────────────

import uuid, requests
from decimal import Decimal
from django.conf import settings
from django.shortcuts import redirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from sslcommerz_lib import SSLCOMMERZ
from .models import Order, Product


@api_view(['POST'])
def create_order(request):
    d          = request.data
    product    = Product.objects.get(id=d['product_id'])
    qty        = int(d.get('quantity', 1))
    amount_usd = product.price * qty
    amount_bdt = Decimal(str(amount_usd)) * Decimal('110')  # adjust exchange rate
    tran_id    = f"ORDER-{uuid.uuid4().hex[:12].upper()}"

    order = Order.objects.create(
        user           = request.user if request.user.is_authenticated else None,
        product        = product,
        quantity       = qty,
        address        = d['address'],
        phone          = d['phone'],
        payment_method = d['payment_method'],
        total_amount   = amount_bdt,
        transaction_id = tran_id,
    )

    method = d['payment_method']

    # ── COD ─────────────────────────────────────────────────────────
    if method == 'cod':
        return Response({'id': order.id, 'payment_url': None})

    # ── bKash ────────────────────────────────────────────────────────
    if method == 'bkash':
        token_res = requests.post(
            'https://tokenized.pay.bka.sh/v1.2.0-beta/tokenized/checkout/token/grant',
            json={
                'app_key':    settings.BKASH_APP_KEY,
                'app_secret': settings.BKASH_APP_SECRET,
            },
            headers={
                'username': settings.BKASH_USERNAME,
                'password': settings.BKASH_PASSWORD,
            },
        ).json()
        id_token = token_res['id_token']

        pay_res = requests.post(
            'https://tokenized.pay.bka.sh/v1.2.0-beta/tokenized/checkout/create',
            json={
                'mode':          '0011',
                'payerReference': str(order.id),
                'callbackURL':   f"{settings.BASE_URL}/api/payment/bkash/callback/",
                'amount':        str(amount_bdt),
                'currency':      'BDT',
                'intent':        'sale',
                'merchantInvoiceNumber': tran_id,
            },
            headers={
                'Authorization': id_token,
                'X-APP-Key':     settings.BKASH_APP_KEY,
            },
        ).json()

        url = pay_res.get('bkashURL')
        if not url:
            return Response({'error': 'bKash init failed', 'detail': pay_res}, status=400)
        return Response({'id': order.id, 'payment_url': url})

    # ── SSL Commerz ──────────────────────────────────────────────────
    if method == 'ssl':
        sslcz = SSLCOMMERZ({
            'store_id':   settings.SSL_STORE_ID,
            'store_pass': settings.SSL_STORE_PASS,
            'issandbox':  False,
        })
        res = sslcz.createSession({
            'total_amount':    float(amount_bdt),
            'currency':        'BDT',
            'tran_id':         tran_id,
            'success_url':     f"{settings.BASE_URL}/api/payment/ssl/success/",
            'fail_url':        f"{settings.BASE_URL}/api/payment/ssl/fail/",
            'cancel_url':      f"{settings.BASE_URL}/api/payment/ssl/cancel/",
            'cus_name':        getattr(request.user, 'username', 'Customer'),
            'cus_email':       getattr(request.user, 'email', 'customer@shopbd.com'),
            'cus_phone':       d['phone'],
            'cus_add1':        d['address'],
            'cus_country':     'Bangladesh',
            'shipping_method': 'NO',
            'product_name':    product.name,
            'product_category':'General',
            'product_profile': 'general',
        })
        if res.get('status') != 'SUCCESS':
            return Response({'error': 'SSL Commerz init failed'}, status=400)
        return Response({'id': order.id, 'payment_url': res['GatewayPageURL']})

    # ── Shurjopay ────────────────────────────────────────────────────
    if method == 'shurjopay':
        auth = requests.post(
            'https://engine.shurjopayment.com/api/get_token',
            json={
                'username': settings.SHURJOPAY_USERNAME,
                'password': settings.SHURJOPAY_PASSWORD,
            },
        ).json()
        token    = auth['token']
        store_id = auth['store_id']

        pay = requests.post(
            'https://engine.shurjopayment.com/api/secret-pay',
            json={
                'prefix':            'SP',
                'token':             token,
                'store_id':          store_id,
                'return_url':        f"{settings.BASE_URL}/api/payment/shurjopay/callback/",
                'cancel_url':        f"{settings.BASE_URL}/api/payment/shurjopay/cancel/",
                'amount':            float(amount_bdt),
                'currency':          'BDT',
                'order_id':          tran_id,
                'discsount_amount':  0,
                'disc_percent':      0,
                'customer_name':     getattr(request.user, 'username', 'Customer'),
                'customer_email':    getattr(request.user, 'email', 'customer@shopbd.com'),
                'customer_phone':    d['phone'],
                'customer_address':  d['address'],
                'customer_city':     'Dhaka',
                'customer_state':    'Dhaka',
                'customer_postcode': '1200',
                'customer_country':  'Bangladesh',
                'value1':            str(order.id),
            },
        ).json()

        url = pay.get('checkout_url')
        if not url:
            return Response({'error': 'Shurjopay init failed', 'detail': pay}, status=400)
        return Response({'id': order.id, 'payment_url': url})

    return Response({'error': 'Invalid payment method'}, status=400)


# ── Payment callbacks ────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def bkash_callback(request):
    status   = request.GET.get('status')
    pay_id   = request.GET.get('paymentID')
    order_id = request.data.get('merchantInvoiceNumber','').replace('ORDER-','')
    if status == 'success':
        Order.objects.filter(transaction_id__icontains=order_id).update(payment_status='paid')
        return redirect(f"{settings.FRONTEND_URL}/?payment=success")
    Order.objects.filter(transaction_id__icontains=order_id).update(payment_status='failed')
    return redirect(f"{settings.FRONTEND_URL}/?payment=failed")


@api_view(['POST'])
@permission_classes([AllowAny])
def ssl_success(request):
    tran_id = request.data.get('tran_id','')
    Order.objects.filter(transaction_id=tran_id).update(payment_status='paid')
    return redirect(f"{settings.FRONTEND_URL}/?payment=success")

@api_view(['POST'])
@permission_classes([AllowAny])
def ssl_fail(request):
    tran_id = request.data.get('tran_id','')
    Order.objects.filter(transaction_id=tran_id).update(payment_status='failed')
    return redirect(f"{settings.FRONTEND_URL}/?payment=failed")

@api_view(['POST'])
@permission_classes([AllowAny])
def ssl_cancel(request):
    return redirect(f"{settings.FRONTEND_URL}/?payment=cancelled")


@api_view(['GET','POST'])
@permission_classes([AllowAny])
def shurjopay_callback(request):
    order_id = request.GET.get('order_id','')
    Order.objects.filter(transaction_id=order_id).update(payment_status='paid')
    return redirect(f"{settings.FRONTEND_URL}/?payment=success")


─── urls.py additions ───────────────────────────────────────────────────

from store.views import (
    create_order,
    bkash_callback, ssl_success, ssl_fail, ssl_cancel,
    shurjopay_callback,
)

urlpatterns += [
    path('api/orders/',                       create_order,         name='create_order'),
    path('api/payment/bkash/callback/',       bkash_callback,       name='bkash_callback'),
    path('api/payment/ssl/success/',          ssl_success,          name='ssl_success'),
    path('api/payment/ssl/fail/',             ssl_fail,             name='ssl_fail'),
    path('api/payment/ssl/cancel/',           ssl_cancel,           name='ssl_cancel'),
    path('api/payment/shurjopay/callback/',   shurjopay_callback,   name='shurjopay_callback'),
]


─── settings.py ────────────────────────────────────────────────────────

BASE_URL     = 'https://yourdomain.com'      # production domain
FRONTEND_URL = 'https://yourdomain.com'

# bKash (Tokenized Payment Gateway)
BKASH_USERNAME   = 'your_bkash_username'
BKASH_PASSWORD   = 'your_bkash_password'
BKASH_APP_KEY    = 'your_app_key'
BKASH_APP_SECRET = 'your_app_secret'

# SSL Commerz
SSL_STORE_ID   = 'your_store_id'
SSL_STORE_PASS = 'your_store_password'

# Shurjopay
SHURJOPAY_USERNAME = 'your_username'
SHURJOPAY_PASSWORD = 'your_password'

═══════════════════════════════════════════════════════════════════════ */