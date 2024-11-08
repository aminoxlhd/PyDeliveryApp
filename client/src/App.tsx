import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import RestaurantsPage from './pages/RestaurantsPage';
import MenuPage from './pages/MenuPage';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<RestaurantsPage />} />
          <Route path="/restaurant/:restaurantId/menu" element={<MenuPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;

