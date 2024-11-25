import axios from "axios";
import { UserData } from "../schemas/user";
import { toast } from "react-toastify";

const RbacUserAxiosInstance = axios.create({
	baseURL: `${process.env.REACT_APP_BACKEND_BASE_URL}/rbac/user`,
	headers: { "Content-Type": "application/json" },
});

export const createUser = async (
	email: string,
	password: string,
	token: string | null
): Promise<void> => {
	try {
		await RbacUserAxiosInstance.post(
			"",
			{ email: email, password: password },
			{
				headers: {
					Authorization: `Bearer ${token}`,
				},
			}
		);
		toast.success("User Created");
	} catch (error) {
		if (axios.isAxiosError(error)) {
			toast.error("you are not authorized");
			console.error({ error: error.message });
		}
	}
};

export const getUsers = async (token: string | null): Promise<UserData[]> => {
	try {
		const res = await RbacUserAxiosInstance.get("", {
			headers: {
				Authorization: `Bearer ${token}`,
			},
		});
		return res.data;
	} catch (error) {
		if (axios.isAxiosError(error)) {
			toast.error("you are not authorized");
			console.error({ error: error.message });
		}
		return [] as UserData[];
	}
};

export const updateUser = async (
	id: string,
	value: string,
	token: string | null
): Promise<void> => {
	try {
		await RbacUserAxiosInstance.patch(
			`/${id}`,
			{ email: value },
			{
				headers: {
					Authorization: `Bearer ${token}`,
				},
			}
		);
		toast.success("User email Updated");
	} catch (error) {
		if (axios.isAxiosError(error)) {
			toast.error("you are not authorized");
			console.error({ error: error.message });
		}
	}
};

export const removeUser = async (
	id: string,
	token: string | null
): Promise<void> => {
	try {
		await RbacUserAxiosInstance.delete(`/${id}`, {
			headers: {
				Authorization: `Bearer ${token}`,
			},
		});
		toast.success("User Deleted");
	} catch (error) {
		if (axios.isAxiosError(error)) {
			toast.error("you are not authorized");
			console.error({ error: error.message });
		}
	}
};
