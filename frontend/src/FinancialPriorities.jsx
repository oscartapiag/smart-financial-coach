import { useState, useEffect } from 'react'
import './FinancialPriorities.css'

function FinancialPriorities({ onBack, fileId }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [financialData, setFinancialData] = useState({
    creditCardDebt: {
      totalDebt: 0,
      highestApr: 0,
      minimumPayments: 0,
      debtAccounts: 0
    },
    emergencyFund: {
      currentFund: 0,
      targetFund: 0
    },
    retirementMatch: {
      employerMatchPercentage: 0,
      matchLimit: 0,
      currentContribution: 0,
      salary: 0
    },
    investingAllocation: {
      riskTolerance: 3,
      investmentExperience: 3,
      preferredRetirementAccount: 'both',
      hysaRate: 2.0
    }
  })
  const [priorities, setPriorities] = useState(null)
  const [currentStep, setCurrentStep] = useState(0)
  const [showResults, setShowResults] = useState(false)

  const steps = [
    { id: 'creditCardDebt', title: 'Credit Card Debt', icon: '💳' },
    { id: 'emergencyFund', title: 'Emergency Fund', icon: '💰' },
    { id: 'retirementMatch', title: 'Retirement Match', icon: '🏦' },
    { id: 'investingAllocation', title: 'Investing Allocation', icon: '📈' }
  ]

  const handleInputChange = (category, field, value) => {
    setFinancialData(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [field]: parseFloat(value) || 0
      }
    }))
  }

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1)
    } else {
      calculatePriorities()
    }
  }

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  const calculatePriorities = async () => {
    try {
      setLoading(true)
      setError(null)

      const response = await fetch(`http://localhost:8000/files/${fileId}/financial-priorities`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          financial_data: financialData
        })
      })

      if (response.ok) {
        const data = await response.json()
        setPriorities(data)
        setShowResults(true)
      } else {
        setError('Failed to calculate financial priorities')
      }
    } catch (err) {
      setError('Error connecting to server')
      console.error('Financial priorities error:', err)
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

  const renderCreditCardDebtStep = () => (
    <div className="step-content">
      <div className="step-header">
        <div className="step-icon">💳</div>
        <h2>Credit Card Debt Analysis</h2>
        <p className="step-description">
          Priority 1: Pay off credit card debt as fast as possible. Credit card debt typically has 15-25% APR, making it the highest priority.
        </p>
      </div>

      <div className="input-section">
        <div className="input-group">
          <label className="input-label">What is your total credit card debt? ($)</label>
          <input
            type="number"
            value={financialData.creditCardDebt.totalDebt || ''}
            onChange={(e) => handleInputChange('creditCardDebt', 'totalDebt', e.target.value)}
            placeholder="0"
            className="amount-input"
          />
        </div>

        <div className="input-group">
          <label className="input-label">What is your highest credit card APR? (%)</label>
          <input
            type="number"
            step="0.1"
            value={financialData.creditCardDebt.highestApr || ''}
            onChange={(e) => handleInputChange('creditCardDebt', 'highestApr', e.target.value)}
            placeholder="0"
            className="amount-input"
          />
        </div>

        <div className="input-group">
          <label className="input-label">What are your total minimum monthly payments? ($)</label>
          <input
            type="number"
            value={financialData.creditCardDebt.minimumPayments || ''}
            onChange={(e) => handleInputChange('creditCardDebt', 'minimumPayments', e.target.value)}
            placeholder="0"
            className="amount-input"
          />
        </div>

        <div className="input-group">
          <label className="input-label">How many credit card accounts do you have?</label>
          <input
            type="number"
            value={financialData.creditCardDebt.debtAccounts || ''}
            onChange={(e) => handleInputChange('creditCardDebt', 'debtAccounts', e.target.value)}
            placeholder="0"
            className="amount-input"
          />
        </div>
      </div>
    </div>
  )

  const renderEmergencyFundStep = () => (
    <div className="step-content">
      <div className="step-header">
        <div className="step-icon">💰</div>
        <h2>Emergency Fund Analysis</h2>
        <p className="step-description">
          Priority 2: Build emergency fund to cover 6 months of expenses. Based on your spending patterns, you need: {formatCurrency(priorities?.financial_overview?.six_month_expenses || 0)}
        </p>
      </div>

      <div className="input-section">
        <div className="input-group">
          <label className="input-label">How much do you currently have in your emergency fund? ($)</label>
          <input
            type="number"
            value={financialData.emergencyFund.currentFund || ''}
            onChange={(e) => handleInputChange('emergencyFund', 'currentFund', e.target.value)}
            placeholder="0"
            className="amount-input"
          />
        </div>

        <div className="info-box">
          <h4>Target Emergency Fund</h4>
          <p>{formatCurrency(priorities?.financial_overview?.six_month_expenses || 0)} (6 months of expenses)</p>
        </div>
      </div>
    </div>
  )

  const renderRetirementMatchStep = () => (
    <div className="step-content">
      <div className="step-header">
        <div className="step-icon">🏦</div>
        <h2>Retirement Match Analysis</h2>
        <p className="step-description">
          Priority 3: Always invest enough to capture employer match. This is free money - never miss it!
        </p>
      </div>

      <div className="input-section">
        <div className="input-group">
          <label className="input-label">What percentage does your employer match? (%)</label>
          <input
            type="number"
            step="0.1"
            value={financialData.retirementMatch.employerMatchPercentage || ''}
            onChange={(e) => handleInputChange('retirementMatch', 'employerMatchPercentage', e.target.value)}
            placeholder="0"
            className="amount-input"
          />
        </div>

        <div className="input-group">
          <label className="input-label">What's the maximum percentage they'll match? (%)</label>
          <input
            type="number"
            step="0.1"
            value={financialData.retirementMatch.matchLimit || ''}
            onChange={(e) => handleInputChange('retirementMatch', 'matchLimit', e.target.value)}
            placeholder="0"
            className="amount-input"
          />
        </div>

        <div className="input-group">
          <label className="input-label">What percentage are you currently contributing? (%)</label>
          <input
            type="number"
            step="0.1"
            value={financialData.retirementMatch.currentContribution || ''}
            onChange={(e) => handleInputChange('retirementMatch', 'currentContribution', e.target.value)}
            placeholder="0"
            className="amount-input"
          />
        </div>

        <div className="input-group">
          <label className="input-label">What is your annual salary? ($)</label>
          <input
            type="number"
            value={financialData.retirementMatch.salary || ''}
            onChange={(e) => handleInputChange('retirementMatch', 'salary', e.target.value)}
            placeholder="0"
            className="amount-input"
          />
        </div>
      </div>
    </div>
  )

  const renderInvestingAllocationStep = () => (
    <div className="step-content">
      <div className="step-header">
        <div className="step-icon">📈</div>
        <h2>Investing Allocation Analysis</h2>
        <p className="step-description">
          Priority 4: 80% retirement/SPY, 20% HYSA or high-risk securities. This is for any remaining discretionary income after priorities 1-3.
        </p>
      </div>

      <div className="input-section">
        <div className="input-group">
          <label className="input-label">What's your risk tolerance? (1=Very Conservative, 5=Very Aggressive)</label>
          <select
            value={financialData.investingAllocation.riskTolerance}
            onChange={(e) => handleInputChange('investingAllocation', 'riskTolerance', e.target.value)}
            className="amount-input"
          >
            <option value={1}>1 - Very Conservative</option>
            <option value={2}>2 - Conservative</option>
            <option value={3}>3 - Moderate</option>
            <option value={4}>4 - Aggressive</option>
            <option value={5}>5 - Very Aggressive</option>
          </select>
        </div>

        <div className="input-group">
          <label className="input-label">How experienced are you with investing? (1=Beginner, 5=Expert)</label>
          <select
            value={financialData.investingAllocation.investmentExperience}
            onChange={(e) => handleInputChange('investingAllocation', 'investmentExperience', e.target.value)}
            className="amount-input"
          >
            <option value={1}>1 - Beginner</option>
            <option value={2}>2 - Some Experience</option>
            <option value={3}>3 - Moderate</option>
            <option value={4}>4 - Experienced</option>
            <option value={5}>5 - Expert</option>
          </select>
        </div>

        <div className="input-group">
          <label className="input-label">Do you prefer 401k, IRA, or both?</label>
          <select
            value={financialData.investingAllocation.preferredRetirementAccount}
            onChange={(e) => handleInputChange('investingAllocation', 'preferredRetirementAccount', e.target.value)}
            className="amount-input"
          >
            <option value="401k">401k</option>
            <option value="ira">IRA</option>
            <option value="both">Both</option>
          </select>
        </div>

        <div className="input-group">
          <label className="input-label">What's your current HYSA interest rate? (%)</label>
          <input
            type="number"
            step="0.1"
            value={financialData.investingAllocation.hysaRate || ''}
            onChange={(e) => handleInputChange('investingAllocation', 'hysaRate', e.target.value)}
            placeholder="2.0"
            className="amount-input"
          />
        </div>
      </div>
    </div>
  )

  const renderResults = () => (
    <div className="results-content">
      <div className="results-header">
        <h2>🎯 Your Personalized Financial Plan</h2>
        <p className="results-subtitle">Based on your spending patterns and financial goals</p>
      </div>

      <div className="financial-overview">
        <h3>📊 Financial Overview</h3>
        <div className="overview-grid">
          <div className="overview-item">
            <span className="overview-label">Monthly Discretionary Income:</span>
            <span className="overview-value">{formatCurrency(priorities.financial_overview.monthly_discretionary_income)}</span>
          </div>
          <div className="overview-item">
            <span className="overview-label">6-Month Expenses:</span>
            <span className="overview-value">{formatCurrency(priorities.financial_overview.six_month_expenses)}</span>
          </div>
          <div className="overview-item">
            <span className="overview-label">Total Allocated:</span>
            <span className="overview-value">{formatCurrency(priorities.financial_overview.total_allocated)}</span>
          </div>
          <div className="overview-item">
            <span className="overview-label">Remaining After Plan:</span>
            <span className="overview-value">{formatCurrency(priorities.financial_overview.remaining_after_plan)}</span>
          </div>
        </div>
      </div>

      <div className="priorities-section">
        <h3>🎯 Financial Priorities</h3>
        {priorities.priorities.map((priority, index) => (
          <div key={index} className="priority-card">
            <div className="priority-header">
              <div className="priority-number">{priority.priority}</div>
              <div className="priority-title">{priority.name}</div>
              <div className="priority-status">{priority.status.replace('_', ' ').toUpperCase()}</div>
            </div>
            
            <div className="priority-description">{priority.description}</div>
            
            <div className="priority-details">
              <div className="detail-item">
                <span className="detail-label">Monthly Allocation:</span>
                <span className="detail-value">{formatCurrency(priority.monthly_allocation)}</span>
              </div>
              {priority.months_to_complete !== Infinity && priority.months_to_complete > 0 && (
                <div className="detail-item">
                  <span className="detail-label">Time to Complete:</span>
                  <span className="detail-value">{priority.months_to_complete.toFixed(1)} months</span>
                </div>
              )}
            </div>

            <div className="recommendations">
              <h4>Recommendations:</h4>
              <ul>
                {priority.recommendations.map((rec, recIndex) => (
                  <li key={recIndex}>{rec}</li>
                ))}
              </ul>
            </div>
          </div>
        ))}
      </div>

      <div className="next-steps">
        <h3>💡 Next Steps</h3>
        <ul>
          {priorities.next_steps.map((step, index) => (
            <li key={index}>{step}</li>
          ))}
        </ul>
      </div>
    </div>
  )

  if (loading) {
    return (
      <div className="financial-priorities">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p className="loading-text">Calculating your financial priorities...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="financial-priorities">
        <div className="error-container">
          <h3 className="error-title">Error Loading Financial Priorities</h3>
          <p className="error-message">{error}</p>
          <button className="retry-button" onClick={() => setError(null)}>
            Try Again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="financial-priorities">
      <div className="priorities-header">
        <button className="back-button" onClick={onBack}>
          ← Back to Analysis
        </button>
        <h1 className="priorities-title">Financial Priorities Planner</h1>
        <p className="priorities-subtitle">Get personalized recommendations for your discretionary income</p>
      </div>

      {!showResults ? (
        <div className="priorities-content">
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}></div>
          </div>

          <div className="step-indicator">
            <span>Step {currentStep + 1} of {steps.length}: {steps[currentStep].title}</span>
          </div>

          {currentStep === 0 && renderCreditCardDebtStep()}
          {currentStep === 1 && renderEmergencyFundStep()}
          {currentStep === 2 && renderRetirementMatchStep()}
          {currentStep === 3 && renderInvestingAllocationStep()}

          <div className="step-navigation">
            {currentStep > 0 && (
              <button className="nav-button back-button" onClick={handleBack}>
                ← Back
              </button>
            )}
            <button className="nav-button next-button" onClick={handleNext}>
              {currentStep === steps.length - 1 ? 'Calculate Plan' : 'Next →'}
            </button>
          </div>
        </div>
      ) : (
        <div className="priorities-content">
          {renderResults()}
          <div className="results-actions">
            <button className="nav-button back-button" onClick={() => setShowResults(false)}>
              ← Start Over
            </button>
            <button className="nav-button next-button" onClick={onBack}>
              Back to Analysis
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default FinancialPriorities
