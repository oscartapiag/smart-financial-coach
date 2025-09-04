import { useState, useEffect } from 'react'
import './SubscriptionsPage.css'

function SubscriptionsPage({ fileId, onBack }) {
  const [loading, setLoading] = useState(true)
  const [subscriptions, setSubscriptions] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchSubscriptions()
  }, [fileId])

  const fetchSubscriptions = async () => {
    try {
      setLoading(true)
      const response = await fetch(`http://localhost:8000/files/${fileId}/subscriptions`)
      
      if (response.ok) {
        const data = await response.json()
        console.log('Subscriptions data received:', data)
        setSubscriptions(data)
      } else {
        setError('Failed to fetch subscriptions data')
      }
    } catch (err) {
      setError('Error connecting to server')
      console.error('Subscriptions fetch error:', err)
    } finally {
      setLoading(false)
    }
  }

  const formatAmount = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount)
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  if (loading) {
    return (
      <div className="subscriptions-page">
        <div className="loading-container">
          <div className="loading-content">
            <h2 className="loading-title">Loading Subscriptions</h2>
            <p className="loading-subtitle">Please wait while we fetch your subscription data...</p>
            <div className="loading-spinner"></div>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="subscriptions-page">
        <div className="error-container">
          <div className="error-content">
            <h2 className="error-title">Error Loading Subscriptions</h2>
            <p className="error-message">{error}</p>
            <button className="retry-button" onClick={fetchSubscriptions}>
              Try Again
            </button>
          </div>
        </div>
      </div>
    )
  }

  const totalMonthlyCost = subscriptions?.total_monthly_cost || 0
  const totalYearlyCost = totalMonthlyCost * 12
  
  console.log('Subscriptions data:', subscriptions)
  console.log('Total monthly cost:', totalMonthlyCost)
  console.log('Total yearly cost:', totalYearlyCost)

  return (
    <div className="subscriptions-page">
      <div className="subscriptions-header">
        <button className="back-button" onClick={onBack}>
          ← Back to Analysis
        </button>
        <h1 className="subscriptions-title">Your Subscriptions</h1>
      </div>

      <div className="subscriptions-content">
        {/* Summary Cards */}
        <div className="summary-cards">
          <div className="summary-card">
            <h3 className="summary-title">Total Subscriptions</h3>
            <p className="summary-value">{subscriptions?.total_subscriptions || 0}</p>
          </div>
          <div className="summary-card">
            <h3 className="summary-title">Monthly Cost</h3>
            <p className="summary-value">{formatAmount(totalMonthlyCost)}</p>
          </div>
          <div className="summary-card">
            <h3 className="summary-title">Yearly Cost</h3>
            <p className="summary-value">{formatAmount(totalYearlyCost)}</p>
          </div>
        </div>

        {/* Subscriptions List */}
        <div className="subscriptions-list">
          <h2 className="list-title">Active Subscriptions</h2>
          
          {!subscriptions?.subscriptions || subscriptions.subscriptions.length === 0 ? (
            <div className="no-subscriptions">
              <div className="no-subscriptions-icon">📱</div>
              <h3>No Subscriptions Found</h3>
              <p>We couldn't find any subscription data in your transaction history.</p>
            </div>
          ) : (
            <div className="subscriptions-grid">
              {subscriptions.subscriptions.map((subscription, index) => (
                <div key={index} className="subscription-card">
                  <div className="subscription-header">
                    <div className="subscription-icon">
                      {subscription.category === 'Entertainment' ? '🎬' :
                       subscription.category === 'Software' ? '💻' :
                       subscription.category === 'Music' ? '🎵' :
                       subscription.category === 'Fitness' ? '💪' :
                       subscription.category === 'News' ? '📰' :
                       subscription.category === 'Cloud' ? '☁️' :
                       subscription.category === 'Gaming' ? '🎮' : '📱'}
                    </div>
                    <div className="subscription-info">
                      <h3 className="subscription-name">{subscription.merchant || 'Unknown Service'}</h3>
                      <p className="subscription-category">Confidence: {(subscription.subscription_score * 100).toFixed(1)}%</p>
                    </div>
                  </div>
                  
                  <div className="subscription-details">
                    <div className="detail-row">
                      <span className="detail-label">Monthly Cost:</span>
                      <span className="detail-value">{formatAmount(subscription.average_monthly_cost || 0)}</span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label">Coverage (months):</span>
                      <span className="detail-value">{subscription.coverage_months || 0}</span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label">Avg Gap (days):</span>
                      <span className="detail-value">{subscription.median_gap_days?.toFixed(1) || 'N/A'}</span>
                    </div>
                  </div>
                  
                  {subscription.website && (
                    <div className="subscription-actions">
                      <button 
                        className="action-button primary"
                        onClick={() => window.open(subscription.website, '_blank')}
                        title={`Open ${subscription.merchant} website`}
                      >
                        🔗 Manage Subscription
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default SubscriptionsPage
