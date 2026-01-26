import { useState } from 'react'
import { Download, Copy, Check, ChevronLeft, ChevronRight, Scissors, FileJson, List, X } from 'lucide-react'
import { Button } from './ui/button'
import { Badge } from './ui/badge'

export function ChunkResults({ result, pdfUrl, onClose }) {
  const [currentChunkIndex, setCurrentChunkIndex] = useState(0)
  const [copiedIndex, setCopiedIndex] = useState(null)
  
  if (!result || !result.chunking) return null
  
  const { chunking, conversion } = result
  const { chunks, total_chunks, total_tokens, original_length, chunker_name, parameters } = chunking
  
  const currentChunk = chunks[currentChunkIndex]
  
  const handleCopyChunk = async (index) => {
    const chunk = chunks[index]
    await navigator.clipboard.writeText(chunk.text)
    setCopiedIndex(index)
    setTimeout(() => setCopiedIndex(null), 2000)
  }
  
  const handleDownloadChunks = () => {
    const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `chunks_${chunker_name}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }
  
  const handlePrevChunk = () => {
    setCurrentChunkIndex(prev => Math.max(0, prev - 1))
  }
  
  const handleNextChunk = () => {
    setCurrentChunkIndex(prev => Math.min(total_chunks - 1, prev + 1))
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-slate-900 rounded-xl shadow-2xl w-[95vw] h-[90vh] flex flex-col">
        {/* Header */}
        <div className="border-b border-slate-200 dark:border-slate-800 px-6 py-4 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
              <Scissors className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                Document Chunks
              </h2>
              <p className="text-xs text-slate-500">
                {chunker_name} • {total_chunks} chunks • {total_tokens.toLocaleString()} tokens
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button onClick={handleDownloadChunks} variant="outline" size="sm" className="gap-2">
              <Download className="w-4 h-4" />
              Export JSON
            </Button>
            <Button onClick={onClose} variant="ghost" size="icon">
              <X className="w-5 h-5" />
            </Button>
          </div>
        </div>

        {/* Main Content - Document Left, Chunks Right */}
        <div className="flex-1 flex overflow-hidden">
          {/* Left Panel - Original Document */}
          <div className="w-1/2 border-r border-slate-200 dark:border-slate-800 flex flex-col">
            <div className="px-4 py-2 bg-slate-50 dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 flex-shrink-0">
              <h3 className="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">
                Original Document
              </h3>
            </div>
            <div className="flex-1 overflow-hidden">
              {pdfUrl ? (
                <iframe
                  src={pdfUrl}
                  className="w-full h-full"
                  title="PDF Preview"
                />
              ) : conversion?.content ? (
                <div className="h-full overflow-auto p-4">
                  <pre className="text-sm font-mono whitespace-pre-wrap text-slate-700 dark:text-slate-300">
                    {conversion.content}
                  </pre>
                </div>
              ) : (
                <div className="flex items-center justify-center h-full text-slate-400">
                  <p>Document preview not available</p>
                </div>
              )}
            </div>
          </div>

          {/* Right Panel - Chunks */}
          <div className="w-1/2 flex flex-col">
            {/* Stats Bar */}
            <div className="px-4 py-2 bg-slate-50 dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 flex-shrink-0">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">
                  Chunks ({total_chunks})
                </h3>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-slate-500">
                    Avg: {Math.round(original_length / total_chunks).toLocaleString()} chars
                  </span>
                  {parameters.chunk_size && (
                    <Badge variant="outline" className="text-[10px]">
                      Size: {parameters.chunk_size}
                    </Badge>
                  )}
                </div>
              </div>
            </div>

            {/* Chunks Content */}
            <div className="flex-1 flex overflow-hidden">
              {/* Chunk List */}
              <div className="w-48 border-r border-slate-200 dark:border-slate-800 overflow-y-auto flex-shrink-0 bg-slate-50/50 dark:bg-slate-800/30">
                <div className="p-2 space-y-1">
                  {chunks.map((chunk, index) => (
                    <button
                      key={index}
                      onClick={() => setCurrentChunkIndex(index)}
                      className={`w-full text-left p-2 rounded-md text-xs transition-colors ${
                        currentChunkIndex === index
                          ? 'bg-purple-100 dark:bg-purple-900/30 border border-purple-300 dark:border-purple-700'
                          : 'hover:bg-slate-100 dark:hover:bg-slate-800 border border-transparent'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-medium text-slate-700 dark:text-slate-300">
                          #{index + 1}
                        </span>
                        <span className="text-[10px] text-slate-500">
                          {chunk.token_count}t
                        </span>
                      </div>
                      <p className="text-[10px] text-slate-500 dark:text-slate-400 line-clamp-2">
                        {chunk.text.slice(0, 60)}...
                      </p>
                    </button>
                  ))}
                </div>
              </div>

              {/* Chunk Detail */}
              <div className="flex-1 flex flex-col overflow-hidden">
                {/* Chunk Navigation */}
                <div className="px-4 py-2 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between flex-shrink-0">
                  <div className="flex items-center gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={handlePrevChunk}
                      disabled={currentChunkIndex === 0}
                    >
                      <ChevronLeft className="w-4 h-4" />
                    </Button>
                    <span className="text-sm font-medium">
                      Chunk {currentChunkIndex + 1} / {total_chunks}
                    </span>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={handleNextChunk}
                      disabled={currentChunkIndex === total_chunks - 1}
                    >
                      <ChevronRight className="w-4 h-4" />
                    </Button>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleCopyChunk(currentChunkIndex)}
                    className="gap-2"
                  >
                    {copiedIndex === currentChunkIndex ? (
                      <>
                        <Check className="w-4 h-4 text-green-500" />
                        Copied
                      </>
                    ) : (
                      <>
                        <Copy className="w-4 h-4" />
                        Copy
                      </>
                    )}
                  </Button>
                </div>

                {/* Chunk Metadata */}
                <div className="px-4 py-2 bg-purple-50 dark:bg-purple-900/20 border-b border-slate-200 dark:border-slate-800 flex-shrink-0">
                  <div className="flex items-center gap-4 text-xs text-slate-600 dark:text-slate-400">
                    <span>
                      <strong>{currentChunk.token_count}</strong> tokens
                    </span>
                    <span>
                      <strong>{currentChunk.text.length.toLocaleString()}</strong> chars
                    </span>
                    <span className="text-slate-400">
                      pos: {currentChunk.start_index} - {currentChunk.end_index}
                    </span>
                  </div>
                </div>

                {/* Chunk Content */}
                <div className="flex-1 overflow-auto p-4">
                  <pre className="text-sm font-mono whitespace-pre-wrap text-slate-800 dark:text-slate-200 leading-relaxed">
                    {currentChunk.text}
                  </pre>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ChunkResults
