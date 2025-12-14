document.addEventListener("DOMContentLoaded", () => {
    const canvas = document.getElementById("progressChart");

    if (!canvas) {
        console.error("Canvas progressChart introuvable");
        return;
    }

    const ctx = canvas.getContext("2d");

    new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Séances",
                    data: sessions,
                    backgroundColor: "rgba(29,161,242,0.7)",
                    yAxisID: "y1"
                },
                {
                    label: "Durée (min)",
                    data: durations,
                    backgroundColor: "rgba(72,219,251,0.7)",
                    yAxisID: "y1"
                },
                {
                    label: "Charge totale (kg x reps)",
                    data: totalWeight,
                    type: "line",
                    borderColor: "rgba(255,99,132,1)",
                    backgroundColor: "rgba(255,99,132,0.2)",
                    fill: true,
                    yAxisID: "y2"
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: "index",
                intersect: false
            },
            plugins: {
                legend: {
                    labels: {
                        color: "white"
                    }
                }
            },
            scales: {
                x: {
                    ticks: { color: "white" }
                },
                y1: {
                    type: "linear",
                    position: "left",
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: "Séances / Durée (min)",
                        color: "white"
                    },
                    ticks: { color: "white" }
                },
                y2: {
                    type: "linear",
                    position: "right",
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: "Charge totale (kg x reps)",
                        color: "white"
                    },
                    ticks: { color: "white" },
                    grid: {
                        drawOnChartArea: false
                    }
                }
            }
        }
    });
});
