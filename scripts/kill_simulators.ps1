# Kill simulator-related python processes safely
try {
    Get-CimInstance Win32_Process |
      Where-Object { ($_.Name -match 'python') -and ($_.CommandLine -match 'fake.py|mission_planner|simulator.py|mission_planner_simulation.py') } |
      ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
} catch {
    # ignore errors (e.g., insufficient privileges)
}
