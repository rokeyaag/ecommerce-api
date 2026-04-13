import React from 'react';

const ProductCard = ({ product, onAddToCart }) => {
  return (
    <div style={{ background: 'rgba(255,255,255,0.05)', borderRadius: '16px', padding: '20px', border: '1px solid rgba(255,255,255,0.1)' }}>
      <div style={{ width: '100%', height: '180px', background: 'rgba(255,255,255,0.08)', borderRadius: '12px', marginBottom: '16px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <span style={{ fontSize: '48px' }}>🛍️</span>
      </div>
      <h3 style={{ color: '#fff', fontSize: '18px', fontWeight: '700', marginBottom: '8px' }}>{product.name}</h3>
      <div style={{ fontSize: '22px', fontWeight: '800', color: '#e94560', marginBottom: '8px' }}>৳{product.price}</div>
      <div style={{ color: 'rgba(255,255,255,0.5)', fontSize: '13px', marginBottom: '16px' }}>Stock: {product.stock}</div>
      <button onClick={() => onAddToCart(product)} style={{ width: '100%', padding: '10px', background: 'linear-gradient(135deg, #e94560, #0f3460)', color: 'white', border: 'none', borderRadius: '8px', fontWeight: '700', cursor: 'pointer' }}>Cart-এ যোগ</button>
    </div>
  );
};

export default ProductCard;