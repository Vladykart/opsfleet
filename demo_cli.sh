#!/bin/bash
echo "🚀 OpsFleet Enhanced CLI Demo"
echo "================================"
echo ""
echo "Features:"
echo "  ✨ Beautiful banner and UI"
echo "  ⌨️  Keyboard navigation (Ctrl+C to exit)"
echo "  📋 Command menu with /help"
echo "  📜 Query history with /history"
echo "  📊 Database schema with /schema"
echo "  📈 Session stats with /stats"
echo "  💾 Export history with /export"
echo ""
echo "Starting enhanced CLI..."
echo ""

source venv/bin/activate
python3 cli_enhanced.py
