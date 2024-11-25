import { Button } from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import { GridToolbarContainer } from "@mui/x-data-grid";

interface IAddToolBar {
	openModal: () => void;
	children?: React.ReactNode;
}

const AddToolBar = ({ openModal, children }: IAddToolBar) => (
	<GridToolbarContainer>
		<Button startIcon={<AddIcon />} onClick={openModal}>
			{children}
		</Button>
	</GridToolbarContainer>
);

export default AddToolBar;
