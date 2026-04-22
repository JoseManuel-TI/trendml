"use client";

import {
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LineElement,
  LinearScale,
  PointElement,
  Tooltip,
} from "chart.js";
import { Line } from "react-chartjs-2";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

type Props = {
  labels: string[];
  values: number[];
  label: string;
};

export function LineChart({ labels, values, label }: Props) {
  return (
    <Line
      data={{
        labels,
        datasets: [
          {
            label,
            data: values,
            borderColor: "#10b981",
            backgroundColor: "rgba(16,185,129,0.25)",
            tension: 0.35,
          },
        ],
      }}
      options={{
        responsive: true,
        plugins: { legend: { display: true } },
      }}
    />
  );
}
