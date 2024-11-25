import { Box } from "@mui/material";
import { useState } from "react";
import _ from "lodash";
import { login } from "../axios/login";
import Login from "../components/Login";
import { useNavigate } from "react-router-dom";

const LoginPage = () => {
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");

	const navigate = useNavigate();

	const onSubmitHandler = async () => {
		const { permissions, token } = await login(email, password);
		if (_.isEmpty(token)) return;
		localStorage.setItem("permissions", JSON.stringify(permissions));
		localStorage.setItem("token", token);
		navigate("/");
	};

	return (
		<Box
			alignItems="center"
			display="flex"
			justifyContent="center"
			minHeight="100vh"
		>
			<Login
				email={email}
				setEmail={setEmail}
				password={password}
				setPassword={setPassword}
				onSubmitHandler={onSubmitHandler}
			/>
		</Box>
	);
};

export default LoginPage;
