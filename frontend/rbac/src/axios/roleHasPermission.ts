import axios from "axios";
import { toast } from "react-toastify";
import { PermissionData } from "../schemas/permission";

const RbacRoleHasPermissionAxiosInstance = axios.create({
	baseURL: `${process.env.REACT_APP_BACKEND_BASE_URL}/rbac/role-has-permission`,
	headers: { "Content-Type": "application/json" },
});

export const createRoleHasPermission = async (
	roleId: string,
	permissionId: string,
	token: string | null
): Promise<void> => {
	try {
		await RbacRoleHasPermissionAxiosInstance.post(
			"",
			{ role_id: roleId, permission_id: permissionId },
			{
				headers: {
					Authorization: `Bearer ${token}`,
				},
			}
		);
		toast.success("Permission Mapped");
	} catch (error) {
		if (axios.isAxiosError(error)) {
			toast.error("you are not authorized");
			console.error({ error: error.message });
		}
	}
};

export const getRoleHasPermissions = async (
	id: string,
	token: string | null
): Promise<PermissionData[]> => {
	try {
		const res = await RbacRoleHasPermissionAxiosInstance.get(`/${id}`, {
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
		return [] as PermissionData[];
	}
};

export const updateRoleHasPermission = async (
	roleId: string,
	oldPermissionId: string,
	newPermissionId: string,
	token: string | null
): Promise<void> => {
	try {
		await RbacRoleHasPermissionAxiosInstance.patch(
			`/${roleId}`,
			{
				old_permission_id: oldPermissionId,
				new_permission_id: newPermissionId,
			},
			{
				headers: {
					Authorization: `Bearer ${token}`,
				},
			}
		);
		toast.success("Permission Mapped Updated");
	} catch (error) {
		if (axios.isAxiosError(error)) {
			toast.error("you are not authorized");
			console.error({ error: error.message });
		}
	}
};

export const removeRoleHasPermission = async (
	roleId: string,
	permissionId: string,
	token: string | null
): Promise<void> => {
	try {
		await RbacRoleHasPermissionAxiosInstance.delete(
			`/${roleId}/${permissionId}`,
			{
				headers: {
					Authorization: `Bearer ${token}`,
				},
			}
		);
		toast.success("Permission Mapped Deleted");
	} catch (error) {
		if (axios.isAxiosError(error)) {
			toast.error("you are not authorized");
			console.error({ error: error.message });
		}
	}
};
