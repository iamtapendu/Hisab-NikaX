import api from '@/lib/api';


export async function getProfile() {
    try {
        const response = await api.get("/users/profile");
        return response.data;
    } catch (error) {
        if (error.response)
            throw error.response.data;

        throw { msg: "Network error. Please try again.", errors: error.name + ":" + error.message };
    }

}

export async function getAllUsers() {
    try {
        const response = await api.get("/users/");
        return response.data;
    } catch (error) {
        if (error.response)
            throw error.response.data;

        throw { msg: "Network error. Please try again.", errors: error.name + ":" + error.message };
    }

}
