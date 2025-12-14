document.addEventListener('DOMContentLoaded', () => {

    const chartLabels = JSON.parse(
        document.getElementById('labels-data').textContent
    );
    const sessionCounts = JSON.parse(
        document.getElementById('sessions-data').textContent
    );
    const durations = JSON.parse(
        document.getElementById('durations-data').textContent
    );
    const totalWeight = JSON.parse(
        document.getElementById('weight-data').textContent
    );

    const ctx = document.getElementById('progressChart');

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartLabels,
            datasets: [
                {
                    label: 'Séances',
                    data: sessionCounts,
                },
                {
                    label: 'Durée totale (min)',
                    data: durations,
                },
                {
                    label: 'Charge totale (kg)',
                    data: totalWeight,
                }
            ]
        }
    });

});
