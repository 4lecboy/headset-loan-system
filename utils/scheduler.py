"""
Scheduler utilities for running periodic tasks
"""
import threading
import schedule
import time
from datetime import datetime
from utils.email_sender import send_scheduled_email

class SchedulerManager:
    """
    Manager class for scheduling and running periodic tasks
    """
    def __init__(self):
        self.exit_event = threading.Event()
        self.scheduler_thread = None
        self.is_running = False
    
    def start(self):
        """
        Start the scheduler thread
        """
        if self.is_running:
            print("Scheduler is already running")
            return
        
        self.exit_event.clear()
        self.scheduler_thread = threading.Thread(
            target=self._run_scheduler, 
            args=(self.exit_event,),
            daemon=True
        )
        self.scheduler_thread.start()
        self.is_running = True
        print(f"Scheduler started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def stop(self):
        """
        Stop the scheduler thread
        """
        if not self.is_running:
            print("Scheduler is not running")
            return
        
        self.exit_event.set()
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
        # Examples:
        # - Archive old logs
        # - Generate weekly reports
        return True
    
    def _monthly_report_task(self):
        """
        Generate monthly reports
        """
        print(f"Running monthly report task at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        # Implement monthly report generation logic here
        # Examples:
        # - Generate comprehensive monthly statistics
        # - Send monthly summary to management
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