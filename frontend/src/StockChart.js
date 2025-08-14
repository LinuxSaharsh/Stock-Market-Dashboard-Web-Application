import React from "react";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from "chart.js";

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

export default function StockChart() {
  // Mock stock price data
  const stockLabels = ["Mon", "Tue", "Wed", "Thu", "Fri"];
  const stockPrices = [150, 153, 148, 155, 160];

  const data = {
    labels: stockLabels,
    datasets: [
      {
        label: "AAPL Stock Price ($)",
        data: stockPrices,
        borderColor: "rgba(75,192,192,1)",
        backgroundColor: "rgba(75,192,192,0.2)",
        tension: 0.3,
        fill: true
      }
    ]
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { position: "top" },
      title: { display: true, text: "Apple Inc. Stock Prices" }
    }
  };

  return <Line data={data} options={options} />;
}
