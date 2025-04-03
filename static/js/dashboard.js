document.addEventListener('DOMContentLoaded', function() {
    // Bar chart for monthly income vs expenses
    const monthlyBarChart = document.getElementById('monthlyBarChart');
    if (monthlyBarChart) {
        const ctx = monthlyBarChart.getContext('2d');
        const monthsLabels = JSON.parse(monthlyBarChart.dataset.months);
        const incomeData = JSON.parse(monthlyBarChart.dataset.income);
        const expenseData = JSON.parse(monthlyBarChart.dataset.expenses);

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: monthsLabels,
                datasets: [
                    {
                        label: 'Income',
                        data: incomeData,
                        backgroundColor: 'rgba(75, 192, 192, 0.7)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Expenses',
                        data: expenseData,
                        backgroundColor: 'rgba(255, 99, 132, 0.7)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Monthly Income vs Expenses'
                    },
                    legend: {
                        position: 'top'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.dataset.label}: ₹${context.raw.toFixed(2)}`;
                            }
                        }
                    }
                }
            }
        });
    }

    // Pie chart for income categories
    const incomePieChart = document.getElementById('incomePieChart');
    if (incomePieChart && JSON.parse(incomePieChart.dataset.categories).length > 0) {
        const ctx = incomePieChart.getContext('2d');
        const categories = JSON.parse(incomePieChart.dataset.categories);
        const amounts = JSON.parse(incomePieChart.dataset.amounts);

        // Generate random colors for each category
        const backgroundColors = generateColors(categories.length);

        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: categories,
                datasets: [{
                    data: amounts,
                    backgroundColor: backgroundColors,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Income by Category'
                    },
                    legend: {
                        position: 'right'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw.toFixed(2);
                                const total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.raw / total) * 100).toFixed(1);
                                return `${label}: ₹${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    // Pie chart for expense categories
    const expensePieChart = document.getElementById('expensePieChart');
    if (expensePieChart && JSON.parse(expensePieChart.dataset.categories).length > 0) {
        const ctx = expensePieChart.getContext('2d');
        const categories = JSON.parse(expensePieChart.dataset.categories);
        const amounts = JSON.parse(expensePieChart.dataset.amounts);

        // Generate random colors for each category
        const backgroundColors = generateColors(categories.length);

        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: categories,
                datasets: [{
                    data: amounts,
                    backgroundColor: backgroundColors,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Expenses by Category'
                    },
                    legend: {
                        position: 'right'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw.toFixed(2);
                                const total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.raw / total) * 100).toFixed(1);
                                return `${label}: ₹${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    // Helper function to generate random colors
    function generateColors(count) {
        const colors = [
            'rgba(255, 99, 132, 0.7)',
            'rgba(54, 162, 235, 0.7)',
            'rgba(255, 206, 86, 0.7)',
            'rgba(75, 192, 192, 0.7)',
            'rgba(153, 102, 255, 0.7)',
            'rgba(255, 159, 64, 0.7)',
            'rgba(199, 199, 199, 0.7)',
            'rgba(83, 102, 255, 0.7)',
            'rgba(40, 159, 64, 0.7)',
            'rgba(210, 199, 199, 0.7)',
        ];

        const result = [];
        for (let i = 0; i < count; i++) {
            result.push(colors[i % colors.length]);
        }
        return result;
    }

    // Handle budget alert dismissal
    const budgetAlert = document.getElementById('budgetAlert');
    if (budgetAlert) {
        const closeBtn = budgetAlert.querySelector('.btn-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                budgetAlert.style.display = 'none';
            });
        }
    }
});