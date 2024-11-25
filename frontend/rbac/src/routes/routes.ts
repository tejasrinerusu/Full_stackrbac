import HomePage from "../pages/homePage";
import SettingPage from "../pages/settingPage";

interface Route {
	container: () => JSX.Element;
	path: string;
	showHeader: boolean;
	title?: string;
	children?: Route[];
	permissions: string[];
}

export const routes: Route[] = [
	{
		container: HomePage,
		path: "/",
		showHeader: true,
		title: "Home",
		permissions: [],
	},
	{
		container: SettingPage,
		path: "/setting",
		showHeader: true,
		title: "Setting",
		permissions: ["setting.read"],
	},
];
