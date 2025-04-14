#!/usr/bin/env python3
"""
Standalone headset monitoring application with system tray icon
"""

from utils.scheduler import SchedulerManager

def main():
    """
    Main entry point for the standalone monitoring application
    """
    scheduler = SchedulerManager()
    scheduler.start()

if __name__ == '__main__':
    main()