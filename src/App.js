import React, { useState } from "react";
import axios from "axios";
import "bootstrap/dist/css/bootstrap.min.css";
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
                response = await axios.post("http://127.0.0.1:8080/predict", formData, {
                    headers: { "Content-Type": "multipart/form-data" },
                });
            } else {
                const values = expressionValues.split(",").map(Number);
                response = await axios.post("http://127.0.0.1:8080/predict", {
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
        <div className="container mt-4">
            <h2 className="mb-3">Gene Expression Disease Predictor</h2>
            
            <input
                type="text"
                className="form-control"
                placeholder="Enter expression values, e.g. 1.2, 0.5, -0.8, 2.3"
                value={expressionValues}
                onChange={handleChange}
                disabled={file !== null}
            />
            
            <div className="mt-3">
                <input type="file" className="form-control" onChange={handleFileChange} accept=".csv" />
            </div>

            <button className="btn btn-primary mt-3" onClick={handleSubmit} disabled={loading}>
                {loading ? "Predicting..." : "Predict Disease"}
            </button>

            {error && <p className="text-danger mt-3">{error}</p>}

            {prediction && (
                <div className="mt-3">
                    <h4>Prediction Results:</h4>
                    <p><strong>Random Forest:</strong> {prediction.RandomForestPrediction}</p>
                    <p><strong>SVM:</strong> {prediction.SVM_Prediction}</p>
                </div>
            )}

            {chartData && (
                <div className="mt-4">
                    <h4>Gene Expression Data</h4>
                    <Bar data={chartData} options={{ responsive: true, maintainAspectRatio: false }} />
                </div>
            )}
        </div>
    );
}

export default App;
