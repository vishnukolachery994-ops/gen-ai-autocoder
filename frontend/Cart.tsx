import React, { useState, useEffect } from 'react';

interface CartItem {
  id: number;
  name: string;
  price: number;
  quantity: number;
  image_url?: string;
}

export const Cart: React.FC = () => {
  const [items, setItems] = useState<CartItem[]>([]);
  const [isOrdering, setIsOrdering] = useState(false);

  // Load items from localStorage on mount to persist data
  useEffect(() => {
    const savedCart = localStorage.getItem('jewelry_cart');
    if (savedCart) {
      setItems(JSON.parse(savedCart));
    }
  }, []);

  // Calculate Subtotal
  const subtotal = items.reduce((acc, item) => acc + (item.price * item.quantity), 0);

  const removeItem = (id: number) => {
    const updated = items.filter(item => item.id !== id);
    setItems(updated);
    localStorage.setItem('jewelry_cart', JSON.stringify(updated));
  };

  const placeOrder = async () => {
    if (items.length === 0) return alert("Your cart is empty!");
    
    setIsOrdering(true);
    try {
      const response = await fetch('/api/order', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          items: items,
          total: subtotal 
        })
      });

      if (response.ok) {
        alert("Order Placed Successfully!");
        setItems([]);
        localStorage.removeItem('jewelry_cart');
      }
    } catch (error) {
      console.error("Order failed:", error);
    } finally {
      setIsOrdering(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white shadow-lg rounded-lg">
      <h2 className="text-3xl font-serif font-bold text-gray-800 mb-6 border-b pb-4">
        Shopping Bag
      </h2>

      {items.length === 0 ? (
        <div className="text-center py-10">
          <p className="text-gray-500 text-lg">Your bag is currently empty.</p>
          <button className="mt-4 text-gold-600 hover:underline font-medium">Continue Shopping</button>
        </div>
      ) : (
        <div className="space-y-4">
          {items.map((item) => (
            <div key={item.id} className="flex items-center justify-between border-p-4 border-b">
              <div className="flex items-center space-x-4">
                <img 
                  src={item.image_url || 'https://via.placeholder.com/80'} 
                  alt={item.name} 
                  className="w-20 h-20 object-cover rounded shadow-sm"
                />
                <div>
                  <h3 className="text-lg font-semibold text-gray-700">{item.name}</h3>
                  <p className="text-sm text-gray-500">Qty: {item.quantity}</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-lg font-bold text-gray-900">${(item.price * item.quantity).toLocaleString()}</p>
                <button 
                  onClick={() => removeItem(item.id)}
                  className="text-red-500 text-xs hover:text-red-700 transition-colors"
                >
                  Remove
                </button>
              </div>
            </div>
          ))}

          <div className="mt-8 bg-gray-50 p-6 rounded-lg">
            <div className="flex justify-between text-xl font-bold text-gray-900 mb-4">
              <span>Total Amount</span>
              <span>${subtotal.toLocaleString()}</span>
            </div>
            <button 
              onClick={placeOrder}
              disabled={isOrdering}
              className={`w-full py-4 rounded-full font-bold text-white transition-all ${
                isOrdering ? 'bg-gray-400' : 'bg-black hover:bg-gray-800 shadow-xl active:scale-95'
              }`}
            >
              {isOrdering ? 'Processing...' : 'Secure Checkout'}
            </button>
            <p className="text-center text-xs text-gray-400 mt-4 uppercase tracking-widest">
              Complimentary Shipping & Returns
            </p>
          </div>
        </div>
      )}
    </div>
  );
};