import axios from "axios";
import { toast } from "react-toastify";
import { RoleData } from "../schemas/role";

const RbacUserHasRoleAxiosInstance = axios.create({
	baseURL: `${process.env.REACT_APP_BACKEND_BASE_URL}/rbac/user-has-role`,
	headers: { "Content-Type": "application/json" },
});

export const createUserHasRole = async (
	userId: string,
	roleId: string,
	token: string | null
): Promise<void> => {
	try {
		await RbacUserHasRoleAxiosInstance.post(
			"",
			{ user_id: userId, role_id: roleId },
			{
				headers: {
					Authorization: `Bearer ${token}`,
				},
			}
		);
		toast.success("Role Mapped");
	} catch (error) {
		if (axios.isAxiosError(error)) {
			toast.error("you are not authorized");
			console.error({ error: error.message });
		}
	}
};

export const getUserHasRoles = async (
	id: string,
	token: string | null
): Promise<RoleData[]> => {
	try {
		const res = await RbacUserHasRoleAxiosInstance.get(`/${id}`, {
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

export const updateUserHasRole = async (
	userId: string,
	oldRoleId: string,
	newRoleId: string,
	token: string | null
): Promise<void> => {
	try {
		await RbacUserHasRoleAxiosInstance.patch(
			`/${userId}`,
			{
				old_role_id: oldRoleId,
				new_role_id: newRoleId,
			},
			{
				headers: {
					Authorization: `Bearer ${token}`,
				},
			}
		);
		toast.success("Role Mapped Updated");
	} catch (error) {
		if (axios.isAxiosError(error)) {
			toast.error("you are not authorized");
			console.error({ error: error.message });
		}
	}
};

export const removeUserHasRole = async (
	userId: string,
	roleId: string,
	token: string | null
): Promise<void> => {
	try {
		await RbacUserHasRoleAxiosInstance.delete(`/${userId}/${roleId}`, {
			headers: {
				Authorization: `Bearer ${token}`,
			},
		});
		toast.success("Role Mapped Deleted");
	} catch (error) {
		if (axios.isAxiosError(error)) {
			toast.error("you are not authorized");
			console.error({ error: error.message });
		}
	}
};
