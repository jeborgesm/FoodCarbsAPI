from . import db

class Food(db.Model):
    __tablename__ = 'foods'
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(255), nullable=False)
    carbohydrates_100g = db.Column(db.Float, nullable=True)
    serving_size = db.Column(db.String(100), nullable=True)  # Increased length to 100
    serving_quantity = db.Column(db.Float, nullable=True)
    countries = db.Column(db.String(255), nullable=True)
    image_nutrition_url = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<Food {self.product_name}>'


