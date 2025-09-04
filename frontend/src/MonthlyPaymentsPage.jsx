import { useState } from 'react'
import './MonthlyPaymentsPage.css'
import WealthProjectionsPage from './WealthProjectionsPage'

function MonthlyPaymentsPage({ onBack, netWorthData, fileId }) {
  const [contributions, setContributions] = useState({
    contrib_checking: 0.0,
    contrib_hysa: 0.0,
    contrib_retirement: 0.0,
    move_checking_to_invest: 0.0
  })

  const [debtPayments, setDebtPayments] = useState({
    pay_mortgage: 0.0,
    pay_cc: 0.0,
    pay_personal: 0.0,
    pay_student: 0.0,
    pay_car: 0.0,
    pay_other_debt: 0.0
  })

  const [showWealthProjections, setShowWealthProjections] = useState(false)

  const handleContributionChange = (field, value) => {
    setContributions(prev => ({
      ...prev,
      [field]: parseFloat(value) || 0
    }))
  }

  const handleDebtPaymentChange = (field, value) => {
    setDebtPayments(prev => ({
      ...prev,
      [field]: parseFloat(value) || 0
    }))
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount)
  }

  const calculateTotalContributions = () => {
    return Object.values(contributions).reduce((total, amount) => total + amount, 0)
  }

  const calculateTotalDebtPayments = () => {
    return Object.values(debtPayments).reduce((total, amount) => total + amount, 0)
  }

  const handleCalculateProjection = () => {
    console.log('Calculating projection with:', { contributions, debtPayments, netWorthData })
    setShowWealthProjections(true)
  }

  const handleBackFromWealthProjections = () => {
    setShowWealthProjections(false)
  }

  if (showWealthProjections) {
    return <WealthProjectionsPage 
      onBack={handleBackFromWealthProjections}
      netWorthData={netWorthData}
      monthlyData={{ contributions, debtPayments }}
      fileId={fileId}
    />
  }

  return (
    <div className="monthly-payments-page">
      <div className="payments-header">
        <button className="back-button" onClick={onBack}>
          ← Back to Net Worth Calculator
        </button>
        <h1 className="payments-title">Monthly Contributions & Payments</h1>
        <p className="payments-subtitle">Set your monthly contributions and debt payments to see future projections</p>
      </div>

      <div className="payments-content">
        <div className="payments-grid">
          {/* Contributions Section */}
          <div className="contributions-section">
            <div className="section-header contributions-header">
              <h2>Monthly Contributions</h2>
              <p className="section-subtitle">Add money to your accounts each month</p>
            </div>
            
            <div className="input-section">
              <div className="input-group">
                <h3 className="input-title">Checking Account</h3>
                <p className="input-description">How much do you add to your checking account each month?</p>
                <div className="input-container">
                  <input
                    type="number"
                    step="0.01"
                    value={contributions.contrib_checking || ''}
                    onChange={(e) => handleContributionChange('contrib_checking', e.target.value)}
                    placeholder="$0.00"
                    className="amount-input"
                  />
                </div>
              </div>

              <div className="input-group">
                <h3 className="input-title">High-Yield Savings Account</h3>
                <p className="input-description">How much do you contribute to your HYSA each month?</p>
                <div className="input-container">
                  <input
                    type="number"
                    step="0.01"
                    value={contributions.contrib_hysa || ''}
                    onChange={(e) => handleContributionChange('contrib_hysa', e.target.value)}
                    placeholder="$0.00"
                    className="amount-input"
                  />
                </div>
              </div>

              <div className="input-group">
                <h3 className="input-title">Retirement Accounts</h3>
                <p className="input-description">How much do you contribute to 401(k), IRA, or other retirement accounts monthly?</p>
                <div className="input-container">
                  <input
                    type="number"
                    step="0.01"
                    value={contributions.contrib_retirement || ''}
                    onChange={(e) => handleContributionChange('contrib_retirement', e.target.value)}
                    placeholder="$0.00"
                    className="amount-input"
                  />
                </div>
              </div>

              <div className="input-group">
                <h3 className="input-title">Auto-Invest from Checking</h3>
                <p className="input-description">How much do you automatically move from checking to investments each month?</p>
                <div className="input-container">
                  <input
                    type="number"
                    step="0.01"
                    value={contributions.move_checking_to_invest || ''}
                    onChange={(e) => handleContributionChange('move_checking_to_invest', e.target.value)}
                    placeholder="$0.00"
                    className="amount-input"
                  />
                </div>
              </div>
            </div>

            <div className="section-total">
              <h3>Total Monthly Contributions: {formatCurrency(calculateTotalContributions())}</h3>
            </div>
          </div>

          {/* Debt Payments Section */}
          <div className="debt-payments-section">
            <div className="section-header debt-header">
              <h2>Monthly Debt Payments</h2>
              <p className="section-subtitle">Pay down your debts each month</p>
            </div>
            
            <div className="input-section">
              <div className="input-group">
                <h3 className="input-title">Mortgage Payment</h3>
                <p className="input-description">How much do you pay toward your mortgage each month?</p>
                <div className="input-container">
                  <input
                    type="number"
                    step="0.01"
                    value={debtPayments.pay_mortgage || ''}
                    onChange={(e) => handleDebtPaymentChange('pay_mortgage', e.target.value)}
                    placeholder="$0.00"
                    className="amount-input"
                  />
                </div>
              </div>

              <div className="input-group">
                <h3 className="input-title">Credit Card Payments</h3>
                <p className="input-description">How much do you pay toward credit card debt each month?</p>
                <div className="input-container">
                  <input
                    type="number"
                    step="0.01"
                    value={debtPayments.pay_cc || ''}
                    onChange={(e) => handleDebtPaymentChange('pay_cc', e.target.value)}
                    placeholder="$0.00"
                    className="amount-input"
                  />
                </div>
              </div>

              <div className="input-group">
                <h3 className="input-title">Personal Loan Payments</h3>
                <p className="input-description">How much do you pay toward personal loans each month?</p>
                <div className="input-container">
                  <input
                    type="number"
                    step="0.01"
                    value={debtPayments.pay_personal || ''}
                    onChange={(e) => handleDebtPaymentChange('pay_personal', e.target.value)}
                    placeholder="$0.00"
                    className="amount-input"
                  />
                </div>
              </div>

              <div className="input-group">
                <h3 className="input-title">Student Loan Payments</h3>
                <p className="input-description">How much do you pay toward student loans each month?</p>
                <div className="input-container">
                  <input
                    type="number"
                    step="0.01"
                    value={debtPayments.pay_student || ''}
                    onChange={(e) => handleDebtPaymentChange('pay_student', e.target.value)}
                    placeholder="$0.00"
                    className="amount-input"
                  />
                </div>
              </div>

              <div className="input-group">
                <h3 className="input-title">Car Loan Payments</h3>
                <p className="input-description">How much do you pay toward car loans each month?</p>
                <div className="input-container">
                  <input
                    type="number"
                    step="0.01"
                    value={debtPayments.pay_car || ''}
                    onChange={(e) => handleDebtPaymentChange('pay_car', e.target.value)}
                    placeholder="$0.00"
                    className="amount-input"
                  />
                </div>
              </div>

              <div className="input-group">
                <h3 className="input-title">Other Debt Payments</h3>
                <p className="input-description">How much do you pay toward other debts each month?</p>
                <div className="input-container">
                  <input
                    type="number"
                    step="0.01"
                    value={debtPayments.pay_other_debt || ''}
                    onChange={(e) => handleDebtPaymentChange('pay_other_debt', e.target.value)}
                    placeholder="$0.00"
                    className="amount-input"
                  />
                </div>
              </div>
            </div>

            <div className="section-total">
              <h3>Total Monthly Debt Payments: {formatCurrency(calculateTotalDebtPayments())}</h3>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="action-section">
          <div className="summary-card">
            <h3>Monthly Cash Flow Summary</h3>
            <div className="summary-row">
              <span>Total Contributions:</span>
              <span className="positive">+{formatCurrency(calculateTotalContributions())}</span>
            </div>
            <div className="summary-row">
              <span>Total Debt Payments:</span>
              <span className="negative">-{formatCurrency(calculateTotalDebtPayments())}</span>
            </div>
            <div className="summary-row total">
              <span>Net Monthly Cash Flow:</span>
              <span className={calculateTotalContributions() - calculateTotalDebtPayments() >= 0 ? 'positive' : 'negative'}>
                {calculateTotalContributions() - calculateTotalDebtPayments() >= 0 ? '+' : ''}{formatCurrency(calculateTotalContributions() - calculateTotalDebtPayments())}
              </span>
            </div>
          </div>
          
          <button className="calculate-projection-button" onClick={handleCalculateProjection}>
            Calculate Future Projections
          </button>
        </div>
      </div>
    </div>
  )
}

export default MonthlyPaymentsPage
