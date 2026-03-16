# Installation Guide

This guide walks you through setting up the Whisper Transcription Toolkit on your system.

## System Requirements

### Minimum Requirements

- Python 3.9 or higher
- 8 GB RAM
- 5 GB free disk space
- Internet connection (for model downloads)

### Recommended Requirements

- Python 3.10+
- Python 3.10 or 3.11 recommended for the most predictable package compatibility
- 16+ GB RAM
- NVIDIA GPU with 8+ GB VRAM (RTX 3070, RTX 3080, RTX 3090, RTX 4080, RTX 4090)
- CUDA 11.8+ or 12.x
- SSD storage for input/output directories

## Step-by-Step Installation

### 1. Install Python

**Windows:**

1. Download Python from [python.org](https://www.python.org/downloads/)
2. During installation, check "Add Python to PATH"
3. Verify: Open Command Prompt and run `python --version`

**Linux (Ubuntu/Debian):**

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**macOS:**

```bash
# Using Homebrew
brew install python
```

### 2. Install CUDA (For GPU Acceleration)

**Windows:**

1. Download CUDA Toolkit from [NVIDIA Developer](https://developer.nvidia.com/cuda-downloads)
2. Install the toolkit (recommended: CUDA 12.1 or newer)
3. Verify installation: `nvidia-smi` in Command Prompt

**Linux:**

```bash
# Ubuntu/Debian example
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda
```

### 3. Install FFmpeg

**Windows:**

```bash
# Using Chocolatey (recommended)
choco install ffmpeg

# Or download from https://ffmpeg.org/download.html
# Extract and add to PATH
```

**Linux:**

```bash
sudo apt install ffmpeg
```

**macOS:**

```bash
brew install ffmpeg
```

### 4. Clone Repository and Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/whisper-transcription-toolkit.git
cd whisper-transcription-toolkit

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install requirements
pip install --upgrade -r requirements.txt
```

Run commands from the repository root with the virtual environment activated.

Windows example:

```powershell
Set-Location 'F:\Dev\AI\Branched\whisper-transcription-toolkit'
. '.\.venv\Scripts\Activate.ps1'
python .\setup_environment.py --install --test
```

If system FFmpeg is not available in PATH, you can install a Python-managed fallback:

```bash
pip install imageio-ffmpeg
```

Note: the pinned `requirements.txt` reflects a verified CUDA-enabled Windows environment. If you are on another platform, using a different CUDA toolkit, or running CPU-only, adjust the PyTorch package versions as needed.

### 5. Verify Installation

Run the setup script to verify everything is working:

```bash
python setup_environment.py --install --test
```

This will:

- Install/upgrade all required packages
- Check system capabilities
- Test transcription functionality
- Provide performance expectations

## GPU Setup Verification

### Check CUDA Installation

```bash
nvidia-smi
nvcc --version
```

### Test PyTorch CUDA Support

```bash
python -c "import torch; print('CUDA Available:', torch.cuda.is_available())"
python -c "import torch; print('GPU Name:', torch.cuda.get_device_name(0))"
```

Expected output for working GPU setup:

```text
CUDA Available: True
GPU Name: NVIDIA GeForce RTX 3090
```

## Model Downloads

Whisper models are downloaded automatically on first use. Expected sizes:

| Model    | Size    | Download Time (typical) |
| -------- | ------- | ----------------------- |
| tiny     | 39 MB   | 5-10 seconds            |
| base     | 74 MB   | 10-20 seconds           |
| small    | 244 MB  | 30-60 seconds           |
| medium   | 769 MB  | 1-3 minutes             |
| large-v3 | 1.55 GB | 3-10 minutes            |

Models are cached in:

- **Windows:** `C:\Users\{username}\.cache\whisper\`
- **Linux:** `~/.cache/whisper/`
- **macOS:** `~/Library/Caches/whisper/`

## Troubleshooting Installation

### Common Issues

**1. "CUDA not available" despite having NVIDIA GPU**

```bash
# Uninstall CPU-only PyTorch
pip uninstall torch torchvision torchaudio

# Install CUDA-enabled PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**2. "FFmpeg not found"**

- Ensure FFmpeg is installed and in system PATH
- Test with `ffmpeg -version`
- On Windows, you may need to restart Command Prompt after installation
- Alternative in virtualenv: `pip install imageio-ffmpeg`

**3. "Permission denied" or "Access denied"**

- Run terminal as Administrator (Windows) or use `sudo` (Linux)
- Or install in user space: `pip install --user -r requirements.txt`

**4. "Out of memory" during transcription**

- Use smaller model (base instead of large-v3)
- Process files individually instead of batch
- Close other applications using GPU/RAM

**5. Slow performance despite GPU**

- Verify CUDA version compatibility
- Check if other processes are using GPU: `nvidia-smi`
- Ensure adequate cooling for sustained performance

### Performance Optimization

**For RTX 3090/4090 (24GB VRAM):**

- Use `large-v3` model for best quality
- Batch processing: 4-8 files simultaneously
- Expected speed: ~3x real-time

**For RTX 3070/3080 (8-12GB VRAM):**

- Use `large-v2` or `medium` model
- Batch processing: 1-2 files simultaneously
- Expected speed: ~2x real-time

**For CPU-only systems:**

- Use `base` or `small` model
- Process files individually
- Expected speed: ~0.2-0.5x real-time

## Next Steps

After successful installation:

1. **Test with sample file:**

   ```bash
   python transcribe_single.py path/to/test/video.mp4
   ```

2. **Run interactive batch processing:**

   ```bash
   python transcript_batch.py
   ```

3. **Check the [Usage Guide](usage.md) for detailed examples**

## Getting Help

- 📖 Read the [Usage Guide](usage.md)
- 🐛 Check [Troubleshooting](troubleshooting.md)
- 💬 Open an issue on GitHub
- 📧 Check the project documentation
