import React, { useEffect, useState } from 'react';

interface Restaurant {
  id: number;
  name: string;
  address: string;
  image_url?: string;
}

const RestaurantsPage: React.FC = () => {
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);

  useEffect(() => {
    fetch('/api/restaurants')
      .then(response => response.json())
      .then(data => setRestaurants(data))
      .catch(error => console.error('Error fetching restaurants:', error));
  }, []);

  return (
    <div>
      <h2>Available Restaurants</h2>
      <div className="restaurant-list">
        {restaurants.map((restaurant) => (
          <div key={restaurant.id} className="restaurant-card">
            <h3>{restaurant.name}</h3>
            <p>{restaurant.address}</p>
            {restaurant.image_url && (
              <img src={restaurant.image_url} alt={`Image of ${restaurant.name}`} />
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default RestaurantsPage;
