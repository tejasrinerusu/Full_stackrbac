import {
	Autocomplete,
	Box,
	Button,
	Grid,
	IconButton,
	TextField,
	Typography,
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import DeleteIcon from "@mui/icons-material/DeleteOutlined";
import DoneIcon from "@mui/icons-material/Done";
import LockOpenOutlinedIcon from "@mui/icons-material/LockOpenOutlined";
import LockOutlinedIcon from "@mui/icons-material/LockOutlined";
import { forwardRef, useCallback, useEffect, useState } from "react";
import {
	createRoleHasPermission,
	getRoleHasPermissions,
	removeRoleHasPermission,
	updateRoleHasPermission,
} from "../../axios/roleHasPermission";
import { PermissionData } from "../../schemas/permission";
import _ from "lodash";
import { getPermissions } from "../../axios/permission";
import { toast } from "react-toastify";

interface IRoleHasPermissionModal {
	id: string;
	name: string;
}

const RoleHasPermissionModal = forwardRef(
	({ id, name }: IRoleHasPermissionModal, ref) => {
		const [roleHasPermissionData, setRoleHasPermissionData] = useState<
			PermissionData[]
		>([]);
		const [permissionData, setPermissionData] = useState<PermissionData[]>(
			[]
		);
		const [addPermission, setAddPermission] = useState(false);
		const [newPermission, setNewPermission] = useState("");
		const [lock, setLock] = useState(true);

		const jwt = localStorage.getItem("token");

		const getRoleHasPermissionData = useCallback(async () => {
			setRoleHasPermissionData(await getRoleHasPermissions(id, jwt));
		}, [id, jwt]);

		const getPermissionData = useCallback(async () => {
			const permissions = await getPermissions(jwt);
			setPermissionData(permissions);
			setNewPermission(permissions[0].name);
		}, [jwt]);

		useEffect(() => {
			getRoleHasPermissionData();
			getPermissionData();
		}, [getRoleHasPermissionData, getPermissionData]);

		return (
			<Box
				sx={{
					position: "absolute" as "absolute",
					top: "50%",
					left: "50%",
					transform: "translate(-50%, -50%)",
					width: 400,
					bgcolor: "background.paper",
					borderRadius: 2,
					boxShadow: 24,
					p: 4,
				}}
			>
				<Typography variant="h5" sx={{ mb: 2 }}>
					Role: {name}
				</Typography>
				<Grid display="flex" alignItems="center">
					<Typography variant="h5">Permissions:</Typography>
					<IconButton
						onClick={() => {
							setLock(!lock);
						}}
					>
						{lock ? <LockOutlinedIcon /> : <LockOpenOutlinedIcon />}
					</IconButton>
				</Grid>
				{roleHasPermissionData.map((roleHasPermission) => {
					let changePermission: string;
					return (
						<Grid key={roleHasPermission.id} display="flex">
							<Autocomplete
								disabled={lock}
								disableClearable
								options={_.map(permissionData, "name")}
								sx={{ width: 200, my: 2 }}
								onChange={(_, newValue) => {
									changePermission = newValue;
								}}
								renderInput={(params) => (
									<TextField
										{...params}
										label={roleHasPermission.name}
									/>
								)}
							/>
							{!lock && (
								<IconButton
									sx={{ my: 2, ml: 5 }}
									onClick={async () => {
										const oldPermission = _.find(
											permissionData,
											{
												name: roleHasPermission.name,
											}
										);
										const newPermission = _.find(
											permissionData,
											{
												name: changePermission,
											}
										);
										if (!oldPermission || !newPermission) {
											toast.error(
												"permission id not found"
											);
											return;
										}

										await updateRoleHasPermission(
											id,
											oldPermission.id,
											newPermission.id,
											jwt
										);
										await getRoleHasPermissionData();
									}}
								>
									<DoneIcon />
								</IconButton>
							)}
							{lock && (
								<IconButton
									sx={{ my: 2, ml: 5 }}
									onClick={async () => {
										const permission = _.find(
											permissionData,
											{
												name: roleHasPermission.name,
											}
										);
										if (!permission) {
											toast.error(
												"permission id not found"
											);
											return;
										}
										await removeRoleHasPermission(
											id,
											permission.id,
											jwt
										);
										await getRoleHasPermissionData();
									}}
								>
									<DeleteIcon />
								</IconButton>
							)}
						</Grid>
					);
				})}
				{addPermission && (
					<Grid display="flex">
						<Autocomplete
							disableClearable
							options={_.map(permissionData, "name")}
							sx={{ width: 200, my: 2 }}
							value={newPermission}
							onChange={(_, newValue) =>
								setNewPermission(newValue)
							}
							renderInput={(params) => (
								<TextField {...params} label="New Permission" />
							)}
						/>
						<Button
							variant="contained"
							sx={{ my: 2, ml: 5, height: 50 }}
							onClick={async () => {
								const permission = _.find(permissionData, {
									name: newPermission,
								});
								if (!permission) {
									toast.error("permission id not found");
									return;
								}

								await createRoleHasPermission(
									id,
									permission.id,
									jwt
								);
								await getRoleHasPermissionData();
								setAddPermission(false);
							}}
						>
							Add
						</Button>
					</Grid>
				)}
				<Button
					disabled={addPermission}
					startIcon={<AddIcon />}
					onClick={() => setAddPermission(true)}
				>
					Add Permission
				</Button>
			</Box>
		);
	}
);

export default RoleHasPermissionModal;
