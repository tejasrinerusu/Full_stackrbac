import { useCallback, useEffect, useState } from "react";
import { RoleData } from "../schemas/role";
import { createRole, getRoles, removeRole, updateRole } from "../axios/role";
import { Box, Button, Modal, TextField, Typography } from "@mui/material";
import _ from "lodash";
import {
	DataGrid,
	GridActionsCellItem,
	GridCellEditStopParams,
	GridColDef,
	GridRowParams,
	GridRowsProp,
	MuiBaseEvent,
	MuiEvent,
} from "@mui/x-data-grid";
import DeleteIcon from "@mui/icons-material/DeleteOutlined";
import EditIcon from "@mui/icons-material/Edit";
import { AddToolBar, RoleHasPermissionModal } from "../components/Rbac";

const RolePage = () => {
	const [roleData, setRoleData] = useState<RoleData[]>([]);
	const [modalOpen, setModalOpen] = useState(false);
	const [roleHasPermissionModalOpen, setRoleHasPermissionModalOpen] =
		useState(false);
	const [newRole, setNewRole] = useState("");
	const [roleHasPermission, setRoleHasPermission] = useState("");
	const [roleHasPermissionId, setRoleHasPermissionId] = useState("");

	const jwt = localStorage.getItem("token");
	const permissions = JSON.parse(localStorage.getItem("permissions")!);

	const rows: GridRowsProp = roleData;

	const columns: GridColDef[] = [
		{ field: "id", headerName: "ID", width: 150 },
		{
			field: "name",
			headerName: "Name",
			width: 150,
			editable: _.includes(permissions, "setting.update") ? true : false,
		},
		{
			field: "actions",
			type: "actions",
			headerName: "Edit/Delete",
			width: 150,
			getActions: (params: GridRowParams<RoleData>) => [
				<GridActionsCellItem
					icon={<EditIcon />}
					label="Edit"
					onClick={() => {
						setRoleHasPermission(params.row.name);
						setRoleHasPermissionId(params.id.toString());
						setRoleHasPermissionModalOpen(true);
					}}
				/>,
				<GridActionsCellItem
					icon={<DeleteIcon />}
					label="Delete"
					onClick={async () => {
						await removeRole(params.id.toString(), jwt);
						await getRoleData();
					}}
					color="inherit"
				/>,
			],
		},
	];

	const getRoleData = useCallback(async () => {
		setRoleData(await getRoles(jwt));
	}, [jwt]);

	useEffect(() => {
		getRoleData();
	}, [getRoleData]);

	return (
		<Box
			sx={{
				width: "100%",
			}}
		>
			{_.includes(permissions, "setting.read") && (
				<DataGrid
					rows={rows}
					columns={columns}
					initialState={{
						columns: {
							columnVisibilityModel: {
								actions: _.includes(
									permissions,
									"setting.delete"
								)
									? true
									: false,
								id: false,
							},
						},
					}}
					onCellEditStop={async (
						params: GridCellEditStopParams,
						event: MuiEvent<MuiBaseEvent>
					) => {
						const newValue = (
							(event as React.SyntheticEvent<HTMLElement>)
								.target as HTMLInputElement
						).value;
						if (newValue === undefined || newValue === params.value)
							return;
						await updateRole(params.id.toString(), newValue, jwt);
						await getRoleData();
					}}
					slots={{
						toolbar: _.includes(permissions, "setting.create")
							? AddToolBar
							: null,
					}}
					slotProps={{
						toolbar: {
							openModal: () => setModalOpen(true),
							children: "Add Role",
						},
					}}
				/>
			)}

			<Modal open={modalOpen} onClose={() => setModalOpen(false)}>
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
					<Typography variant="h5" sx={{ mb: 5 }}>
						Create New Role
					</Typography>
					<TextField
						label="Role Name"
						variant="outlined"
						value={newRole}
						onChange={(
							event: React.ChangeEvent<HTMLInputElement>
						) => {
							setNewRole(event.target.value);
						}}
					/>
					<Button
						variant="contained"
						sx={{ ml: 5, height: 50 }}
						onClick={async () => {
							await createRole(newRole, jwt);
							await getRoleData();
							setModalOpen(false);
							setNewRole("");
						}}
					>
						Add
					</Button>
				</Box>
			</Modal>

			<Modal
				open={roleHasPermissionModalOpen}
				onClose={() => setRoleHasPermissionModalOpen(false)}
			>
				<RoleHasPermissionModal
					id={roleHasPermissionId}
					name={roleHasPermission}
				/>
			</Modal>
		</Box>
	);
};

export default RolePage;
