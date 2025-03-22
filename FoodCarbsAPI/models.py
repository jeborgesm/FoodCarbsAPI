from . import db
from sqlalchemy import Index

class Food(db.Model):
    __tablename__ = 'foods'
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(255), index=True)  # Add index=True
    carbohydrates_100g = db.Column(db.Float)
    serving_size = db.Column(db.String(255))
    serving_quantity = db.Column(db.Float)
    countries = db.Column(db.String(255))
    image_nutrition_url = db.Column(db.String(255))

    # Add an index to the product_name column
    __table_args__ = (
        Index('ix_product_name', 'product_name'),
    )


    def __repr__(self):
        return f'<Food {self.product_name}>'


