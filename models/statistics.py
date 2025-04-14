from config.database import connect_to_mysql, execute_query

class StatisticsModel:
    def get_headset_stats(self, start_date, end_date):
        """
        Get headset statistics for a date range
        
        Args:
            start_date (str): Start date (YYYY-MM-DD)
            end_date (str): End date (YYYY-MM-DD)
            
        Returns:
            list: List of tuples with date, issued count, and returned count
        """
        query = """
        SELECT DATE(DateIssued) as DateIssued, 
               SUM(CASE WHEN Status = 'Issued' THEN 1 ELSE 0 END) AS Issued, 
               SUM(CASE WHEN Status = 'Returned' THEN 1 ELSE 0 END) AS Returned 
        FROM sentrecords 
        WHERE DATE(DateIssued) >= %s 
        AND DATE(DateIssued) <= %s 
        GROUP BY DATE(DateIssued)
        """
        return execute_query(query, (start_date, end_date))
    
    def count_total_headsets(self):
        """
        Count the total number of headsets in the system
        
        Returns:
            int: Total number of headsets
        """
        query = "SELECT COUNT(*) FROM storage_list"
        result = execute_query(query, fetch_one=True)
        return result[0] if result else 0
    
    def count_issued_headsets(self):
        """
        Count the number of currently issued headsets
        
        Returns:
            int: Number of issued headsets
        """
        query = "SELECT COUNT(*) FROM storage_list WHERE Flag = 0"
        result = execute_query(query, fetch_one=True)
        return result[0] if result else 0
    
    def count_available_headsets(self):
        """
        Count the number of available headsets
        
        Returns:
            int: Number of available headsets
        """
        query = "SELECT COUNT(*) FROM storage_list WHERE Flag = 1"
        result = execute_query(query, fetch_one=True)
        return result[0] if result else 0
    
    def count_never_returned(self):
        """
        Count headsets that have never been returned
        
        Returns:
            int: Number of never-returned headsets
        """
        query = """
        SELECT COUNT(*) FROM sentrecords 
        WHERE Status = 'Issued' 
        AND DATEDIFF(CURRENT_DATE(), DateIssued) > 30
        """
        result = execute_query(query, fetch_one=True)
        return result[0] if result else 0
    
    def get_top_borrowers(self, limit=5):
        """
        Get top borrowers based on number of borrowed items
        
        Args:
            limit (int): Number of top borrowers to return
            
        Returns:
            list: List of (name, count) tuples
        """
        query = """
        SELECT Name, COUNT(*) as count 
        FROM sentrecords 
        GROUP BY Name 
        ORDER BY count DESC 
        LIMIT %s
        """
        return execute_query(query, (limit,))
    
    def get_most_borrowed_headsets(self, limit=5):
        """
        Get most frequently borrowed headsets
        
        Args:
            limit (int): Number of headsets to return
            
        Returns:
            list: List of (asset_tag, count) tuples
        """
        query = """
        SELECT AssetTag, COUNT(*) as count 
        FROM sentrecords 
        GROUP BY AssetTag 
        ORDER BY count DESC 
        LIMIT %s
        """
        return execute_query(query, (limit,))
    
    def get_exportable_stats(self, start_date, end_date):
        """
        Get comprehensive statistics for export
        
        Args:
            start_date (str): Start date (YYYY-MM-DD)
            end_date (str): End date (YYYY-MM-DD)
            
        Returns:
            list: List of dictionaries with statistical data
        """
        query = """
        SELECT 
            DATE(sr.DateIssued) as Date,
            COUNT(CASE WHEN sr.Status = 'Issued' THEN 1 END) as Issued,
            COUNT(CASE WHEN sr.Status = 'Returned' THEN 1 END) as Returned,
            AVG(CASE WHEN sr.Status = 'Returned' 
                THEN TIMESTAMPDIFF(HOUR, sr.DateIssued, sr.ReturnedDate) 
                ELSE NULL END) as AvgReturnTimeHours,
            COUNT(DISTINCT sr.AshimaID) as UniqueUsers,
            COUNT(DISTINCT sr.Campaign) as Campaigns
        FROM 
            sentrecords sr
        WHERE 
            DATE(sr.DateIssued) BETWEEN %s AND %s
        GROUP BY 
            Date
        ORDER BY 
            Date
        """
        results = execute_query(query, (start_date, end_date))
        
        # Convert to list of dictionaries for easier handling
        if not results:
            return []
            
        stats = []
        for row in results:
            stats.append({
                'Date': row[0].strftime('%Y-%m-%d') if row[0] else None,
                'Issued': row[1] or 0,
                'Returned': row[2] or 0,
                'AvgReturnTimeHours': float(row[3]) if row[3] else 0,
                'UniqueUsers': row[4] or 0,
                'Campaigns': row[5] or 0
            })
            
        return stats