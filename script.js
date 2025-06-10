document.addEventListener('DOMContentLoaded', () => {
    const unifiedFileInput = document.getElementById('unifiedFileInput');
    const unifiedFileListContainer = document.getElementById('unified-file-list-container');
    const unifiedFileListEl = document.getElementById('unified-file-list');
    const analyzeDataButton = document.getElementById('analyzeDataButton');
    const comparisonChartCard = document.getElementById('comparisonChartCard');
    const anomalyExplanationsCard = document.getElementById('anomalyExplanationsCard');
    const anomalyDetailsContainer = document.getElementById('anomalyDetailsContainer');
    const resultsSection = document.getElementById('resultsSection');
    const messageBanner = document.getElementById('message-banner');
    const messageText = document.getElementById('message-text');
    const closeMessageBanner = document.getElementById('close-message-banner');

    let allSelectedFiles = []; 
    let comparisonChartInstance = null; 

    document.getElementById('currentYear').textContent = new Date().getFullYear();
    
    function showMessage(message, type = 'info') {
        messageText.textContent = message;
        messageBanner.className = 'message-banner';
        messageBanner.classList.add(type);
        messageBanner.classList.remove('hidden');
    }
    closeMessageBanner.addEventListener('click', () => messageBanner.classList.add('hidden'));

    unifiedFileInput.addEventListener('change', (event) => {
        allSelectedFiles = Array.from(event.target.files);
        unifiedFileListEl.innerHTML = ''; 
        if (allSelectedFiles.length > 0) {
            let csvCount = 0;
            let jsonCount = 0;
            allSelectedFiles.forEach(file => {
                const listItem = document.createElement('li');
                listItem.textContent = `${file.name} (${file.type || 'unknown type'})`;
                unifiedFileListEl.appendChild(listItem);
                if (file.name.endsWith('.csv')) csvCount++;
                else if (file.name.endsWith('.json')) jsonCount++;
            });
            unifiedFileListContainer.classList.remove('hidden');
            messageBanner.classList.add('hidden'); 
            if (csvCount > 2) showMessage('Please select a maximum of 2 CSV files.', 'info');
            if (jsonCount > 1) showMessage('Please select a maximum of 1 JSON file.', 'info');
            if (csvCount > 0 && csvCount !== 2 && csvCount <=2) showMessage('For chart analysis, please select exactly 2 CSV files.', 'info');
        } else {
            unifiedFileListContainer.classList.add('hidden');
        }
    });
    
    analyzeDataButton.addEventListener('click', async () => {
        if (allSelectedFiles.length === 0) {
            showMessage('Please select files to process.', 'error');
            return;
        }
        let csvFiles = allSelectedFiles.filter(file => file.name.endsWith('.csv'));
        let jsonFiles = allSelectedFiles.filter(file => file.name.endsWith('.json'));

        if (csvFiles.length > 2 || jsonFiles.length > 1 || (csvFiles.length > 0 && csvFiles.length !== 2)) {
            if (csvFiles.length > 2) showMessage('Too many CSV files. Select max 2.', 'error');
            if (jsonFiles.length > 1) showMessage('Too many JSON files. Select max 1.', 'error');
            if (csvFiles.length > 0 && csvFiles.length !== 2) showMessage('For chart, select exactly 2 CSVs.', 'error');
            return;
        }

        analyzeDataButton.disabled = true;
        analyzeDataButton.innerHTML = `<span class="btn-icon"><i class="fa-solid fa-spinner fa-spin"></i></span><span class="btn-text">Analyzing...</span>`;
        comparisonChartCard.classList.add('hidden');
        anomalyExplanationsCard.classList.add('hidden');
        if (comparisonChartInstance) {
            comparisonChartInstance.destroy(); 
            comparisonChartInstance = null;
        }
        anomalyDetailsContainer.innerHTML = '';

        try {
            showMessage('Processing files...', 'info');
            const backendResponse = await sendFilesToBackendAndGetResults(csvFiles, jsonFiles[0]);
            messageBanner.classList.add('hidden'); 
            let resultsDisplayed = false;

            if (backendResponse.csvFile1Content && backendResponse.csvFile2Content) {
                displayAnomalyPercentageChart(backendResponse.csvFile1Content, backendResponse.csvFile2Content);
                resultsDisplayed = true;
            }
            if (backendResponse.jsonExplanationData) {
                try {
                    const jsonData = JSON.parse(backendResponse.jsonExplanationData);
                    displayAnomalyExplanations(jsonData);
                    resultsDisplayed = true;
                } catch (jsonError) {
                    console.error("Error parsing JSON from backend:", jsonError);
                    showMessage(`Error displaying explanations: Invalid JSON. ${jsonError.message}`, 'error');
                }
            }
            if (resultsDisplayed) {
                resultsSection.classList.remove('hidden');
                setTimeout(() => resultsSection.classList.add('visible'), 50);
            } else if (csvFiles.length === 0 && jsonFiles.length === 0 && allSelectedFiles.length > 0) {
                showMessage('No valid CSV or JSON files were selected for processing.', 'info');
            } else if (allSelectedFiles.length === 0) {
                showMessage('No files selected.', 'info');
            }
        } catch (error) {
            console.error("Error in analysis:", error);
            showMessage(`Analysis Error: ${error.message || 'Unknown error.'}`, 'error');
        } finally {
            analyzeDataButton.disabled = false;
            analyzeDataButton.innerHTML = `<span class="btn-icon"><i class="fa-solid fa-magnifying-glass-chart"></i></span><span class="btn-text">Analyze Data</span>`;
        }
    });

    async function sendFilesToBackendAndGetResults(csvFileObjects, jsonFileObject) {
        const readFileAsText = file => new Promise((resolve, reject) => {
            if (!file) { resolve(null); return; }
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = () => reject(reader.error);
            reader.readAsText(file);
        });

        let csv1Content = null, csv2Content = null, jsonDataString = null;

        if (csvFileObjects && csvFileObjects.length === 2) {
            try {
                [csv1Content, csv2Content] = await Promise.all(csvFileObjects.map(readFileAsText));
            } catch (e) { throw new Error("Failed to read CSV content."); }
        }
        if (jsonFileObject) {
            try { jsonDataString = await readFileAsText(jsonFileObject); } 
            catch (e) { throw new Error("Failed to read JSON content."); }
        }
        
        return new Promise(resolve => setTimeout(() => {
            const response = { 
                csvFile1Content: csv1Content, 
                csvFile2Content: csv2Content, 
                jsonExplanationData: jsonDataString 
            };
            
            if (!csv1Content && csvFileObjects.length === 0) {
                 response.csvFile1Content = `id,other_col,output\n1,abc,0\n2,def,1\n3,ghi,1\n4,jkl,0\n5,mno,1`; 
                 response.csvFile2Content = `id,another,output\n1,pqr,1\n2,stu,1\n3,vwx,0\n4,yz,1\n5,123,1`; 
            }
            if (!jsonDataString && !jsonFileObject) {
                response.jsonExplanationData = JSON.stringify([
                    { id: "placeholder_1", anomaly_score: -0.01, explanation: "Placeholder anomaly 1." },
                    { id: "placeholder_2", anomaly_score: -0.02, explanation: "Placeholder anomaly 2." }
                ]);
            }
            resolve(response);
        }, 500));
    }
    
    function displayAnomalyPercentageChart(csv1String, csv2String) { 
        try {
            const parsedCsv1 = parseCSVStringWithPapaparse(csv1String);
            const parsedCsv2 = parseCSVStringWithPapaparse(csv2String);

            if (!parsedCsv1.meta.fields || !parsedCsv1.meta.fields.includes("output")) {
                 throw new Error(`First CSV missing 'output' column.`);
            }
            if (!parsedCsv2.meta.fields || !parsedCsv2.meta.fields.includes("output")) {
                 throw new Error(`Second CSV missing 'output' column.`);
            }
            
            const chartData = prepareAnomalyPercentageChartData(parsedCsv1.data, parsedCsv2.data);
            renderAnomalyPercentageChart(chartData);
            comparisonChartCard.classList.remove('hidden');
        } catch (e) {
            console.error("Error displaying anomaly percentage chart:", e);
            const chartContainer = document.getElementById('comparisonChartContainer');
            chartContainer.innerHTML = `<p class="text-red-400 text-center p-4">Chart Error: ${e.message}</p>`;
            comparisonChartCard.classList.remove('hidden');
        }
    }
    
    function parseCSVStringWithPapaparse(csvString) {
        if (!csvString || typeof csvString !== 'string' || csvString.trim() === '') {
            return { data: [], errors: [{ message: "Invalid CSV string" }], meta: { fields: [] } };
        }
        const result = Papa.parse(csvString.trim(), { header: true, skipEmptyLines: true, dynamicTyping: true });
        if (result.errors.length > 0) console.warn("Papaparse (CSV) errors:", result.errors.map(e => e.message).join(';'));
        if (!result.meta.fields || result.meta.fields.length === 0) console.warn("Papaparse (CSV) no headers.");
        return result;
    }
    
    function calculateAnomalyPercentage(csvData) {
        if (!csvData || csvData.length === 0) return 0;
        let anomalyCount = 0;
        csvData.forEach(row => {
            if (Number(row["output"]) === 1) { 
                anomalyCount++;
            }
        });
        return (anomalyCount / csvData.length) * 100; 
    }

    function prepareAnomalyPercentageChartData(dataCsv1, dataCsv2) {
        const percentageCsv1 = calculateAnomalyPercentage(dataCsv1);
        const percentageCsv2 = calculateAnomalyPercentage(dataCsv2);
        
        console.log("Anomaly Percentage in Zero-Shot CSV:", percentageCsv1.toFixed(2) + "%");
        console.log("Anomaly Percentage in PEFT CSV:", percentageCsv2.toFixed(2) + "%");

        return {
            labels: ["Anomaly % in Zero-Shot", "Anomaly % in PEFT"], 
            datasets: [{
                label: "Percentage of Detected Anomalies", 
                data: [parseFloat(percentageCsv1.toFixed(2)), parseFloat(percentageCsv2.toFixed(2))],
                backgroundColor: ['rgba(14, 165, 233, 0.7)', 'rgba(236, 72, 153, 0.7)'],
                borderColor: ['rgba(14, 165, 233, 1)', 'rgba(236, 72, 153, 1)'],
                borderWidth: 1.5, borderRadius: 5,
            }]
        };
    }

    function renderAnomalyPercentageChart(chartData) {
        if (comparisonChartInstance) comparisonChartInstance.destroy(); 
        const chartContainer = document.getElementById('comparisonChartContainer');
        chartContainer.innerHTML = '<canvas id="comparisonChart"></canvas>'; 
        const ctx = document.getElementById('comparisonChart').getContext('2d');
        Chart.defaults.font.family = 'Inter, sans-serif';
        comparisonChartInstance = new Chart(ctx, {
            type: 'bar', data: chartData,
            options: {
                responsive: true, maintainAspectRatio: false, indexAxis: 'y', 
                plugins: {
                    legend: { display: false },
                    title: {
                        display: true, text: "Comparison of Detected Anomaly Percentages",
                        color: '#E2E8F0', font: { size: 16, weight: '600' },
                        padding: { top: 10, bottom: 20 }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.9)', 
                        titleColor: '#E2E8F0', bodyColor: '#CBD5E1', 
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || context.label || '';
                                if (label) label += ': ';
                                if (context.parsed.x !== null) label += context.parsed.x.toFixed(2) + '%'; 
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    x: { 
                        beginAtZero: true, 
                        max: 100, 
                        grid: { color: 'rgba(51, 65, 85, 0.3)' }, 
                        ticks: { color: '#94A3B8', callback: function(value) { return value + "%" } } 
                    },
                    y: { grid: { display: false }, ticks: { color: '#94A3B8', font: { size: 13 } } }
                },
                animation: { duration: 800, easing: 'easeInOutQuart' }
            }
        });
    }

    function displayAnomalyExplanations(anomalies) {
        anomalyDetailsContainer.innerHTML = ''; 
        if (!Array.isArray(anomalies) || anomalies.length === 0) {
            anomalyDetailsContainer.innerHTML = '<p class="text-slate-400 italic">No anomalies to display or invalid JSON format.</p>';
            anomalyExplanationsCard.classList.remove('hidden');
            return;
        }
        anomalies.forEach(anomaly => {
            const itemDiv = document.createElement('div');
            itemDiv.className = 'anomaly-item';
            const idEl = document.createElement('h4');
            idEl.textContent = `Anomaly ID: ${anomaly.id || 'N/A'}`;
            itemDiv.appendChild(idEl);
            const scoreEl = document.createElement('p');
            const scoreValue = typeof anomaly.anomaly_score === 'number' ? anomaly.anomaly_score.toFixed(6) : 'N/A';
            scoreEl.innerHTML = `<strong>Score:</strong> ${scoreValue}`;
            itemDiv.appendChild(scoreEl);
            const explanationEl = document.createElement('p');
            explanationEl.innerHTML = `<strong>Explanation:</strong> ${anomaly.explanation || 'No explanation provided.'}`;
            itemDiv.appendChild(explanationEl);
            anomalyDetailsContainer.appendChild(itemDiv);
        });
        anomalyExplanationsCard.classList.remove('hidden');
    }
});
