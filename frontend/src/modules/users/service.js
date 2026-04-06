import api from '@/lib/api';
import { handleRequest } from '@/lib/utils';

export const getProfile = () => {
    return handleRequest(api.get("/users/profile"));
}

export const getAllUsers = () => {
    return handleRequest(api.get("/users/"));
}

export const getUser = (user_id) => {
    return handleRequest(api.get(`/users/${user_id}`));
}

export const getUserByUsername = (username) => {
    return handleRequest(api.get(`/users/username/${username}`));
}

export const createUser = (payload) => {
    return handleRequest(api.post("/users/", payload));
}

export const updateUser = (user_id, payload) => {
    return handleRequest(api.put(`/users/${user_id}`, payload));
}

export const updatePassword = (user_id, payload) => {
    return handleRequest(api.patch(`/users/${user_id}`, payload));
}