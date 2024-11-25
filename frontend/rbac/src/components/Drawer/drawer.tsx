import {
	AppBar,
	Box,
	Button,
	Divider,
	Drawer,
	List,
	ListItem,
	ListItemButton,
	ListItemText,
	Toolbar,
	Typography,
} from "@mui/material";
import { routes } from "../../routes/routes";
import { useNavigate } from "react-router-dom";
import _ from "lodash";
import React from "react";

interface ICustomDrawer {
	children: JSX.Element;
}

const CustomDrawer = ({ children }: ICustomDrawer) => {
	const permissions = JSON.parse(localStorage.getItem("permissions")!);

	const navigate = useNavigate();

	return (
		<Box sx={{ display: "flex" }}>
			<AppBar
				position="fixed"
				sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}
			>
				<Toolbar sx={{ justifyContent: "space-between" }}>
					<Typography variant="h6">Full Stack RBAC</Typography>
					<Button
						color="inherit"
						onClick={() => {
							localStorage.removeItem("token");
							localStorage.removeItem("permissions");
							navigate("/login");
						}}
					>
						Logout
					</Button>
				</Toolbar>
			</AppBar>
			<Drawer
				variant="permanent"
				sx={{
					width: 240,
					flexShrink: 0,
					[`& .MuiDrawer-paper`]: {
						width: 240,
						boxSizing: "border-box",
					},
				}}
			>
				<Toolbar />
				<Box sx={{ overflow: "auto" }}>
					<List>
						{routes.map((route) => {
							let isAllowed = true;
							route.permissions.forEach((permission) => {
								if (!_.includes(permissions, permission))
									isAllowed = false;
							});

							return (
								isAllowed && (
									<React.Fragment key={route.title}>
										<ListItem disablePadding>
											<ListItemButton
												onClick={() =>
													navigate(route.path)
												}
											>
												<ListItemText
													primary={route.title}
												/>
											</ListItemButton>
										</ListItem>
										<Divider />
									</React.Fragment>
								)
							);
						})}
					</List>
				</Box>
			</Drawer>
			<Box sx={{ flexGrow: 1 }}>{children}</Box>
		</Box>
	);
};

export default CustomDrawer;
