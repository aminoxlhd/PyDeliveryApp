import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:5000',
});

export const getRestaurants = async () => {
    const response = await api.get('/restaurants');
    return response.data;
};

export const loginUser = async (email: string, password: string) => {
    const response = await api.post('/login', { email, password });
    return response.data;
};

