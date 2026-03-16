#!/usr/bin/env python3
"""
Whisper Transcription Toolkit - Batch Processing
Batch transcription of multiple video/audio files with interactive and CLI modes

This file was developed with AI assistance (GitHub Copilot/Claude) for code generation,
optimization, and user interface design while maintaining human oversight for 
architecture and functionality.

Author: Human + AI Collaboration  
License: MIT
"""

import os
import subprocess
import time
import json
import whisper
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import psutil
import GPUtil

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

def get_system_resources():
    """Monitor system resources for performance tracking"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()

    try:
        gpus = GPUtil.getGPUs()
        gpu_info = {
            'gpu_utilization': gpus[0].load * 100,
            'gpu_memory_used': gpus[0].memoryUsed,
            'gpu_memory_total': gpus[0].memoryTotal
        } if gpus else None
    except:
        gpu_info = None

    return {
        'cpu_percent': cpu_percent,
        'memory_percent': memory.percent,
        'memory_available': memory.available // (1024**3),  # GB
        'gpu_info': gpu_info
    }

def convert_mp4_to_mp3(input_file, output_file):
    """Convert MP4 to MP3 using FFmpeg with optimized settings"""
    try:
        cmd = [
            'ffmpeg',
            '-i', str(input_file),
            '-vn',  # No video stream
            '-acodec', 'mp3',
            '-ab', '192k',  # Audio bitrate: 192 kbps (good quality)
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

def transcribe_single_file(audio_file, model, output_base_dir, input_base_dir):
    """Transcribe a single audio file and return processing results"""
    audio_path = Path(audio_file)
    
    # Preserve folder structure from input to output
    try:
        relative_path = audio_path.relative_to(Path(input_base_dir))
        output_dir = Path(output_base_dir) / relative_path.parent
    except ValueError:
        # If file is not within input_base_dir, use root of output
        output_dir = Path(output_base_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    base_name = audio_path.stem

    start_time = time.time()
    
    try:
        # Transcribe with German language optimization
        result = model.transcribe(
            str(audio_path),
            language="de",  # German language
            word_timestamps=True,
            verbose=False  # Reduce console output for batch processing
        )

        # Create output file paths
        txt_path = output_dir / f"{base_name}_transcript.txt"
        srt_path = output_dir / f"{base_name}_subtitles.srt"
        json_path = output_dir / f"{base_name}_metadata.json"

        # Write transcript files
        with open(txt_path, 'w', encoding='utf-8') as txt_file, \
             open(srt_path, 'w', encoding='utf-8') as srt_file:

            srt_counter = 1
            for segment in result["segments"]:
                # TXT format: timestamped text
                txt_file.write(f"[{format_time(segment['start'])} -> {format_time(segment['end'])}] {segment['text']}\n")

                # SRT format: subtitle format for video players
                srt_file.write(f"{srt_counter}\n")
                srt_file.write(f"{format_srt_time(segment['start'])} --> {format_srt_time(segment['end'])}\n")
                srt_file.write(f"{segment['text'].strip()}\n\n")
                srt_counter += 1

        end_time = time.time()
        processing_time = end_time - start_time

        # Create detailed metadata
        metadata = {
            'file_name': audio_path.name,
            'language': result.get('language', 'de'),
            'processing_time_seconds': processing_time,
            'segments_count': len(result["segments"]),
            'full_text': result["text"]
        }

        with open(json_path, 'w', encoding='utf-8') as json_file:
            json.dump(metadata, json_file, indent=2, ensure_ascii=False)

        return {
            'success': True,
            'file': str(audio_path),
            'processing_time': processing_time,
            'segments': len(result["segments"]),
            'output_dir': str(output_dir)
        }

    except Exception as e:
        return {
            'success': False,
            'file': str(audio_path),
            'error': str(e)
        }

def find_media_files(input_dir, exclude_hidden=True):
    """
    Find all supported media files in directory
    
    Args:
        input_dir: Directory to search
        exclude_hidden: Whether to exclude files in folders starting with '.'
    
    Returns:
        List of Path objects for found media files
    """
    input_path = Path(input_dir)
    
    # Supported file formats
    video_formats = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}
    audio_formats = {'.wav', '.mp3', '.flac', '.m4a'}
    supported_formats = video_formats | audio_formats

    media_files = []
    for file_path in input_path.rglob('*'):
        # Skip hidden folders if requested
        if exclude_hidden and any(part.startswith('.') for part in file_path.relative_to(input_path).parts):
            continue
        if file_path.suffix.lower() in supported_formats:
            media_files.append(file_path)
    
    return media_files, video_formats

def batch_process_videos(input_dir, output_dir=None, mode="direct", model_name="large-v3", max_workers=1):
    """
    Batch process videos with choice of direct transcription or MP3 conversion
    
    Args:
        input_dir: Input directory with video/audio files
        output_dir: Output directory for transcripts (default: input_dir/Output)
        mode: "direct" for direct MP4 transcription, "convert" for MP3 conversion first
        model_name: Whisper model to use
        max_workers: Number of parallel workers (careful with GPU memory)
    """
    input_path = Path(input_dir)
    configure_ffmpeg_path()
    
    # Set default output directory
    if output_dir is None:
        output_dir = input_path / "Output"
    output_path = Path(output_dir)

    # Find all media files
    media_files, video_formats = find_media_files(input_dir)

    if not media_files:
        print(f"❌ No supported media files found in {input_dir}")
        print("Supported formats: MP4, AVI, MOV, MKV, WebM, WAV, MP3, FLAC, M4A")
        return

    print(f"📁 Found {len(media_files)} media files")
    for media_file in media_files:
        relative_path = media_file.relative_to(input_path)
        print(f"   📄 {relative_path}")

    # Load Whisper model
    print(f"\n🤖 Loading Whisper model: {model_name}")
    model = whisper.load_model(model_name)

    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)

    # Conversion phase (if needed)
    files_to_transcribe = []
    conversion_stats = {'successful': 0, 'failed': 0, 'time': 0}
    
    if mode == "convert":
        video_files = [f for f in media_files if f.suffix.lower() in video_formats]
        audio_files = [f for f in media_files if f.suffix.lower() not in video_formats]
        
        if video_files:
            print(f"\n🔄 Converting {len(video_files)} video files to MP3...")
            conversion_start = time.time()
            
            # Create temp directory for converted files
            temp_audio_dir = output_path / "temp_audio"
            temp_audio_dir.mkdir(exist_ok=True)
            
            # Convert videos to MP3
            for video_file in video_files:
                relative_path = video_file.relative_to(input_path)
                mp3_output_dir = temp_audio_dir / relative_path.parent
                mp3_output_dir.mkdir(parents=True, exist_ok=True)
                mp3_file = mp3_output_dir / (video_file.stem + ".mp3")
                
                print(f"🔄 Converting: {video_file.name}")
                success, error = convert_mp4_to_mp3(video_file, mp3_file)
                if success:
                    conversion_stats['successful'] += 1
                    files_to_transcribe.append(mp3_file)
                    print(f"   ✅ → {mp3_file.name}")
                else:
                    conversion_stats['failed'] += 1
                    print(f"   ❌ Failed: {error}")
            
            conversion_stats['time'] = time.time() - conversion_start
            print(f"\n📊 Conversion completed: {conversion_stats['successful']}/{len(video_files)} successful in {conversion_stats['time']:.1f}s")
        
        # Add existing audio files
        files_to_transcribe.extend(audio_files)
        
    else:  # Direct mode
        files_to_transcribe = media_files
        print(f"\n🎯 Direct transcription mode - processing {len(files_to_transcribe)} files")

    if not files_to_transcribe:
        print("❌ No files to transcribe")
        return

    # Transcription phase
    print(f"\n🎤 Starting transcription of {len(files_to_transcribe)} files...")
    transcription_start = time.time()
    
    # System resource monitoring
    resources_before = get_system_resources()
    print(f"💻 System resources:")
    print(f"   CPU: {resources_before['cpu_percent']:.1f}%")
    print(f"   RAM: {resources_before['memory_percent']:.1f}% ({resources_before['memory_available']}GB free)")
    if resources_before['gpu_info']:
        gpu = resources_before['gpu_info']
        print(f"   GPU: {gpu['gpu_utilization']:.1f}% ({gpu['gpu_memory_used']:.0f}/{gpu['gpu_memory_total']:.0f}MB)")

    # Process files
    successful_transcriptions = 0
    failed_transcriptions = 0
    total_processing_time = 0
    transcription_results = []

    # Use the correct input base directory for file structure preservation
    input_base_for_structure = input_dir if mode == "direct" else temp_audio_dir

    for i, audio_file in enumerate(files_to_transcribe, 1):
        print(f"\n📝 [{i}/{len(files_to_transcribe)}] Processing: {audio_file.name}")
        
        result = transcribe_single_file(
            audio_file, 
            model, 
            output_dir, 
            input_base_for_structure
        )
        
        transcription_results.append(result)
        
        if result['success']:
            successful_transcriptions += 1
            total_processing_time += result['processing_time']
            print(f"   ✅ Completed in {result['processing_time']:.1f}s ({result['segments']} segments)")
        else:
            failed_transcriptions += 1
            print(f"   ❌ Failed: {result['error']}")

    # Cleanup temporary files
    if mode == "convert" and 'temp_audio_dir' in locals():
        print(f"\n🧹 Cleaning up temporary files...")
        import shutil
        try:
            shutil.rmtree(temp_audio_dir)
        except Exception as e:
            print(f"⚠️  Warning: Could not remove temp directory: {e}")

    # Final statistics
    total_time = time.time() - transcription_start
    
    print(f"\n📊 ===== BATCH PROCESSING COMPLETED =====")
    if mode == "convert":
        print(f"🔄 Conversion: {conversion_stats['successful']}/{conversion_stats['successful'] + conversion_stats['failed']} files in {conversion_stats['time']:.1f}s")
    print(f"🎤 Transcription: {successful_transcriptions}/{len(files_to_transcribe)} files successful")
    print(f"⏱️  Total time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
    if successful_transcriptions > 0:
        print(f"📈 Average per file: {total_time/successful_transcriptions:.1f}s")

    # Save detailed statistics
    stats_file = output_path / "batch_statistics.json"
    batch_stats = {
        'mode': mode,
        'model': model_name,
        'total_files': len(media_files),
        'files_to_transcribe': len(files_to_transcribe),
        'successful_transcriptions': successful_transcriptions,
        'failed_transcriptions': failed_transcriptions,
        'total_time': total_time,
        'average_time_per_file': total_time / successful_transcriptions if successful_transcriptions > 0 else 0,
        'conversion_stats': conversion_stats,
        'transcription_results': transcription_results,
        'system_resources_before': resources_before
    }

    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(batch_stats, f, indent=2, ensure_ascii=False)

    print(f"📄 Detailed statistics saved: {stats_file}")

def format_time(seconds):
    """Format seconds to HH:MM:SS or MM:SS"""
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

def interactive_mode():
    """Interactive mode for user-friendly operation"""
    print("🎬 === Whisper Transcription Toolkit ===\n")
    
    # Get input directory
    while True:
        input_dir = input("📁 Enter input directory path: ").strip().strip('"')
        if os.path.exists(input_dir):
            break
        print(f"❌ Directory not found: {input_dir}")
    
    # Get output directory
    default_output = os.path.join(input_dir, "Output")
    output_dir = input(f"📤 Enter output directory [default: {default_output}]: ").strip().strip('"')
    if not output_dir:
        output_dir = default_output
    
    # Choose processing mode
    print("\n🔧 Choose processing mode:")
    print("1. Direct MP4/Video transcription (recommended)")
    print("2. Convert to MP3 first, then transcribe (saves disk space)")
    
    while True:
        choice = input("Enter choice (1 or 2): ").strip()
        if choice == "1":
            mode = "direct"
            break
        elif choice == "2":
            mode = "convert"
            break
        print("❌ Please enter 1 or 2")
    
    # Choose model
    print("\n🤖 Choose Whisper model:")
    models = [
        ("tiny", "39 MB, fastest, basic accuracy"),
        ("base", "74 MB, fast, good for testing"), 
        ("small", "244 MB, balanced speed/accuracy"),
        ("medium", "769 MB, high accuracy"),
        ("large", "1550 MB, very high accuracy"),
        ("large-v2", "1550 MB, improved large model"),
        ("large-v3", "1550 MB, best accuracy (recommended)")
    ]
    
    for i, (model, desc) in enumerate(models, 1):
        print(f"{i}. {model} - {desc}")
    
    while True:
        try:
            choice = int(input(f"Enter choice (1-{len(models)}) [default: 7 for large-v3]: ").strip() or "7")
            if 1 <= choice <= len(models):
                model_name = models[choice - 1][0]
                break
        except ValueError:
            pass
        print(f"❌ Please enter a number between 1 and {len(models)}")
    
    # Show configuration summary
    print(f"\n⚙️  Configuration Summary:")
    print(f"📁 Input: {input_dir}")
    print(f"📤 Output: {output_dir}")
    print(f"🔧 Mode: {mode}")
    print(f"🤖 Model: {model_name}")
    
    confirm = input("\nProceed with transcription? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ Operation cancelled")
        return
    
    # Start processing
    batch_process_videos(input_dir, output_dir, mode, model_name)

def main():
    parser = argparse.ArgumentParser(
        description='Batch transcription with choice of direct MP4 or MP3 conversion',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (recommended for first-time users)
  python transcript_batch.py

  # Direct command line usage
  python transcript_batch.py "/path/to/videos" --output "/path/to/output" --mode direct --model large-v3
  
  # Convert to MP3 first (saves disk space)
  python transcript_batch.py "/path/to/videos" --mode convert --model base
        """
    )
    
    parser.add_argument('input_dir', nargs='?', help='Input directory with video/audio files')
    parser.add_argument('--output', '-o', help='Output directory for transcripts')
    parser.add_argument('--mode', '-m', choices=['direct', 'convert'], default='direct',
                        help='Processing mode: direct (MP4→transcript) or convert (MP4→MP3→transcript)')
    parser.add_argument('--model', choices=['tiny', 'base', 'small', 'medium', 'large', 'large-v2', 'large-v3'],
                        default='large-v3', help='Whisper model to use (default: large-v3)')
    parser.add_argument('--workers', '-w', type=int, default=1,
                        help='Number of parallel workers (be careful with GPU memory)')
    
    args = parser.parse_args()
    
    if args.input_dir:
        # Command line mode
        if not os.path.exists(args.input_dir):
            print(f"❌ Input directory not found: {args.input_dir}")
            return 1
        
        output_dir = args.output or os.path.join(args.input_dir, "Output")
        
        batch_process_videos(
            args.input_dir,
            output_dir,
            args.mode,
            args.model,
            args.workers
        )
        return 0
    else:
        # Interactive mode
        try:
            interactive_mode()
            return 0
        except KeyboardInterrupt:
            print("\n⏹️  Operation cancelled by user")
            return 1
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return 1

if __name__ == "__main__":
    exit(main())