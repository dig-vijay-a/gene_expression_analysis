import React, { useState } from "react";
import { Container, TextField, Button, Typography, Paper, Grid, CircularProgress } from "@mui/material";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import axios from "axios";

const API_URL = "http://127.0.0.1:5000";

function App() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [token, setToken] = useState(localStorage.getItem("token"));
    const [expressionValues, setExpressionValues] = useState("");
    const [prediction, setPrediction] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [file, setFile] = useState(null);

    const handleAuth = async (endpoint) => {
        try {
            const response = await axios.post(`${API_URL}/${endpoint}`, { username, password });
            if (endpoint === "login") {
                localStorage.setItem("token", response.data.token);
                setToken(response.data.token);
            }
            alert(response.data.message || "Login Successful");
        } catch (err) {
            alert(err.response.data.error || "Authentication failed");
        }
    };

    const handleLogout = () => {
        localStorage.removeItem("token");
        setToken(null);
    };

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

        try {
            let response;
            const headers = { Authorization: `Bearer ${token}` };

            if (file) {
                const formData = new FormData();
                formData.append("file", file);
                response = await axios.post(`${API_URL}/predict`, formData, { headers });
            } else {
                const values = expressionValues.split(",").map(Number);
                response = await axios.post(`${API_URL}/predict`, { expression_values: values }, { headers });
            }

            setPrediction(response.data);
        } catch (err) {
            setError("Error fetching prediction. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <Container maxWidth="md" sx={{ mt: 5 }}>
            <Paper elevation={3} sx={{ p: 4 }}>
                {!token ? (
                    <>
                        <Typography variant="h4" gutterBottom>Login / Register</Typography>
                        <TextField fullWidth label="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
                        <TextField fullWidth type="password" label="Password" value={password} onChange={(e) => setPassword(e.target.value)} sx={{ mt: 2 }} />
                        <Button variant="contained" sx={{ mt: 2 }} onClick={() => handleAuth("register")}>Register</Button>
                        <Button variant="contained" sx={{ mt: 2, ml: 2 }} onClick={() => handleAuth("login")}>Login</Button>
                    </>
                ) : (
                    <>
                        <Typography variant="h4">Gene Expression Predictor</Typography>
                        <Button variant="contained" color="secondary" onClick={handleLogout} sx={{ float: "right" }}>Logout</Button>

                        <TextField fullWidth label="Enter Expression Values" value={expressionValues} onChange={handleChange} sx={{ mt: 2 }} />
                        <Button variant="contained" component="label" startIcon={<CloudUploadIcon />} sx={{ mt: 2 }}>
                            Upload CSV <input type="file" hidden onChange={handleFileChange} accept=".csv" />
                        </Button>
                        <Button variant="contained" onClick={handleSubmit} sx={{ mt: 2 }}>{loading ? <CircularProgress size={24} /> : "Predict"}</Button>

                        {prediction && <Typography variant="h6">Prediction: {JSON.stringify(prediction)}</Typography>}
                    </>
                )}
            </Paper>
        </Container>
    );
}

export default App;