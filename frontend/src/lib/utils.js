export async function handleRequest(request) {
    try {
        const response = await request;
        return response.data;
    } catch (error) {
        if (error.response)
            throw error.response.data;

        throw {
            msg: "Network error. Please try again.",
            errors: error.name + ":" + error.message
        };
    }
}
