import { AppBar, Toolbar, Typography, Button } from "@mui/material";
import { FileDownload } from "@mui/icons-material";

interface HeaderProps {
  onExport: () => void;
}

export const Header = ({ onExport }: HeaderProps) => {
  return (
    <AppBar position="static" color="primary" elevation={2}>
      <Toolbar>
        <Typography variant="h5" component="div" sx={{ flexGrow: 1 }}>
          📸 PicsFeed - Vote on Random Pictures
        </Typography>
        <Button
          color="inherit"
          startIcon={<FileDownload />}
          onClick={onExport}
          variant="outlined"
          sx={{ borderColor: "white", "&:hover": { borderColor: "white" } }}
        >
          Export to CSV
        </Button>
      </Toolbar>
    </AppBar>
  );
};
