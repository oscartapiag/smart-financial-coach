import { useState } from 'react'
import './NetWorthCalculator.css'
import MonthlyPaymentsPage from './MonthlyPaymentsPage'

function NetWorthCalculator({ onBack }) {
  const [assets, setAssets] = useState({
    realEstate: { value: 0, rate: 3.5 },
    checking: { value: 0, rate: 0 },
    savings: { value: 0, rate: 2.0 },
    retirement: { value: 0, rate: 10.0 },
    cars: { value: 0, rate: -10.0 },
    otherAssets: { value: 0, rate: 0 }
  })

  const [liabilities, setLiabilities] = useState({
    realEstateLoans: { value: 0, rate: 6.0 },
    creditCardDebt: { value: 0, rate: 22.0 },
    personalLoans: { value: 0, rate: 12.0 },
    studentLoans: { value: 0, rate: 7.0 },
    carLoans: { value: 0, rate: 9.0 },
    otherDebt: { value: 0, rate: 0 }
  })

  const [showRates, setShowRates] = useState({})
  const [showMonthlyPayments, setShowMonthlyPayments] = useState(false)

  const calculateTotal = (items) => {
    return Object.values(items).reduce((total, item) => total + (item.value || 0), 0)
  }

  const calculateProjectedValue = (value, rate) => {
    return value * (1 + rate / 100)
  }

  const totalAssets = calculateTotal(assets)
  const totalLiabilities = calculateTotal(liabilities)
  const netWorth = totalAssets - totalLiabilities

  const handleAssetChange = (category, field, value) => {
    setAssets(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [field]: parseFloat(value) || 0
      }
    }))
  }

  const handleLiabilityChange = (category, field, value) => {
    setLiabilities(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [field]: parseFloat(value) || 0
      }
    }))
  }

  const toggleRateVisibility = (category) => {
    setShowRates(prev => ({
      ...prev,
      [category]: !prev[category]
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

  const handleCalculateNetWorth = () => {
    setShowMonthlyPayments(true)
  }

  const handleBackFromMonthlyPayments = () => {
    setShowMonthlyPayments(false)
  }

  if (showMonthlyPayments) {
    return <MonthlyPaymentsPage 
      onBack={handleBackFromMonthlyPayments} 
      netWorthData={{ assets, liabilities, netWorth }}
    />
  }

  return (
    <div className="net-worth-calculator">
      <div className="calculator-header">
        <button className="back-button" onClick={onBack}>
          ← Back to Analysis
        </button>
        <h1 className="calculator-title">Net Worth Calculator</h1>
      </div>

      <div className="calculator-content">
        <div className="calculator-grid">
          {/* Assets Column */}
          <div className="assets-column">
            <div className="column-header assets-header">
              <h2>Assets: {formatCurrency(totalAssets)}</h2>
            </div>
            
            <div className="input-section">
              <div className="input-group">
                <h3 className="input-title">Real Estate</h3>
                <p className="input-description">Estimate the current value of your house (and other real estate you own).</p>
                <div className="input-container">
                  <input
                    type="number"
                    value={assets.realEstate.value || ''}
                    onChange={(e) => handleAssetChange('realEstate', 'value', e.target.value)}
                    placeholder="$0"
                    className="amount-input"
                  />
                  <button 
                    className="rate-button"
                    onClick={() => toggleRateVisibility('realEstate')}
                  >
                    {assets.realEstate.rate}%
                  </button>
                </div>
                {showRates.realEstate && (
                  <div className="rate-input">
                    <label>Annual Growth Rate:</label>
                    <input
                      type="number"
                      step="0.1"
                      value={assets.realEstate.rate}
                      onChange={(e) => handleAssetChange('realEstate', 'rate', e.target.value)}
                      className="rate-field"
                    />
                    <span>%</span>
                  </div>
                )}
              </div>

              <div className="input-group">
                <h3 className="input-title">Checking Accounts</h3>
                <p className="input-description">How much money do you currently have in your checking account(s)?</p>
                <div className="input-container">
                  <input
                    type="number"
                    value={assets.checking.value || ''}
                    onChange={(e) => handleAssetChange('checking', 'value', e.target.value)}
                    placeholder="$0"
                    className="amount-input"
                  />
                </div>
              </div>

              <div className="input-group">
                <h3 className="input-title">Savings Accounts</h3>
                <p className="input-description">How much money do you currently have in your savings account(s)?</p>
                <div className="input-container">
                  <input
                    type="number"
                    value={assets.savings.value || ''}
                    onChange={(e) => handleAssetChange('savings', 'value', e.target.value)}
                    placeholder="$0"
                    className="amount-input"
                  />
                  <button 
                    className="rate-button"
                    onClick={() => toggleRateVisibility('savings')}
                  >
                    {assets.savings.rate}%
                  </button>
                </div>
                {showRates.savings && (
                  <div className="rate-input">
                    <label>Annual Growth Rate (HYSA):</label>
                    <input
                      type="number"
                      step="0.1"
                      value={assets.savings.rate}
                      onChange={(e) => handleAssetChange('savings', 'rate', e.target.value)}
                      className="rate-field"
                    />
                    <span>%</span>
                  </div>
                )}
              </div>

              <div className="input-group">
                <h3 className="input-title">Retirement Accounts</h3>
                <p className="input-description">How much money do you have in 401(k)s, 403(b)s, IRAs, or other retirement accounts?</p>
                <div className="input-container">
                  <input
                    type="number"
                    value={assets.retirement.value || ''}
                    onChange={(e) => handleAssetChange('retirement', 'value', e.target.value)}
                    placeholder="$0"
                    className="amount-input"
                  />
                  <button 
                    className="rate-button"
                    onClick={() => toggleRateVisibility('retirement')}
                  >
                    {assets.retirement.rate}%
                  </button>
                </div>
                {showRates.retirement && (
                  <div className="rate-input">
                    <label>Annual Growth Rate (Stocks):</label>
                    <input
                      type="number"
                      step="0.1"
                      value={assets.retirement.rate}
                      onChange={(e) => handleAssetChange('retirement', 'rate', e.target.value)}
                      className="rate-field"
                    />
                    <span>%</span>
                  </div>
                )}
              </div>

              <div className="input-group">
                <h3 className="input-title">Cars</h3>
                <p className="input-description">Estimate the current value of your car (and other vehicles you own).</p>
                <div className="input-container">
                  <input
                    type="number"
                    value={assets.cars.value || ''}
                    onChange={(e) => handleAssetChange('cars', 'value', e.target.value)}
                    placeholder="$0"
                    className="amount-input"
                  />
                  <button 
                    className="rate-button"
                    onClick={() => toggleRateVisibility('cars')}
                  >
                    {assets.cars.rate}%
                  </button>
                </div>
                {showRates.cars && (
                  <div className="rate-input">
                    <label>Annual Depreciation Rate:</label>
                    <input
                      type="number"
                      step="0.1"
                      value={assets.cars.rate}
                      onChange={(e) => handleAssetChange('cars', 'rate', e.target.value)}
                      className="rate-field"
                    />
                    <span>%</span>
                  </div>
                )}
              </div>

              <div className="input-group">
                <h3 className="input-title">Other Assets</h3>
                <p className="input-description">Estimate the value of any antiques, jewelry, stocks, bonds, business assets, etc.</p>
                <div className="input-container">
                  <input
                    type="number"
                    value={assets.otherAssets.value || ''}
                    onChange={(e) => handleAssetChange('otherAssets', 'value', e.target.value)}
                    placeholder="$0"
                    className="amount-input"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Liabilities Column */}
          <div className="liabilities-column">
            <div className="column-header liabilities-header">
              <h2>Liabilities: <span className="liability-total-red">{formatCurrency(totalLiabilities)}</span></h2>
            </div>
            
            <div className="input-section">
              <div className="input-group">
                <h3 className="input-title">Real Estate Loans</h3>
                <p className="input-description">What's the total amount you still owe on your mortgage (and other properties you own)?</p>
                <div className="input-container">
                  <input
                    type="number"
                    value={liabilities.realEstateLoans.value || ''}
                    onChange={(e) => handleLiabilityChange('realEstateLoans', 'value', e.target.value)}
                    placeholder="$0"
                    className="amount-input"
                  />
                  <button 
                    className="rate-button"
                    onClick={() => toggleRateVisibility('realEstateLoans')}
                  >
                    {liabilities.realEstateLoans.rate}%
                  </button>
                </div>
                {showRates.realEstateLoans && (
                  <div className="rate-input">
                    <label>Annual Interest Rate:</label>
                    <input
                      type="number"
                      step="0.1"
                      value={liabilities.realEstateLoans.rate}
                      onChange={(e) => handleLiabilityChange('realEstateLoans', 'rate', e.target.value)}
                      className="rate-field"
                    />
                    <span>%</span>
                  </div>
                )}
              </div>

              <div className="input-group">
                <h3 className="input-title">Credit Card Debt</h3>
                <p className="input-description">How much credit card debt do you owe? Enter the total amount, not monthly payments.</p>
                <div className="input-container">
                  <input
                    type="number"
                    value={liabilities.creditCardDebt.value || ''}
                    onChange={(e) => handleLiabilityChange('creditCardDebt', 'value', e.target.value)}
                    placeholder="$0"
                    className="amount-input"
                  />
                  <button 
                    className="rate-button"
                    onClick={() => toggleRateVisibility('creditCardDebt')}
                  >
                    {liabilities.creditCardDebt.rate}%
                  </button>
                </div>
                {showRates.creditCardDebt && (
                  <div className="rate-input">
                    <label>Annual Interest Rate:</label>
                    <input
                      type="number"
                      step="0.1"
                      value={liabilities.creditCardDebt.rate}
                      onChange={(e) => handleLiabilityChange('creditCardDebt', 'rate', e.target.value)}
                      className="rate-field"
                    />
                    <span>%</span>
                  </div>
                )}
              </div>

              <div className="input-group">
                <h3 className="input-title">Personal Loans</h3>
                <p className="input-description">Do you have any personal loan debt (i.e. family or friends, payday loans)?</p>
                <div className="input-container">
                  <input
                    type="number"
                    value={liabilities.personalLoans.value || ''}
                    onChange={(e) => handleLiabilityChange('personalLoans', 'value', e.target.value)}
                    placeholder="$0"
                    className="amount-input"
                  />
                  <button 
                    className="rate-button"
                    onClick={() => toggleRateVisibility('personalLoans')}
                  >
                    {liabilities.personalLoans.rate}%
                  </button>
                </div>
                {showRates.personalLoans && (
                  <div className="rate-input">
                    <label>Annual Interest Rate:</label>
                    <input
                      type="number"
                      step="0.1"
                      value={liabilities.personalLoans.rate}
                      onChange={(e) => handleLiabilityChange('personalLoans', 'rate', e.target.value)}
                      className="rate-field"
                    />
                    <span>%</span>
                  </div>
                )}
              </div>

              <div className="input-group">
                <h3 className="input-title">Student Loans</h3>
                <p className="input-description">Do you have student loan debt? Enter the total amount owed, not monthly payments.</p>
                <div className="input-container">
                  <input
                    type="number"
                    value={liabilities.studentLoans.value || ''}
                    onChange={(e) => handleLiabilityChange('studentLoans', 'value', e.target.value)}
                    placeholder="$0"
                    className="amount-input"
                  />
                  <button 
                    className="rate-button"
                    onClick={() => toggleRateVisibility('studentLoans')}
                  >
                    {liabilities.studentLoans.rate}%
                  </button>
                </div>
                {showRates.studentLoans && (
                  <div className="rate-input">
                    <label>Annual Interest Rate:</label>
                    <input
                      type="number"
                      step="0.1"
                      value={liabilities.studentLoans.rate}
                      onChange={(e) => handleLiabilityChange('studentLoans', 'rate', e.target.value)}
                      className="rate-field"
                    />
                    <span>%</span>
                  </div>
                )}
              </div>

              <div className="input-group">
                <h3 className="input-title">Car Loans</h3>
                <p className="input-description">How much do you owe on your vehicle(s)? Enter the total amount owed, not monthly payments.</p>
                <div className="input-container">
                  <input
                    type="number"
                    value={liabilities.carLoans.value || ''}
                    onChange={(e) => handleLiabilityChange('carLoans', 'value', e.target.value)}
                    placeholder="$0"
                    className="amount-input"
                  />
                  <button 
                    className="rate-button"
                    onClick={() => toggleRateVisibility('carLoans')}
                  >
                    {liabilities.carLoans.rate}%
                  </button>
                </div>
                {showRates.carLoans && (
                  <div className="rate-input">
                    <label>Annual Interest Rate:</label>
                    <input
                      type="number"
                      step="0.1"
                      value={liabilities.carLoans.rate}
                      onChange={(e) => handleLiabilityChange('carLoans', 'rate', e.target.value)}
                      className="rate-field"
                    />
                    <span>%</span>
                  </div>
                )}
              </div>

              <div className="input-group">
                <h3 className="input-title">Other Debt</h3>
                <p className="input-description">List any other debts you owe (i.e. medical bills, business loans, HELOCs).</p>
                <div className="input-container">
                  <input
                    type="number"
                    value={liabilities.otherDebt.value || ''}
                    onChange={(e) => handleLiabilityChange('otherDebt', 'value', e.target.value)}
                    placeholder="$0"
                    className="amount-input"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Net Worth Display */}
        <div className="net-worth-display">
          <h2 className="net-worth-title">Net Worth: {formatCurrency(netWorth)}</h2>
          <button className="calculate-button" onClick={handleCalculateNetWorth}>Calculate Net Worth</button>
        </div>
      </div>
    </div>
  )
}

export default NetWorthCalculator
