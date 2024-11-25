import { useCallback, useEffect, useState } from "react";
import {
	createPermission,
	getPermissions,
	removePermission,
	updatePermission,
} from "../axios/permission";
import { PermissionData } from "../schemas/permission";
import { Box, Button, Modal, TextField, Typography } from "@mui/material";
import DeleteIcon from "@mui/icons-material/DeleteOutlined";
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
import { AddToolBar } from "../components/Rbac";
import _ from "lodash";

const PermissionPage = () => {
	const [permissionData, setPermissionData] = useState<PermissionData[]>([]);
	const [modalOpen, setModalOpen] = useState(false);
	const [newPermission, setNewPermission] = useState("");

	const jwt = localStorage.getItem("token");
	const permissions = JSON.parse(localStorage.getItem("permissions")!);

	const rows: GridRowsProp = permissionData;

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
			headerName: "Delete",
			width: 150,
			getActions: (params: GridRowParams<PermissionData>) => [
				<GridActionsCellItem
					icon={<DeleteIcon />}
					label="Delete"
					onClick={async () => {
						await removePermission(params.id.toString(), jwt);
						await getPermissionData();
					}}
					color="inherit"
				/>,
			],
		},
	];

	const getPermissionData = useCallback(async () => {
		setPermissionData(await getPermissions(jwt));
	}, [jwt]);

	useEffect(() => {
		getPermissionData();
	}, [getPermissionData]);

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
						await updatePermission(
							params.id.toString(),
							newValue,
							jwt
						);
						await getPermissionData();
					}}
					slots={{
						toolbar: _.includes(permissions, "setting.create")
							? AddToolBar
							: null,
					}}
					slotProps={{
						toolbar: {
							openModal: () => setModalOpen(true),
							children: "Add Permission",
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
						Create New Permission
					</Typography>
					<TextField
						label="Permission Name"
						variant="outlined"
						value={newPermission}
						onChange={(
							event: React.ChangeEvent<HTMLInputElement>
						) => {
							setNewPermission(event.target.value);
						}}
					/>
					<Button
						variant="contained"
						sx={{ ml: 5, height: 50 }}
						onClick={async () => {
							await createPermission(newPermission, jwt);
							await getPermissionData();
							setModalOpen(false);
							setNewPermission("");
						}}
					>
						Add
					</Button>
				</Box>
			</Modal>
		</Box>
	);
};

export default PermissionPage;
