import React, { useState, useEffect } from 'react';
import { Database, ShieldCheck, ShieldAlert, Cpu, Sparkles, Loader2 } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Select } from './ui/select';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';

export function EmbeddingsPanel({ chunks, isLoading: parentLoading }) {
    const [providers, setProviders] = useState([]);
    const [selectedProvider, setSelectedProvider] = useState('auto');
    const [embeddings, setEmbeddings] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchProviders();
    }, []);

    const fetchProviders = async () => {
        try {
            const response = await fetch('/embeddings/providers');
            const data = await response.json();
            const rawProviders = data.providers || [];

            const autoOpt = {
                name: 'auto',
                available: true,
                configured: true,
                message: 'Automatically pick best available provider'
            };

            setProviders([autoOpt, ...rawProviders]);
        } catch (err) {
            console.error('Failed to fetch embedding providers:', err);
        }
    };

    const handleGenerateEmbeddings = async () => {
        if (!chunks || chunks.length === 0) return;

        setIsLoading(true);
        setError(null);
        setEmbeddings(null);

        try {
            // Get exact text content from chunks
            const texts = chunks.map(c => c.text);

            const response = await fetch('/embeddings/embed', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    texts: texts,
                    model: selectedProvider
                })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                setEmbeddings(data);
            } else {
                setError(data.detail || 'Embedding generation failed');
            }
        } catch (err) {
            setError('Failed to generate embeddings: ' + err.message);
        } finally {
            setIsLoading(false);
        }
    };

    if (!chunks || chunks.length === 0) {
        return null;
    }

    return (
        <Card className="mt-6 border-blue-100 dark:border-blue-900 shadow-sm overflow-hidden bg-white dark:bg-slate-950">
            <CardHeader className="bg-blue-50/50 dark:bg-blue-950/10 border-b border-blue-50 dark:border-blue-900/50">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <Database className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                        <div>
                            <CardTitle className="text-base">Vector Embeddings</CardTitle>
                            <CardDescription className="text-xs">Turn chunks into mathematical vectors for search</CardDescription>
                        </div>
                    </div>
                    <Badge variant="outline" className="bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 border-blue-200 dark:border-blue-800">
                        {chunks.length} Chunks
                    </Badge>
                </div>
            </CardHeader>
            <CardContent className="p-6">
                <div className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-end">
                        <div className="space-y-2">
                            <label className="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
                                Embedding Provider
                            </label>
                            <Select
                                value={selectedProvider}
                                onChange={(e) => setSelectedProvider(e.target.value)}
                                disabled={isLoading || parentLoading}
                                className="w-full"
                            >
                                {providers.map((p) => (
                                    <option key={p.name} value={p.name} disabled={!p.available}>
                                        {p.name.charAt(0).toUpperCase() + p.name.slice(1)}
                                        {!p.available ? ' (unavailable)' : (!p.configured ? ' (misconfigured)' : '')}
                                    </option>
                                ))}
                            </Select>
                        </div>
                        <Button
                            onClick={handleGenerateEmbeddings}
                            disabled={isLoading || parentLoading}
                            className="w-full bg-blue-600 hover:bg-blue-700 text-white shadow-md transition-all active:scale-[0.98]"
                        >
                            {isLoading ? (
                                <>
                                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                    Generating...
                                </>
                            ) : (
                                <>
                                    <Sparkles className="w-4 h-4 mr-2" />
                                    Generate Embeddings
                                </>
                            )}
                        </Button>
                    </div>

                    {error && (
                        <Alert variant="destructive" className="bg-red-50 dark:bg-red-950/20 border-red-100 dark:border-red-900/50 text-red-800 dark:text-red-400">
                            <ShieldAlert className="w-4 h-4" />
                            <AlertDescription className="text-xs ml-2">{error}</AlertDescription>
                        </Alert>
                    )}

                    {embeddings && (
                        <div className="space-y-3 animate-in fade-in slide-in-from-top-2 duration-500">
                            <div className="flex items-center gap-2 p-3 rounded-lg bg-green-50 dark:bg-green-950/20 border border-green-100 dark:border-green-900/50 text-green-800 dark:text-green-400">
                                <ShieldCheck className="w-4 h-4" />
                                <span className="text-xs font-medium">Successfully generated {embeddings.count} embeddings using {embeddings.model_used}</span>
                            </div>

                            <div className="rounded-lg border border-slate-200 dark:border-slate-800 overflow-hidden">
                                <div className="bg-slate-50 dark:bg-slate-900/50 px-3 py-2 border-b border-slate-200 dark:border-slate-800">
                                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-tighter">Vector Preview (Showing first 5 dimensions)</span>
                                </div>
                                <div className="p-0 overflow-x-auto">
                                    <table className="w-full text-xs text-left">
                                        <thead>
                                            <tr className="bg-slate-50/50 dark:bg-slate-900/20 border-b border-slate-100 dark:border-slate-900">
                                                <th className="px-3 py-2 font-semibold text-slate-600 dark:text-slate-400">Chunk</th>
                                                <th className="px-3 py-2 font-semibold text-slate-600 dark:text-slate-400">Preview (First 5 values)</th>
                                                <th className="px-3 py-2 font-semibold text-slate-600 dark:text-slate-400">Dimensions</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-slate-100 dark:divide-slate-900">
                                            {embeddings.embeddings.slice(0, 5).map((vec, i) => (
                                                <tr key={i} className="hover:bg-slate-50/30 dark:hover:bg-slate-900/10">
                                                    <td className="px-3 py-2 font-mono text-slate-500">#{i + 1}</td>
                                                    <td className="px-3 py-2 font-mono text-blue-600 dark:text-blue-400">
                                                        [{vec.slice(0, 5).map(v => v.toFixed(4)).join(', ')}...]
                                                    </td>
                                                    <td className="px-3 py-2">
                                                        <Badge variant="outline" className="text-[10px] h-4">{vec.length}d</Badge>
                                                    </td>
                                                </tr>
                                            ))}
                                            {embeddings.embeddings.length > 5 && (
                                                <tr>
                                                    <td colSpan="3" className="px-3 py-2 text-center text-[10px] text-slate-400 italic bg-slate-50/30 dark:bg-slate-900/5">
                                                        + {embeddings.embeddings.length - 5} more vectors
                                                    </td>
                                                </tr>
                                            )}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </CardContent>
        </Card>
    );
}
