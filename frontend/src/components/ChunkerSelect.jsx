import { useState } from 'react'
import { ChevronDown, ChevronUp } from 'lucide-react'
import { Select } from './ui/select'

export function ChunkerSelect({ 
  chunkers, 
  selectedChunker, 
  onChunkerChange, 
  params, 
  onParamsChange,
  disabled 
}) {
  const [showParams, setShowParams] = useState(false)
  const selectedChunkerInfo = chunkers.find(c => c.name === selectedChunker)

  const handleParamChange = (paramName, value, paramType) => {
    let parsedValue = value
    if (paramType === 'integer' || paramType === 'number') {
      parsedValue = value === '' ? '' : parseInt(value, 10)
    }
    onParamsChange({
      ...params,
      [paramName]: parsedValue
    })
  }

  const renderParamInput = (paramName, paramSpec) => {
    const value = params[paramName] !== undefined ? params[paramName] : paramSpec.default
    
    if (paramSpec.enum) {
      return (
        <Select
          value={value}
          onChange={(e) => handleParamChange(paramName, e.target.value, paramSpec.type)}
          disabled={disabled}
          className="w-full h-8 text-xs"
        >
          {paramSpec.enum.map((opt) => (
            <option key={opt || 'default'} value={opt}>
              {opt || '(default)'}
            </option>
          ))}
        </Select>
      )
    }

    if (paramSpec.type === 'integer' || paramSpec.type === 'number') {
      return (
        <input
          type="number"
          value={value}
          onChange={(e) => handleParamChange(paramName, e.target.value, paramSpec.type)}
          min={paramSpec.minimum}
          max={paramSpec.maximum}
          disabled={disabled}
          className="w-full h-8 px-2 text-xs border border-slate-300 dark:border-slate-600 rounded-md bg-white dark:bg-slate-800 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      )
    }

    return (
      <input
        type="text"
        value={value}
        onChange={(e) => handleParamChange(paramName, e.target.value, paramSpec.type)}
        disabled={disabled}
        className="w-full h-8 px-2 text-xs border border-slate-300 dark:border-slate-600 rounded-md bg-white dark:bg-slate-800 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      />
    )
  }

  const schema = selectedChunkerInfo?.parameters || {}
  const hasParams = Object.keys(schema).length > 0

  return (
    <div className="space-y-2">
      {/* Chunker Selection - Simple dropdown like Output Format */}
      <label className="text-xs font-medium text-slate-700 dark:text-slate-300">
        Text Chunking (for RAG)
      </label>
      <Select
        value={selectedChunker}
        onChange={(e) => onChunkerChange(e.target.value)}
        disabled={disabled}
        className="w-full"
      >
        <option value="">None</option>
        {chunkers.filter(c => c.available).map((chunker) => (
          <option key={chunker.name} value={chunker.name}>
            {chunker.name.charAt(0).toUpperCase() + chunker.name.slice(1)}
          </option>
        ))}
      </Select>

      {/* Show params toggle when chunker is selected */}
      {selectedChunker && hasParams && (
        <div className="space-y-2">
          <button
            type="button"
            onClick={() => setShowParams(!showParams)}
            className="flex items-center gap-1 text-xs text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
          >
            {showParams ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
            {showParams ? 'Hide' : 'Show'} chunk settings
          </button>

          {showParams && (
            <div className="space-y-3 p-3 bg-slate-50 dark:bg-slate-800/50 rounded-md">
              {Object.entries(schema).map(([paramName, paramSpec]) => (
                <div key={paramName} className="space-y-1">
                  <label className="text-xs font-medium text-slate-600 dark:text-slate-400">
                    {paramName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </label>
                  {renderParamInput(paramName, paramSpec)}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default ChunkerSelect
