import React, { useState, useRef } from 'react'
import { Persona, api } from '../../../api/client'
import { Card, CardContent, CardHeader, CardTitle } from '../../ui/Card'
import { Button } from '../../ui/Button'
import { Input } from '../../ui/Input'
import { Badge } from '../../ui/Badge'
import {
  Database,
  Upload,
  ClipboardPaste,
  Shield,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  FileSpreadsheet,
  Download,
  RotateCcw,
  X,
  Info,
  HelpCircle,
  FileText,
  RefreshCw,
} from 'lucide-react'

export interface DataWorkspacePageProps {
  personas: Persona[]
  activeStudentId: string
  onSelectPersona: (personaId: string) => void
  onRefresh: () => void
}

export function DataWorkspacePage({
  personas,
  activeStudentId,
  onSelectPersona,
  onRefresh,
}: DataWorkspacePageProps) {
  const [activeTab, setActiveTab] = useState<'demo' | 'upload' | 'paste' | 'authorized'>('demo')

  // File Upload State
  const [fileContent, setFileContent] = useState<string>('')
  const [fileName, setFileName] = useState<string>('')
  const [fileSizeBytes, setFileSizeBytes] = useState<number>(0)
  const [isDragging, setIsDragging] = useState<boolean>(false)
  const [importStudentName, setImportStudentName] = useState<string>('Rinkesh')
  const [importDegreeProgram, setImportDegreeProgram] = useState<string>('B.Tech IT')
  const [filePreview, setFilePreview] = useState<any>(null)
  const [isValidatingFile, setIsValidatingFile] = useState<boolean>(false)
  const [isCommittingFile, setIsCommittingFile] = useState<boolean>(false)
  const [fileMessage, setFileMessage] = useState<string | null>(null)
  const [fileError, setFileError] = useState<string | null>(null)
  const [showRequirements, setShowRequirements] = useState<boolean>(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Paste State
  const [pasteText, setPasteText] = useState<string>(
    'Course Code / Name | Component | Present / Total | Percentage\nCEUE203 / OOP | LECT | 14 / 15 | 93.3%\nCSUC201 / FDSA | LAB | 7 / 11 | 63.6%'
  )
  const [pastePreview, setPastePreview] = useState<any>(null)
  const [isValidatingPaste, setIsValidatingPaste] = useState<boolean>(false)
  const [isCommittingPaste, setIsCommittingPaste] = useState<boolean>(false)
  const [pasteMessage, setPasteMessage] = useState<string | null>(null)

  // Authorized Stub State
  const [authStubResult, setAuthStubResult] = useState<any>(null)
  const [isTestingAuth, setIsTestingAuth] = useState<boolean>(false)

  // Reset State
  const [isResetting, setIsResetting] = useState<boolean>(false)

  // Process File Object
  const processFile = (file: File) => {
    if (!file) return
    setFileName(file.name)
    setFileSizeBytes(file.size)
    setFileError(null)
    setFileMessage(null)
    setFilePreview(null)

    const reader = new FileReader()
    reader.onload = async (event) => {
      const text = (event.target?.result as string) || ''
      setFileContent(text)
      handlePreviewFile(text)
    }
    reader.readAsText(file)
  }

  // Handle File Input Change
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) processFile(file)
  }

  // Clear Selected File
  const handleClearFile = () => {
    setFileName('')
    setFileContent('')
    setFileSizeBytes(0)
    setFilePreview(null)
    setFileError(null)
    setFileMessage(null)
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  // Preview File Upload
  const handlePreviewFile = async (content = fileContent) => {
    if (!importStudentName.trim()) {
      setFileError('Please specify the Student Full Name before validating.')
      return
    }
    if (!importDegreeProgram.trim()) {
      setFileError('Please specify the Degree Program before validating.')
      return
    }
    setIsValidatingFile(true)
    setFileError(null)
    setFileMessage(null)
    try {
      const res = await api.previewFile({
        content,
        student_name: importStudentName.trim(),
        program: importDegreeProgram.trim(),
      })
      setFilePreview(res)
      if (!res.valid && res.errors?.length) {
        setFileError(`Validation issue detected: ${res.errors.join('; ')}`)
      }
    } catch (err: any) {
      let friendlyMsg = err.message || 'Data validation failed'
      if (friendlyMsg.includes('500')) {
        friendlyMsg = 'The server reported a data-processing error while parsing this file. Please verify CSV columns and data types.'
      } else if (friendlyMsg.includes('400') || friendlyMsg.includes('422')) {
        friendlyMsg = friendlyMsg.replace(/^Validation error:\s*/i, '')
      }
      setFileError(friendlyMsg)
    } finally {
      setIsValidatingFile(false)
    }
  }

  // Commit File Upload
  const handleCommitFile = async () => {
    if (!filePreview?.valid) return
    setIsCommittingFile(true)
    setFileError(null)
    try {
      const res = await api.commitFile({
        content: fileContent,
        student_name: importStudentName.trim(),
        program: importDegreeProgram.trim(),
        semester: 3,
        academic_year: '2026-27',
      })
      setFileMessage(`✓ Imported ${res.recordsCount} records cleanly! Switched to active profile: ${res.studentName}`)
      onSelectPersona(res.studentId)
      onRefresh()
    } catch (err: any) {
      setFileError(`Import commit error: ${err.message}`)
    } finally {
      setIsCommittingFile(false)
    }
  }

  // Preview Paste
  const handlePreviewPaste = async () => {
    if (!pasteText.trim()) return
    setIsValidatingPaste(true)
    setPasteMessage(null)
    try {
      const res = await api.previewPaste({
        text: pasteText,
        student_id: activeStudentId,
      })
      setPastePreview(res)
    } catch (err: any) {
      setPasteMessage(`Parse error: ${err.message}`)
    } finally {
      setIsValidatingPaste(false)
    }
  }

  // Commit Paste
  const handleCommitPaste = async () => {
    if (!pastePreview?.valid) return
    setIsCommittingPaste(true)
    try {
      const res = await api.commitPaste({
        text: pasteText,
        student_id: activeStudentId,
      })
      setPasteMessage(`✓ Committed ${res.recordsCommitted} attendance records to active profile!`)
      onRefresh()
    } catch (err: any) {
      setPasteMessage(`Commit error: ${err.message}`)
    } finally {
      setIsCommittingPaste(false)
    }
  }

  // Test Authorized Stub
  const handleTestAuthorized = async () => {
    setIsTestingAuth(true)
    try {
      const res = await api.testAuthorizedConnector()
      setAuthStubResult(res)
    } catch (err: any) {
      setAuthStubResult({ error: err.message })
    } finally {
      setIsTestingAuth(false)
    }
  }

  // Reset Workspace
  const handleResetWorkspace = async () => {
    if (!confirm('Reset all demo personas to factory seed scenarios?')) return
    setIsResetting(true)
    try {
      await api.resetWorkspace('student_synth_strong')
      onSelectPersona('student_synth_strong')
      onRefresh()
      alert('Workspace reset to baseline scenarios successfully.')
    } catch (err: any) {
      alert(`Reset error: ${err.message}`)
    } finally {
      setIsResetting(false)
    }
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* 1. Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200/90 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-sm">
              <Database className="w-5 h-5" />
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900">
              Connect Academic Data
            </h1>
          </div>
          <p className="text-sm text-slate-500 mt-1">
            Manage student records: select synthetic demo archetypes, upload local spreadsheets, or review institutional connectors.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleResetWorkspace}
            isLoading={isResetting}
            className="text-xs text-slate-600 border-slate-300 h-8 gap-1.5"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset Demo Scenarios</span>
          </Button>
        </div>
      </div>

      {/* Security Banner */}
      <div className="p-4 rounded-xl border border-blue-200 bg-blue-50/80 text-blue-900 text-xs sm:text-sm flex items-start gap-3 shadow-2xs">
        <Shield className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
        <div className="leading-relaxed">
          <strong className="font-semibold">Security & Integrity Notice:</strong> EduPulse never asks for, accepts, or stores university passwords, session tokens, or CAPTCHAs. All intelligence runs exclusively on self-supplied files, synthetic archetypes, or university-authorized sandboxes. Live unauthorized campus portal scraping is strictly prohibited.
        </div>
      </div>

      {/* 2. Tabs */}
      <div className="flex rounded-lg bg-slate-100 p-1 border border-slate-200 w-full overflow-x-auto">
        <button
          onClick={() => setActiveTab('demo')}
          className={`flex-1 min-w-[130px] py-2 text-xs font-semibold rounded-md transition-all cursor-pointer flex items-center justify-center gap-1.5 ${
            activeTab === 'demo' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          <Sparkles className="w-3.5 h-3.5 text-blue-600" />
          <span>Use Demo Data</span>
        </button>

        <button
          onClick={() => setActiveTab('upload')}
          className={`flex-1 min-w-[140px] py-2 text-xs font-semibold rounded-md transition-all cursor-pointer flex items-center justify-center gap-1.5 ${
            activeTab === 'upload' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          <Upload className="w-3.5 h-3.5 text-emerald-600" />
          <span>Upload Academic CSV</span>
        </button>

        <button
          onClick={() => setActiveTab('paste')}
          className={`flex-1 min-w-[130px] py-2 text-xs font-semibold rounded-md transition-all cursor-pointer flex items-center justify-center gap-1.5 ${
            activeTab === 'paste' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          <ClipboardPaste className="w-3.5 h-3.5 text-amber-600" />
          <span>Paste Data</span>
        </button>

        <button
          onClick={() => setActiveTab('authorized')}
          className={`flex-1 min-w-[160px] py-2 text-xs font-semibold rounded-md transition-all cursor-pointer flex items-center justify-center gap-1.5 ${
            activeTab === 'authorized' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          <Shield className="w-3.5 h-3.5 text-purple-600" />
          <span>Connect Authorized Provider</span>
        </button>
      </div>

      {/* ------------------------------------------------------------- */}
      {/* TAB 1: Use Demo Data (Personas) */}
      {/* ------------------------------------------------------------- */}
      {activeTab === 'demo' && (
        <div className="space-y-4">
          <div>
            <h3 className="text-base font-bold text-slate-900">Synthetic Student Archetypes</h3>
            <p className="text-xs text-slate-500">
              Select from varied synthetic student personas to test analytics across different academic scenarios:
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {personas.map((p) => {
              const isActive = p.id === activeStudentId
              return (
                <Card
                  key={p.id}
                  className={`bg-white border transition-all ${
                    isActive
                      ? 'border-blue-500 ring-2 ring-blue-500/20 shadow-xs'
                      : 'border-slate-200/90 hover:border-slate-300'
                  }`}
                >
                  <CardContent className="p-5 flex flex-col justify-between h-full space-y-3">
                    <div className="space-y-1.5">
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <h4 className="font-bold text-sm text-slate-900">
                            {p.name} <span className="text-slate-400 font-normal">({p.external_id})</span>
                          </h4>
                          <span className="text-xs text-slate-500">
                            {p.program} • Semester {p.semester}
                          </span>
                        </div>
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
                          {p.archetype}
                        </span>
                      </div>

                      <p className="text-xs text-slate-600 leading-relaxed pt-1">{p.description}</p>
                    </div>

                    <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                      <span className="text-[11px] text-slate-500">
                        Status: <strong className="text-slate-700">{p.academic_status}</strong>
                      </span>
                      <Button
                        variant={isActive ? 'secondary' : 'primary'}
                        size="sm"
                        onClick={() => onSelectPersona(p.id)}
                        className="text-xs font-semibold h-8 px-4"
                      >
                        {isActive ? 'Active Profile ✓' : 'Load Profile'}
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------- */}
      {/* TAB 2: Import Academic Data (CSV / JSON) */}
      {/* ------------------------------------------------------------- */}
      {activeTab === 'upload' && (
        <div className="space-y-6">
          <Card className="border-slate-200/90 bg-white shadow-xs">
            <CardHeader className="p-5 pb-3 border-b border-slate-100 flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-sm font-bold uppercase tracking-wider text-slate-900 flex items-center gap-2">
                  <FileSpreadsheet className="w-4 h-4 text-emerald-600" />
                  Upload Academic CSV
                </CardTitle>
                <p className="text-xs text-slate-500 mt-0.5">
                  Self-supplied CSV files exported from your student view. Verified locally before analysis.
                </p>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowRequirements(!showRequirements)}
                className="text-xs font-semibold h-8 flex items-center gap-1.5"
              >
                <HelpCircle className="w-3.5 h-3.5 text-blue-600" />
                <span>{showRequirements ? 'Hide Requirements' : 'View Requirements'}</span>
              </Button>
            </CardHeader>

            <CardContent className="p-5 space-y-4">
              {/* Requirements & Template Downloads Drawer */}
              {showRequirements && (
                <div className="p-4 rounded-xl border border-blue-200 bg-blue-50/70 text-blue-950 text-xs space-y-3">
                  <div className="flex items-center gap-2 font-bold text-blue-900">
                    <Info className="w-4 h-4 text-blue-600" />
                    <span>CSV Specification & Requirements</span>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
                    <div className="bg-white p-3 rounded-lg border border-blue-100 shadow-2xs space-y-1.5">
                      <div className="font-bold text-slate-800 flex items-center justify-between">
                        <span>Attendance Summary CSV</span>
                        <a
                          href={api.getTemplateUrl('attendance')}
                          download
                          className="text-[11px] text-blue-600 hover:text-blue-700 underline font-medium flex items-center gap-1"
                        >
                          <Download className="w-3 h-3" /> Template
                        </a>
                      </div>
                      <p className="text-slate-600 text-[11px]">
                        Required columns: <code className="bg-slate-100 px-1 py-0.5 rounded text-slate-800">course_code</code>,{' '}
                        <code className="bg-slate-100 px-1 py-0.5 rounded text-slate-800">component</code> (LECT, LAB, OTHER),{' '}
                        <code className="bg-slate-100 px-1 py-0.5 rounded text-slate-800">present_count</code>,{' '}
                        <code className="bg-slate-100 px-1 py-0.5 rounded text-slate-800">total_count</code>.
                      </p>
                    </div>

                    <div className="bg-white p-3 rounded-lg border border-blue-100 shadow-2xs space-y-1.5">
                      <div className="font-bold text-slate-800 flex items-center justify-between">
                        <span>Academic Marks CSV</span>
                        <a
                          href={api.getTemplateUrl('marks')}
                          download
                          className="text-[11px] text-blue-600 hover:text-blue-700 underline font-medium flex items-center gap-1"
                        >
                          <Download className="w-3 h-3" /> Template
                        </a>
                      </div>
                      <p className="text-slate-600 text-[11px]">
                        Required columns: <code className="bg-slate-100 px-1 py-0.5 rounded text-slate-800">course_code</code>,{' '}
                        <code className="bg-slate-100 px-1 py-0.5 rounded text-slate-800">assessment_type</code>,{' '}
                        <code className="bg-slate-100 px-1 py-0.5 rounded text-slate-800">obtained_marks</code>,{' '}
                        <code className="bg-slate-100 px-1 py-0.5 rounded text-slate-800">total_marks</code>.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Form Metadata */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">
                    Student Full Name <span className="text-rose-500">*</span>
                  </label>
                  <Input
                    value={importStudentName}
                    onChange={(e) => {
                      setImportStudentName(e.target.value)
                      if (fileContent) handlePreviewFile(fileContent)
                    }}
                    placeholder="e.g. Rinkesh"
                    className="text-xs"
                  />
                  {!importStudentName.trim() && (
                    <span className="text-[11px] text-rose-500 mt-1 block">Full name is required</span>
                  )}
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">
                    Degree Program <span className="text-rose-500">*</span>
                  </label>
                  <Input
                    value={importDegreeProgram}
                    onChange={(e) => {
                      setImportDegreeProgram(e.target.value)
                      if (fileContent) handlePreviewFile(fileContent)
                    }}
                    placeholder="e.g. B.Tech IT"
                    className="text-xs"
                  />
                  {!importDegreeProgram.trim() && (
                    <span className="text-[11px] text-rose-500 mt-1 block">Degree program is required</span>
                  )}
                </div>
              </div>

              {/* Drag & Drop Upload Zone */}
              {!fileName ? (
                <div
                  onDragOver={(e) => {
                    e.preventDefault()
                    setIsDragging(true)
                  }}
                  onDragLeave={() => setIsDragging(false)}
                  onDrop={(e) => {
                    e.preventDefault()
                    setIsDragging(false)
                    const file = e.dataTransfer.files?.[0]
                    if (file) processFile(file)
                  }}
                  className={`border-2 border-dashed rounded-xl p-8 text-center transition-all cursor-pointer ${
                    isDragging
                      ? 'border-blue-500 bg-blue-50/70 scale-[0.99]'
                      : 'border-slate-300 hover:border-blue-400 bg-slate-50/50'
                  }`}
                  onClick={() => fileInputRef.current?.click()}
                >
                  <Upload className={`w-9 h-9 mx-auto mb-2 transition-colors ${isDragging ? 'text-blue-600' : 'text-slate-400'}`} />
                  <div className="text-xs font-bold text-blue-600 hover:text-blue-700 block mb-1">
                    Drag and drop your CSV file here, or browse
                  </div>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".csv"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                  <p className="text-[11px] text-slate-400 max-w-md mx-auto">
                    Supports standard attendance export (CEUE203, LECT, 14, 15) and marks/evaluation tabular records
                  </p>
                </div>
              ) : (
                /* Selected File Metadata Card */
                <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/80 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center shrink-0">
                      <FileSpreadsheet className="w-5 h-5" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-slate-900">{fileName}</span>
                        {filePreview?.importType && (
                          <Badge variant="low" className="text-[9px] uppercase">
                            {filePreview.importType} CSV
                          </Badge>
                        )}
                      </div>
                      <span className="text-[11px] text-slate-500">
                        {(fileSizeBytes / 1024).toFixed(1)} KB • Local Verified
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 w-full sm:w-auto justify-end">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handlePreviewFile(fileContent)}
                      isLoading={isValidatingFile}
                      className="text-xs font-semibold h-8"
                    >
                      <RefreshCw className="w-3.5 h-3.5 mr-1" /> Re-validate
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleClearFile}
                      className="text-xs text-rose-600 hover:text-rose-700 hover:bg-rose-50 h-8"
                    >
                      <X className="w-3.5 h-3.5 mr-1" /> Clear
                    </Button>
                  </div>
                </div>
              )}

              {/* Validation Progress Spinner */}
              {isValidatingFile && (
                <div className="p-4 rounded-xl border border-blue-200 bg-blue-50/60 text-blue-900 flex items-center gap-3 text-xs">
                  <RefreshCw className="w-4 h-4 animate-spin text-blue-600" />
                  <span>Validating CSV structure, course codes, and numeric counts...</span>
                </div>
              )}

              {/* Actionable Error State Card */}
              {fileError && (
                <div className="p-4 rounded-xl border border-rose-300 bg-rose-50/90 text-rose-950 space-y-3">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-2 font-bold text-rose-900 text-xs sm:text-sm">
                      <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0" />
                      <span>We couldn't validate this file.</span>
                    </div>
                  </div>

                  <div className="text-xs text-rose-800 leading-relaxed pl-6 space-y-1">
                    <p>The server reported a data-processing issue with this file:</p>
                    {filePreview?.errors?.length ? (
                      <ul className="list-disc pl-4 space-y-0.5 text-rose-900 font-medium pt-1">
                        {filePreview.errors.map((err: string, i: number) => (
                          <li key={i}>{err}</li>
                        ))}
                      </ul>
                    ) : (
                      <p className="font-semibold">{fileError}</p>
                    )}
                    <p className="text-[11px] text-rose-700 pt-1">
                      Check the CSV format and required columns, then try again.
                    </p>
                  </div>

                  <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-rose-200 pl-6">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handlePreviewFile(fileContent)}
                      className="text-xs font-semibold h-8 bg-white hover:bg-rose-100/50 text-rose-900 border-rose-300"
                    >
                      Try Again
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setShowRequirements(true)}
                      className="text-xs font-semibold h-8 bg-white hover:bg-slate-100 text-slate-800"
                    >
                      View Requirements
                    </Button>
                    <a
                      href={api.getTemplateUrl('attendance')}
                      download
                      className="text-xs text-blue-700 underline font-semibold ml-auto flex items-center gap-1"
                    >
                      <Download className="w-3.5 h-3.5" /> Download Sample CSV
                    </a>
                  </div>
                </div>
              )}

              {/* Validation & Preview Output (Success) */}
              {filePreview?.valid && (
                <div className="p-4 rounded-xl border border-slate-200 bg-slate-50 space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                      <span className="text-xs font-bold text-slate-800">Validation Status</span>
                    </div>
                    <Badge variant="low" className="text-[10px]">
                      Valid Batch ({filePreview.rowCount} Rows)
                    </Badge>
                  </div>

                  {/* Clean Records Table Preview */}
                  <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-200">
                        <tr>
                          <th className="py-2 px-3">Course Code</th>
                          <th className="py-2 px-3">Component / Type</th>
                          <th className="py-2 px-3 text-right">Present / Obtained</th>
                          <th className="py-2 px-3 text-right">Total</th>
                          <th className="py-2 px-3 text-right">Calculated %</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {filePreview.records.slice(0, 5).map((r: any, idx: number) => (
                          <tr key={idx} className="hover:bg-slate-50/70">
                            <td className="py-2 px-3 font-semibold text-slate-900">{r.courseId}</td>
                            <td className="py-2 px-3 text-slate-600">{r.component}</td>
                            <td className="py-2 px-3 text-right text-slate-800 font-medium">{r.presentCount}</td>
                            <td className="py-2 px-3 text-right text-slate-600">{r.totalCount}</td>
                            <td className="py-2 px-3 text-right font-bold text-slate-900">
                              {r.percentage !== null ? `${r.percentage}%` : 'N/A'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    {filePreview.records.length > 5 && (
                      <div className="py-1.5 px-3 bg-slate-50 text-[11px] text-slate-500 text-center border-t border-slate-100">
                        Showing 5 of {filePreview.records.length} records in this batch
                      </div>
                    )}
                  </div>

                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-1">
                    <div className="text-[11px] text-slate-500">
                      Checksum: <code className="bg-slate-200 px-1 py-0.5 rounded text-slate-700">{filePreview.checksum}</code>
                    </div>
                    <Button
                      variant="primary"
                      size="sm"
                      isLoading={isCommittingFile}
                      onClick={handleCommitFile}
                      className="text-xs font-semibold h-9 px-6"
                    >
                      Confirm and Commit Import
                    </Button>
                  </div>
                </div>
              )}

              {/* Commit Success Confirmation */}
              {fileMessage && (
                <div className="text-xs p-3 rounded-xl bg-emerald-50 text-emerald-900 border border-emerald-300 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span>{fileMessage}</span>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* ------------------------------------------------------------- */}
      {/* TAB 3: Paste Academic Data */}
      {/* ------------------------------------------------------------- */}
      {activeTab === 'paste' && (
        <Card className="border-slate-200/90 bg-white shadow-xs">
          <CardHeader className="p-5 pb-3 border-b border-slate-100">
            <CardTitle className="text-sm font-bold uppercase tracking-wider text-slate-900 flex items-center gap-2">
              <ClipboardPaste className="w-4 h-4 text-amber-600" />
              Paste Academic Records
            </CardTitle>
            <p className="text-xs text-slate-500">
              Copy attendance or marks rows directly from your portal screen and parse them cleanly.
            </p>
          </CardHeader>
          <CardContent className="p-5 space-y-4">
            <textarea
              rows={5}
              value={pasteText}
              onChange={(e) => setPasteText(e.target.value)}
              className="w-full rounded-lg border border-slate-300 p-3 text-xs font-mono text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Course Code / Name | Component | Present / Total | Percentage..."
            />

            <div className="flex gap-3">
              <Button
                variant="outline"
                size="sm"
                isLoading={isValidatingPaste}
                onClick={handlePreviewPaste}
                className="text-xs font-semibold h-8"
              >
                Preview Pasted Data
              </Button>
            </div>

            {pastePreview && (
              <div className="p-4 rounded-xl border border-slate-200 bg-slate-50 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-800">Parsed Preview</span>
                  {pastePreview.valid ? (
                    <Badge variant="low" className="text-[10px]">
                      Parsed {pastePreview.rowCount} records cleanly
                    </Badge>
                  ) : (
                    <Badge variant="high" className="text-[10px]">
                      Parsing Errors Detected
                    </Badge>
                  )}
                </div>

                {pastePreview.valid ? (
                  <Button
                    variant="primary"
                    size="sm"
                    isLoading={isCommittingPaste}
                    onClick={handleCommitPaste}
                    className="w-full text-xs font-semibold h-8"
                  >
                    Commit Pasted Attendance
                  </Button>
                ) : (
                  <div className="text-xs text-rose-700 space-y-1">
                    {pastePreview.errors?.map((err: string, i: number) => (
                      <div key={i}>• {err}</div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {pasteMessage && (
              <div className="text-xs p-3 rounded-lg bg-emerald-50 text-emerald-800 border border-emerald-200">
                {pasteMessage}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* ------------------------------------------------------------- */}
      {/* TAB 4: Authorized Academic Provider */}
      {/* ------------------------------------------------------------- */}
      {activeTab === 'authorized' && (
        <Card className="border-slate-200/90 bg-white shadow-xs">
          <CardHeader className="p-5 pb-3 border-b border-slate-100">
            <CardTitle className="text-sm font-bold uppercase tracking-wider text-slate-900 flex items-center gap-2">
              <Shield className="w-4 h-4 text-purple-600" />
              Authorized Institutional Connector
            </CardTitle>
          </CardHeader>
          <CardContent className="p-5 space-y-4">
            <div className="p-4 rounded-xl border border-amber-200 bg-amber-50/70 text-amber-950 text-xs sm:text-sm space-y-2">
              <div className="flex items-center gap-2 font-bold text-amber-900">
                <AlertTriangle className="w-4 h-4 text-amber-600" />
                Live university synchronization requires an authorized institutional integration.
              </div>
              <p className="text-xs text-amber-800 leading-relaxed">
                EduPulse does not claim live connection to CHARUSAT or any other institution. Direct integration with a live university Student Information System (SIS) strictly requires:
              </p>
              <ul className="list-disc pl-5 space-y-1 text-xs text-amber-900">
                <li>Institutional SSO / OAuth 2.0 (SAML 2.0 or OIDC sanctioned by university administration)</li>
                <li>Read-Only API Scopes restricted to official attendance and evaluation endpoints</li>
                <li>Zero Credential Retention: User passwords, OTPs, or CAPTCHAs are never accepted or stored</li>
                <li>No Scraping Compliance: Live campus portal scraping without institutional authorization is strictly prohibited</li>
              </ul>
            </div>

            <div className="pt-2">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
                Security Boundary Verification
              </h4>
              <p className="text-xs text-slate-500 mb-3">
                Invoke the production connector stub to verify that unauthorized connections are cleanly rejected with a <code>NotAuthorizedError</code>:
              </p>
              <Button
                variant="outline"
                size="sm"
                isLoading={isTestingAuth}
                onClick={handleTestAuthorized}
                className="text-xs font-semibold h-8"
              >
                Invoke AuthorizedCharusatProvider() Stub
              </Button>
            </div>

            {authStubResult && (
              <div className="p-4 rounded-xl border border-blue-200 bg-blue-50/70 text-blue-900 text-xs space-y-1.5">
                <div className="flex items-center gap-2 font-bold">
                  <CheckCircle2 className="w-4 h-4 text-blue-600" />
                  <span>Security Boundary Verified: {authStubResult.error_type}</span>
                </div>
                <p className="text-xs text-blue-800">{authStubResult.explanation}</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
