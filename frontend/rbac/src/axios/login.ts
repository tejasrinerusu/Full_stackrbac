import axios from "axios";
import { toast } from "react-toastify";
import { LoginData } from "../schemas/login";

const LoginAxiosInstance = axios.create({
	baseURL: process.env.REACT_APP_BACKEND_BASE_URL,
	headers: { "Content-Type": "application/json" },
});

export const login = async (
	email: string,
	password: string
): Promise<LoginData> => {
	try {
		const res = await LoginAxiosInstance.post("/auth/login", {
			email: email,
			password: password,
		});
		toast.success("Login success");
		return res.data;
	} catch (error) {
		if (axios.isAxiosError(error)) {
			toast.error("Incorrect email/password");
			console.error({ error: error.message });
		}
		return {} as LoginData;
	}
};
