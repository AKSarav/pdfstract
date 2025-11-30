import { useState } from 'react'
import { ChevronDown, Trash2 } from 'lucide-react'

function formatTime(isoString) {
  if (!isoString) return 'unknown'
  const date = new Date(isoString)
  
  // Format as local time: "Jan 15, 2025 • 2:30 PM"
  const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
  const timeStr = date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true })
  return `${dateStr} • ${timeStr}`
}

export function RecentComparisons({ tasks, onViewDetails, onDelete }) {
  const [expanded, setExpanded] = useState(false)

  if (!tasks || tasks.length === 0) return null

  return (
    <div className="border-t border-slate-200 dark:border-slate-800 pt-4 mt-4">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-2 text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide hover:text-slate-900 dark:hover:text-slate-100 transition-colors"
      >
        📋 Recent Comparisons
        <ChevronDown 
          className={`w-3 h-3 transition-transform ${expanded ? 'rotate-180' : ''}`}
        />
      </button>

      {expanded && (
        <div className="mt-3 space-y-2 max-h-48 overflow-y-auto">
          {tasks.map(task => (
            <div
              key={task.task_id}
              className="p-2 rounded bg-slate-50 dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors group"
            >
              <div 
                className="cursor-pointer"
                onClick={() => onViewDetails(task.task_id)}
              >
                <div className="font-medium truncate text-slate-900 dark:text-slate-100 text-xs">
                  {task.filename}
                </div>
                <div className="text-slate-500 dark:text-slate-400 text-xs">
                  {task.libraries_count} models • {task.total_duration_seconds ? task.total_duration_seconds.toFixed(2) : '~'}s
                </div>
                <div className="text-slate-400 dark:text-slate-500 text-[10px]">
                  {formatTime(task.created_at)}
                </div>
              </div>
              
              <div className="flex gap-1 mt-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    onViewDetails(task.task_id)
                  }}
                  className="flex-1 text-[10px] px-2 py-1 rounded bg-blue-500/10 dark:bg-blue-500/20 text-blue-600 dark:text-blue-400 hover:bg-blue-500/20 dark:hover:bg-blue-500/30 transition-colors"
                >
                  View
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    if (confirm('Delete this comparison?')) {
                      onDelete(task.task_id)
                    }
                  }}
                  className="text-[10px] px-2 py-1 rounded bg-red-500/10 dark:bg-red-500/20 text-red-600 dark:text-red-400 hover:bg-red-500/20 dark:hover:bg-red-500/30 transition-colors"
                  title="Delete"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

