import jwtDecode, { JwtPayload } from "jwt-decode";
import { Navigate } from "react-router-dom";

interface IProtectedRoute {
	children: JSX.Element;
}

const ProtectedRoute = ({ children }: IProtectedRoute) => {
	const jwt = localStorage.getItem("token");
	if (!jwt) return <Navigate to="/login" replace />;
	const payload = jwtDecode<JwtPayload>(jwt);
	if (!payload.exp) return <Navigate to="/login" replace />;
	if (payload.exp * 1000 < Date.now()) {
		return <Navigate to="/login" replace />;
	}

	return children;
};

export default ProtectedRoute;
