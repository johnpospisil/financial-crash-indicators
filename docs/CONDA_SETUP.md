# Virtual Environment Setup

This project uses the existing `tf` virtual environment.

## Quick Start

1. **Activate the environment**

   ```bash
   source tf/bin/activate
   ```

2. **Install project dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API keys**

   ```bash
   cp .env.example .env
   # Then edit .env and add your FRED API key
   ```

4. **Verify installation**
   ```bash
   python -c "import pandas, fredapi, plotly, dash; print('All packages installed successfully!')"
   ```

## Environment Management

### View installed packages

```bash
source tf/bin/activate
pip list
```

### Update packages

```bash
source tf/bin/activate
pip install --upgrade -r requirements.txt
```

### Add Jupyter kernel (if needed)

```bash
source tf/bin/activate
python -m ipykernel install --user --name=tf --display-name="Python (tf)"
```

Then in Jupyter, select the "Python (tf)" kernel.

## Working with Jupyter Notebooks

### Start Jupyter

```bash
source tf/bin/activate
jupyter notebook notebooks/
```

### Ensure correct kernel

In Jupyter:

- Click "Kernel" → "Change Kernel" → "Python (tf)"
- Or verify the top-right shows "Python (tf)"

## Troubleshooting

### ModuleNotFoundError

```bash
source tf/bin/activate
pip install -r requirements.txt
```

### Jupyter can't find the environment

```bash
source tf/bin/activate
python -m ipykernel install --user --name=tf --display-name="Python (tf)"
```

### Wrong Python version

Check Python version:

```bash
source tf/bin/activate
python --version
```

Should be Python 3.8 or higher.

### Deactivate environment

```bash
deactivate
```
