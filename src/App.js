import React, { useState } from "react";
import { ThemeProvider, createTheme, CssBaseline, Container, Paper, Button, Typography, TextField } from "@mui/material";
import axios from "axios";

const API_URL = "https://your-api.onrender.com";
const theme = createTheme({ palette: { mode: "light" } });

export default function App() {
    const [message, setMessage] = useState("");
    const [response, setResponse] = useState("");

    const sendMessage = async () => {
        const res = await axios.post(`${API_URL}/chatbot`, { message });
        setResponse(res.data.response);
    };

    return (
        <ThemeProvider theme={theme}>
            <CssBaseline />
            <Container maxWidth="md">
                <Paper sx={{ p: 4, textAlign: "center" }}>
                    <Typography variant="h4">AI Chatbot for Biologists 🤖</Typography>
                    <TextField fullWidth label="Ask me anything..." variant="outlined" value={message} onChange={(e) => setMessage(e.target.value)} />
                    <Button variant="contained" color="primary" onClick={sendMessage} sx={{ mt: 2 }}>Ask AI</Button>
                    {response && <Typography variant="body1" sx={{ mt: 3 }}><strong>AI:</strong> {response}</Typography>}
                </Paper>
            </Container>
        </ThemeProvider>
    );
}
export defualt App;