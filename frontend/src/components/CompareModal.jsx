import { useState } from 'react'
import { Button } from './ui/button'
import { X } from 'lucide-react'

export function CompareModal({ isOpen, onClose, libraries, onRun, isLoading }) {
  const [selected, setSelected] = useState([])

  const toggleLibrary = (lib) => {
    if (selected.includes(lib)) {
      setSelected(selected.filter(l => l !== lib))
    } else if (selected.length < 3) {
      setSelected([...selected, lib])
    }
  }

  const handleRun = () => {
    if (selected.length > 0) {
      onRun(selected)
      setSelected([])
    }
  }

  if (!isOpen) return null

  const availableLibs = libraries.filter(lib => lib.available)

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-slate-950 rounded-lg p-6 max-w-md w-full mx-4 border border-slate-200 dark:border-slate-800">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
            Compare Models
          </h2>
          <button 
            onClick={onClose}
            disabled={isLoading}
            className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 disabled:opacity-50"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <p className="text-sm text-slate-600 dark:text-slate-400 mb-4">
          Select up to 3 libraries to compare (max 3 at once)
        </p>

        <div className="space-y-2 mb-6 max-h-64 overflow-y-auto">
          {availableLibs.length > 0 ? (
            availableLibs.map(lib => (
              <label 
                key={lib.name}
                className="flex items-center p-2 rounded hover:bg-slate-50 dark:hover:bg-slate-800 cursor-pointer transition-colors"
              >
                <input
                  type="checkbox"
                  checked={selected.includes(lib.name)}
                  onChange={() => toggleLibrary(lib.name)}
                  disabled={selected.length === 3 && !selected.includes(lib.name) || isLoading}
                  className="mr-3 w-4 h-4 cursor-pointer"
                />
                <span className="text-sm text-slate-700 dark:text-slate-300">
                  {lib.name}
                </span>
              </label>
            ))
          ) : (
            <p className="text-sm text-slate-500 italic">No available libraries</p>
          )}
        </div>

        <div className="flex gap-2">
          <Button 
            variant="outline" 
            onClick={onClose}
            disabled={isLoading}
            className="flex-1"
          >
            Cancel
          </Button>
          <Button 
            onClick={handleRun}
            disabled={selected.length === 0 || isLoading}
            className="flex-1"
          >
            {isLoading ? 'Comparing...' : `Compare (${selected.length})`}
          </Button>
        </div>
      </div>
    </div>
  )
}

