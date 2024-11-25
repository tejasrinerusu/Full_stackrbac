import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import "./App.css";
import CustomDrawer from "./components/Drawer/drawer";
import { Navigate, Route, Routes } from "react-router-dom";
import LoginPage from "./pages/loginPage";
import { routes } from "./routes/routes";
import ProtectedRoute from "./routes/protectedRoute";
import ErrorPage from "./pages/errorPage";

function App() {
	return (
		<>
			<Routes>
				{routes.map((route) => (
					<Route
						path={route.path}
						element={
							<ProtectedRoute>
								<CustomDrawer>
									<route.container />
								</CustomDrawer>
							</ProtectedRoute>
						}
						key={route.path}
					>
						{route.children &&
							route.children.map((nestedRoute) => (
								<Route
									path={`${route.path}${nestedRoute.path}`}
									element={
										<ProtectedRoute>
											<nestedRoute.container />
										</ProtectedRoute>
									}
									key={`${route.path}${nestedRoute.path}`}
								/>
							))}
					</Route>
				))}
				<Route
					path="/login"
					element={
						<CustomDrawer>
							<LoginPage />
						</CustomDrawer>
					}
				/>
				<Route
					path="/error"
					element={
						<CustomDrawer>
							<ErrorPage />
						</CustomDrawer>
					}
				/>
				<Route path="*" element={<Navigate to="/" replace />} />
			</Routes>
			<ToastContainer />
		</>
	);
}

export default App;
