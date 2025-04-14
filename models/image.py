from config.database import connect_to_mysql, execute_query
from PIL import Image
import io

def get_image_from_db(image_id):
    """
    Retrieve an image from the database
    
    Args:
        image_id (int): ID of the image to retrieve
        
    Returns:
        tuple: (image_data, PIL.Image) or (None, None) if not found
    """
    query = "SELECT image_data FROM images WHERE id = %s"
    result = execute_query(query, (image_id,), fetch_one=True)
    
    if result:
        image_data = result[0]
        # Convert the raw bytes to a PIL Image object
        image = Image.open(io.BytesIO(image_data))
        return image_data, image
    else:
        print("Image not found.")
        return None, None

def save_image_to_db(image_path, description=None):
    """
    Save an image to the database
    
    Args:
        image_path (str): Path to the image file
        description (str, optional): Image description
        
    Returns:
        int: ID of the saved image or None if failed
    """
    try:
        with open(image_path, 'rb') as file:
            image_data = file.read()
            
        query = "INSERT INTO images (image_data, description) VALUES (%s, %s)"
        conn = connect_to_mysql()
        cursor = conn.cursor()
        
        cursor.execute(query, (image_data, description))
        conn.commit()
        
        # Get the ID of the inserted image
        image_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        
        return image_id
    except Exception as e:
        print(f"Error saving image to database: {e}")
        return None