import { useState, useEffect } from 'react'
import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
} from 'chart.js'
import 'chartjs-adapter-date-fns'
import './WealthProjectionsPage.css'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
)

function WealthProjectionsPage({ onBack, netWorthData, monthlyData }) {
  const [selectedTimeframe, setSelectedTimeframe] = useState('1y')
  const [projectionData, setProjectionData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const timeOptions = [
    { value: '3m', label: '3 Months' },
    { value: '1y', label: '1 Year' },
    { value: '2y', label: '2 Years' },
    { value: '5y', label: '5 Years' },
    { value: '10y', label: '10 Years' },
    { value: '20y', label: '20 Years' },
    { value: '50y', label: '50 Years' }
  ]

  useEffect(() => {
    if (selectedTimeframe) {
      fetchWealthProjections(selectedTimeframe)
    }
  }, [selectedTimeframe])

  const fetchWealthProjections = async (timeframe) => {
    try {
      setLoading(true)
      setError(null)
      
      // Prepare the data for the API call
      const requestData = {
        assets: netWorthData.assets,
        liabilities: netWorthData.liabilities,
        contributions: monthlyData.contributions,
        debtPayments: monthlyData.debtPayments,
        timeframe: timeframe
      }

      console.log('Fetching wealth projections with data:', requestData)

      const response = await fetch('http://localhost:8000/wealth/projections', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
      })

      if (response.ok) {
        const data = await response.json()
        console.log('Wealth projections received:', data)
        setProjectionData(data)
      } else {
        setError('Failed to fetch wealth projections')
        console.error('Wealth projections fetch error:', response.status, response.statusText)
      }
    } catch (err) {
      setError('Error connecting to server')
      console.error('Wealth projections fetch error:', err)
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount)
  }

  const prepareChartData = () => {
    if (!projectionData?.projections || !projectionData.projections[selectedTimeframe]?.time_series) {
      return {
        labels: [],
        datasets: []
      }
    }

    // Use the month-over-month time series data from the selected timeframe
    let timeSeriesData = projectionData.projections[selectedTimeframe].time_series
    
    // For longer time periods, sample the data to reduce density
    const timeframeMonths = {
      '3m': 3,
      '1y': 12,
      '2y': 24,
      '5y': 60,
      '10y': 120,
      '20y': 240,
      '50y': 600
    }
    
    const totalMonths = timeframeMonths[selectedTimeframe] || 12
    
    // Sample data points based on timeframe length
    let sampledData = timeSeriesData
    let sampleInterval = 1
    
    if (totalMonths > 120) { // 10+ years
      sampleInterval = Math.ceil(totalMonths / 60) // Show ~60 points max
      sampledData = timeSeriesData.filter((_, index) => index % sampleInterval === 0)
    } else if (totalMonths > 24) { // 2+ years
      sampleInterval = Math.ceil(totalMonths / 30) // Show ~30 points max
      sampledData = timeSeriesData.filter((_, index) => index % sampleInterval === 0)
    }
    
    // Format labels for better display
    const labels = sampledData.map(item => {
      // Convert "2024-01" format to "Jan 2024"
      const [year, month] = item.month.split('-')
      const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
      return `${monthNames[parseInt(month) - 1]} ${year}`
    })
    
    // Adjust point visibility based on data density
    const showPoints = sampledData.length <= 30
    const pointRadius = showPoints ? 3 : 0
    const pointHoverRadius = showPoints ? 5 : 0
    
    return {
      labels,
      datasets: [
        {
          label: 'Net Worth',
          data: sampledData.map(item => item.net_worth),
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          borderWidth: 3,
          fill: true,
          tension: 0.4,
          pointBackgroundColor: '#3b82f6',
          pointBorderColor: '#ffffff',
          pointBorderWidth: 2,
          pointRadius: pointRadius,
          pointHoverRadius: pointHoverRadius
        },
        {
          label: 'Assets',
          data: sampledData.map(item => item.assets_total),
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          borderWidth: 2,
          fill: false,
          tension: 0.4,
          pointBackgroundColor: '#10b981',
          pointBorderColor: '#ffffff',
          pointBorderWidth: 2,
          pointRadius: pointRadius,
          pointHoverRadius: pointHoverRadius
        },
        {
          label: 'Liabilities',
          data: sampledData.map(item => item.liabilities_total),
          borderColor: '#ef4444',
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          borderWidth: 2,
          fill: false,
          tension: 0.4,
          pointBackgroundColor: '#ef4444',
          pointBorderColor: '#ffffff',
          pointBorderWidth: 2,
          pointRadius: pointRadius,
          pointHoverRadius: pointHoverRadius
        }
      ]
    }
  }

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      title: {
        display: true,
        text: `Wealth Projections - ${timeOptions.find(opt => opt.value === selectedTimeframe)?.label}`,
        font: {
          size: 18,
          weight: 'bold'
        },
        color: '#1f2937'
      },
      legend: {
        display: true,
        position: 'top',
        labels: {
          usePointStyle: true,
          padding: 20,
          font: {
            size: 12,
            weight: 'bold'
          }
        }
      },
      tooltip: {
        mode: 'index',
        intersect: false,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#ffffff',
        bodyColor: '#ffffff',
        borderColor: '#e5e7eb',
        borderWidth: 1,
        callbacks: {
          label: function(context) {
            return `${context.dataset.label}: ${formatCurrency(context.parsed.y)}`
          }
        }
      }
    },
    scales: {
      x: {
        display: true,
        title: {
          display: true,
          text: 'Time',
          font: {
            size: 14,
            weight: 'bold'
          }
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.1)'
        }
      },
      y: {
        display: true,
        title: {
          display: true,
          text: 'Amount ($)',
          font: {
            size: 14,
            weight: 'bold'
          }
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.1)'
        },
        ticks: {
          callback: function(value) {
            return formatCurrency(value)
          }
        }
      }
    },
    interaction: {
      mode: 'nearest',
      axis: 'x',
      intersect: false
    }
  }

  const getCurrentNetWorth = () => {
    if (!projectionData?.projections || !projectionData.projections[selectedTimeframe]?.time_series || projectionData.projections[selectedTimeframe].time_series.length === 0) return 0
    return projectionData.projections[selectedTimeframe].time_series[0].net_worth
  }

  const getProjectedNetWorth = () => {
    if (!projectionData?.projections || !projectionData.projections[selectedTimeframe]?.time_series || projectionData.projections[selectedTimeframe].time_series.length === 0) return 0
    const timeSeries = projectionData.projections[selectedTimeframe].time_series
    return timeSeries[timeSeries.length - 1].net_worth
  }

  const getTotalGrowth = () => {
    return getProjectedNetWorth() - getCurrentNetWorth()
  }

  const getGrowthPercentage = () => {
    const current = getCurrentNetWorth()
    if (current === 0) return 0
    return ((getTotalGrowth() / current) * 100)
  }

  return (
    <div className="wealth-projections-page">
      <div className="projections-header">
        <button className="back-button" onClick={onBack}>
          ← Back to Monthly Payments
        </button>
        <h1 className="projections-title">Wealth Projections</h1>
        <p className="projections-subtitle">See how your wealth will grow over time</p>
      </div>

      <div className="projections-content">
        {/* Time Selection */}
        <div className="time-selection">
          <h2 className="section-title">Select Timeframe</h2>
          <div className="time-buttons">
            {timeOptions.map((option) => (
              <button
                key={option.value}
                className={`time-button ${selectedTimeframe === option.value ? 'active' : ''}`}
                onClick={() => setSelectedTimeframe(option.value)}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>

        {/* Summary Cards */}
        {projectionData && (
          <div className="summary-cards">
            <div className="summary-card">
              <h3 className="summary-title">Current Net Worth</h3>
              <p className="summary-value">{formatCurrency(getCurrentNetWorth())}</p>
            </div>
            <div className="summary-card">
              <h3 className="summary-title">Projected Net Worth</h3>
              <p className="summary-value">{formatCurrency(getProjectedNetWorth())}</p>
            </div>
            <div className="summary-card">
              <h3 className="summary-title">Total Growth</h3>
              <p className={`summary-value ${getTotalGrowth() >= 0 ? 'positive' : 'negative'}`}>
                {getTotalGrowth() >= 0 ? '+' : ''}{formatCurrency(getTotalGrowth())}
              </p>
            </div>
            <div className="summary-card">
              <h3 className="summary-title">Growth %</h3>
              <p className={`summary-value ${getGrowthPercentage() >= 0 ? 'positive' : 'negative'}`}>
                {getGrowthPercentage() >= 0 ? '+' : ''}{getGrowthPercentage().toFixed(1)}%
              </p>
            </div>
          </div>
        )}

        {/* Chart Section */}
        <div className="chart-section">
          <div className="chart-container">
            {loading ? (
              <div className="loading-container">
                <div className="loading-spinner"></div>
                <p className="loading-text">Calculating projections...</p>
              </div>
            ) : error ? (
              <div className="error-container">
                <h3 className="error-title">Error Loading Projections</h3>
                <p className="error-message">{error}</p>
                <button className="retry-button" onClick={() => fetchWealthProjections(selectedTimeframe)}>
                  Try Again
                </button>
              </div>
            ) : projectionData ? (
              <Line 
                key={`wealth-chart-${selectedTimeframe}`}
                data={prepareChartData()} 
                options={chartOptions} 
              />
            ) : (
              <div className="no-data">
                <h3>No Projection Data</h3>
                <p>Select a timeframe to see your wealth projections</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default WealthProjectionsPage
