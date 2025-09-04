import { useState } from 'react'
import './SavingsPlanner.css'

function SavingsPlanner({ onBack, fileId }) {
  const [targetAmount, setTargetAmount] = useState('')
  const [months, setMonths] = useState('')
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleAnalyze = async () => {
    if (!targetAmount || !months) {
      setError('Please enter both target amount and time period')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await fetch('http://localhost:8000/savings/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          file_id: fileId,
          target_amount: parseFloat(targetAmount),
          months: parseInt(months)
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      setAnalysis(data)
    } catch (err) {
      console.error('Error analyzing savings goal:', err)
      setError('Failed to analyze savings goal. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (amount) => {
    if (amount === null || amount === undefined || isNaN(amount)) {
      return '$0'
    }
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount)
  }

  const formatPercentage = (value) => {
    return `${Math.round(value)}%`
  }

  return (
    <div className="savings-planner-page">
      <div className="savings-planner-container">
        <div className="savings-planner-header">
          <button className="back-button" onClick={onBack}>
            ← Back to Analysis
          </button>
          <h1 className="page-title">💰 Savings Planner</h1>
          <p className="page-subtitle">Set your savings goal and get personalized advice on how to achieve it</p>
        </div>

        {!analysis ? (
          <div className="savings-input-section">
            <div className="input-card">
              <h2 className="input-title">Set Your Savings Goal</h2>
              
              <div className="input-group">
                <label htmlFor="targetAmount" className="input-label">
                  Target Amount ($)
                </label>
                <input
                  id="targetAmount"
                  type="number"
                  value={targetAmount}
                  onChange={(e) => setTargetAmount(e.target.value)}
                  placeholder="e.g., 5000"
                  className="input-field"
                  min="0"
                  step="0.01"
                />
              </div>

              <div className="input-group">
                <label htmlFor="months" className="input-label">
                  Time Period (Months)
                </label>
                <input
                  id="months"
                  type="number"
                  value={months}
                  onChange={(e) => setMonths(e.target.value)}
                  placeholder="e.g., 12"
                  className="input-field"
                  min="1"
                  max="120"
                  step="1"
                />
                <div className="input-hint">
                  Enter any number of months (1-120)
                </div>
              </div>

              {error && (
                <div className="error-message">
                  {error}
                </div>
              )}

              <button 
                className="analyze-button"
                onClick={handleAnalyze}
                disabled={loading || !targetAmount || !months}
              >
                {loading ? 'Analyzing...' : 'Analyze My Goal'}
              </button>
            </div>
          </div>
        ) : (
          <div className="analysis-results">
            <div className="results-header">
              <h2 className="results-title">Your Savings Analysis</h2>
              <button 
                className="new-analysis-button"
                onClick={() => {
                  setAnalysis(null)
                  setTargetAmount('')
                  setMonths('')
                  setError(null)
                }}
              >
                Set New Goal
              </button>
            </div>

            {/* Goal Summary */}
            <div className="goal-summary">
              <h3 className="section-title">Goal Summary</h3>
              <div className="goal-cards">
                <div className="goal-card">
                  <h4 className="goal-label">Target Amount</h4>
                  <p className="goal-value">{formatCurrency(analysis.goal.target_amount)}</p>
                </div>
                <div className="goal-card">
                  <h4 className="goal-label">Time Period</h4>
                  <p className="goal-value">{analysis.goal.months_to_save} months</p>
                </div>
                <div className="goal-card">
                  <h4 className="goal-label">Monthly Target</h4>
                  <p className="goal-value">{formatCurrency(analysis.goal.monthly_target)}</p>
                </div>
              </div>
            </div>

            {/* Current Financials */}
            <div className="current-financials">
              <h3 className="section-title">Your Current Financial Situation</h3>
              <div className="financial-cards">
                <div className="financial-card">
                  <h4 className="financial-label">Monthly Income</h4>
                  <p className="financial-value income">{formatCurrency(analysis.current_financials.monthly_income)}</p>
                </div>
                <div className="financial-card">
                  <h4 className="financial-label">Monthly Expenses</h4>
                  <p className="financial-value expense">{formatCurrency(analysis.current_financials.monthly_expenses)}</p>
                </div>
                <div className="financial-card">
                  <h4 className="financial-label">Current Monthly Savings</h4>
                  <p className={`financial-value ${analysis.current_financials.monthly_savings >= 0 ? 'positive' : 'negative'}`}>
                    {formatCurrency(analysis.current_financials.monthly_savings)}
                  </p>
                </div>
              </div>
            </div>

            {/* Analysis Results */}
            <div className="analysis-results-section">
              <h3 className="section-title">Analysis Results</h3>
              <div className={`achievement-status ${analysis.analysis.can_achieve_goal ? 'achievable' : 'not-achievable'}`}>
                <div className="status-icon">
                  {analysis.analysis.can_achieve_goal ? '✅' : '⚠️'}
                </div>
                <div className="status-content">
                  <h4 className="status-title">
                    {analysis.analysis.can_achieve_goal ? 'Goal is Achievable!' : 'Goal Needs Adjustment'}
                  </h4>
                  <p className="status-description">
                    {analysis.analysis.can_achieve_goal 
                      ? `You can save ${formatCurrency(analysis.goal.monthly_target)} per month to reach your goal.`
                      : `You need to save an additional ${formatCurrency(analysis.analysis.shortfall)} per month to reach your goal.`
                    }
                  </p>
                </div>
              </div>
            </div>

            {/* Suggested Cuts */}
            {analysis.suggested_cuts && analysis.suggested_cuts.length > 0 && (
              <div className="suggested-cuts">
                <h3 className="section-title">Suggested Spending Reductions</h3>
                <p className="cuts-description">
                  Here are the categories where you can reduce spending to reach your goal:
                </p>
                <div className="cuts-grid">
                  {analysis.suggested_cuts.map((cut, index) => (
                    <div key={index} className={`cut-card priority-${cut.priority}`}>
                      <div className="cut-header">
                        <h4 className="cut-category">{cut.category}</h4>
                        <span className={`priority-badge priority-${cut.priority}`}>
                          Priority {cut.priority}
                        </span>
                      </div>
                      <div className="cut-details">
                        <div className="cut-amount">
                          <span className="cut-label">Current:</span>
                          <span className="cut-current">{formatCurrency(cut.current_monthly)}</span>
                        </div>
                        <div className="cut-amount">
                          <span className="cut-label">Suggested:</span>
                          <span className="cut-suggested">{formatCurrency(cut.suggested_monthly)}</span>
                        </div>
                        <div className="cut-savings">
                          <span className="savings-label">Monthly Savings:</span>
                          <span className="savings-amount">{formatCurrency(cut.reduction_amount)}</span>
                          <span className="savings-percentage">({formatPercentage(cut.reduction_percentage)})</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                
                <div className="total-savings">
                  <h4 className="total-savings-title">Total Monthly Savings from Reductions</h4>
                  <p className="total-savings-amount">{formatCurrency(analysis.analysis.total_suggested_savings)}</p>
                </div>
              </div>
            )}

            {/* Alternative Strategies */}
            {analysis.alternative_strategies && analysis.alternative_strategies.length > 0 && (
              <div className="alternative-strategies">
                <h3 className="section-title">Alternative Strategies</h3>
                <div className="strategies-list">
                  {analysis.alternative_strategies.map((strategy, index) => (
                    <div key={index} className="strategy-item">
                      <div className="strategy-icon">💡</div>
                      <p className="strategy-text">{strategy}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Summary */}
            <div className="final-summary">
              <h3 className="section-title">Summary</h3>
              <div className="summary-cards">
                <div className="summary-card">
                  <h4 className="summary-label">Categories Analyzed</h4>
                  <p className="summary-value">{analysis.summary.total_categories_analyzed}</p>
                </div>
                <div className="summary-card">
                  <h4 className="summary-label">High Priority Cuts</h4>
                  <p className="summary-value">{analysis.summary.high_priority_cuts}</p>
                </div>
                <div className="summary-card">
                  <h4 className="summary-label">Total Monthly Reduction</h4>
                  <p className="summary-value">{formatCurrency(analysis.summary.total_monthly_reduction)}</p>
                </div>
                <div className="summary-card">
                  <h4 className="summary-label">Goal Achievable with Cuts</h4>
                  <p className={`summary-value ${analysis.summary.achievable_with_cuts ? 'positive' : 'negative'}`}>
                    {analysis.summary.achievable_with_cuts ? 'Yes' : 'No'}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default SavingsPlanner
