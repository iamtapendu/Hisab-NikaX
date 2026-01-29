import api from "../../lib/api";

export async function loginUser({ username, password }) {
    const payload = new URLSearchParams();
    payload.append("grant_type", "password");
    payload.append("username", username);
    payload.append("password", password);
    payload.append("scope", "");

    try {
        const response = await api.post(
            "/auth/login",
            payload,
            {
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            }
        );

        return response.data;
        // {
        //   access_token,
        //   refresh_token,
        //   token_type
        // }

    } catch (error) {
        if (error.response) {
            // Backend 4xx / 5xx
            throw error.response.data;
        }

        // Network / timeout error
        throw { msg: "Network error. Please try again.", errors: {} };
    }
}
