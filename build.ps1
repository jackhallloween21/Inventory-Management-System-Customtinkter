# build.ps1 — Build a standalone single-file Windows executable
# Run from the project root:  .\build.ps1

$ErrorActionPreference = "Stop"

# Locate customtkinter's asset directory so PyInstaller bundles it too
$ctk_path = python -c "import customtkinter, os; print(os.path.dirname(customtkinter.__file__))"

pyinstaller `
    --onefile `
    --windowed `
    --name "InventoryApp" `
    --add-data "imgs;imgs" `
    --add-data "$ctk_path;customtkinter" `
    main.py

Write-Host ""
Write-Host "Build complete. Executable is at: dist\InventoryApp.exe"
Write-Host "Copy your inventory.db next to the .exe before first run (optional — auto-created if missing)."
