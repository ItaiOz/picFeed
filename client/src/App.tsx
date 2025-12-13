import { Container, Grid, CircularProgress, Alert, Box } from "@mui/material";
import { Header } from "./components/Header";
import { ImageCard } from "./components/ImageCard";
import { useAppRequests } from "./hooks/useAppRequests";

export const App = () => {
  const {
    images,
    loading,
    error,
    handleVote,
    handleExport,
  } = useAppRequests();

  if (loading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
      >
        <CircularProgress size={60} />
      </Box>
    );
  }

  if (error) {
    return (
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Alert severity="error">Error: {error}</Alert>
      </Container>
    );
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Header onExport={handleExport} />
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Grid container spacing={3}>
          {images.map((image) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={image.id}>
              <ImageCard image={image} onVote={handleVote} />
            </Grid>
          ))}
        </Grid>
      </Container>
    </Box>
  );
};
