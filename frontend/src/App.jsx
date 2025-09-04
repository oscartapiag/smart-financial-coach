import { useState, useRef, useEffect } from 'react'
import AnalysisPage from './AnalysisPage'
import SubscriptionsPage from './SubscriptionsPage'
import './App.css'

function App() {
  const [isVisible, setIsVisible] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState(null) // 'success', 'error', or null
  const [uploadMessage, setUploadMessage] = useState('')
  const [uploadedFileId, setUploadedFileId] = useState(null)
  const [isDragOver, setIsDragOver] = useState(false)
  const [showAnalysis, setShowAnalysis] = useState(false)
  const [currentPage, setCurrentPage] = useState('analysis') // 'analysis' or 'subscriptions'
  const fileInputRef = useRef(null)

  // Trigger fade-in animation on component mount
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(true)
    }, 100)
    return () => clearTimeout(timer)
  }, [])

  // Handle URL-based navigation
  useEffect(() => {
    const path = window.location.pathname
    if (path.includes('/subscriptions/')) {
      const fileId = path.split('/subscriptions/')[1]
      if (fileId && fileId !== uploadedFileId) {
        setUploadedFileId(fileId)
      }
      setCurrentPage('subscriptions')
      setShowAnalysis(true)
    } else {
      setCurrentPage('analysis')
    }
  }, [uploadedFileId])

  const uploadFileToAPI = async (file) => {
    setIsUploading(true)
    setUploadStatus(null)
    setUploadMessage('')

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('http://localhost:8000/upload-transactions', {
        method: 'POST',
        body: formData,
      })

      const data = await response.json()

      if (response.ok) {
        setUploadStatus('success')
        setUploadedFileId(data.file_id)
        if (data.is_duplicate) {
          setUploadMessage(`File already exists! Using existing file (${data.filename})`)
        } else {
          setUploadMessage(`Successfully uploaded ${data.filename} with ${data.rows} transactions`)
        }
        
        // Navigate to analysis page after 2 seconds
        setTimeout(() => {
          setShowAnalysis(true)
        }, 2000)
      } else {
        setUploadStatus('error')
        setUploadMessage(data.detail || 'Upload failed')
      }
    } catch (error) {
      setUploadStatus('error')
      setUploadMessage('Failed to connect to server. Please make sure the backend is running.')
      console.error('Upload error:', error)
    } finally {
      setIsUploading(false)
    }
  }

  const handleFileUpload = (event) => {
    const file = event.target.files[0]
    if (file && file.type === 'text/csv') {
      uploadFileToAPI(file)
    } else {
      setUploadStatus('error')
      setUploadMessage('Please select a valid CSV file')
    }
  }

  const handleUploadClick = () => {
    fileInputRef.current?.click()
  }

  const handleDragEnter = (event) => {
    event.preventDefault()
    setIsDragOver(true)
  }

  const handleDragLeave = (event) => {
    event.preventDefault()
    setIsDragOver(false)
  }

  const handleDragOver = (event) => {
    event.preventDefault()
  }

  const handleDrop = (event) => {
    event.preventDefault()
    setIsDragOver(false)
    const files = event.dataTransfer.files
    if (files.length > 0) {
      const file = files[0]
      if (file.type === 'text/csv') {
        uploadFileToAPI(file)
      } else {
        setUploadStatus('error')
        setUploadMessage('Please drop a valid CSV file')
      }
    }
  }

  const handleBackToUpload = () => {
    setShowAnalysis(false)
    setUploadStatus(null)
    setUploadMessage('')
    setUploadedFileId(null)
    setCurrentPage('analysis')
  }

  const handleNavigateToSubscriptions = () => {
    setCurrentPage('subscriptions')
    window.history.pushState({}, '', `/subscriptions/${uploadedFileId}`)
  }

  const handleBackToAnalysis = () => {
    setCurrentPage('analysis')
    window.history.pushState({}, '', '/')
  }

  // Show analysis page if file was uploaded successfully
  if (showAnalysis && uploadedFileId) {
    if (currentPage === 'subscriptions') {
      return <SubscriptionsPage fileId={uploadedFileId} onBack={handleBackToAnalysis} />
    }
    return <AnalysisPage 
      fileId={uploadedFileId} 
      onBack={handleBackToUpload}
      onNavigateToSubscriptions={handleNavigateToSubscriptions}
    />
  }

  return (
    <div className="app">
      <div 
        className={`welcome-banner ${isVisible ? 'fade-in' : ''} ${isDragOver ? 'drag-over' : ''}`}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        <h1 className="welcome-title">
          Welcome: Ready to change your financial future?
        </h1>
        <p className="upload-text">Please upload your CSV file or drag and drop it here.</p>
        
        <div className="upload-section">
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv"
            onChange={handleFileUpload}
            style={{ display: 'none' }}
          />
          <button 
            className={`upload-button ${isUploading ? 'uploading' : ''}`} 
            onClick={handleUploadClick}
            disabled={isUploading}
          >
            {isUploading ? 'Uploading...' : 'Upload CSV'}
          </button>
        </div>

        {/* Status Messages */}
        {uploadStatus && (
          <div className={`status-message ${uploadStatus}`}>
            <div className="status-icon">
              {uploadStatus === 'success' ? '✅' : '❌'}
            </div>
            <div className="status-text">
              {uploadMessage}
            </div>
            {uploadStatus === 'success' && uploadedFileId && (
              <div className="file-id">
                File ID: {uploadedFileId}
                <button 
                  className="view-analysis-button"
                  onClick={() => setShowAnalysis(true)}
                >
                  View Analysis →
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default App
