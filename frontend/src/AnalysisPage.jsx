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
import NetWorthCalculator from './NetWorthCalculator'
import SavingsPlanner from './SavingsPlanner'

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

function AnalysisPage({ fileId, onBack, onNavigateToSubscriptions }) {
  const [loading, setLoading] = useState(true)
  const [loadingProgress, setLoadingProgress] = useState(0)
  const [analysisData, setAnalysisData] = useState(null)
  const [timeSeriesData, setTimeSeriesData] = useState(null)
  const [categoryData, setCategoryData] = useState(null)
  const [selectedPeriod, setSelectedPeriod] = useState('30d')
  const [chartType, setChartType] = useState('bar') // 'bar' or 'pie'
  const [excludeRent, setExcludeRent] = useState(false)
  const [error, setError] = useState(null)
  const [aiInsights, setAiInsights] = useState(null)
  const [aiInsightsLoading, setAiInsightsLoading] = useState(false)
  const [aiInsightsError, setAiInsightsError] = useState(false)
  const [aiInsightsRetryCount, setAiInsightsRetryCount] = useState(0)
  const [aiInsightsFetched, setAiInsightsFetched] = useState(false)
  const [showNetWorthCalculator, setShowNetWorthCalculator] = useState(false)
  const [showSavingsPlanner, setShowSavingsPlanner] = useState(false)

  // Debug AI insights state changes
  useEffect(() => {
    console.log('AI insights state changed:', { 
      aiInsights: !!aiInsights, 
      aiInsightsLoading, 
      aiInsightsError, 
      aiInsightsFetched 
    })
  }, [aiInsights, aiInsightsLoading, aiInsightsError, aiInsightsFetched])

  useEffect(() => {
    // Check if we already have data - if so, skip loading animation
    if (analysisData && timeSeriesData && categoryData) {
      setLoading(false)
      return
    }

    // Simulate 1-second loading with progress bar
    const loadingInterval = setInterval(() => {
      setLoadingProgress(prev => {
        if (prev >= 100) {
          clearInterval(loadingInterval)
          return 100
        }
        return prev + 10 // Increment by 10% every 100ms for 1 second
      })
    }, 500)

    // Fetch analysis data and default time series data after loading completes
    const fetchInitialData = async () => {
      try {
        // Fetch analysis data first
        const analysisResponse = await fetch(`http://localhost:8000/files/${fileId}/analysis`)
        if (analysisResponse.ok) {
          const analysisData = await analysisResponse.json()
          setAnalysisData(analysisData)
          
          // Then fetch default 30-day time series and category data (AI insights loaded separately)
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

    // Start fetching data after 1 second
    const fetchTimer = setTimeout(fetchInitialData, 1000)

    return () => {
      clearInterval(loadingInterval)
      clearTimeout(fetchTimer)
    }
  }, [fileId, analysisData, timeSeriesData, categoryData])

  // Separate useEffect to fetch AI insights after page loads (only once, always 30 days)
  useEffect(() => {
    console.log('AI insights useEffect triggered:', { 
      analysisData: !!analysisData, 
      timeSeriesData: !!timeSeriesData, 
      categoryData: !!categoryData, 
      loading, 
      aiInsightsFetched 
    })
    
    if (analysisData && timeSeriesData && categoryData && !loading && !aiInsightsFetched) {
      // Page has loaded, wait a bit then fetch AI insights in background (30 days only)
      console.log('Page loaded, will fetch AI insights for 30 days in background after delay...')
      
      // Add a delay to ensure page is fully rendered
      const delayTimer = setTimeout(() => {
        try {
          console.log('Starting AI insights fetch for 30 days after delay...')
          setAiInsightsFetched(true) // Mark as fetched to prevent re-triggering
          fetchAiInsights()
        } catch (error) {
          console.error('Error in fetchAiInsights:', error)
          setAiInsightsError(true)
        }
      }, 2000) // 2 second delay
      
      return () => clearTimeout(delayTimer)
    }
  }, [analysisData, timeSeriesData, categoryData, loading, aiInsightsFetched])

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

  const fetchAiInsights = async (retryCount = 0) => {
    console.log('=== FETCH AI INSIGHTS CALLED ===')
    console.log('Parameters:', { retryCount, aiInsightsLoading, fileId })
    
    // Prevent multiple simultaneous calls
    if (aiInsightsLoading) {
      console.log('AI insights already loading, skipping duplicate call')
      return
    }
    
    try {
      console.log('Setting AI insights loading to true...')
      setAiInsightsLoading(true)
      setAiInsightsError(false)
      const url = `http://localhost:8000/files/${fileId}/insights?period=30d`
      console.log(`Fetching AI insights for 30 days (attempt ${retryCount + 1})`)
      console.log(`URL: ${url}`)
      
      // Add timeout to prevent hanging
      const controller = new AbortController()
      const timeoutId = setTimeout(() => {
        console.log('AI insights request timeout, aborting...')
        controller.abort()
      }, 60000) // 60 second timeout
      
      console.log('Making fetch request...')
      const response = await fetch(url, {
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
        }
      })
      
      clearTimeout(timeoutId)
      console.log('Response received:', { status: response.status, ok: response.ok })
      
      if (response.ok) {
        const data = await response.json()
        console.log(`AI insights received for 30 days:`, data)
        
        // Validate the response structure
        if (data && data.insights && data.insights.cards && Array.isArray(data.insights.cards)) {
          console.log('AI insights cards received:', data.insights.cards)
          console.log('Setting AI insights state...')
          setAiInsights(data.insights.cards)
          setAiInsightsRetryCount(0) // Reset retry count on success
          console.log('AI insights state set successfully!')
        } else {
          console.error('Invalid AI insights response structure:', data)
          setAiInsightsError(true)
        }
      } else {
        console.error(`Failed to fetch AI insights for 30 days:`, response.status, response.statusText)
        setAiInsightsError(true)
      }
    } catch (err) {
      console.error('Error in fetchAiInsights:', err)
      if (err.name === 'AbortError') {
        console.error('AI insights request timed out after 60 seconds')
      } else {
        console.error('AI insights fetch error:', err)
      }
      
      // Retry logic - only retry once
      if (retryCount < 1) {
        console.log(`Retrying AI insights fetch in 5 seconds... (attempt ${retryCount + 2})`)
        setTimeout(() => {
          fetchAiInsights(retryCount + 1)
        }, 5000)
        return
      }
      
      setAiInsightsError(true)
    } finally {
      console.log('Setting AI insights loading to false...')
      setAiInsightsLoading(false)
      console.log('=== FETCH AI INSIGHTS COMPLETED ===')
    }
  }

  const handlePeriodSelect = (period) => {
    console.log(`Period changed from ${selectedPeriod} to ${period}`)
    setSelectedPeriod(period)
    fetchTimeSeriesData(period)
    fetchCategoryData(period)
    // AI insights remain static for 30 days only
  }

  const handleNavigateToNetWorthCalculator = () => {
    setShowNetWorthCalculator(true)
  }

  const handleBackFromNetWorthCalculator = () => {
    setShowNetWorthCalculator(false)
  }

  const handleNavigateToSavingsPlanner = () => {
    setShowSavingsPlanner(true)
  }

  const handleBackFromSavingsPlanner = () => {
    setShowSavingsPlanner(false)
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

  // AI Insights calculation functions
  const getLargestTransaction = () => {
    try {
      if (!timeSeriesData?.spending) return null
      let largest = { amount: 0, date: '', description: 'Largest spending day' }
      
      timeSeriesData.spending.forEach(day => {
        if (day.daily_amount && Math.abs(day.daily_amount) > largest.amount) {
          largest = {
            amount: Math.abs(day.daily_amount),
            date: day.date,
            description: 'Largest spending day'
          }
        }
      })
      
      return largest.amount > 0 ? largest : null
    } catch (error) {
      console.error('Error in getLargestTransaction:', error)
      return null
    }
  }

  const getBarsSpending = () => {
    try {
      if (!categoryData?.top_categories) return 0
      return categoryData.top_categories['Bars']?.total_amount || 0
    } catch (error) {
      console.error('Error in getBarsSpending:', error)
      return 0
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
        top: 5,
        bottom: 5,
        left: 5,
        right: 5
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

  // Safety check to prevent rendering if critical data is missing
  if (!analysisData || !timeSeriesData || !categoryData) {
    console.error('Missing critical data:', { analysisData: !!analysisData, timeSeriesData: !!timeSeriesData, categoryData: !!categoryData })
    return (
      <div className="analysis-page">
        <div className="error-container">
          <div className="error-content">
            <div className="error-icon">⚠️</div>
            <h2 className="error-title">Data Loading Issue</h2>
            <p className="error-message">Some data is still loading. Please wait or refresh the page.</p>
            <button className="back-button" onClick={() => window.location.reload()}>
              Refresh Page
            </button>
          </div>
        </div>
      </div>
    )
  }

  let chartData
  try {
    chartData = prepareChartData()
  } catch (error) {
    console.error('Error preparing chart data:', error)
    return (
      <div className="analysis-page">
        <div className="error-container">
          <div className="error-content">
            <div className="error-icon">❌</div>
            <h2 className="error-title">Chart Error</h2>
            <p className="error-message">There was an error preparing the chart data. Please refresh the page.</p>
            <button className="back-button" onClick={() => window.location.reload()}>
              Refresh Page
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (showNetWorthCalculator) {
    return <NetWorthCalculator onBack={handleBackFromNetWorthCalculator} fileId={fileId} />
  }

  if (showSavingsPlanner) {
    return <SavingsPlanner onBack={handleBackFromSavingsPlanner} fileId={fileId} />
  }

  return (
    <div className="analysis-page">
      <div className="analysis-container">
        <div className="analysis-header">
          <button className="back-button" onClick={onBack}>
            ← Back to Upload
          </button>
          <h1 className="analysis-title">Financial Analysis Dashboard</h1>
        </div>

        {analysisData && (
          <div className="analysis-content">
            <div className="three-column-layout">
              {/* Left Column - AI Insights */}
              <div className="left-column">
                <div className="ai-insights-section">
                  <h3 className="section-title">AI Insights of the past 30 days</h3>
                  <div className="insights-content">
                    {aiInsightsLoading ? (
                      <div className="insight-card loading">
                        <h4 className="insight-title">🤖 AI Insights Loading...</h4>
                        <p className="insight-text">
                          Our AI is analyzing your financial data to provide personalized insights. 
                          This may take a few moments...
                        </p>
                        <div className="loading-spinner-small"></div>
                      </div>
                    ) : aiInsights && !aiInsightsError ? (
                      // Show AI-generated insights
                      aiInsights.map((insight, index) => (
                        <div key={index} className="insight-card">
                          <h4 className="insight-title">🤖 {insight.title}</h4>
                          <p className="insight-text">{insight.summary}</p>
                          {insight.cta && (
                            <div className="insight-cta">
                              <strong>{insight.cta.label}:</strong> {insight.cta.action}
                            </div>
                          )}
                        </div>
                      ))
                    ) : (
                      // Fallback to default insights
                      <>
                        {!aiInsightsError && (
                          <div className="insight-card">
                            <h4 className="insight-title">🤖 AI Insights Coming Soon</h4>
                            <p className="insight-text">
                              Our AI is analyzing your data in the background to provide personalized insights. 
                              Here are some quick insights while you wait...
                            </p>
                          </div>
                        )}
                        
                        {getLargestTransaction() && (
                          <div className="insight-card">
                            <h4 className="insight-title">💰 Largest Transaction</h4>
                            <p className="insight-text">
                              Your largest spending day was <strong>${getLargestTransaction().amount.toFixed(2)}</strong> on {getLargestTransaction().date}. 
                              Consider reviewing such high-expense days for potential savings opportunities.
                            </p>
                          </div>
                        )}
                        
                        {getBarsSpending() > 0 && (
                          <div className="insight-card">
                            <h4 className="insight-title">🍺 Bars Spending</h4>
                            <p className="insight-text">
                              You've spent <strong>${getBarsSpending().toFixed(2)}</strong> on bars this month. 
                              Remember: moderation in alcohol consumption benefits both your wallet and your health. 
                              Consider setting a monthly entertainment budget to maintain balance.
                            </p>
                          </div>
                        )}
                      </>
                    )}
                  </div>
                </div>
              </div>

              {/* Center Column - Main Data */}
              <div className="center-column">
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
                  
                </div>
              </div>
            )}

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

              {/* Right Column - Tools */}
              <div className="right-column">
                <div className="tools-section">
                  <h3 className="section-title">Financial Tools</h3>
                  <div className="tools-content">
                    <button 
                      className="tool-button"
                      onClick={onNavigateToSubscriptions}
                    >
                      <div className="tool-icon">📱</div>
                      <div className="tool-info">
                        <h4 className="tool-title">Subscriptions</h4>
                        <p className="tool-description">View and manage your current subscriptions.</p>
                      </div>
                    </button>
                    
                    <button 
                      className="tool-button"
                      onClick={handleNavigateToNetWorthCalculator}
                    >
                      <div className="tool-icon">📈</div>
                      <div className="tool-info">
                        <h4 className="tool-title">Net Worth Calculator</h4>
                        <p className="tool-description">Calculate your net worth and see how it will change over time and when your debts will be paid off!</p>
                      </div>
                    </button>
                    
                    <button 
                      className="tool-button"
                      onClick={handleNavigateToSavingsPlanner}
                    >
                      <div className="tool-icon">💰</div>
                      <div className="tool-info">
                        <h4 className="tool-title">Savings Planner</h4>
                        <p className="tool-description">Set a savings goal and get personalized advice on how to achieve it!</p>
                      </div>
                    </button>
                    
                    <button 
                      className="tool-button"
                      onClick={() => window.open('https://www.creditkarma.com/calculators/credit-cards/debt-repayment', '_blank')}
                    >
                      <div className="tool-icon">💳</div>
                      <div className="tool-info">
                        <h4 className="tool-title">Credit Card Debt Calculator</h4>
                        <p className="tool-description">Calculate how long it will take to pay off your credit card debt with Credit Karma's calculator.</p>
                      </div>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default AnalysisPage






