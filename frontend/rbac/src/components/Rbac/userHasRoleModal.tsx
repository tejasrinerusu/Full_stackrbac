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
import { RoleData } from "../../schemas/role";
import {
	createUserHasRole,
	getUserHasRoles,
	removeUserHasRole,
	updateUserHasRole,
} from "../../axios/userHasRole";
import { getRoles } from "../../axios/role";
import _ from "lodash";
import { toast } from "react-toastify";

interface IUserHasRoleModal {
	id: string;
	email: string;
}

const UserHasRoleModal = forwardRef(({ id, email }: IUserHasRoleModal, ref) => {
	const [userHasRoleData, setUserHasRoleData] = useState<RoleData[]>([]);
	const [roleData, setRoleData] = useState<RoleData[]>([]);
	const [addRole, setAddRole] = useState(false);

	const [newRole, setNewRole] = useState("");
	const [lock, setLock] = useState(true);

	const jwt = localStorage.getItem("token");

	const getUserHasRoleData = useCallback(async () => {
		setUserHasRoleData(await getUserHasRoles(id, jwt));
	}, [id, jwt]);

	const getRoleData = useCallback(async () => {
		const roles = await getRoles(jwt);
		setRoleData(roles);
		setNewRole(roles[0].name);
	}, [jwt]);

	useEffect(() => {
		getUserHasRoleData();
		getRoleData();
	}, [getUserHasRoleData, getRoleData]);

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
				User: {email}
			</Typography>
			<Grid display="flex" alignItems="center">
				<Typography variant="h5">Role:</Typography>
				<IconButton
					onClick={() => {
						setLock(!lock);
					}}
				>
					{lock ? <LockOutlinedIcon /> : <LockOpenOutlinedIcon />}
				</IconButton>
			</Grid>
			{userHasRoleData.map((userHasRole) => {
				let changeRole: string;
				return (
					<Grid key={userHasRole.id} display="flex">
						<Autocomplete
							disabled={lock}
							disableClearable
							options={_.map(roleData, "name")}
							sx={{ width: 200, my: 2 }}
							onChange={(_, newValue) => {
								changeRole = newValue;
							}}
							renderInput={(params) => (
								<TextField
									{...params}
									label={userHasRole.name}
								/>
							)}
						/>
						{!lock && (
							<IconButton
								sx={{ my: 2, ml: 5 }}
								onClick={async () => {
									const oldRole = _.find(roleData, {
										name: userHasRole.name,
									});
									const newRole = _.find(roleData, {
										name: changeRole,
									});
									if (!oldRole || !newRole) {
										toast.error("role id not found");
										return;
									}

									await updateUserHasRole(
										id,
										oldRole.id,
										newRole.id,
										jwt
									);
									await getUserHasRoleData();
								}}
							>
								<DoneIcon />
							</IconButton>
						)}
						{lock && (
							<IconButton
								sx={{ my: 2, ml: 5 }}
								onClick={async () => {
									const role = _.find(roleData, {
										name: userHasRole.name,
									});
									if (!role) {
										toast.error("role id not found");
										return;
									}
									await removeUserHasRole(id, role.id, jwt);
									await getUserHasRoleData();
								}}
							>
								<DeleteIcon />
							</IconButton>
						)}
					</Grid>
				);
			})}
			{addRole && (
				<Grid display="flex">
					<Autocomplete
						disableClearable
						options={_.map(roleData, "name")}
						sx={{ width: 200, my: 2 }}
						value={newRole}
						onChange={(_, newValue) => setNewRole(newValue)}
						renderInput={(params) => (
							<TextField {...params} label="New Role" />
						)}
					/>
					<Button
						variant="contained"
						sx={{ my: 2, ml: 5, height: 50 }}
						onClick={async () => {
							const role = _.find(roleData, {
								name: newRole,
							});
							if (!role) {
								toast.error("role id not found");
								return;
							}

							await createUserHasRole(id, role.id, jwt);
							await getUserHasRoleData();
							setAddRole(false);
						}}
					>
						Add
					</Button>
				</Grid>
			)}
			<Button
				disabled={addRole}
				startIcon={<AddIcon />}
				onClick={() => setAddRole(true)}
			>
				Add Role
			</Button>
		</Box>
	);
});

export default UserHasRoleModal;
