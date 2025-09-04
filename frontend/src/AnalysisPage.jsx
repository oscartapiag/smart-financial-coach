import { useState, useEffect } from 'react'
import { Bar, Line, Pie } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
  ArcElement,
} from 'chart.js'
import './AnalysisPage.css'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
  ArcElement
)

function AnalysisPage({ fileId, onBack }) {
  const [loading, setLoading] = useState(true)
  const [loadingProgress, setLoadingProgress] = useState(0)
  const [analysisData, setAnalysisData] = useState(null)
  const [timeSeriesData, setTimeSeriesData] = useState(null)
  const [categoryData, setCategoryData] = useState(null)
  const [selectedPeriod, setSelectedPeriod] = useState('30d')
  const [chartType, setChartType] = useState('bar') // 'bar' or 'pie'
  const [excludeRent, setExcludeRent] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    // Simulate 5-second loading with progress bar
    const loadingInterval = setInterval(() => {
      setLoadingProgress(prev => {
        if (prev >= 100) {
          clearInterval(loadingInterval)
          return 100
        }
        return prev + 2 // Increment by 2% every 100ms for 5 seconds
      })
    }, 40)

    // Fetch analysis data and default time series data after loading completes
    const fetchInitialData = async () => {
      try {
        // Fetch analysis data first
        const analysisResponse = await fetch(`http://localhost:8000/files/${fileId}/analysis`)
        if (analysisResponse.ok) {
          const analysisData = await analysisResponse.json()
          setAnalysisData(analysisData)
          
          // Then fetch default 30-day time series and category data
          const timeSeriesUrl = `http://localhost:8000/files/${fileId}/time-series?period=30d`
          const categoryUrl = `http://localhost:8000/files/${fileId}/categories-by-time?period=30d`
          
          console.log('Fetching default 30-day data from:', timeSeriesUrl, categoryUrl)
          
          const [timeSeriesResponse, categoryResponse] = await Promise.all([
            fetch(timeSeriesUrl),
            fetch(categoryUrl)
          ])
          
          if (timeSeriesResponse.ok) {
            const timeSeriesData = await timeSeriesResponse.json()
            console.log('Default 30-day time series data received:', timeSeriesData)
            setTimeSeriesData(timeSeriesData)
          } else {
            console.error('Failed to fetch default time series data:', timeSeriesResponse.status)
          }
          
          if (categoryResponse.ok) {
            const categoryData = await categoryResponse.json()
            console.log('Default 30-day category data received:', categoryData)
            setCategoryData(categoryData)
          } else {
            console.error('Failed to fetch default category data:', categoryResponse.status)
          }
        } else {
          setError('Failed to fetch analysis data')
        }
      } catch (err) {
        setError('Error connecting to server')
        console.error('Initial data fetch error:', err)
      } finally {
        setLoading(false)
      }
    }

    // Start fetching data after 5 seconds
    const fetchTimer = setTimeout(fetchInitialData, 3000)

    return () => {
      clearInterval(loadingInterval)
      clearTimeout(fetchTimer)
    }
  }, [fileId])

  const fetchTimeSeriesData = async (period) => {
    try {
      const url = `http://localhost:8000/files/${fileId}/time-series?period=${period}`
      console.log(`Fetching time series data for period: ${period}`)
      console.log(`API URL: ${url}`)
      
      const response = await fetch(url)
      if (response.ok) {
        const data = await response.json()
        console.log(`Time series data received for ${period}:`, data)
        console.log(`Income data points: ${data.income?.length || 0}`)
        console.log(`Spending data points: ${data.spending?.length || 0}`)
        console.log(`Category breakdown:`, data.category_breakdown)
        console.log(`Summary:`, data.summary)
        setTimeSeriesData(data)
      } else {
        console.error(`Failed to fetch time series data for ${period}:`, response.status, response.statusText)
        setError('Failed to fetch time series data')
      }
    } catch (err) {
      setError('Error fetching time series data')
      console.error('Time series fetch error:', err)
    }
  }

  const fetchCategoryData = async (period) => {
    try {
      const url = `http://localhost:8000/files/${fileId}/categories-by-time?period=${period}`
      console.log(`Fetching category data for period: ${period}`)
      console.log(`Category API URL: ${url}`)
      
      const response = await fetch(url)
      if (response.ok) {
        const data = await response.json()
        console.log(`Category data received for ${period}:`, data)
        setCategoryData(data)
      } else {
        console.error(`Failed to fetch category data for ${period}:`, response.status, response.statusText)
      }
    } catch (err) {
      console.error('Category data fetch error:', err)
    }
  }

  const handlePeriodSelect = (period) => {
    console.log(`Period changed from ${selectedPeriod} to ${period}`)
    setSelectedPeriod(period)
    fetchTimeSeriesData(period)
    fetchCategoryData(period)
  }

  const prepareChartData = () => {
    console.log('=== PREPARING CHART DATA ===')
    console.log('Selected period:', selectedPeriod)
    console.log('Category data received:', categoryData)
    console.log('Analysis data received:', analysisData)
    console.log('Category data top_categories:', categoryData?.top_categories)
    console.log('Analysis data top_spending_categories:', analysisData?.category_analysis?.top_spending_categories)
    
    // Use category data from the categories-by-time endpoint if available
    if (categoryData?.top_categories) {
      console.log('Using category data:', categoryData.top_categories)
      let categories = Object.keys(categoryData.top_categories)
      let values = Object.values(categoryData.top_categories).map(cat => cat.total_amount)
      
      // Filter out rent if excludeRent is true
      if (excludeRent) {
        const rentIndex = categories.findIndex(cat => cat.toLowerCase() === 'rent')
        if (rentIndex !== -1) {
          categories = categories.filter((_, index) => index !== rentIndex)
          values = values.filter((_, index) => index !== rentIndex)
        }
      }
      
      console.log(`Chart data for ${selectedPeriod} (excludeRent: ${excludeRent}):`, { categories, values })
      return {
        labels: categories,
        datasets: [
          {
            label: `Spending Amount (${selectedPeriod})`,
            data: values,
            backgroundColor: [
              'rgba(102, 126, 234, 0.8)',
              'rgba(118, 75, 162, 0.8)',
              'rgba(240, 147, 251, 0.8)',
              'rgba(245, 87, 108, 0.8)',
              'rgba(79, 172, 254, 0.8)',
              'rgba(34, 197, 94, 0.8)',
              'rgba(251, 191, 36, 0.8)',
              'rgba(239, 68, 68, 0.8)',
              'rgba(139, 92, 246, 0.8)',
              'rgba(6, 182, 212, 0.8)',
            ],
            borderColor: [
              'rgba(102, 126, 234, 1)',
              'rgba(118, 75, 162, 1)',
              'rgba(240, 147, 251, 1)',
              'rgba(245, 87, 108, 1)',
              'rgba(79, 172, 254, 1)',
              'rgba(34, 197, 94, 1)',
              'rgba(251, 191, 36, 1)',
              'rgba(239, 68, 68, 1)',
              'rgba(139, 92, 246, 1)',
              'rgba(6, 182, 212, 1)',
            ],
            borderWidth: 2,
            borderRadius: 8,
            borderSkipped: false,
            barThickness: 'flex',
            maxBarThickness: 50,
          },
        ],
      }
    }
    
    // Fallback to original analysis data
    if (!analysisData?.category_analysis?.top_spending_categories) {
      console.log('No category data available')
      return null
    }

    console.log('Using analysis data category breakdown:', analysisData.category_analysis.top_spending_categories)
    let categories = Object.keys(analysisData.category_analysis.top_spending_categories)
    let values = Object.values(analysisData.category_analysis.top_spending_categories)

    // Filter out rent if excludeRent is true
    if (excludeRent) {
      const rentIndex = categories.findIndex(cat => cat.toLowerCase() === 'rent')
      if (rentIndex !== -1) {
        categories = categories.filter((_, index) => index !== rentIndex)
        values = values.filter((_, index) => index !== rentIndex)
      }
    }

    return {
      labels: categories,
      datasets: [
        {
          label: 'Spending Amount',
          data: values,
          backgroundColor: [
            'rgba(102, 126, 234, 0.8)',
            'rgba(118, 75, 162, 0.8)',
            'rgba(240, 147, 251, 0.8)',
            'rgba(245, 87, 108, 0.8)',
            'rgba(79, 172, 254, 0.8)',
            'rgba(34, 197, 94, 0.8)',
            'rgba(251, 191, 36, 0.8)',
            'rgba(239, 68, 68, 0.8)',
            'rgba(139, 92, 246, 0.8)',
            'rgba(6, 182, 212, 0.8)',
          ],
          borderColor: [
            'rgba(102, 126, 234, 1)',
            'rgba(118, 75, 162, 1)',
            'rgba(240, 147, 251, 1)',
            'rgba(245, 87, 108, 1)',
            'rgba(79, 172, 254, 1)',
            'rgba(34, 197, 94, 1)',
            'rgba(251, 191, 36, 1)',
            'rgba(239, 68, 68, 1)',
            'rgba(139, 92, 246, 1)',
            'rgba(6, 182, 212, 1)',
          ],
          borderWidth: 2,
          borderRadius: 8,
          borderSkipped: false,
          barThickness: 'flex',
          maxBarThickness: 50,
        },
      ],
    }
  }

  const prepareCombinedTimeData = () => {
    if (!timeSeriesData?.income || !timeSeriesData?.spending) {
      return null
    }

    // The API returns arrays of objects with date, cumulative_amount, and daily_amount
    const incomeData = timeSeriesData.income.map(item => item.cumulative_amount)
    const spendingData = timeSeriesData.spending.map(item => item.cumulative_amount)
    const labels = timeSeriesData.income.map(item => item.date)

    return {
      labels: labels,
      datasets: [
        {
          label: 'Income (Cumulative)',
          data: incomeData,
          borderColor: 'rgba(34, 197, 94, 1)',
          backgroundColor: 'rgba(34, 197, 94, 0.1)',
          borderWidth: 3,
          fill: false,
          tension: 0.4,
          pointBackgroundColor: 'rgba(34, 197, 94, 1)',
          pointBorderColor: 'rgba(34, 197, 94, 1)',
          pointRadius: 4,
          pointHoverRadius: 6,
        },
        {
          label: 'Spending (Cumulative)',
          data: spendingData,
          borderColor: 'rgba(239, 68, 68, 1)',
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          borderWidth: 3,
          fill: false,
          tension: 0.4,
          pointBackgroundColor: 'rgba(239, 68, 68, 1)',
          pointBorderColor: 'rgba(239, 68, 68, 1)',
          pointRadius: 4,
          pointHoverRadius: 6,
        },
      ],
    }
  }

  const lineChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: '#2d3748',
          font: {
            size: 14,
            weight: 'bold'
          }
        }
      },
      tooltip: {
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        titleColor: '#2d3748',
        bodyColor: '#4a5568',
        borderColor: '#e2e8f0',
        borderWidth: 1,
        cornerRadius: 8,
        displayColors: true,
        callbacks: {
          label: function(context) {
            const datasetLabel = context.dataset.label
            const value = context.parsed.y
            const date = context.label
            
            // Find the corresponding data point to get daily amount
            const dataIndex = context.dataIndex
            let dailyAmount = 0
            
            if (datasetLabel.includes('Income')) {
              dailyAmount = timeSeriesData?.income?.[dataIndex]?.daily_amount || 0
            } else if (datasetLabel.includes('Spending')) {
              dailyAmount = timeSeriesData?.spending?.[dataIndex]?.daily_amount || 0
            }
            
            return [
              `${datasetLabel}: $${value.toFixed(2)}`,
              `Daily: $${dailyAmount.toFixed(2)}`
            ]
          }
        }
      }
    },
    scales: {
      x: {
        ticks: {
          color: '#4a5568',
          font: {
            size: 12
          },
          maxRotation: 45,
          minRotation: 0
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.1)',
          drawBorder: false
        }
      },
      y: {
        beginAtZero: true,
        ticks: {
          color: '#4a5568',
          font: {
            size: 12
          },
          callback: function(value) {
            return '$' + value.toFixed(0)
          }
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.1)',
          drawBorder: false
        }
      }
    }
  }

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: 'y', // Makes the bar chart horizontal
    plugins: {
      legend: {
        display: false
      },
      title: {
        display: false
      },
      tooltip: {
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        titleColor: '#2d3748',
        bodyColor: '#4a5568',
        borderColor: '#e2e8f0',
        borderWidth: 1,
        cornerRadius: 8,
        displayColors: true,
        callbacks: {
          label: function(context) {
            return `$${context.parsed.x.toFixed(2)}`
          }
        }
      }
    },
    layout: {
      padding: {
        top: 10,
        bottom: 10,
        left: 10,
        right: 10
      }
    },
    scales: {
      x: {
        beginAtZero: true,
        ticks: {
          color: '#4a5568',
          font: {
            size: 12
          },
          callback: function(value) {
            return '$' + value.toFixed(0)
          }
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.1)',
          drawBorder: false
        },
        border: {
          display: false
        }
      },
      y: {
        ticks: {
          color: '#4a5568',
          font: {
            size: 12
          }
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.1)',
          drawBorder: false,
          display: false
        },
        border: {
          display: false
        }
      }
    }
  }

  const pieChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    layout: {
      padding: {
        top: 10,
        bottom: 10,
        left: 10,
        right: 10
      }
    },
    plugins: {
      legend: {
        position: 'right',
        labels: {
          usePointStyle: true,
          padding: 15,
          font: {
            size: 11
          },
          color: '#2d3748'
        }
      },
      title: {
        display: false
      },
      tooltip: {
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        titleColor: '#2d3748',
        bodyColor: '#4a5568',
        borderColor: '#e2e8f0',
        borderWidth: 1,
        cornerRadius: 8,
        displayColors: true,
        callbacks: {
          label: function(context) {
            const total = context.dataset.data.reduce((a, b) => a + b, 0)
            const percentage = ((context.parsed / total) * 100).toFixed(1)
            return `${context.label}: $${context.parsed.toFixed(2)} (${percentage}%)`
          }
        }
      }
    }
  }

  if (loading) {
    return (
      <div className="analysis-page">
        <div className="loading-container">
          <div className="loading-content">
            <h2 className="loading-title">Analyzing Your Financial Data</h2>
            <p className="loading-subtitle">Please wait while we process your transactions...</p>
            
            <div className="loading-bar-container">
              <div className="loading-bar">
                <div 
                  className="loading-bar-fill" 
                  style={{ width: `${loadingProgress}%` }}
                ></div>
              </div>
              <div className="loading-percentage">{loadingProgress}%</div>
            </div>
            
            <div className="loading-steps">
              <div className={`loading-step ${loadingProgress > 20 ? 'completed' : ''}`}>
                <span className="step-icon">📊</span>
                <span className="step-text">Processing transactions</span>
              </div>
              <div className={`loading-step ${loadingProgress > 50 ? 'completed' : ''}`}>
                <span className="step-icon">🔍</span>
                <span className="step-text">Categorizing expenses</span>
              </div>
              <div className={`loading-step ${loadingProgress > 80 ? 'completed' : ''}`}>
                <span className="step-icon">📈</span>
                <span className="step-text">Generating insights</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="analysis-page">
        <div className="error-container">
          <div className="error-content">
            <div className="error-icon">❌</div>
            <h2 className="error-title">Analysis Failed</h2>
            <p className="error-message">{error}</p>
            <button className="back-button" onClick={onBack}>
              Back to Upload
            </button>
          </div>
        </div>
      </div>
    )
  }

  const chartData = prepareChartData()

  return (
    <div className="analysis-page">
      <div className="analysis-container">
        <div className="analysis-header">
          <button className="back-button" onClick={onBack}>
            ← Back to Upload
          </button>
          <h1 className="analysis-title">Financial Analysis</h1>
        </div>

        {analysisData && (
          <div className="analysis-content">
            {/* Time Period Selection */}
            <div className="time-period-section">
              <h3 className="section-title">Select Time Period To View Spending/Income</h3>
              <div className="period-buttons">
                <button 
                  className={`period-button ${selectedPeriod === '14d' ? 'active' : ''}`}
                  onClick={() => handlePeriodSelect('14d')}
                >
                  14 Days
                </button>
                <button 
                  className={`period-button ${selectedPeriod === '30d' ? 'active' : ''}`}
                  onClick={() => handlePeriodSelect('30d')}
                >
                  30 Days
                </button>
                <button 
                  className={`period-button ${selectedPeriod === '90d' ? 'active' : ''}`}
                  onClick={() => handlePeriodSelect('90d')}
                >
                  90 Days
                </button>
                <button 
                  className={`period-button ${selectedPeriod === '1y' ? 'active' : ''}`}
                  onClick={() => handlePeriodSelect('1y')}
                >
                  1 Year
                </button>
              </div>
            </div>

            {/* Time-based Chart */}
            {selectedPeriod && (
              <div className="time-charts-section">
                <div className="combined-chart-container">
                  <h3 className="chart-title">
                    Income vs. Spending Over Time ({selectedPeriod === '14d' ? '14 Days' : 
                                                   selectedPeriod === '30d' ? '30 Days' : 
                                                   selectedPeriod === '90d' ? '90 Days' : '1 Year'})
                  </h3>
                  <div className="chart-wrapper">
                    {prepareCombinedTimeData() && (
                      <Line 
                        key={`line-chart-${selectedPeriod}`}
                        data={prepareCombinedTimeData()} 
                        options={lineChartOptions} 
                      />
                    )}
                  </div>
                  
                  {/* Time Series Summary */}
                  {timeSeriesData?.summary && (
                    <div className="time-series-summary">
                      <div className="summary-item">
                        <span className="summary-label">Total Income:</span>
                        <span className="summary-value income">${timeSeriesData.summary.total_income.toFixed(2)}</span>
                      </div>
                      <div className="summary-item">
                        <span className="summary-label">Total Spending:</span>
                        <span className="summary-value spending">${timeSeriesData.summary.total_spending.toFixed(2)}</span>
                      </div>
                      <div className="summary-item">
                        <span className="summary-label">Net Amount:</span>
                        <span className={`summary-value ${timeSeriesData.summary.net_amount >= 0 ? 'positive' : 'negative'}`}>
                          ${timeSeriesData.summary.net_amount.toFixed(2)}
                        </span>
                      </div>
                    </div>
                  )}

                  {/* Detailed Time Series Information */}
                  {timeSeriesData && (
                    <div className="detailed-summary">
                      <h4 className="detailed-title">Period Details</h4>
                      <div className="detailed-grid">
                        <div className="detailed-item">
                          <span className="detailed-label">Period:</span>
                          <span className="detailed-value">{selectedPeriod === '14d' ? '14 Days' : 
                                                           selectedPeriod === '30d' ? '30 Days' : 
                                                           selectedPeriod === '90d' ? '90 Days' : '1 Year'}</span>
                        </div>
                        <div className="detailed-item">
                          <span className="detailed-label">Date Range:</span>
                          <span className="detailed-value">
                            {timeSeriesData.date_range?.start_date} to {timeSeriesData.date_range?.end_date}
                          </span>
                        </div>
                        <div className="detailed-item">
                          <span className="detailed-label">Days Covered:</span>
                          <span className="detailed-value">{timeSeriesData.date_range?.days_covered} days</span>
                        </div>
                        <div className="detailed-item">
                          <span className="detailed-label">Data Points:</span>
                          <span className="detailed-value">{timeSeriesData.summary?.data_points} points</span>
                        </div>
                        <div className="detailed-item">
                          <span className="detailed-label">Income Transactions:</span>
                          <span className="detailed-value">{timeSeriesData.summary?.income_transactions}</span>
                        </div>
                        <div className="detailed-item">
                          <span className="detailed-label">Spending Transactions:</span>
                          <span className="detailed-value">{timeSeriesData.summary?.spending_transactions}</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Chart Type Selection */}
            <div className="chart-type-section">
              <h3 className="section-title">Chart Type</h3>
              <div className="chart-type-buttons">
                <button 
                  className={`chart-type-button ${chartType === 'bar' ? 'active' : ''}`}
                  onClick={() => setChartType('bar')}
                >
                  📊 Bar Chart
                </button>
                <button 
                  className={`chart-type-button ${chartType === 'pie' ? 'active' : ''}`}
                  onClick={() => setChartType('pie')}
                >
                  🥧 Pie Chart
                </button>
              </div>
              
              <div className="rent-exclusion-toggle">
                <label className="toggle-label">
                  <input 
                    type="checkbox" 
                    checked={excludeRent}
                    onChange={(e) => setExcludeRent(e.target.checked)}
                    className="toggle-checkbox"
                  />
                  <span className="toggle-text">Exclude Rent (Zoom in on other categories)</span>
                </label>
              </div>
            </div>

            {/* Chart Section */}
            {chartData && selectedPeriod && (
              <div className="chart-section">
                <div className="chart-container">
                  <h3 className="chart-title">
                    Top Spending Categories ({selectedPeriod === '14d' ? '14 Days' : 
                                           selectedPeriod === '30d' ? '30 Days' : 
                                           selectedPeriod === '90d' ? '90 Days' : '1 Year'})
                  </h3>
                  {chartType === 'bar' ? (
                    <Bar 
                      key={`bar-chart-${selectedPeriod}`} 
                      data={chartData} 
                      options={chartOptions} 
                    />
                  ) : (
                    <div className="pie-chart-wrapper">
                      <Pie 
                        key={`pie-chart-${selectedPeriod}`} 
                        data={chartData} 
                        options={pieChartOptions} 
                      />
                    </div>
                  )}
                </div>
              </div>
            )}


          </div>
        )}
      </div>
    </div>
  )
}

export default AnalysisPage






