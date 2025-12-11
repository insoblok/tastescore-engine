import axios from "axios";

const apiClient = axios.create({
	baseURL: import.meta.env.VITE_API_URL,
	timeout: 30000, // Increased to 30 seconds for protocol checks
	headers: {
		"Content-Type": "application/json",
	},
});

export default apiClient;
