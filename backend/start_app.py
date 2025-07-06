#!/usr/bin/env python3
"""
Startup script voor de NBA Dashboard Flask app
Installeert automatisch dependencies en start de server
"""

import subprocess
import sys
import os

def install_requirements():
    """Installeer dependencies uit requirements.txt"""
    print("🔧 Installeren van dependencies...")
    try:
        # Eerst setuptools en wheel upgraden
        print("📦 Upgraden van setuptools en wheel...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "setuptools", "wheel"])
        
        # Dan requirements installeren
        print("📦 Installeren van project dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies succesvol geïnstalleerd!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Fout bij installeren dependencies: {e}")
        return False

def start_flask_app():
    """Start de Flask app"""
    print("🚀 Starten van Flask app...")
    print("📍 API beschikbaar op: http://localhost:5000")
    print("📍 Health check: http://localhost:5000/api/health")
    print("📍 Analytics Dashboard: http://localhost:5000/analytics-dashboard.html")
    print("=" * 50)
    try:
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n👋 Flask app gestopt")
    except Exception as e:
        print(f"❌ Fout bij starten Flask app: {e}")

if __name__ == "__main__":
    print("🏀 NBA Dashboard Startup")
    print("=" * 30)
    
    # Controleer of requirements.txt bestaat
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt niet gevonden!")
        sys.exit(1)
    
    # Installeer dependencies
    if install_requirements():
        # Start Flask app
        start_flask_app()
    else:
        print("❌ Kan Flask app niet starten vanwege dependency problemen")
        print("💡 Probeer handmatig: pip install -r requirements.txt")
        sys.exit(1) 