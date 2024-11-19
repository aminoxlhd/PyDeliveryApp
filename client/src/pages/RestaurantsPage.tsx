import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface Restaurant {
  id: number;
  name: string;
  address: string;
  image_url?: string;
}

const RestaurantsPage: React.FC = () => {
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);

  useEffect(() => {
    axios.get('/api/restaurants')
      .then(response => setRestaurants(response.data))
      .catch(error => console.error('Error fetching restaurants:', error));
  }, []);

  return (
    <div>
      <h1>المطاعم المتاحة</h1>
      <div className="restaurant-list">
        {restaurants.map((restaurant) => (
          <div key={restaurant.id} className="restaurant-card">
            <h3>{restaurant.name}</h3>
            <p>{restaurant.address}</p>
            {restaurant.image_url && (
              <img src={restaurant.image_url} alt={`صورة ${restaurant.name}`} />
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default RestaurantsPage;

