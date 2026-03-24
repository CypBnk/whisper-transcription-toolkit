# Whisper Transcription Toolkit

A comprehensive Python toolkit for transcribing German audio and video files using OpenAI Whisper with GPU acceleration support.

> **Note:** This project was developed with AI assistance (GitHub Copilot/Claude) for code generation, optimization, and documentation. The core functionality and architecture were collaboratively designed between human expertise and AI capabilities.

## Features

🎯 **Dual Processing Modes**

- Direct MP4/Video transcription (recommended)
- MP3 conversion + transcription for storage efficiency

🚀 **High Performance**

- GPU acceleration with CUDA support
- Batch processing capabilities
- ~2.8x real-time speed on RTX 3090

📁 **Smart File Management**

- Preserves folder structure (Input/Project → Output/Project)
- Ignores hidden folders (starting with .)
- Supports multiple formats: MP4, AVI, MOV, MKV, WebM, WAV, MP3

📄 **Multiple Output Formats**

- TXT: Plain text with timestamps
- SRT: Subtitle files for video players
- JSON: Detailed metadata and processing info

🎛️ **User-Friendly Interface**

- Interactive mode with guided setup
- Command-line interface for automation
- Real-time progress tracking and system monitoring

## Requirements

- Python 3.9+
- Python 3.10 or 3.11 recommended for the most predictable package compatibility
- NVIDIA GPU with CUDA support (optional but recommended)
- FFmpeg (for video processing)
- 8GB+ RAM (16GB+ recommended for large files)

## Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/whisper-transcription-toolkit.git
cd whisper-transcription-toolkit
```

1. **Create and activate virtual environment**

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

1. **Install dependencies**

```bash
pip install --upgrade -r requirements.txt
```

Optional (NVIDIA CUDA 12.8 wheels):

```bash
pip install --upgrade -r requirements.cuda-cu128.txt
```

Run project commands from the repository root with the virtual environment activated.

Windows example:

```powershell
Set-Location 'F:\Dev\AI\Branched\whisper-transcription-toolkit'
. '.\.venv\Scripts\Activate.ps1'
python .\setup_environment.py --test
```

`requirements.txt` is the portable default set. Use `requirements.cuda-cu128.txt` only when you explicitly want CUDA 12.8 PyTorch wheels.

1. **Install FFmpeg**

- **Windows**: `choco install ffmpeg` or download from [FFmpeg.org](https://ffmpeg.org/download.html)
- **Linux**: `sudo apt install ffmpeg`
- **Mac**: `brew install ffmpeg`
- **Optional fallback**: `pip install imageio-ffmpeg` (toolkit can use bundled ffmpeg from Python env)

## Quick Start

### Interactive Mode (Recommended)

```bash
python transcript_batch.py
```

Follow the prompts to select input directory, processing mode, and model.

### Command Line Usage

```bash
# Direct transcription with best quality
python transcript_batch.py "/path/to/videos" --mode direct --model large-v3

# Convert to MP3 first (saves disk space)
python transcript_batch.py "/path/to/videos" --mode convert --model base --output "/path/to/output"

# Single file transcription
python transcribe_single.py "/path/to/video.mp4" --model large-v3
```

## Models & Performance

| Model    | Size    | Speed    | Accuracy | Use Case                 |
| -------- | ------- | -------- | -------- | ------------------------ |
| tiny     | 39 MB   | Fastest  | Basic    | Quick testing            |
| base     | 74 MB   | Fast     | Good     | Development/drafts       |
| small    | 244 MB  | Moderate | Better   | General use              |
| medium   | 769 MB  | Slower   | High     | Quality transcription    |
| large-v3 | 1550 MB | Slowest  | Best     | Production/final results |

### Expected Performance (RTX 3090)

- **Single 1-hour video**: 3-8 minutes processing time
- **Batch processing**: ~2.8x real-time speed per file
- **5x 1-hour videos**: 15-25 minutes total

## GPU Setup

For NVIDIA GPU acceleration:

1. **Install CUDA Toolkit** from [NVIDIA Developer](https://developer.nvidia.com/cuda-downloads)
2. **Verify installation**:

```bash
nvidia-smi
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
```

## File Structure

```text
whisper-transcription-toolkit/
├── README.md
├── requirements.txt
├── setup_environment.py      # Environment validation script
├── transcript_batch.py       # Main batch processing script
├── transcribe_single.py      # Single file transcription
├── convert_mp4_to_mp3.py    # Video to audio conversion utility
├── docs/
│   ├── installation.md
│   ├── usage.md
│   └── troubleshooting.md
└── examples/
    ├── example_config.json
    └── sample_output/
```

## Usage Examples

### Example 1: Corporate Meeting Transcription

```bash
# Process meeting recordings with high accuracy
python transcript_batch.py "./meetings" --mode direct --model large-v3 --output "./transcripts"
```

### Example 2: Podcast Processing

```bash
# Convert podcasts to MP3 first to save space
python transcript_batch.py "./podcasts" --mode convert --model medium
```

### Example 3: Single Interview

```bash
# Quick transcription of single interview
python transcribe_single.py "./interview.mp4" --model base
```

## Output Structure

For input file `Input/Project/meeting.mp4`, the output will be:

```text
Output/Project/
├── meeting_transcript.txt    # Plain text with timestamps
├── meeting_subtitles.srt    # Video subtitle format
└── meeting_metadata.json    # Processing details and full text
```

## Configuration

### German Language Optimization

The toolkit is pre-configured for German language processing with:

- Language detection set to "de"
- German-specific Whisper models when available
- Proper handling of German umlauts and characters

### System Resource Management

- Automatic GPU/CPU detection
- Memory usage monitoring
- Parallel processing optimization
- Temporary file cleanup

## Troubleshooting

### Common Issues

1. **CUDA not detected**

   ```bash
   # Reinstall PyTorch with CUDA support
   pip uninstall torch torchvision torchaudio
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   ```

2. **Out of memory errors**
   - Use smaller model (base instead of large-v3)
   - Process files individually instead of batch
   - Close other GPU applications

3. **FFmpeg not found**

   ```bash
   # Windows
   choco install ffmpeg
   # Or use Python-managed fallback in virtualenv
   pip install imageio-ffmpeg
   # Add to PATH if needed
   ```

### Performance Optimization

- **Use SSD storage** for input/output directories
- **Close unnecessary applications** before processing
- **Use direct mode** for best performance with sufficient RAM
- **Process during low system usage** for optimal results

## Contributing

We welcome contributions! This project embraces AI-assisted development while maintaining high code quality standards.

### Development Philosophy

- **Human + AI Collaboration**: This project was built with AI assistance and we encourage contributors to use AI tools (GitHub Copilot, Claude, etc.) for code generation and optimization
- **Human Oversight**: All AI-generated code should be reviewed, tested, and validated by humans
- **Attribution**: Please mention AI assistance in pull request descriptions when applicable

### Contribution Process

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Develop with or without AI assistance (both approaches welcome)
4. Test thoroughly on your system
5. Commit changes with clear messages
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open Pull Request with description of changes and any AI tools used

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) for the transcription models
- [FFmpeg](https://ffmpeg.org/) for video/audio processing
- [PyTorch](https://pytorch.org/) for GPU acceleration
- **AI Collaboration**: This project was developed with assistance from AI tools (GitHub Copilot/Claude) for code generation, optimization, and documentation enhancement

## Support

For issues and questions:

- 📖 Check the [documentation](docs/)
- 🐛 Report bugs via [GitHub Issues](https://github.com/yourusername/whisper-transcription-toolkit/issues)
- 💡 Request features via [GitHub Discussions](https://github.com/yourusername/whisper-transcription-toolkit/discussions)
