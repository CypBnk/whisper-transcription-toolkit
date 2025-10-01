#!/usr/bin/env python3
"""
Whisper Transcription Toolkit - Video to Audio Converter
Convert MP4 and other video formats to MP3 audio for transcription

This file was developed with AI assistance (GitHub Copilot/Claude) for code generation
and optimization while maintaining human oversight for functionality and user experience.

Author: Human + AI Collaboration
License: MIT
"""

import os
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import argparse

def convert_mp4_to_mp3(input_file, output_file, quality="192k"):
    """
    Convert MP4 to MP3 using FFmpeg
    
    Args:
        input_file: Path to input MP4 file
        output_file: Path to output MP3 file
        quality: Audio bitrate (default: 192k for good quality)
    
    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    try:
        cmd = [
            'ffmpeg',
            '-i', str(input_file),
            '-vn',  # No video stream
            '-acodec', 'mp3',
            '-ab', quality,  # Audio bitrate
            '-ar', '44100',  # Sample rate: 44.1 kHz
            '-y',  # Overwrite output file without asking
            str(output_file)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return True, None
        else:
            return False, result.stderr
    except Exception as e:
        return False, str(e)

def batch_convert_mp4_to_mp3(input_dir, output_dir=None, max_workers=4, quality="192k"):
    """
    Convert all MP4 files to MP3 in parallel while preserving folder structure
    
    Args:
        input_dir: Directory containing MP4 files
        output_dir: Output directory (default: input_dir/converted_audio)
        max_workers: Number of parallel conversion processes
        quality: Audio quality (128k, 192k, 320k)
    
    Returns:
        Path: Output directory with converted files
    """
    input_path = Path(input_dir)
    
    if output_dir is None:
        output_path = input_path / "converted_audio"
    else:
        output_path = Path(output_dir)
    
    # Find all MP4 files, excluding hidden folders
    mp4_files = []
    for file_path in input_path.rglob('*.mp4'):
        # Skip files in folders starting with a dot
        if any(part.startswith('.') for part in file_path.relative_to(input_path).parts):
            continue
        mp4_files.append(file_path)
    
    # Also check for other video formats
    video_extensions = ['.avi', '.mov', '.mkv', '.webm']
    for ext in video_extensions:
        for file_path in input_path.rglob(f'*{ext}'):
            if any(part.startswith('.') for part in file_path.relative_to(input_path).parts):
                continue
            mp4_files.append(file_path)

    if not mp4_files:
        print(f"❌ No video files found in {input_dir}")
        return None

    print(f"📁 Found {len(mp4_files)} video files to convert")
    
    # Create conversion tasks while preserving folder structure
    conversion_tasks = []
    for video_file in mp4_files:
        # Maintain folder structure
        relative_path = video_file.relative_to(input_path)
        mp3_output_dir = output_path / relative_path.parent
        mp3_output_dir.mkdir(parents=True, exist_ok=True)
        
        mp3_file = mp3_output_dir / (video_file.stem + ".mp3")
        conversion_tasks.append((video_file, mp3_file))
        
        print(f"   📄 {relative_path} → {mp3_file.relative_to(output_path)}")

    print(f"\n🔄 Starting conversion with {max_workers} parallel workers...")
    print(f"🎵 Audio quality: {quality}")
    
    # Convert in parallel
    successful = 0
    failed = 0
    
    def convert_single(task):
        video_file, mp3_file = task
        success, error = convert_mp4_to_mp3(video_file, mp3_file, quality)
        if success:
            print(f"✅ Converted: {video_file.name}")
            return True
        else:
            print(f"❌ Failed {video_file.name}: {error}")
            return False
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(convert_single, conversion_tasks)
        for result in results:
            if result:
                successful += 1
            else:
                failed += 1

    print(f"\n📊 Conversion completed:")
    print(f"   ✅ Successful: {successful}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📁 Output directory: {output_path}")
    
    return output_path

def interactive_convert():
    """Interactive mode for MP4 to MP3 conversion"""
    print("🎵 === MP4 to MP3 Converter ===\n")
    
    # Get input directory
    while True:
        input_dir = input("📁 Enter input directory with video files: ").strip().strip('"')
        if os.path.exists(input_dir):
            break
        print(f"❌ Directory not found: {input_dir}")
    
    # Get output directory
    default_output = os.path.join(input_dir, "converted_audio")
    output_dir = input(f"📤 Enter output directory [default: {default_output}]: ").strip().strip('"')
    if not output_dir:
        output_dir = default_output
    
    # Choose quality
    print("\n🎵 Choose audio quality:")
    qualities = [
        ("128k", "Small size, acceptable quality"),
        ("192k", "Good balance (recommended)"),
        ("320k", "High quality, larger files")
    ]
    
    for i, (qual, desc) in enumerate(qualities, 1):
        print(f"{i}. {qual} - {desc}")
    
    while True:
        try:
            choice = int(input("Enter choice (1-3) [default: 2 for 192k]: ").strip() or "2")
            if 1 <= choice <= 3:
                quality = qualities[choice - 1][0]
                break
        except ValueError:
            pass
        print("❌ Please enter 1, 2, or 3")
    
    # Choose parallel workers
    max_workers = 4
    workers_input = input(f"🔧 Number of parallel conversions [default: {max_workers}]: ").strip()
    if workers_input:
        try:
            max_workers = int(workers_input)
            max_workers = max(1, min(max_workers, 8))  # Limit between 1-8
        except ValueError:
            pass
    
    print(f"\n⚙️  Configuration:")
    print(f"📁 Input: {input_dir}")
    print(f"📤 Output: {output_dir}")
    print(f"🎵 Quality: {quality}")
    print(f"🔧 Workers: {max_workers}")
    
    confirm = input("\nProceed with conversion? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ Operation cancelled")
        return
    
    # Start conversion
    result_dir = batch_convert_mp4_to_mp3(input_dir, output_dir, max_workers, quality)
    
    if result_dir:
        print(f"\n🎉 Conversion completed successfully!")
        print(f"📁 Converted files are in: {result_dir}")

def main():
    parser = argparse.ArgumentParser(
        description='Convert MP4 video files to MP3 audio files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python convert_mp4_to_mp3.py

  # Convert all MP4s in a directory
  python convert_mp4_to_mp3.py "/path/to/videos" --output "/path/to/audio"
  
  # High quality conversion with 8 parallel workers
  python convert_mp4_to_mp3.py "/path/to/videos" --quality 320k --workers 8
        """
    )
    
    parser.add_argument('input_dir', nargs='?', help='Directory with video files to convert')
    parser.add_argument('--output', '-o', help='Output directory for MP3 files')
    parser.add_argument('--quality', '-q', choices=['128k', '192k', '320k'], default='192k',
                        help='Audio quality/bitrate (default: 192k)')
    parser.add_argument('--workers', '-w', type=int, default=4,
                        help='Number of parallel conversions (default: 4)')
    
    args = parser.parse_args()
    
    if args.input_dir:
        # Command line mode
        if not os.path.exists(args.input_dir):
            print(f"❌ Input directory not found: {args.input_dir}")
            return 1
        
        result_dir = batch_convert_mp4_to_mp3(
            args.input_dir,
            args.output,
            args.workers,
            args.quality
        )
        
        if result_dir:
            print(f"\n🎉 Conversion completed!")
            return 0
        else:
            return 1
    else:
        # Interactive mode
        try:
            interactive_convert()
            return 0
        except KeyboardInterrupt:
            print("\n⏹️  Operation cancelled by user")
            return 1
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return 1

if __name__ == "__main__":
    exit(main())