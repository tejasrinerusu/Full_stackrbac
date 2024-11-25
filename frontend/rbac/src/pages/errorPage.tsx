import { Box, Typography } from "@mui/material";

const ErrorPage = () => (
	<Box
		alignItems="center"
		display="flex"
		flexDirection="column"
		justifyContent="center"
		minHeight="100vh"
	>
		<Typography variant="h1">Unauthorized</Typography>
		<Typography variant="h3">
			You do not have permission to access this page
		</Typography>
	</Box>
);

export default ErrorPage;
