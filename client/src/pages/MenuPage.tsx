import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';

interface MenuItem {
  id: number;
  name: string;
  price: number;
  image_url?: string;
}

const MenuPage: React.FC = () => {
  const { restaurantId } = useParams<{ restaurantId: string }>();
  const [menuItems, setMenuItems] = useState<MenuItem[]>([]);

  useEffect(() => {
    fetch(`/api/restaurants/${restaurantId}/menu`) // يجب تغيير المسار حسب API الخاص بك
      .then(response => response.json())
      .then(data => setMenuItems(data))
      .catch(error => console.error('Error fetching menu items:', error));
  }, [restaurantId]);

  return (
    <div>
      <h2>Menu for Restaurant {restaurantId}</h2>
      <div className="menu-list">
        {menuItems.map((item) => (
          <div key={item.id} className="menu-card">
            <h3>{item.name}</h3>
            <p>Price: {item.price} DH</p>
            {item.image_url && (
              <img src={item.image_url} alt={`Image of ${item.name}`} />
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default MenuPage;
