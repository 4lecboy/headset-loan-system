"""
Scheduler utilities for running periodic tasks
"""
import threading
import schedule
import time
from datetime import datetime
from PIL import Image
from pystray import Icon, MenuItem as item, Menu

from utils.email_sender import send_scheduled_email

class SchedulerManager:
    """
    Manager class for scheduling and running periodic tasks
    with system tray integration
    """
    def __init__(self):
        self.exit_event = threading.Event()
        self.scheduler_thread = None
        self.tray_thread = None
        self.icon = None
        self.is_running = False
    
    def start(self):
        """
        Start the scheduler thread and system tray icon
        """
        if self.is_running:
            print("Scheduler is already running")
            return
        
        self.exit_event.clear()
        
        # Start scheduler thread
        self.scheduler_thread = threading.Thread(
            target=self._run_scheduler, 
            args=(self.exit_event,),
            daemon=True
        )
        self.scheduler_thread.start()
        
        # Start system tray thread
        self.tray_thread = threading.Thread(
            target=self._run_tray_icon,
            daemon=True
        )
        self.tray_thread.start()
        
        self.is_running = True
        print(f"Scheduler started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def stop(self):
        """
        Stop the scheduler thread and system tray icon
        """
        if not self.is_running:
            print("Scheduler is not running")
            return
        
        self.exit_event.set()
        
        if self.icon:
            self.icon.stop()
            
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5.0)
            self.scheduler_thread = None
            
        self.is_running = False
        print(f"Scheduler stopped at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def _run_scheduler(self, exit_event):
        """
        Run the scheduler loop
        
        Args:
            exit_event (threading.Event): Event to signal thread termination
        """
        # Set up scheduled tasks
        self._setup_tasks()
        
        # Run the scheduler loop
        while not exit_event.is_set():
            schedule.run_pending()
            time.sleep(1)
    
    def _setup_tasks(self):
        """
        Set up scheduled tasks
        """
        # Clear any existing jobs
        schedule.clear()
        
        # Daily email report at 4:00 PM
        schedule.every().day.at("16:00").do(send_scheduled_email)
        
        # Weekly tasks - Run every Monday at 9:00 AM
        schedule.every().monday.at("09:00").do(self._weekly_cleanup_task)
        
        # Monthly tasks - Run on the 1st day of each month at 1:00 AM
        schedule.every().month.at("01:00").do(self._monthly_report_task)
        
        print("Scheduled tasks have been set up")
    
    def _weekly_cleanup_task(self):
        """
        Perform weekly cleanup tasks
        """
        print(f"Running weekly cleanup task at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        # Implement weekly cleanup logic here
        return True
    
    def _monthly_report_task(self):
        """
        Generate monthly reports
        """
        print(f"Running monthly report task at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        # Implement monthly report generation logic here
        return True
    
    def add_task(self, schedule_spec, task_func):
        """
        Add a custom task to the scheduler
        
        Args:
            schedule_spec: A schedule specification (e.g., schedule.every().day.at("10:00"))
            task_func: Function to execute
            
        Returns:
            schedule: The schedule job
        """
        return schedule_spec.do(task_func)
    
    def _run_tray_icon(self):
        """
        Create and run system tray icon
        """
        try:
            # Create menu
            menu = Menu(
                item('Send Email Now', self._on_send_now),
                item('Exit', self._on_exit)
            )
            
            # Try to load the icon file
            try:
                image = Image.open("hed.ico")
            except FileNotFoundError:
                # Create a basic square icon if file not found
                image = Image.new('RGB', (64, 64), color=(73, 109, 137))
            
            # Create and run the system tray icon
            self.icon = Icon("Headset Monitor", image, "Headset Loan System", menu)
            self.icon.run()
            
        except Exception as e:
            print(f"Error creating system tray icon: {e}")
    
    def _on_send_now(self, icon, item):
        """
        Handle 'Send Email Now' menu item click
        
        Args:
            icon: Icon instance
            item: Menu item instance
        """
        print("Sending email now...")
        threading.Thread(target=send_scheduled_email).start()
    
    def _on_exit(self, icon, item):
        """
        Handle 'Exit' menu item click
        
        Args:
            icon: Icon instance
            item: Menu item instance
        """
        self.exit_event.set()
        icon.stop()

# For backwards compatibility
def run_schedule(exit_event):
    """
    Legacy function to run the scheduler directly
    
    Args:
        exit_event (threading.Event): Event to signal thread termination
    """
    schedule.every().day.at("16:00").do(send_scheduled_email)
    while not exit_event.is_set():
        schedule.run_pending()
        time.sleep(2)