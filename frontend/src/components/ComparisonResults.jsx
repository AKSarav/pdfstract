import { useState } from 'react'
import { Download, Copy, X } from 'lucide-react'

export function ComparisonResults({ task, comparisons, onClose, onDownload }) {
  const [selectedContent, setSelectedContent] = useState(null)
  const [copied, setCopied] = useState(false)

  const handleCopy = (content) => {
    navigator.clipboard.writeText(content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  if (!task) return null

  const successComparisons = comparisons.filter(c => c.status === 'success')

  return (
    <>
      {/* Results Grid Modal */}
      {!selectedContent && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-slate-950 rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto border border-slate-200 dark:border-slate-800">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                  Comparison Results
                </h2>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  {task.filename || 'File'} • Total: {(task.total_duration_seconds || task.total_duration)?.toFixed(2)}s
                </p>
              </div>
              <button 
                onClick={onClose}
                className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Results Table */}
            <div className="overflow-x-auto mb-4">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-200 dark:border-slate-700">
                    <th className="text-left py-2 px-3 font-semibold text-slate-700 dark:text-slate-300">Library</th>
                    <th className="text-right py-2 px-3 font-semibold text-slate-700 dark:text-slate-300">Time</th>
                    <th className="text-right py-2 px-3 font-semibold text-slate-700 dark:text-slate-300">Size</th>
                    <th className="text-center py-2 px-3 font-semibold text-slate-700 dark:text-slate-300">Status</th>
                    <th className="text-center py-2 px-3 font-semibold text-slate-700 dark:text-slate-300">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {comparisons.map(comp => (
                    <tr 
                      key={comp.library_name}
                      className="border-b border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors cursor-pointer"
                    >
                      <td className="py-3 px-3 font-medium text-slate-900 dark:text-slate-100">
                        {comp.library_name}
                      </td>
                      <td className="py-3 px-3 text-right text-slate-600 dark:text-slate-400">
                        {comp.duration_seconds ? comp.duration_seconds.toFixed(2) : '~'}s
                      </td>
                      <td className="py-3 px-3 text-right text-slate-600 dark:text-slate-400">
                        {comp.output_size_bytes ? (comp.output_size_bytes / 1024).toFixed(1) : '~'} KB
                      </td>
                      <td className="py-3 px-3 text-center">
                        {comp.status === 'success' && (
                          <span className="inline-block px-2 py-1 rounded text-xs font-medium bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300">
                            ✓ Success
                          </span>
                        )}
                        {comp.status === 'failed' && (
                          <span className="inline-block px-2 py-1 rounded text-xs font-medium bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300">
                            ✗ Failed
                          </span>
                        )}
                        {comp.status === 'timeout' && (
                          <span className="inline-block px-2 py-1 rounded text-xs font-medium bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300">
                            ⏱ Timeout
                          </span>
                        )}
                      </td>
                      <td className="py-3 px-3 text-center">
                        {comp.status === 'success' && (
                          <button
                            onClick={() => setSelectedContent(comp)}
                            className="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium text-xs"
                          >
                            View
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2 pt-4 border-t border-slate-200 dark:border-slate-700">
              <button
                onClick={onClose}
                className="flex-1 px-4 py-2 rounded border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors text-sm font-medium"
              >
                Close
              </button>
              {successComparisons.length > 0 && (
                <button
                  onClick={() => onDownload(task.task_id, null)}
                  className="flex-1 px-4 py-2 rounded bg-blue-600 hover:bg-blue-700 text-white transition-colors text-sm font-medium flex items-center justify-center gap-2"
                >
                  <Download className="w-4 h-4" />
                  Download All
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Content Detail Modal */}
      {selectedContent && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-slate-950 rounded-lg p-6 max-w-4xl w-full mx-4 max-h-[80vh] overflow-y-auto border border-slate-200 dark:border-slate-800">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                  {selectedContent.library_name} - Results
                </h2>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  Duration: {selectedContent.duration_seconds?.toFixed(2)}s • Size: {(selectedContent.output_size_bytes / 1024).toFixed(1)} KB
                </p>
              </div>
              <button 
                onClick={() => setSelectedContent(null)}
                className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Content Display */}
            <div className="mb-4 p-4 rounded bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 max-h-96 overflow-y-auto">
              <pre className="text-xs font-mono text-slate-700 dark:text-slate-300 whitespace-pre-wrap break-words">
                {typeof selectedContent.content === 'string' 
                  ? selectedContent.content.slice(0, 5000) + (selectedContent.content.length > 5000 ? '...\n(truncated)' : '')
                  : JSON.stringify(selectedContent.content, null, 2).slice(0, 5000) + '...'
                }
              </pre>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2 pt-4 border-t border-slate-200 dark:border-slate-700">
              <button
                onClick={() => setSelectedContent(null)}
                className="flex-1 px-4 py-2 rounded border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors text-sm font-medium"
              >
                Back
              </button>
              <button
                onClick={() => handleCopy(typeof selectedContent.content === 'string' ? selectedContent.content : JSON.stringify(selectedContent.content, null, 2))}
                className="flex-1 px-4 py-2 rounded bg-slate-200 dark:bg-slate-800 hover:bg-slate-300 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 transition-colors text-sm font-medium flex items-center justify-center gap-2"
              >
                <Copy className="w-4 h-4" />
                {copied ? 'Copied!' : 'Copy'}
              </button>
              <button
                onClick={() => onDownload(task.task_id, selectedContent.library_name)}
                className="flex-1 px-4 py-2 rounded bg-blue-600 hover:bg-blue-700 text-white transition-colors text-sm font-medium flex items-center justify-center gap-2"
              >
                <Download className="w-4 h-4" />
                Download
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

