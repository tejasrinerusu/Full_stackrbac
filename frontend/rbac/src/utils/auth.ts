import _ from "lodash";
import { routes } from "../routes/routes";

export const auth = (path: string) => {
	const permissions = JSON.parse(localStorage.getItem("permissions")!);

	routes.forEach((route) => {
		if (route.path === path) {
			route.permissions.forEach((permission) => {
				if (!_.includes(permissions, permission))
					window.location.href = "/error";
			});
		}
	});
};
