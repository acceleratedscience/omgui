/**
    Convert data structure for Plotly compatibility
    - - -
    We follow the data structure from chart.js for data input,
    because it only declares the labels once, instead of repeating them.

    Input:
    {
        "labels": [
            "2024-12-05",
            "2024-12-12"
        ],
        "datasets": [
            {
                "label": "AMZN",
                "data": [
                    250.0, 266.94
                ]
            },
            {
                "label": "GOOGL",
                "data": [
                    350.0, 375.49
                ]
            }
        ]
    }

    Output:
    {
        "AMZN": {
            "x": [
                "2024-12-05",
                "2024-12-12"
            ],
            "y": [
                250.0, 266.94
            ]
        },
        "GOOGL": {
            "x": [
                "2024-12-05",
                "2024-12-12"
            ],
            "y": [
                350.0, 375.49
            ]
        }
    }
*/

function convertDataStructure(chartData) {
	// Return original data if the datastructure
	// doesn't follow the epxected pattern
	if (!chartData || !chartData.labels || !chartData.datasets) {
		return chartData
	}

	const convertedData = {}
	const labels = chartData.labels

	chartData.datasets.forEach((dataset) => {
		const label = dataset.label
		const data = dataset.data

		convertedData[label] = {
			x: labels,
			y: data,
		}
	})

	return convertedData
}
