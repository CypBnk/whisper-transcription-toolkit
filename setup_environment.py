#!/usr/bin/env python3
"""
Whisper Transcription Toolkit - Environment Setup and Validation
System requirements validation and environment setup for optimal transcription performance

This file was developed with AI assistance (GitHub Copilot/Claude) for comprehensive
system checking, troubleshooting guidance, and user experience optimization.

Author: Human + AI Collaboration
License: MIT
"""

import torch
import whisper
import psutil
import GPUtil
import os
import subprocess
import sys

def check_system_requirements():
    """Validate system setup for optimal transcription performance"""
    print("🔍 === System Environment Check ===\n")
    
    issues = []
    recommendations = []
    
    # Python version check
    import sys
    python_version = sys.version_info
    print(f"🐍 Python Version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    if python_version < (3, 9):
        issues.append("Python 3.9+ required for optimal Whisper performance")
    
    # PyTorch and CUDA check
    print(f"🔥 PyTorch Version: {torch.__version__}")
    cuda_available = torch.cuda.is_available()
    print(f"🚀 CUDA Available: {cuda_available}")
    
    if cuda_available:
        gpu_count = torch.cuda.device_count()
        print(f"🎮 GPU Count: {gpu_count}")
        
        for i in range(gpu_count):
            gpu_name = torch.cuda.get_device_name(i)
            gpu_memory = torch.cuda.get_device_properties(i).total_memory / (1024**3)
            print(f"   GPU {i}: {gpu_name} ({gpu_memory:.1f} GB)")
            
            if gpu_memory < 4:
                recommendations.append(f"GPU {i} has limited memory. Consider using smaller Whisper models (tiny/base)")
            elif gpu_memory >= 8:
                recommendations.append(f"GPU {i} can handle large Whisper models (large-v3)")
    else:
        issues.append("CUDA not detected. Transcription will use CPU (slower)")
        recommendations.append("Install CUDA toolkit for GPU acceleration")
    
    # System RAM check
    memory = psutil.virtual_memory()
    ram_gb = memory.total / (1024**3)
    ram_available = memory.available / (1024**3)
    print(f"💾 System RAM: {ram_gb:.1f} GB total, {ram_available:.1f} GB available")
    
    if ram_gb < 8:
        issues.append("Less than 8GB RAM detected. May struggle with large models/files")
    elif ram_gb >= 16:
        print("   ✅ Sufficient RAM for large batch processing")
    
    # CPU check
    cpu_count = psutil.cpu_count()
    print(f"⚡ CPU Cores: {cpu_count}")
    
    if cpu_count >= 8:
        print("   ✅ Good CPU core count for parallel processing")
    elif cpu_count < 4:
        recommendations.append("Low CPU core count. Consider processing files sequentially")
    
    # FFmpeg check
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("🎬 FFmpeg: ✅ Available")
        else:
            issues.append("FFmpeg not working properly")
    except FileNotFoundError:
        issues.append("FFmpeg not found. Required for video processing")
        recommendations.append("Install FFmpeg: https://ffmpeg.org/download.html")
    
    # Whisper model test
    try:
        print("\n🤖 Testing Whisper model loading...")
        model = whisper.load_model("tiny")
        print("   ✅ Whisper models can be loaded successfully")
    except Exception as e:
        issues.append(f"Cannot load Whisper models: {str(e)}")
    
    # Display results
    print(f"\n📊 === System Assessment ===")
    
    if not issues:
        print("✅ All checks passed! Your system is ready for transcription.")
    else:
        print("⚠️  Issues detected:")
        for issue in issues:
            print(f"   ❌ {issue}")
    
    if recommendations:
        print("\n💡 Recommendations:")
        for rec in recommendations:
            print(f"   🔧 {rec}")
    
    # Performance expectations
    print(f"\n🎯 Expected Performance:")
    if cuda_available and ram_gb >= 16:
        print("   🚀 Excellent - GPU acceleration with large models")
        print("   ⏱️  ~2-4x real-time speed for transcription")
    elif cuda_available:
        print("   🏃 Good - GPU acceleration available")
        print("   ⏱️  ~1-2x real-time speed for transcription")
    elif ram_gb >= 8:
        print("   🚶 Fair - CPU processing with adequate RAM")
        print("   ⏱️  ~0.2-0.5x real-time speed for transcription")
    else:
        print("   🐌 Limited - Consider hardware upgrades")
        print("   ⏱️  <0.2x real-time speed for transcription")
    
    return len(issues) == 0

def test_transcription():
    """Test transcription with a small sample"""
    print("\n🧪 === Transcription Test ===")
    
    try:
        # Load tiny model for quick test
        print("Loading tiny model for test...")
        model = whisper.load_model("tiny")
        
        # Create a simple test (silent audio)
        import numpy as np
        
        # Generate 1 second of silence
        sample_rate = 16000
        duration = 1.0
        audio = np.zeros(int(sample_rate * duration), dtype=np.float32)
        
        print("Running test transcription...")
        result = model.transcribe(audio, language="de")
        
        print("✅ Transcription test completed successfully")
        print(f"   Detected language: {result.get('language', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Transcription test failed: {str(e)}")
        return False

def install_requirements():
    """Install or upgrade required packages"""
    print("\n📦 === Package Installation ===")
    
    requirements = [
        "openai-whisper>=20230314",
        "torch",
        "torchvision", 
        "torchaudio",
        "psutil>=5.9.0",
        "GPUtil>=1.4.0"
    ]
    
    print("Installing/upgrading required packages...")
    
    for package in requirements:
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "--upgrade", package
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {package}")
            else:
                print(f"❌ {package}: {result.stderr}")
                
        except Exception as e:
            print(f"❌ {package}: {str(e)}")

def main():
    """Run complete environment setup and validation"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Setup and validate environment for Whisper transcription"
    )
    parser.add_argument('--install', action='store_true', 
                       help='Install/upgrade required packages')
    parser.add_argument('--test', action='store_true',
                       help='Run transcription test')
    
    args = parser.parse_args()
    
    if args.install:
        install_requirements()
        print("\n" + "="*50)
    
    # Always run system check
    system_ok = check_system_requirements()
    
    if args.test:
        print("\n" + "="*50)
        test_ok = test_transcription()
        system_ok = system_ok and test_ok
    
    print(f"\n🎯 === Final Status ===")
    if system_ok:
        print("🎉 Your system is ready for transcription!")
        print("\nNext steps:")
        print("1. Run: python transcript_batch.py")
        print("2. Or: python transcribe_single.py your_video.mp4")
    else:
        print("⚠️  Please address the issues above before proceeding.")
        print("\nFor help, check the documentation or run with --install")
    
    return 0 if system_ok else 1

if __name__ == "__main__":
    exit(main())