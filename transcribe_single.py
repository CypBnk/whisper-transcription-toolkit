#!/usr/bin/env python3
"""
Whisper Transcription Toolkit - Single File Transcription
Single video/audio file transcription using OpenAI Whisper

This file was developed with AI assistance (GitHub Copilot/Claude) for code generation 
and optimization while maintaining human oversight for architecture and functionality.

Author: Human + AI Collaboration
License: MIT
"""

import time
import os
import whisper
import argparse
import warnings
from pathlib import Path
import json

def configure_ffmpeg_path():
    """Ensure ffmpeg is available on PATH, including bundled imageio-ffmpeg fallback."""
    try:
        import imageio_ffmpeg
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        ffmpeg_dir = str(Path(ffmpeg_exe).parent)
        current_path = os.environ.get("PATH", "")
        if ffmpeg_dir not in current_path.split(os.pathsep):
            os.environ["PATH"] = ffmpeg_dir + os.pathsep + current_path
    except Exception:
        # Continue; system ffmpeg may still be available.
        pass

def transcribe_video(video_path, output_dir=None, model_name="large-v3", language=None, word_timestamps=False):
    """
    Transcribes a single video using OpenAI Whisper while preserving folder structure
    
    Args:
        video_path: Path to the input video/audio file
        output_dir: Optional output directory (auto-determined if None)
        model_name: Whisper model to use (tiny, base, small, medium, large, large-v2, large-v3)
        language: Language code (e.g., 'en' for English, 'de' for German, or None for auto-detect)
        word_timestamps: Enable word-level timestamps (slower, may trigger Triton fallback warnings)
    
    Returns:
        tuple: (txt_path, srt_path) of created output files
    """
    video_path = Path(video_path)
    
    # Auto-determine output directory based on input structure
    if output_dir is None:
        # Try to maintain Input -> Output structure
        input_keywords = ["input", "videos", "audio", "media"]
        output_keywords = ["output", "transcripts", "results"]
        
        # Find if path contains input-like directories
        found_input = False
        for part in video_path.parts:
            if any(keyword in part.lower() for keyword in input_keywords):
                try:
                    # Replace input directory with output equivalent
                    path_parts = list(video_path.parts)
                    for i, p in enumerate(path_parts):
                        if any(keyword in p.lower() for keyword in input_keywords):
                            path_parts[i] = "Output"
                            break
                    output_dir = Path(*path_parts[:-1])  # Remove filename
                    found_input = True
                    break
                except:
                    pass
        
        if not found_input:
            # Default: create Output folder next to input file
            output_dir = video_path.parent / "Output"
    else:
        output_dir = Path(output_dir)

    configure_ffmpeg_path()

    # Load Whisper model
    print(f"Loading Whisper model: {model_name}")
    model = whisper.load_model(model_name)
    
    print(f"Starting transcription: {video_path.name}")
    start_time = time.time()

    # Transcribe with specified language (or auto-detect if not provided)
    transcribe_kwargs = {
        "word_timestamps": word_timestamps,
        "verbose": True
    }
    if language:
        transcribe_kwargs["language"] = language

    # Suppress known optional-kernel warnings when word timestamps are requested.
    if word_timestamps:
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message="Failed to launch Triton kernels, likely due to missing CUDA toolkit;.*",
                category=UserWarning,
            )
            result = model.transcribe(str(video_path), **transcribe_kwargs)
    else:
        result = model.transcribe(str(video_path), **transcribe_kwargs)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    base_name = video_path.stem

    # Output file paths
    prefix = model_prefix(model_name)
    txt_path = output_dir / f"{prefix}_{base_name}_transcript.txt"
    srt_path = output_dir / f"{prefix}_{base_name}_subtitles.srt"
    json_path = output_dir / f"{prefix}_{base_name}_metadata.json"

    # Write transcript files
    with open(txt_path, 'w', encoding='utf-8') as txt_file, \
         open(srt_path, 'w', encoding='utf-8') as srt_file:

        srt_counter = 1
        for segment in result["segments"]:
            # TXT format - plain text with timestamps
            txt_file.write(f"[{format_time(segment['start'])} -> {format_time(segment['end'])}] {segment['text']}\n")

            # SRT format - subtitle format for video players
            srt_file.write(f"{srt_counter}\n")
            srt_file.write(f"{format_srt_time(segment['start'])} --> {format_srt_time(segment['end'])}\n")
            srt_file.write(f"{segment['text'].strip()}\n\n")
            srt_counter += 1

    end_time = time.time()
    duration = end_time - start_time

    # Create metadata JSON with processing details
    metadata = {
        'file_name': video_path.name,
        'language': result.get('language', 'unknown'),
        'processing_time_seconds': duration,
        'segments_count': len(result["segments"]),
        'model_used': model_name,
        'word_timestamps': word_timestamps,
        'full_text': result["text"]
    }

    with open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(metadata, json_file, indent=2, ensure_ascii=False)

    print(f"✅ Transcription completed!")
    print(f"⏱️  Processing time: {duration:.2f} seconds")
    print(f"🗣️  Language detected: {result.get('language', 'unknown')}")
    print(f"📁 Output directory: {output_dir}")
    print(f"📄 Files created:")
    print(f"   - TXT: {txt_path.name}")
    print(f"   - SRT: {srt_path.name}")
    print(f"   - JSON: {json_path.name}")

    return txt_path, srt_path

def model_prefix(model_name: str) -> str:
    """Return a short version prefix for a given Whisper model name."""
    _PREFIX = {
        "medium": "v1",
        "large-v3": "v2",
        "large": "v2",
        "large-v2": "v2",
        "small": "small",
        "base": "base",
        "tiny": "tiny",
    }
    return _PREFIX.get(model_name, model_name)


def format_time(seconds):
    """Format seconds to MM:SS or HH:MM:SS"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"

def format_srt_time(seconds):
    """Format time for SRT subtitle format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}".replace('.', ',')

def main():
    parser = argparse.ArgumentParser(
        description='Transcribe a single video/audio file using OpenAI Whisper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic transcription with best quality model
  python transcribe_single.py "video.mp4"
  
  # Fast transcription with base model
  python transcribe_single.py "audio.wav" --model base
  
  # Custom output directory
  python transcribe_single.py "meeting.mp4" --output "./transcripts" --model large-v3
        """
    )
    
    parser.add_argument('video_path', help='Path to video or audio file')
    parser.add_argument('--output', '-o', help='Output directory (auto-determined if not specified)')
    parser.add_argument('--model', '-m', default='large-v3',
                        choices=['tiny', 'base', 'small', 'medium', 'large', 'large-v2', 'large-v3'],
                        help='Whisper model to use (default: large-v3 for best accuracy)')
    parser.add_argument('--language', '-l', default=None,
                        help='Language code (e.g., "en" for English, "de" for German). If not specified, language will be auto-detected.')
    parser.add_argument('--word-timestamps', action='store_true',
                        help='Enable word-level timestamps (slower; can trigger Triton fallback warnings).')

    args = parser.parse_args()

    # Validate input file
    if not os.path.exists(args.video_path):
        print(f"❌ Error: File not found: {args.video_path}")
        return 1

    try:
        transcribe_video(
            args.video_path,
            args.output,
            args.model,
            args.language,
            args.word_timestamps,
        )
        return 0
    except KeyboardInterrupt:
        print("\n⏹️  Transcription cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Error during transcription: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())