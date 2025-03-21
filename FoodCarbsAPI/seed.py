import csv
import os
import logging
from FoodCarbsAPI import create_app, db
from FoodCarbsAPI.models import Food

app = create_app()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_data(csv_file_path):
    with app.app_context():
        # Create all tables
        db.create_all()

        # Open the CSV file
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            record_count = 0
            error_count = 0
            for row in reader:
                try:
                    # Convert data types and handle missing values
                    carbohydrates_100g = float(row['carbohydrates_100g']) if row['carbohydrates_100g'] else None
                    serving_quantity = float(row['serving_quantity']) if row['serving_quantity'] else None
                    serving_size = row['serving_size'][:100] if row['serving_size'] else None  # Truncate to 100 characters

                    # Create a new Food object for each row in the CSV
                    food = Food(
                        product_name=row['product_name'],
                        carbohydrates_100g=carbohydrates_100g,
                        serving_size=serving_size,
                        serving_quantity=serving_quantity,
                        countries=row['countries'],
                        image_nutrition_url=row['image_nutrition_url']
                    )
                    # Add the Food object to the session
                    db.session.add(food)
                    record_count += 1
                except Exception as e:
                    logger.error(f"Error processing row: {row}, error: {e}")
                    error_count += 1

            # Commit the session to save the data to the database
            db.session.commit()
            logger.info(f"Total records processed: {record_count}")
            logger.info(f"Total records with errors: {error_count}")

if __name__ == '__main__':
    csv_file_path = os.path.join(os.path.dirname(__file__), 'Foods.csv')
    seed_data(csv_file_path)
