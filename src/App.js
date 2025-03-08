import React, { useState } from "react";
import axios from "axios";
import { Container, TextField, Button, Typography, Paper, Grid, CircularProgress } from "@mui/material";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import { Bar } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from "chart.js";

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

function App() {
    const [expressionValues, setExpressionValues] = useState("");
    const [prediction, setPrediction] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [chartData, setChartData] = useState(null);
    const [file, setFile] = useState(null);

    const handleChange = (e) => {
        setExpressionValues(e.target.value);
    };

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const handleSubmit = async () => {
        setLoading(true);
        setError(null);
        setPrediction(null);
        setChartData(null);

        try {
            let response;
            if (file) {
                const formData = new FormData();
                formData.append("file", file);
                response = await axios.post("https://your-api.onrender.com/predict", formData, {
                    headers: { "Content-Type": "multipart/form-data" },
                });
            } else {
                const values = expressionValues.split(",").map(Number);
                response = await axios.post("https://your-api.onrender.com/predict", {
                    expression_values: values,
                });
            }

            setPrediction(response.data);
            if (!file) {
                setChartData({
                    labels: expressionValues.split(",").map((_, i) => `Gene ${i + 1}`),
                    datasets: [
                        {
                            label: "Expression Value",
                            data: expressionValues.split(",").map(Number),
                            backgroundColor: "rgba(75, 192, 192, 0.6)",
                        },
                    ],
                });
            }
        } catch (err) {
            setError("Error fetching prediction. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <Container maxWidth="md" sx={{ mt: 5 }}>
            <Paper elevation={3} sx={{ p: 4 }}>
                <Typography variant="h4" gutterBottom align="center">
                    Gene Expression Disease Predictor
                </Typography>

                <Grid container spacing={2}>
                    <Grid item xs={12}>
                        <TextField
                            fullWidth
                            label="Enter Expression Values (comma-separated)"
                            variant="outlined"
                            value={expressionValues}
                            onChange={handleChange}
                            disabled={file !== null}
                        />
                    </Grid>

                    <Grid item xs={12}>
                        <Button
                            variant="contained"
                            component="label"
                            startIcon={<CloudUploadIcon />}
                            fullWidth
                        >
                            Upload CSV
                            <input type="file" hidden onChange={handleFileChange} accept=".csv" />
                        </Button>
                    </Grid>

                    <Grid item xs={12}>
                        <Button
                            variant="contained"
                            color="primary"
                            onClick={handleSubmit}
                            fullWidth
                            disabled={loading}
                        >
                            {loading ? <CircularProgress size={24} /> : "Predict Disease"}
                        </Button>
                    </Grid>
                </Grid>

                {error && <Typography color="error" sx={{ mt: 2 }}>{error}</Typography>}

                {prediction && (
                    <Paper elevation={2} sx={{ p: 3, mt: 3 }}>
                        <Typography variant="h5">Prediction Results</Typography>
                        <Typography><strong>Random Forest:</strong> {prediction.RandomForestPrediction}</Typography>
                        <Typography><strong>SVM:</strong> {prediction.SVM_Prediction}</Typography>
                    </Paper>
                )}

                {chartData && (
                    <Paper elevation={2} sx={{ p: 3, mt: 3 }}>
                        <Typography variant="h5">Gene Expression Data</Typography>
                        <Bar data={chartData} options={{ responsive: true, maintainAspectRatio: false }} />
                    </Paper>
                )}
            </Paper>
        </Container>
    );
}

export default App;
