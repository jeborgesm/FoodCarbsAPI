from . import db
from sqlalchemy import Index, func
from sqlalchemy.orm import relationship

class Food(db.Model):
    """
    Food model represents the food items with their nutritional information.
    """
    __tablename__ = 'foods'
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(255), nullable=False, index=True)
    carbohydrates_100g = db.Column(db.Float, nullable=False)
    serving_size = db.Column(db.String(255), nullable=True)
    serving_quantity = db.Column(db.Float, nullable=True)
    countries = db.Column(db.String(255), nullable=True)
    image_nutrition_url = db.Column(db.String(255), nullable=True)

    # Add an index to the product_name column
    __table_args__ = (
        Index('ix_product_name', 'product_name'),
    )

    def __repr__(self):
        return f'<Food {self.product_name}>'

    def to_dict(self):
        """
        Convert the Food object to a dictionary.
        """
        return {
            'id': self.id,
            'product_name': self.product_name,
            'carbohydrates_100g': self.carbohydrates_100g,
            'serving_size': self.serving_size,
            'serving_quantity': self.serving_quantity,
            'countries': self.countries,
            'image_nutrition_url': self.image_nutrition_url
        }

