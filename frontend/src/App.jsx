import { useState, useEffect, useRef } from 'react'
import { FileText, Upload, Loader2, Download, CheckCircle2, XCircle, FileDown, Github, Clock, Repeat2, Scissors, DownloadCloud } from 'lucide-react'
import { Button } from './components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card'
import { Select } from './components/ui/select'
import { Badge } from './components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs'
import { Alert, AlertDescription } from './components/ui/alert'
import { CompareModal } from './components/CompareModal'
import { RecentComparisons } from './components/RecentComparisons'
import { ComparisonResults } from './components/ComparisonResults'
import { ChunkerSelect } from './components/ChunkerSelect'
import { ChunkResults } from './components/ChunkResults'

function App() {
  const [libraries, setLibraries] = useState([])
  const [selectedLibrary, setSelectedLibrary] = useState('')
  const [selectedFile, setSelectedFile] = useState(null)
  const [isDragging, setIsDragging] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [pdfUrl, setPdfUrl] = useState(null)
  const [outputFormat, setOutputFormat] = useState('markdown')
  const [toastMessage, setToastMessage] = useState(null)
  const [timeTaken, setTimeTaken] = useState(null)
  const [startTime, setStartTime] = useState(null)
  
  // Comparison states
  const [showCompareModal, setShowCompareModal] = useState(false)
  const [recentTasks, setRecentTasks] = useState([])
  const [currentComparisonTask, setCurrentComparisonTask] = useState(null)
  const [comparisonComparisons, setComparisonComparisons] = useState([])
  const [isComparingLoading, setIsComparingLoading] = useState(false)
  
  // Chunking states
  const [chunkers, setChunkers] = useState([])
  const [selectedChunker, setSelectedChunker] = useState('')
  const [chunkerParams, setChunkerParams] = useState({})
  const [chunkingResult, setChunkingResult] = useState(null)
  const [showChunkResults, setShowChunkResults] = useState(false)
  
  // Download states
  const [downloadingLibraries, setDownloadingLibraries] = useState(new Set())
  
  const toastTimerRef = useRef(null)
  const timerIntervalRef = useRef(null)
  const comparisonProgressInterval = useRef(null)

  useEffect(() => {
    loadLibraries()
    loadHistory()
    loadChunkers()
  }, [])
  
  const loadChunkers = async () => {
    try {
      const response = await fetch('/chunkers')
      const data = await response.json()
      setChunkers(data.chunkers || [])
    } catch (err) {
      console.error('Failed to load chunkers:', err)
    }
  }
  
  const handleChunkConvertedText = async () => {
    if (!result || !result.content) {
      setError('No converted text available to chunk')
      return
    }
    
    // Use the first available chunker if none selected
    const chunkerToUse = selectedChunker || (chunkers.find(c => c.available)?.name)
    if (!chunkerToUse) {
      setError('No chunker available')
      return
    }
    
    setIsLoading(true)
    setError(null)
    
    try {
      const response = await fetch('/chunk', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          text: result.content,
          chunker: chunkerToUse,
          params: JSON.stringify(chunkerParams)
        })
      })
      
      const data = await response.json()
      
      if (response.ok && data.success) {
        setChunkingResult({
          chunking: data.result,
          conversion: { content: result.content }
        })
        setShowChunkResults(true)
      } else {
        setError(data.detail || 'Chunking failed')
      }
    } catch (err) {
      setError('Failed to chunk text: ' + err.message)
    } finally {
      setIsLoading(false)
    }
  }
  
  const handleDownloadLibrary = async (libraryName) => {
    // Add to downloading set
    setDownloadingLibraries(prev => new Set([...prev, libraryName]))
    setError(null)
    
    try {
      const response = await fetch(`/libraries/${libraryName}/download`, {
        method: 'POST'
      })
      
      const data = await response.json()
      
      if (response.ok && data.success) {
        // Refresh libraries list to get updated status
        await loadLibraries()
        setToastMessage(`${libraryName} models downloaded successfully`)
        setTimeout(() => setToastMessage(null), 3000)
      } else {
        setError(data.detail || `Failed to download ${libraryName} models`)
      }
    } catch (err) {
      setError(`Failed to download ${libraryName}: ${err.message}`)
    } finally {
      // Remove from downloading set
      setDownloadingLibraries(prev => {
        const newSet = new Set(prev)
        newSet.delete(libraryName)
        return newSet
      })
    }
  }

  const loadLibraries = async () => {
    try {
      const response = await fetch('/libraries')
      const data = await response.json()
      setLibraries(data.libraries)
      // Auto-select first available library
      const available = data.libraries.find(lib => lib.available)
      if (available) {
        setSelectedLibrary(available.name)
        if (available.name === 'deepseekocr') {
          showGPUToast(available.error)
        }
      }
    } catch (err) {
      setError('Failed to load libraries')
      console.error(err)
    }
  }

  const showGPUToast = (message) => {
    if (toastTimerRef.current) {
      clearTimeout(toastTimerRef.current)
    }
    setToastMessage(message || 'DeepSeek-OCR requires a CUDA-enabled GPU')
    toastTimerRef.current = setTimeout(() => setToastMessage(null), 5000)
  }

  useEffect(() => {
    return () => {
      if (toastTimerRef.current) {
        clearTimeout(toastTimerRef.current)
      }
      if (timerIntervalRef.current) {
        clearInterval(timerIntervalRef.current)
      }
    }
  }, [])

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    const files = e.dataTransfer.files
    if (files.length > 0 && files[0].type === 'application/pdf') {
      setSelectedFile(files[0])
      setError(null)
    } else {
      setError('Please select a PDF file')
    }
  }

  const handleFileSelect = (e) => {
    const file = e.target.files[0]
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file)
      setError(null)
    } else {
      setError('Please select a PDF file')
    }
  }

  const handleLibrarySelect = (value) => {
    setSelectedLibrary(value)
    const lib = libraries.find((item) => item.name === value)
    if (lib && lib.name === 'deepseekocr') {
      showGPUToast(lib.error || 'DeepSeek-OCR requires a CUDA-enabled GPU')
    } else {
      if (toastTimerRef.current) {
        clearTimeout(toastTimerRef.current)
        toastTimerRef.current = null
      }
      setToastMessage(null)
    }
  }

  const handleConvert = async () => {
    if (!selectedFile || !selectedLibrary) {
      setError('Please select a file and library')
      return
    }

    setIsLoading(true)
    setError(null)
    setResult(null)
    setChunkingResult(null)
    setTimeTaken(null)
    
    // Start timer
    const start = Date.now()
    setStartTime(start)
    
    // Update timer every 100ms
    if (timerIntervalRef.current) {
      clearInterval(timerIntervalRef.current)
    }
    timerIntervalRef.current = setInterval(() => {
      const elapsed = ((Date.now() - start) / 1000).toFixed(2)
      setTimeTaken(elapsed)
    }, 100)

    const formData = new FormData()
    formData.append('file', selectedFile)
    formData.append('library', selectedLibrary)
    formData.append('output_format', outputFormat)

    // If chunking is selected, use the convert-and-chunk endpoint
    if (selectedChunker && outputFormat !== 'json') {
      formData.append('chunker', selectedChunker)
      formData.append('chunker_params', JSON.stringify(chunkerParams))
      
      try {
        const response = await fetch('/convert-and-chunk', {
          method: 'POST',
          body: formData,
        })

        const data = await response.json()

        if (response.ok && data.success) {
          // Set result for display
          setResult({
            success: true,
            library_used: data.library_used,
            filename: data.filename,
            format: data.format,
            content: data.conversion.content
          })
          setChunkingResult(data)
          // Create object URL for PDF preview
          const url = URL.createObjectURL(selectedFile)
          setPdfUrl(url)
        } else {
          setError(data.detail || 'Conversion and chunking failed')
        }
      } catch (err) {
        setError('Failed to convert and chunk PDF: ' + err.message)
      } finally {
        setIsLoading(false)
        if (timerIntervalRef.current) {
          clearInterval(timerIntervalRef.current)
        }
      }
    } else {
      // Standard conversion without chunking
      try {
        const response = await fetch('/convert', {
          method: 'POST',
          body: formData,
        })

        const data = await response.json()

        if (response.ok && data.success) {
          setResult(data)
          // Create object URL for PDF preview
          const url = URL.createObjectURL(selectedFile)
          setPdfUrl(url)
        } else {
          setError(data.detail || 'Conversion failed')
        }
      } catch (err) {
        setError('Failed to convert PDF: ' + err.message)
      } finally {
        setIsLoading(false)
        // Stop timer
        if (timerIntervalRef.current) {
          clearInterval(timerIntervalRef.current)
        }
      }
    }
  }

  const handleDownload = () => {
    if (!result || !result.content) return

    const content = result.content || result.data
    const blob = new Blob([typeof content === 'string' ? content : JSON.stringify(content, null, 2)], {
      type: outputFormat === 'json' ? 'application/json' : 'text/markdown',
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${result.filename.replace('.pdf', '')}.${outputFormat === 'json' ? 'json' : 'md'}`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const loadHistory = async () => {
    try {
      const response = await fetch('/history?limit=10')
      const data = await response.json()
      setRecentTasks(data.tasks || [])
    } catch (err) {
      console.error('Failed to load history:', err)
    }
  }

  const handleCompareRun = async (selectedLibraries) => {
    if (!selectedFile) return

    setIsComparingLoading(true)
    setError(null)

    const formData = new FormData()
    formData.append('file', selectedFile)
    formData.append('libraries', JSON.stringify(selectedLibraries))
    formData.append('output_format', outputFormat)

    try {
      const response = await fetch('/compare', {
        method: 'POST',
        body: formData,
      })

      const data = await response.json()

      if (response.ok && data.task_id) {
        setCurrentComparisonTask(data)
        setComparisonComparisons([])
        comparisonProgressInterval.current = setInterval(() => {
          pollComparisonProgress(data.task_id)
        }, 500)
      } else {
        setError(data.detail || 'Comparison failed')
      }
    } catch (err) {
      setError('Failed to start comparison: ' + err.message)
    } finally {
      setIsComparingLoading(false)
      setShowCompareModal(false)
    }
  }

  const pollComparisonProgress = async (taskId) => {
    try {
      const response = await fetch(`/compare/${taskId}`)
      const data = await response.json()

      if (response.ok) {
        setCurrentComparisonTask(data)
        setComparisonComparisons(data.comparisons || [])

        // Stop polling if completed
        if (data.status === 'completed') {
          clearInterval(comparisonProgressInterval.current)
          loadHistory() // Refresh history
        }
      }
    } catch (err) {
      console.error('Failed to poll comparison progress:', err)
    }
  }

  const viewComparisonDetails = async (taskId) => {
    try {
      const response = await fetch(`/compare/${taskId}/results`)
      const data = await response.json()

      if (response.ok) {
        setCurrentComparisonTask(data.task)
        
        // Fetch content for each comparison
        const comparisonsWithContent = await Promise.all(
          data.comparisons.map(async (comp) => {
            if (comp.status === 'success') {
              try {
                const contentResp = await fetch(`/compare/${taskId}/content/${comp.library_name}`)
                const contentData = await contentResp.json()
                return { ...comp, content: contentData.content }
              } catch {
                return comp
              }
            }
            return comp
          })
        )
        
        setComparisonComparisons(comparisonsWithContent)
      }
    } catch (err) {
      console.error('Failed to load comparison details:', err)
      setError('Failed to load comparison details')
    }
  }

  const deleteComparison = async (taskId) => {
    try {
      const response = await fetch(`/compare/${taskId}`, { method: 'DELETE' })
      if (response.ok) {
        loadHistory()
        setCurrentComparisonTask(null)
      }
    } catch (err) {
      console.error('Failed to delete comparison:', err)
    }
  }

  const handleDownloadComparison = async (taskId, library) => {
    try {
      if (library) {
        // Download single library result
        const response = await fetch(`/compare/${taskId}/content/${library}`)
        const data = await response.json()
        
        const content = typeof data.content === 'string' ? data.content : JSON.stringify(data.content, null, 2)
        const blob = new Blob([content], { type: outputFormat === 'json' ? 'application/json' : 'text/markdown' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `${library}_result.${outputFormat === 'json' ? 'json' : 'md'}`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
      } else {
        // Download all results as zip
        const response = await fetch(`/compare/${taskId}/download`)
        if (!response.ok) throw new Error('Download failed')
        
        const blob = await response.blob()
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `comparison_${taskId}.zip`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
      }
    } catch (err) {
      console.error('Failed to download:', err)
    }
  }

  const renderMarkdownPreview = (markdown) => {
    // Simple markdown to HTML converter
    let html = markdown
      .replace(/^### (.*$)/gim, '<h3>$1</h3>')
      .replace(/^## (.*$)/gim, '<h2>$1</h2>')
      .replace(/^# (.*$)/gim, '<h1>$1</h1>')
      .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/gim, '<em>$1</em>')
      .replace(/```([\s\S]*?)```/gim, '<pre><code>$1</code></pre>')
      .replace(/`(.*?)`/gim, '<code>$1</code>')
      .replace(/\[([^\]]+)\]\(([^)]+)\)/gim, '<a href="$2" target="_blank">$1</a>')
      .replace(/\n\n/gim, '</p><p>')
      .replace(/^\* (.*$)/gim, '<li>$1</li>')
      .replace(/^- (.*$)/gim, '<li>$1</li>')
      .replace(/^> (.*$)/gim, '<blockquote>$1</blockquote>')

    return { __html: '<p>' + html + '</p>' }
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900">
      {toastMessage && (
        <div className="fixed inset-x-0 top-4 flex justify-center pointer-events-none z-50">
          <div className="bg-slate-900 text-white text-sm px-4 py-2 rounded-md shadow-lg border border-white/20">
            {toastMessage}
          </div>
        </div>
      )}
      <div className="w-full h-screen flex flex-col">
        {/* Minimal Header */}
        <header className="border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 px-8 py-3 flex-shrink-0">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <FileText className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-semibold text-slate-900 dark:text-slate-100 leading-tight">
                  PDFStract
                </h1>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Get your PDFs ready for AI
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              {isLoading && timeTaken && (
                <div className="flex items-center gap-2 px-3 py-2 rounded-md bg-blue-50 dark:bg-blue-950/20">
                  <Clock className="w-4 h-4 text-blue-600 dark:text-blue-400 animate-spin" />
                  <span className="text-sm font-medium text-blue-600 dark:text-blue-400">
                    {timeTaken}s
                  </span>
                </div>
              )}
              {result && timeTaken && !isLoading && (
                <div className="flex items-center gap-2 px-3 py-2 rounded-md bg-green-50 dark:bg-green-950/20">
                  <Clock className="w-4 h-4 text-green-600 dark:text-green-400" />
                  <span className="text-sm font-medium text-green-600 dark:text-green-400">
                    {timeTaken}s
                  </span>
                </div>
              )}
              {result && (
                <Button onClick={handleDownload} variant="outline" size="sm" className="gap-2">
                  <Download className="w-4 h-4" />
                  Download
                </Button>
              )}
              <a
                href="https://github.com/AKSarav/pdfstract"
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                title="Star on GitHub"
              >
                <Github className="w-5 h-5 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100" />
              </a>
            </div>
          </div>
        </header>

        {/* Main Content - Full Width */}
        <div className="flex-1 overflow-hidden flex">
          {/* Left Panel - Controls (Fixed Width) */}
          <aside className="w-80 border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 flex-shrink-0 overflow-y-auto">
            <div className="p-6 space-y-6">
              {/* File Upload Section */}
              <div className="space-y-3">
                <h2 className="text-sm font-semibold text-slate-900 dark:text-slate-100 uppercase tracking-wide">
                  Upload PDF
                </h2>
                <div
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  className={`border-2 border-dashed rounded-lg transition-all ${
                    isDragging
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-950/20'
                      : selectedFile
                      ? 'border-gray-300 dark:border-gray-800 bg-gray-50 dark:bg-gray-950/20'
                      : 'border-slate-300 dark:border-slate-700 hover:border-slate-400 dark:hover:border-slate-600'
                  }`}
                >
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={handleFileSelect}
                    className="hidden"
                    id="file-input"
                    disabled={isLoading}
                  />
                  <label htmlFor="file-input" className="cursor-pointer block p-6 text-center">
                    {selectedFile ? (
                      <div className="space-y-2">
                        <CheckCircle2 className="w-8 h-8 mx-auto text-green-500" />
                        <p className="text-sm font-medium text-slate-900 dark:text-slate-100 truncate">
                          {selectedFile.name}
                        </p>
                        <p className="text-xs text-slate-500">
                          {formatFileSize(selectedFile.size)}
                        </p>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        <div className="w-12 h-12 mx-auto bg-slate-100 dark:bg-slate-800 rounded-lg flex items-center justify-center">
                          <Upload className="w-6 h-6 text-slate-400" />
                        </div>
                        <div>
                          <p className="text-sm font-medium text-slate-700 dark:text-slate-300">
                            Drop PDF here
                          </p>
                          <p className="text-xs text-slate-500 mt-1">
                            or click to browse
                          </p>
                        </div>
                      </div>
                    )}
                  </label>
                </div>
              </div>

              {/* Configuration Section */}
              <div className="space-y-4">
                <h2 className="text-sm font-semibold text-slate-900 dark:text-slate-100 uppercase tracking-wide">
                  Configuration
                </h2>
                
                {/* Library Selection */}
                <div className="space-y-2">
                  <label className="text-xs font-medium text-slate-700 dark:text-slate-300">
                    Conversion Library
                  </label>
                  <Select
                    value={selectedLibrary}
                    onChange={(e) => handleLibrarySelect(e.target.value)}
                    disabled={isLoading}
                    className="w-full"
                  >
                    <option value="">Select library...</option>
                    {libraries.map((lib) => (
                      <option key={lib.name} value={lib.name} disabled={!lib.available}>
                        {lib.name} {!lib.available && '(unavailable)'}
                      </option>
                    ))}
                  </Select>
                </div>

                {/* Output Format */}
                <div className="space-y-2">
                  <label className="text-xs font-medium text-slate-700 dark:text-slate-300">
                    Output Format
                  </label>
                  <Select
                    value={outputFormat}
                    onChange={(e) => {
                      setOutputFormat(e.target.value)
                      // Clear chunker if switching to JSON (chunking not supported)
                      if (e.target.value === 'json') {
                        setSelectedChunker('')
                        setChunkerParams({})
                      }
                    }}
                    disabled={isLoading}
                    className="w-full"
                  >
                    <option value="markdown">Markdown</option>
                    <option value="json">JSON</option>
                    <option value="text">Plain Text</option>
                  </Select>
                </div>

                {/* Chunking Configuration (only for text-based formats) */}
                {outputFormat !== 'json' && (
                  <div className="space-y-2">
                    {chunkers.length > 0 ? (
                      <ChunkerSelect
                        chunkers={chunkers}
                        selectedChunker={selectedChunker}
                        onChunkerChange={(chunker) => {
                          setSelectedChunker(chunker)
                          setChunkerParams({}) // Reset params when changing chunker
                        }}
                        params={chunkerParams}
                        onParamsChange={setChunkerParams}
                        disabled={isLoading}
                      />
                    ) : (
                      <>
                        <label className="text-xs font-medium text-slate-700 dark:text-slate-300">
                          Text Chunking (for RAG)
                        </label>
                        <Select disabled className="w-full">
                          <option value="">Install chonkie to enable</option>
                        </Select>
                      </>
                    )}
                  </div>
                )}

                {/* Convert Button */}
                <Button
                  onClick={handleConvert}
                  disabled={!selectedFile || !selectedLibrary || isLoading}
                  className="w-full"
                  size="lg"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Converting...
                    </>
                  ) : (
                    <>
                      <FileText className="w-4 h-4 mr-2" />
                      Convert PDF
                    </>
                  )}
                </Button>

                {/* Compare Button */}
                <Button
                  onClick={() => setShowCompareModal(true)}
                  variant="outline"
                  disabled={!selectedFile || isComparingLoading}
                  className="w-full"
                  size="lg"
                >
                  {isComparingLoading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Comparing...
                    </>
                  ) : (
                    <>
                      <Repeat2 className="w-4 h-4 mr-2" />
                      Compare Models
                    </>
                  )}
                </Button>
              </div>

              {/* Library Status */}
              <div className="space-y-3">
                <h2 className="text-sm font-semibold text-slate-900 dark:text-slate-100 uppercase tracking-wide">
                  Available Libraries
                </h2>
                <div className="space-y-2">
                  {libraries.map((lib) => {
                    const isDownloading = downloadingLibraries.has(lib.name)
                    const needsDownload = lib.requires_download && lib.download_status === 'not_started' && lib.available
                    const isReady = lib.download_status === 'ready' || lib.download_status === 'not_required'
                    
                    return (
                      <div
                        key={lib.name}
                        className={`flex items-center justify-between p-2 rounded-md text-xs ${
                          lib.available && isReady
                            ? 'bg-green-50 dark:bg-green-950/20 text-green-700 dark:text-green-400'
                            : lib.available && needsDownload
                            ? 'bg-amber-50 dark:bg-amber-950/20 text-amber-700 dark:text-amber-400'
                            : 'bg-slate-100 dark:bg-slate-800 text-slate-500'
                        }`}
                      >
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{lib.name}</span>
                          {lib.name === 'deepseekocr' && (
                            <Badge variant="outline" className="text-[10px]">
                              GPU only
                            </Badge>
                          )}
                          {lib.name === 'mineru' && (
                            <Badge variant="outline" className="text-[10px]">
                              Docker Only
                            </Badge>
                          )}
                          {lib.name === 'paddleocr' && (
                            <Badge variant="outline" className="text-[10px]">
                              Mac M1/M2, GPU only
                            </Badge>
                          )}
                          {needsDownload && !isDownloading && (
                            <Badge variant="outline" className="text-[10px] text-amber-600">
                              needs models
                            </Badge>
                          )}
                        </div>
                        <div className="flex items-center gap-1">
                          {/* Download button for libraries that need models */}
                          {lib.available && needsDownload && (
                            <button
                              onClick={() => handleDownloadLibrary(lib.name)}
                              disabled={isDownloading}
                              className="p-1 rounded hover:bg-amber-100 dark:hover:bg-amber-900/30 transition-colors"
                              title={`Download ${lib.name} models`}
                            >
                              {isDownloading ? (
                                <Loader2 className="w-4 h-4 animate-spin text-amber-600" />
                              ) : (
                                <DownloadCloud className="w-4 h-4 text-amber-600 hover:text-amber-700" />
                              )}
                            </button>
                          )}
                          {/* Status icon */}
                          {lib.available && isReady ? (
                            <CheckCircle2 className="w-4 h-4 text-green-500" />
                          ) : lib.available && isDownloading ? (
                            <Loader2 className="w-4 h-4 animate-spin text-amber-500" />
                          ) : !lib.available ? (
                            <XCircle className="w-4 h-4 text-slate-400" />
                          ) : null}
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>

              {/* Recent Comparisons History */}
              <RecentComparisons 
                tasks={recentTasks}
                onViewDetails={viewComparisonDetails}
                onDelete={deleteComparison}
              />

              {/* Error Alert */}
              {error && (
                <Alert variant="destructive" className="mt-4">
                  <XCircle className="h-4 w-4" />
                  <AlertDescription className="text-xs">{error}</AlertDescription>
                </Alert>
              )}
            </div>
          </aside>

          {/* Right Panel - Results (Flexible) */}
          <main className="flex-1 overflow-hidden flex flex-col bg-slate-50 dark:bg-slate-900">
            {result ? (
              <>
                {/* Results Header */}
                <div className="border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 px-6 py-3 flex-shrink-0">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <CheckCircle2 className="w-5 h-5 text-green-500" />
                      <div>
                        <h2 className="text-sm font-semibold text-slate-900 dark:text-slate-100">
                          Conversion Complete
                        </h2>
                        <p className="text-xs text-slate-500">
                          {result.library_used} • {result.format}
                          {chunkingResult && ` • ${chunkingResult.chunking?.total_chunks || 0} chunks`}
                        </p>
                      </div>
                    </div>
                    {chunkingResult ? (
                      <Button
                        onClick={() => setShowChunkResults(true)}
                        variant="outline"
                        size="sm"
                        className="gap-2 border-purple-300 text-purple-700 hover:bg-purple-50 dark:border-purple-700 dark:text-purple-400 dark:hover:bg-purple-950/30"
                      >
                        <Scissors className="w-4 h-4" />
                        View Chunks ({chunkingResult.chunking?.total_chunks || 0})
                      </Button>
                    ) : result.format !== 'json' && chunkers.length > 0 && (
                      <Button
                        onClick={() => handleChunkConvertedText()}
                        variant="outline"
                        size="sm"
                        className="gap-2"
                        disabled={isLoading}
                      >
                        <Scissors className="w-4 h-4" />
                        Chunk Text
                      </Button>
                    )}
                  </div>
                </div>

                {/* Results Content - Side by Side */}
                <div className="flex-1 grid grid-cols-2 gap-4 p-4 overflow-hidden">
                  {/* PDF Preview */}
                  <div className="flex flex-col bg-white dark:bg-slate-950 rounded-lg border border-slate-200 dark:border-slate-800 overflow-hidden">
                    <div className="px-4 py-2 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900">
                      <h3 className="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">
                        Original PDF
                      </h3>
                    </div>
                    <div className="flex-1 overflow-hidden">
                      {pdfUrl && (
                        <iframe
                          src={pdfUrl}
                          className="w-full h-full"
                          title="PDF Preview"
                        />
                      )}
                    </div>
                  </div>

                  {/* Converted Content */}
                  <div className="flex flex-col bg-white dark:bg-slate-950 rounded-lg border border-slate-200 dark:border-slate-800 overflow-hidden">
                    {outputFormat === 'json' ? (
                      <Tabs defaultValue="source" className="w-full h-full flex flex-col">
                        <div className="px-4 py-2 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 flex-shrink-0">
                          <TabsList className="h-8 w-full">
                            <TabsTrigger value="source" className="flex-1 text-xs">
                              Source
                            </TabsTrigger>
                            <TabsTrigger value="preview" className="flex-1 text-xs">
                              Preview
                            </TabsTrigger>
                          </TabsList>
                        </div>
                        <TabsContent value="source" className="flex-1 overflow-auto p-4 m-0">
                          <pre className="text-xs font-mono h-full">
                            {JSON.stringify(result.data || result.content, null, 2)}
                          </pre>
                        </TabsContent>
                        <TabsContent value="preview" className="flex-1 overflow-auto p-4 m-0">
                          <div className="text-xs font-mono h-full">
                            {JSON.stringify(result.data || result.content, null, 2)}
                          </div>
                        </TabsContent>
                      </Tabs>
                    ) : (
                      <Tabs defaultValue="source" className="w-full h-full flex flex-col">
                        <div className="px-4 py-2 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 flex-shrink-0">
                          <TabsList className="h-8 w-full">
                            <TabsTrigger value="source" className="flex-1 text-xs">
                              Source
                            </TabsTrigger>
                            <TabsTrigger value="preview" className="flex-1 text-xs">
                              Preview
                            </TabsTrigger>
                          </TabsList>
                        </div>
                        <TabsContent value="source" className="flex-1 overflow-auto p-4 m-0">
                          <pre className="text-xs font-mono h-full whitespace-pre-wrap">
                            {result.content || result.data}
                          </pre>
                        </TabsContent>
                        <TabsContent value="preview" className="flex-1 overflow-auto p-4 m-0">
                          <div
                            className="prose prose-sm max-w-none h-full prose-headings:mt-4 prose-headings:mb-2 prose-p:my-2"
                            dangerouslySetInnerHTML={renderMarkdownPreview(
                              result.content || result.data || ''
                            )}
                          />
                        </TabsContent>
                      </Tabs>
                    )}
                  </div>
                </div>
              </>
            ) : isLoading ? (
              <div className="flex-1 flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
                <div className="text-center space-y-8 max-w-md">
                  {/* Animated spinner */}
                  <div className="flex justify-center">
                    <div className="relative w-20 h-20">
                      <div className="absolute inset-0 rounded-full border-4 border-slate-200 dark:border-slate-700"></div>
                      <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-blue-500 dark:border-t-blue-400 animate-spin"></div>
                    </div>
                  </div>

                  {/* Status text */}
                  <div className="space-y-3">
                    <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                      Converting your PDF
                    </h3>
                    <p className="text-sm text-slate-600 dark:text-slate-400">
                      Using <span className="font-medium text-blue-600 dark:text-blue-400">{selectedLibrary}</span>
                    </p>
                  </div>

                  {/* Timer display */}
                  {timeTaken && (
                    <div className="space-y-2">
                      <div className="flex items-center justify-center gap-2">
                        <Clock className="w-5 h-5 text-blue-600 dark:text-blue-400 animate-pulse" />
                        <span className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                          {timeTaken}
                        </span>
                        <span className="text-sm text-slate-600 dark:text-slate-400">seconds</span>
                      </div>
                      
                      {/* Progress bar */}
                      <div className="space-y-1 mt-6">
                        <div className="text-xs text-slate-500 dark:text-slate-500">Processing...</div>
                        <div className="w-full h-1 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-gradient-to-r from-blue-500 to-blue-600 dark:from-blue-400 dark:to-blue-500 rounded-full animate-pulse"
                            style={{ width: '100%' }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Tips */}
                  <div className="pt-4 border-t border-slate-200 dark:border-slate-700">
                    <p className="text-xs text-slate-500 dark:text-slate-500">
                      💡 Larger files may take longer to process
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex-1 flex items-center justify-center">
                <div className="text-center space-y-6 max-w-md">
                  {/* Title */}
                  <div>
                    <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-100">
                      PDFStract
                    </h3>
                    <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                      The First tool in your AI RAG pipeline
                    </p>
                  </div>

                  {/* Steps */}
                  <div className="bg-slate-50 dark:bg-slate-800/50 rounded-xl p-5 text-left space-y-3">
                    <p className="text-xs font-medium text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-3">
                      How it works
                    </p>
                    {[
                      { num: 1, text: 'Upload your PDF file' },
                      { num: 2, text: 'Choose a conversion library' },
                      { num: 3, text: 'Select the output format' },
                      { num: 4, text: 'Pick a chunking method (optional)' },
                      { num: 5, text: 'Click Convert or Compare' },
                    ].map((step) => (
                      <div key={step.num} className="flex items-center gap-3">
                        <span className="flex-shrink-0 w-6 h-6 bg-blue-100 dark:bg-blue-900/50 text-blue-600 dark:text-blue-400 rounded-full flex items-center justify-center text-xs font-medium">
                          {step.num}
                        </span>
                        <span className="text-sm text-slate-600 dark:text-slate-300">
                          {step.text}
                        </span>
                      </div>
                    ))}
                  </div>

                  {/* GitHub Link */}
                  <a
                    href="https://github.com/pdfstract/pdfstract"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 text-sm text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200 transition-colors"
                  >
                    <Github className="w-4 h-4" />
                    <span>View on GitHub</span>
                  </a>
                </div>
              </div>
            )}
          </main>
        </div>
      </div>

      {/* Compare Modal */}
      <CompareModal
        isOpen={showCompareModal}
        onClose={() => setShowCompareModal(false)}
        libraries={libraries}
        onRun={handleCompareRun}
        isLoading={isComparingLoading}
      />

      {/* Comparison Results Modal */}
      {currentComparisonTask && (
        <ComparisonResults
          task={currentComparisonTask}
          comparisons={comparisonComparisons}
          onClose={() => {
            setCurrentComparisonTask(null)
            setComparisonComparisons([])
            if (comparisonProgressInterval.current) {
              clearInterval(comparisonProgressInterval.current)
            }
          }}
          onDownload={handleDownloadComparison}
        />
      )}

      {/* Chunk Results Modal */}
      {showChunkResults && chunkingResult && (
        <ChunkResults
          result={chunkingResult}
          pdfUrl={pdfUrl}
          onClose={() => setShowChunkResults(false)}
        />
      )}
    </div>
  )
}

export default App

