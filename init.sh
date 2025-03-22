#!/bin/bash
set -e

echo "🔎 Checking for required libraries..."

# Ensure mysql-client and essential libraries are installed
mamba_packages=(
    "mysqlclient"        # MySQL client
    "pandas"             # Data manipulation
    "numpy"              # Numerical computing
    "matplotlib"         # Plotting
    "seaborn"            # Statistical data visualization
    "scipy"              # Scientific computing
    "plotly"             # Interactive visualizations
    "openpyxl"           # Excel file support (for Pandas)
    "xlrd"               # Read older Excel files
    "sqlalchemy"         # SQL database toolkit for Python
)

for package in "${mamba_packages[@]}"; do
    if ! python -c "import $package" &>/dev/null; then
        echo "📦 Installing $package..."
        mamba install -y -c conda-forge "$package"
    else
        echo "✅ $package is already installed."
    fi
done

# Start Jupyter Notebook
exec /usr/local/bin/start-notebook.sh
