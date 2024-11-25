import axios from "axios";
import { RoleData } from "../schemas/role";
import { toast } from "react-toastify";

const RbacRoleAxiosInstance = axios.create({
	baseURL: `${process.env.REACT_APP_BACKEND_BASE_URL}/rbac/role`,
	headers: { "Content-Type": "application/json" },
});

export const createRole = async (
	value: string,
	token: string | null
): Promise<void> => {
	try {
		await RbacRoleAxiosInstance.post(
			"",
			{ name: value },
			{
				headers: {
					Authorization: `Bearer ${token}`,
				},
			}
		);
		toast.success("Role Created");
	} catch (error) {
		if (axios.isAxiosError(error)) {
			toast.error("you are not authorized");
			console.error({ error: error.message });
		}
	}
};

export const getRoles = async (token: string | null): Promise<RoleData[]> => {
	try {
		const res = await RbacRoleAxiosInstance.get("", {
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
		return [] as RoleData[];
	}
};

export const updateRole = async (
	id: string,
	value: string,
	token: string | null
): Promise<void> => {
	try {
		await RbacRoleAxiosInstance.patch(
			`/${id}`,
			{ name: value },
			{
				headers: {
					Authorization: `Bearer ${token}`,
				},
			}
		);
		toast.success("Role name Updated");
	} catch (error) {
		if (axios.isAxiosError(error)) {
			toast.error("you are not authorized");
			console.error({ error: error.message });
		}
	}
};

export const removeRole = async (
	id: string,
	token: string | null
): Promise<void> => {
	try {
		await RbacRoleAxiosInstance.delete(`/${id}`, {
			headers: {
				Authorization: `Bearer ${token}`,
			},
		});
		toast.success("Role Deleted");
	} catch (error) {
		if (axios.isAxiosError(error)) {
			toast.error("you are not authorized");
			console.error({ error: error.message });
		}
	}
};
